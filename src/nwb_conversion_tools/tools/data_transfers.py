"""Collection of helper functions for assessing and performing automated data transfers."""
import os
import json
from typing import Dict

try:  # pragma: no cover
    import globus_cli

    HAVE_GLOBUS = True
except ModuleNotFoundError:
    HAVE_GLOBUS = False
assert HAVE_GLOBUS, "You must install the globus CLI (pip install globus-cli)!"


def get_globus_dataset_content_sizes(globus_endpoint_id: str, path: str, recursive: bool = True) -> Dict[str, int]:
    """
    May require external login via 'globus login' from CLI.

    Returns dictionary whose keys are file names and values are sizes in bytes.
    """
    contents = json.loads(os.popen(f"globus ls -Fjson {globus_endpoint_id}:{path} --recursive").read())
    files_and_sizes = {item["name"]: item["size"] for item in contents["DATA"] if item["type"] == "file"}
    return files_and_sizes


def get_s3_conversion_cost(
    total_mb: int,
    transfer_rate_mb: float = 20.0,
    conversion_rate_mb: float = 17.0,
    upload_rate_mb: float = 40,
    compression_ratio=1.7,
):
    """Evaluate potential cost of performing an entire conversion on S3 using full automation."""
    c = 1 / compression_ratio  # compressed_size = total_size * c
    total_mb_s = (
        total_mb**2 / 2 * (1 / transfer_rate_mb + (2 * c + 1) / conversion_rate_mb + 2 * c**2 / upload_rate_mb)
    )
    cost_gb_m = 0.08 / 1e3  # $0.08 / GB Month
    cost_mb_s = cost_gb_m / (1e3 * 2.628e6)  # assuming 30 day month; unsure how amazon weights shorter months?
    return cost_mb_s * total_mb_s
