import os
from dataclasses import dataclass


@dataclass
class FileMetadata:
    """Encapsulates output file information"""
    file_name: str
    file_path: str


class FileManager:
    """Handles file path generation for extracted datasets."""

    def __init__(self, output_dir):
        self.output_dir = output_dir

    def get_file_metadata(self, group: str, endpoint: str) -> FileMetadata:
        """Generates file metadata containing name and full path"""
        file_name = f"{group}_{endpoint}.csv"
        file_path = os.path.join(self.output_dir, file_name)

        return FileMetadata(file_name, file_path)
