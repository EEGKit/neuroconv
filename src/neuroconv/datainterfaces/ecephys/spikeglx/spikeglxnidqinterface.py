"""Authors: Cody Baker."""
import json
from pathlib import Path
from typing import List

import numpy as np
from pynwb.ecephys import ElectricalSeries

from .spikeglxdatainterface import SpikeGLXRecordingInterface
from .spikeglx_utils import get_session_start_time
from ....tools.signal_processing import parse_rising_and_falling_frames_from_ttl
from ....utils import get_schema_from_method_signature, get_schema_from_hdmf_class, FilePathType, dict_deep_update


class SpikeGLXNIDQInterface(SpikeGLXRecordingInterface):
    """Primary data interface class for converting the high-pass (ap) SpikeGLX format."""

    @classmethod
    def get_source_schema(cls):
        source_schema = get_schema_from_method_signature(class_method=cls.__init__, exclude=["x_pitch", "y_pitch"])
        source_schema["properties"]["file_path"]["description"] = "Path to SpikeGLX .nidq file."
        return source_schema

    def __init__(
        self,
        file_path: FilePathType,
        stub_test: bool = False,
        spikeextractors_backend: bool = False,
        verbose: bool = True,
    ):
        """
        Read channel data from the NIDQ board for the SpikeGLX recording.

        Useful for synchronizing multiple data streams into the common time basis of the SpikeGLX system.

        Parameters
        ----------
        file_path: FilePathType
            Path to .nidq.bin file.
        stub_test: bool
            Whether to shorten file for testing purposes. Default: False.
        verbose: bool
            Whether to output verbose text. Default: True.
        """
        self.stream_id = "nidq"

        folder_path = Path(file_path).parent
        super(SpikeGLXRecordingInterface, self).__init__(
            folder_path=folder_path, stream_id=self.stream_id, verbose=verbose
        )
        self.source_data.update(file_path=str(file_path))

        self.meta = self.recording_extractor.neo_reader.signals_info_dict[(0, self.stream_id)]["meta"]

    def get_metadata_schema(self):
        metadata_schema = super().get_metadata_schema()
        metadata_schema["properties"]["Ecephys"]["properties"].update(
            ElectricalSeriesRaw=get_schema_from_hdmf_class(ElectricalSeries)
        )
        return metadata_schema

    def get_metadata(self):
        metadata = super().get_metadata()
        session_start_time = get_session_start_time(self.meta)
        if session_start_time:
            metadata = dict_deep_update(metadata, dict(NWBFile=dict(session_start_time=session_start_time)))

        # Device metadata
        metadata = dict(Ecephys=dict())
        device_key = "niDev1ProductName"  # At least, this is true for the GIN test data
        if device_key in self.meta:
            header_metadata = dict(self.meta)
            for exclude_key in ["fileCreateTime", device_key]:
                header_metadata.pop(exclude_key)
            device = dict(
                name=self.meta[device_key],
                description=json.dumps(header_metadata),
                manufacturer="National Instruments",
            )
            metadata["Ecephys"].get("Device", list()).append(Device=device)

        # Add groups metadata
        group_names = self.recording_extractor.get_property("group_name")
        if self.recording_extractor.get_property("group_name") is None:
            electrode_groups = [
                dict(
                    name="NIDQChannelGroup",
                    description="A group representing the NIDQ channels.",
                    location="unknown",
                    device=device["name"],
                )
            ]
        else:
            electrode_groups = [
                dict(
                    name=group_name,
                    description="A group representing the NIDQ channels.",
                    location="unknown",
                    device=device["name"],
                )
                for group_name in set(group_names)
            ]
        metadata["Ecephys"].get("ElectrodeGroup", list()).extend(electrode_groups)

        # Electrodes columns descriptions
        metadata["Ecephys"]["Electrodes"] = [
            dict(name="group_name", description="Name of the ElectrodeGroup this electrode is a part of."),
        ]

        metadata["Ecephys"]["ElectricalSeriesNIDQ"] = dict(
            name="ElectricalSeriesNIDQ", description="Raw acquisition traces from the NIDQ (.nidq.bin) channels."
        )
        return metadata

    def get_channel_names(self) -> List[str]:
        """Return a list of channel names as set in the recording extractor."""
        return list(self.recording_extractor.get_channel_ids())

    def get_event_starting_times_from_ttl(self, channel_name: str) -> np.ndarray:
        """
        Return the start of event times from the rising part of TTL pulses on one of the NIDQ channels.

        Parameters
        ----------
        channel_name : int
            Name of the channel in the .nidq.bin file.

        Returns
        -------
        rising_times: numpy.ndarray
            The times of the rising TTL pulse; often used as the start time of the event.
        """
        # TODO: consider RAM cost of these operations and implement safer buffering version
        rising_frames, _ = parse_rising_and_falling_frames_from_ttl(
            trace=self.recording_extractor.get_traces(chanel_id=[channel_name])
        )

        nidq_timestamps = self.recording_extractor.get_times()
        rising_times = nidq_timestamps[rising_frames]

        return rising_times

    def get_conversion_options(self):
        conversion_options = super().get_conversion_options()
        conversion_options.update(es_key="ElectricalSeriesSync")
        return conversion_options
