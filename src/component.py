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
from manifest_manager import ManifestManager
from file_manager import FileManager


class Component(ComponentBase):
    """
        Extends base class for general Python components.
        Initializes the CommonInterface and performs configuration validation.

        For easier debugging the data folder is picked up by default
        from `../data` path, relative to working directory.

        If `debug` parameter is present in the `config.json`,
        the default logger is set to verbose DEBUG mode.
    """

    def __init__(self):
        super().__init__()

    def run(self):
        """
        Main execution code
        """
        config = Configuration(**self.configuration.parameters)
        http_client = HttpClient(BASE_URL)
        client = RosnetClient(config, http_client)

        output_dir = os.path.join(self.configuration.data_dir, "out", "tables")
        os.makedirs(output_dir, exist_ok=True)

        file_manager = FileManager(output_dir)
        manifest_manager = ManifestManager(self, file_manager)

        for group in config.sync_options.datasets:
            if group not in ENDPOINT_GROUPS:
                raise UserException(f"Invalid dataset group: {group}")

            for endpoint in ENDPOINT_GROUPS[group]:
                file_metadata = file_manager.get_file_metadata(group, endpoint)

                client.extract_and_save(group, endpoint, file_metadata.file_path)

                manifest_manager.create_manifest(group, endpoint)

            logging.info("Data extraction complete")


"""
Main entrypoint
"""
if __name__ == "__main__":
    try:
        comp = Component()
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
