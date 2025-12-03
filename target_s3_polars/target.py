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
            "filepath",
            th.StringType(nullable=False),
            required=False,
            title="Output File Path",
            description="The path to the target output file. Default: \"target_s3_polars/\".",
            default="target_s3_polars/",
        ),
        th.Property(
            "file_naming_scheme",
            th.StringType(nullable=False),
            required=False,
            title="File Naming Scheme",
            description="The scheme with which output files will be named. Default: \"{stream}-{timestamp}.{format}\".",
            default="{stream}-{timestamp}.{format}",
        ),
        th.Property(
            "batch_size",
            th.IntegerType(nullable=False, minimum=1),
            required=False,
            title="Output File batch size",
            description="Number of records per file. Default: 10000.",
            default=10000,
        ),
        th.Property(
            "record_as_json",
            th.BooleanType(nullable=False),
            required=False,
            title="Save records as one JSON column",
            description="Complicated NoSQL schemas might be saved as one JSON column. Default: False.",
            default=False,
        ),
        th.Property(
            "max_record_age_in_minutes",
            th.IntegerType(nullable=False, minimum=1),
            required=False,
            title="Max record age in minutes",
            description="Max record age in minutes before trigger drain. Default: 5.",
            default=5,
        ),
    ).to_dict()

    default_sink_class = S3PolarsSink

    def __init__(self, *, config = None, parse_env_config = False, validate_config = True, setup_mapper = True, message_reader = None):
        super().__init__(config=config, parse_env_config=parse_env_config, validate_config=validate_config, setup_mapper=setup_mapper, message_reader=message_reader)
        self._MAX_RECORD_AGE_IN_MINUTES = self.config["max_record_age_in_minutes"]


if __name__ == "__main__":
    S3PolarsTarget.cli()
