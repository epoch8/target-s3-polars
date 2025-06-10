"""S3 target sink class, which handles writing streams."""

from __future__ import annotations

from singer_sdk.sinks import BatchSink

import os
import polars as pl
import fsspec
from datetime import datetime 


class S3PolarsSink(BatchSink):
    """S3Polars target sink class."""

    def __init__(self, target, stream_name, schema, key_properties):
        super().__init__(target, stream_name, schema, key_properties)

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

        self.pl_batches[f'{self.stream_name}-{context["batch_id"]}'] = pl.DataFrame()

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

        # import logging
        # logger = logging.Logger("PROCESS_RECORD")
        # logger.warning(f'CONTEXT: {context}')
        # logger.warning(f'STREAM_NAME: {self.stream_name}')
        # logger.warning(f'{self.stream_name}-{context["batch_id"]}')
        # logger.warning(f'RECORD: {record}')

        self.pl_batches[f'{self.stream_name}-{context["batch_id"]}'] = pl.concat(
            [
                self.pl_batches[f'{self.stream_name}-{context["batch_id"]}'],
                # pl.from_dicts([record]),
                pl.from_dicts([{"record": f"{record}"}]),
            ],
            how="diagonal_relaxed"
        )

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

        with fsspec.open(output_file, "wb") as f:
            self.pl_batches[f'{self.stream_name}-{context["batch_id"]}'].write_parquet(f, compression="snappy")
