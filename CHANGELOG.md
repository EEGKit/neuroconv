# Upcoming

### Fixes
* Prevented the CEDRecordingInterface from writing non-ecephys channel data. [PR #37](https://github.com/catalystneuro/neuroconv/pull/37)

### Improvements
* Unified the `run_conversion` method of `BaseSegmentationExtractorInterface` with that of all the other base interfaces. The method `write_segmentation` now uses the common `make_or_load_nwbfile` context manager [PR #29](https://github.com/catalystneuro/neuroconv/pull/29)
* Coerced the recording extractors with `spikeextractors_backend=True` to BaseRecording objects for Axona, Blackrock, Openephys, and SpikeGadgets. [PR #38](https://github.com/catalystneuro/neuroconv/pull/38)
* Added function to add PlaneSegmentation objects to an nwbfile in `roiextractors` and corresponding unit tests. [PR #23](https://github.com/catalystneuro/neuroconv/pull/23)
* `use_times` argument to be deprecated on the ecephys pipeline. The function `add_electrical_series` now determines whether the timestamps of the spikeinterface recording extractor are uniform or not and automatically stores the data according to best practices [PR #40](https://github.com/catalystneuro/neuroconv/pull/40)
* Add `NWBFile` metadata key at the level of the base data interface so it can always be inherited to be available. [PR #51](https://github.com/catalystneuro/neuroconv/pull/51)

## Documentation and tutorial enhancements:
* Unified the documentation of NeuroConv structure in the User Guide readthedocs. [PR #39](https://github.com/catalystneuro/neuroconv/pull/39)

### Features
* Added conversion interface for DeepLabCut data together with unit tests and a conversion example in the gallery. [PR #24](https://github.com/catalystneuro/neuroconv/pull/24)
* Allow writing of offsets to ElectricalSeries obects from SpikeInterface (requires PyNWB>=2.1.0). [PR #37](https://github.com/catalystneuro/neuroconv/pull/37)
* Added conversion interface for EDF (European Data Format) data together with corresponding unit tests and a conversion example in the gallery. [PR #45](https://github.com/catalystneuro/neuroconv/pull/45)
* Created ImagingExtractorDataChunkIterator, a data chunk iterator for `ImagingExtractor` objects. [PR #54](https://github.com/catalystneuro/neuroconv/pull/54)

### Testing
* Added unittests for correctly writing the scaling factors to the nwbfile in the `add_electrical_series` function of the spikeinterface module. [PR #37](https://github.com/catalystneuro/neuroconv/pull/37)

# v0.1.1
### Fixes
* Fixed the behavior of the `file_paths` usage in the MovieInterface when run via the YAML conversion specification. [PR #33](https://github.com/catalystneuro/neuroconv/pull/33)

### Improvements
* Added function to add ImagingPlane objects to an nwbfile in `roiextractors` and corresponding unit tests. [PR #19](https://github.com/catalystneuro/neuroconv/pull/19)
* Added function to add summary images from a `SegmentationExtractor` object to an nwbfile in the roiextractors module and corresponding unit tests [PR #22](https://github.com/catalystneuro/neuroconv/pull/22)
### Features
* Add non-iterative writing capabilities to `add_electrical_series`. [PR #32](https://github.com/catalystneuro/neuroconv/pull/32)

### Testing
* Added unittests for the `write_as` functionality in the `add_electrical_series` of the spikeinterface module. [PR #32](https://github.com/catalystneuro/neuroconv/pull/32)


# v0.1.0

* The first release of NeuroConv.