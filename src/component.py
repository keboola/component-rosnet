"""
Keboola Extractor for Rosnet API
"""

import os
import logging

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException
from keboola.http_client import HttpClient

from configuration import Configuration, ENDPOINT_GROUPS
from api_client import RosnetClient, BASE_URL


class Component(ComponentBase):
    def __init__(self):
        super().__init__()

    def run(self):
        config = Configuration(**self.configuration.parameters)
        http_client = HttpClient(BASE_URL)
        client = RosnetClient(config, http_client)

        output_dir = os.path.join(self.configuration.data_dir, "out", "tables")
        os.makedirs(output_dir, exist_ok=True)

        for group in config.sync_options.datasets:
            if group not in ENDPOINT_GROUPS:
                raise UserException(f"Invalid dataset group: {group}")

            for endpoint in ENDPOINT_GROUPS[group]:
                client.extract_and_save(group, endpoint, output_dir)

        logging.info("Data extraction complete")


"""
Main entrypoint
"""
if __name__ == "__main__":
    try:
        comp = Component()
        # this triggers the run method by default and is controlled by the configuration.action parameter
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
