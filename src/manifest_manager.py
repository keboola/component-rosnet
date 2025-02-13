import logging
from keboola.component.base import ComponentBase
from file_manager import FileManager, FileMetadata

class ManifestManager:
    """Handles the generation of Keboola manifest files."""

    PRIMARY_KEYS = {
        "food_products": ["ProductId", "ProductDetailId"],
        "general_dayparts": ["Id"],
        "general_employees": ["Id"],
        "general_locations": ["Id"],
    }

    def __init__(self, component: ComponentBase, file_manager: FileManager):
        self.component = component
        self.file_manager = file_manager

    def get_primary_keys(self, dataset_name: str) -> list[str]:
        """Returns the primary keys for a given dataset."""
        return self.PRIMARY_KEYS.get(dataset_name, ["Id"])

    def create_manifest(self, group: str, endpoint: str):
        """
        Generates a Keboola manifest file for a dataset.
        Uses FileManager to ensure consistent file naming.
        """
        file_metadata = self.file_manager.get_file_metadata(group, endpoint)

        output_table = self.component.create_out_table_definition(
            file_metadata.file_name,
            incremental=True,
            primary_key=self.get_primary_keys(endpoint),
            destination=f"out.c-data.{endpoint}",
        )

        self.component.write_manifest(output_table)
        logging.info(f"Manifest created for {file_metadata.file_name}")
