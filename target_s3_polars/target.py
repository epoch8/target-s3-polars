""". target class."""

from __future__ import annotations

from singer_sdk import typing as th
from singer_sdk.target_base import Target

from target_s3_polars.sinks import (
    Sink,
)


class Target(Target):
    """Sample target for .."""

    name = "target-s3-polars"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "filepath",
            th.StringType(nullable=False),
            title="Output File Path",
            description="The path to the target output file",
        ),
        th.Property(
            "file_naming_scheme",
            th.StringType(nullable=False),
            title="File Naming Scheme",
            description="The scheme with which output files will be named",
        ),
        th.Property(
            "auth_token",
            th.StringType(nullable=False),
            secret=True,  # Flag config as protected.
            required=True,
            title="Auth Token",
            description="The path to the target output file",
        ),
    ).to_dict()

    default_sink_class = Sink


if __name__ == "__main__":
    Target.cli()
