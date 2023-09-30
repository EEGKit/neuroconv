"""Unit tests for the DatasetInfo Pydantic model."""
from io import StringIO
from unittest.mock import patch

from neuroconv.tools.testing import mock_DatasetInfo


def test_dataset_info_print():
    """Test the printout display of a Dataset model looks nice."""
    dataset_info = mock_DatasetInfo()

    with patch("sys.stdout", new=StringIO()) as out:
        print(dataset_info)

    expected_print = """
acquisition/TestElectricalSeries/data
-------------------------------------
  full_shape: (1800000, 384)
  dtype: int16
"""
    assert out.getvalue() == expected_print


def test_dataset_info_repr():
    """Test the programmatic repr of a Dataset model is more dataclass-like."""
    dataset_info = mock_DatasetInfo()

    # Important to keep the `repr` unmodified for appearance inside iterables of DatasetInfo objects
    expected_repr = (
        "DatasetInfo(object_id='481a0860-3a0c-40ec-b931-df4a3e9b101f', "
        "location='acquisition/TestElectricalSeries/data', full_shape=(1800000, 384), dtype=dtype('int16'))"
    )
    assert repr(dataset_info) == expected_repr


def test_dataset_info_hashability():
    dataset_info = mock_DatasetInfo()

    test_dict = {dataset_info: True}  # Technically this alone would raise an error if it didn't work...
    assert test_dict[dataset_info] is True  # ... but asserting this for good measure.