"""Authors: Cody Baker and Ben Dichter."""
from abc import abstractmethod

from .utils import get_schema_from_method_signature


class BaseDataInterface:

    @classmethod
    @abstractmethod
    def get_input_schema(cls):
        pass

    def __init__(self, **input_args):
        self.input_args = input_args

    @abstractmethod
    def get_metadata_schema(self):
        pass

    @abstractmethod
    def get_metadata(self):
        pass

    def get_conversion_options_schema(self):
        return get_schema_from_method_signature(self.convert_data, exclude=('nwbfile', 'metadata_dict'))

    @abstractmethod
    def convert_data(self, nwbfile_path, metadata_dict, **conversion_options):
        pass
