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


PRIMARY_KEYS = {
    "food_products": ["ProductId", "ProductDetailId"],
    "general_dayparts": ["Id"],
    "general_employees": ["Id"],
    "general_locations": ["Id"],
}


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

    def create_keboola_manifest(self, file_name, dataset_name):
        """
        Generates a Keboola manifest file for the extracted dataset.
        """
        output_table = self.create_out_table_definition(
            file_name,
            primary_key=PRIMARY_KEYS.get(dataset_name, []),
            incremental=True,
            destination=f"out.c-data.{dataset_name}",
        )

        # Write the manifest file
        self.write_manifest(output_table)
        logging.info(f"Manifest created for {file_name}")

    def run(self):
        """
        Main execution code
        """
        config = Configuration(**self.configuration.parameters)
        http_client = HttpClient(BASE_URL)
        client = RosnetClient(config, http_client)

        output_dir = os.path.join(self.configuration.data_dir, "out", "tables")
        os.makedirs(output_dir, exist_ok=True)

        for group in config.sync_options.datasets:
            if group not in ENDPOINT_GROUPS:
                raise UserException(f"Invalid dataset group: {group}")

            for endpoint in ENDPOINT_GROUPS[group]:
                file_name = f"{endpoint}.csv"

                client.extract_and_save(group, endpoint, output_dir)

                self.create_keboola_manifest(file_name, endpoint)

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
