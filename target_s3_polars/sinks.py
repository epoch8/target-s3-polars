"""S3 target sink class, which handles writing streams."""

from __future__ import annotations

from singer_sdk.sinks import BatchSink

import os
import polars as pl
import fsspec
from datetime import datetime 
import simplejson as json


class S3PolarsSink(BatchSink):
    """S3Polars target sink class."""

    def __init__(self, target, stream_name, schema, key_properties):
        super().__init__(target, stream_name, schema, key_properties)

        self.batches: dict = {}
        self.pl_batches: dict = {}

        os.environ["FSSPEC_S3_ENDPOINT_URL"] = target.config.get("s3_endpoint_url")
        os.environ["FSSPEC_S3_KEY"] = target.config.get("aws_access_key_id")
        os.environ["FSSPEC_S3_SECRET"] = target.config.get("aws_secret_access_key")

    # max_size = 10000  # Max records to write in one batch

    @property
    def max_size(self) -> int:
        """Get max batch size.

        Returns:
            Max number of records to batch before `is_full=True`

        .. versionchanged:: 0.36.0
           This property now takes into account the
           :attr:`~singer_sdk.Sink.batch_size_rows` attribute and the corresponding
           ``batch_size_rows`` target setting.
        """
        # return (
        #     self.batch_size_rows
        #     if self.batch_size_rows is not None
        #     else self.MAX_SIZE_DEFAULT
        # )

        return self.config["batch_size"]

    def start_batch(self, context: dict) -> None:
        """Start a batch.

        Developers may optionally add additional markers to the `context` dict,
        which is unique to this batch.

        Args:
            context: Stream partition or context dictionary.
        """
        # Sample:
        # ------
        # batch_key = context["batch_id"]
        # context["file_path"] = f"{batch_key}.csv"

    def record_as_json(self, batch_name):
        if self.config["record_as_json"]:
            return [
                {"record_as_json": json.dumps(record, use_decimal=True, default=str)}
                for record in self.batches[batch_name]
            ]
        return self.batches[batch_name]

    def dicts_to_pl(self, batch_name):
        if batch_name not in self.pl_batches:
            self.pl_batches[batch_name] = pl.DataFrame(self.record_as_json(batch_name), infer_schema_length=None)
        else:
            self.pl_batches[batch_name] = pl.concat(
                [
                    self.pl_batches[batch_name],
                    pl.DataFrame(self.record_as_json(batch_name), infer_schema_length=None),
                ],
                how="diagonal_relaxed"
            )
        self.batches.pop(batch_name)

    def process_record(self, record: dict, context: dict) -> None:
        """Process the record.

        Developers may optionally read or write additional markers within the
        passed `context` dict from the current batch.

        Args:
            record: Individual record in the stream.
            context: Stream partition or context dictionary.
        """
        # Sample:
        # ------
        # with open(context["file_path"], "a") as csvfile:
        #     csvfile.write(record)

        batch_name = f"{self.stream_name}-{context['batch_id']}"

        if batch_name not in self.batches:
            self.batches[batch_name] = []

        self.batches[batch_name].append(record)

        if len(self.batches[batch_name]) > 10000:
            self.dicts_to_pl(batch_name)

    def process_batch(self, context: dict) -> None:
        """Write out any prepped records and return once fully written.

        Args:
            context: Stream partition or context dictionary.
        """
        # Sample:
        # ------
        # client.upload(context["file_path"])  # Upload file
        # Path(context["file_path"]).unlink()  # Delete local copy

        file_naming_scheme = self.config["file_naming_scheme"].format(
            stream=self.stream_name,
            timestamp=datetime.now().strftime('%Y%m%dT%H%M%S'),
            format="parquet",
        )

        output_file = f"s3://{self.config['filepath']}{file_naming_scheme}"
        batch_name = f"{self.stream_name}-{context['batch_id']}"

        if batch_name in self.batches:
            self.dicts_to_pl(batch_name)

        with fsspec.open(output_file, "wb") as f:
            self.pl_batches[batch_name].write_parquet(f, compression="snappy")

        self.pl_batches.pop(batch_name)
