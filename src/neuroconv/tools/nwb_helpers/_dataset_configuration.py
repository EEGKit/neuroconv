"""Collection of helper functions related to configuration of datasets dependent on backend."""
from typing import Generator, Literal, Union

import h5py
import numpy as np
import zarr
from hdmf.data_utils import DataChunkIterator, DataIO, GenericDataChunkIterator
from hdmf.utils import get_data_shape
from hdmf_zarr import NWBZarrIO
from pynwb import NWBHDF5IO, NWBFile, TimeSeries
from pynwb.base import DynamicTable

from ._models._base_models import DatasetInfo, DatasetIOConfiguration
from ._models._hdf5_models import HDF5BackendConfiguration, HDF5DatasetIOConfiguration
from ._models._zarr_models import ZarrBackendConfiguration, ZarrDatasetIOConfiguration
from ..hdmf import SliceableDataChunkIterator

BACKEND_TO_DATASET_CONFIGURATION = dict(hdf5=HDF5DatasetIOConfiguration, zarr=ZarrDatasetIOConfiguration)
BACKEND_TO_CONFIGURATION = dict(hdf5=HDF5BackendConfiguration, zarr=ZarrBackendConfiguration)


def _get_io_mode(io: Union[NWBHDF5IO, NWBZarrIO]) -> str:
    """NWBHDF5IO and NWBZarrIO have different ways of storing the io mode (e.g. "r", "a", "w") they used on a path."""
    if isinstance(io, NWBHDF5IO):
        return io.mode
    elif isinstance(io, NWBZarrIO):
        return io._ZarrIO__mode


def _is_dataset_written_to_file(
    candidate_dataset: Union[h5py.Dataset, zarr.Array],
    backend: Literal["hdf5", "zarr"],
    existing_file: Union[h5py.File, zarr.Group, None],
) -> bool:
    """
    Determine if the neurodata object is already written to the file on disk.

    This object should then be skipped by the `get_io_datasets` function when working in append mode.
    """
    return (
        isinstance(candidate_dataset, h5py.Dataset)  # If the source data is an HDF5 Dataset
        and backend == "hdf5"
        and candidate_dataset.file == existing_file  # If the source HDF5 Dataset is the appending NWBFile
    ) or (
        isinstance(candidate_dataset, zarr.Array)  # If the source data is an Zarr Array
        and backend == "zarr"
        and candidate_dataset.store == existing_file  # If the source Zarr 'file' is the appending NWBFile
    )


def _get_dataset_metadata(
    neurodata_object: Union[TimeSeries, DynamicTable], field_name: str, backend: Literal["hdf5", "zarr"]
) -> Union[HDF5DatasetIOConfiguration, ZarrDatasetIOConfiguration, None]:
    """Fill in the Dataset model with as many values as can be automatically detected or inferred."""
    DatasetIOConfigurationClass = BACKEND_TO_DATASET_CONFIGURATION[backend]

    candidate_dataset = getattr(neurodata_object, field_name)

    # For now, skip over datasets already wrapped in DataIO
    # Could maybe eventually support modifying chunks in place
    # But setting buffer shape only possible if iterator was wrapped first
    if isinstance(candidate_dataset, DataIO):
        return None

    dataset_configuration = DatasetIOConfigurationClass.from_neurodata_object(
        neurodata_object=neurodata_object, field_name=field_name
    )
    return dataset_configuration


def get_default_dataset_io_configurations(
    nwbfile: NWBFile,
    backend: Union[None, Literal["hdf5", "zarr"]] = None,  # None for auto-detect from append mode, otherwise required
) -> Generator[DatasetIOConfiguration, None, None]:
    """
    Method for automatically detecting all objects in the nfile that could be wrapped in a DataIO.

    Parameters
    ----------
    nwbfile : pynwb.NWBFile
        An in-memory NWBFile object, either generated from the base class or read from an existing file of any backend.
    backend : "hdf5" or "zarr"
        Which backend format type you would like to use in configuring each datasets compression methods and options.

    Yields
    ------
    DatasetIOConfiguration
        A summary of each detected object that can be wrapped in a DataIO.
    """
    if backend is None and nwbfile.read_io is None:
        raise ValueError(
            "Keyword argument `backend` (either 'hdf5' or 'zarr') must be specified if the `nwbfile` was not "
            "read from an existing file!"
        )
    if backend is None and nwbfile.read_io is not None and nwbfile.read_io.mode not in ("r+", "a"):
        raise ValueError(
            "Keyword argument `backend` (either 'hdf5' or 'zarr') must be specified if the `nwbfile` is being appended."
        )

    detected_backend = None
    existing_file = None
    if isinstance(nwbfile.read_io, NWBHDF5IO) and _get_io_mode(io=nwbfile.read_io) in ("r+", "a"):
        detected_backend = "hdf5"
        existing_file = nwbfile.read_io._file
    elif isinstance(nwbfile.read_io, NWBZarrIO) and _get_io_mode(io=nwbfile.read_io) in ("r+", "a"):
        detected_backend = "zarr"
        existing_file = nwbfile.read_io.file.store
    backend = backend or detected_backend

    if detected_backend is not None and detected_backend != backend:
        raise ValueError(
            f"Detected backend '{detected_backend}' for appending file, but specified `backend` "
            f"({backend}) does not match! Set `backend=None` or remove the keyword argument to allow it to auto-detect."
        )

    for neurodata_object in nwbfile.objects.values():
        if isinstance(neurodata_object, DynamicTable):
            dynamic_table = neurodata_object  # for readability

            for column in dynamic_table.columns:
                column_name = column.name
                candidate_dataset = column.data  # VectorData object
                if _is_dataset_written_to_file(
                    candidate_dataset=candidate_dataset, backend=backend, existing_file=existing_file
                ):
                    continue  # skip

                yield _get_dataset_metadata(neurodata_object=column, field_name="data", backend=backend)
        else:
            # Primarily for TimeSeries, but also any extended class that has 'data' or 'timestamps'
            # The most common example of this is ndx-events Events/LabeledEvents types
            time_series = neurodata_object  # for readability

            for field_name in ("data", "timestamps"):
                if field_name not in time_series.fields:  # timestamps is optional
                    continue

                candidate_dataset = getattr(time_series, field_name)
                if _is_dataset_written_to_file(
                    candidate_dataset=candidate_dataset, backend=backend, existing_file=existing_file
                ):
                    continue  # skip

                # Edge case of in-memory ImageSeries with external mode; data is in fields and is empty array
                if isinstance(candidate_dataset, np.ndarray) and candidate_dataset.size == 0:
                    continue  # skip

                yield _get_dataset_metadata(neurodata_object=time_series, field_name=field_name, backend=backend)
