""". target class."""

from __future__ import annotations

from singer_sdk import typing as th
from singer_sdk.target_base import Target

from target_s3_polars.sinks import (
    S3PolarsSink,
)


class S3PolarsTarget(Target):
    """Sample target for S3PolarsSink."""

    name = "target-s3-polars"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "aws_access_key_id",
            th.StringType(nullable=False),
            secret=True,  # Flag config as protected.
            required=True,
            title="AWS access key id",
            description="AWS access key id",
        ),
        th.Property(
            "aws_secret_access_key",
            th.StringType(nullable=False),
            secret=True,  # Flag config as protected.
            required=True,
            title="AWS secret access key",
            description="AWS secret access key",
        ),
        th.Property(
            "s3_endpoint_url",
            th.StringType(nullable=False),
            required=True,
            title="S3 endpoint URL",
            description="S3 endpoint URL",
        ),
        th.Property(
            "s3_bucket",
            th.StringType(nullable=False),
            required=True,
            title="S3 bucket name",
            description="S3 bucket name",
        ),
        th.Property(
            "filepath",
            th.StringType(nullable=False),
            required=False,
            title="Output File Path",
            description="The path to the target output file",
            default="target_s3_polars/",
        ),
        th.Property(
            "file_naming_scheme",
            th.StringType(nullable=False),
            required=False,
            title="File Naming Scheme",
            description="The scheme with which output files will be named",
            default="{stream}-{timestamp}.{format}",
        ),
        th.Property(
            "batch_size",
            th.IntegerType(nullable=False),
            required=False,
            title="Output File batch size",
            description="Number of records per file",
            default=10000,
        ),
    ).to_dict()

    default_sink_class = S3PolarsSink


if __name__ == "__main__":
    S3PolarsTarget.cli()
