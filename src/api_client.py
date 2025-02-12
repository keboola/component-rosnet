import logging
import csv

from keboola.component import UserException
from typing import Any
from keboola.http_client import HttpClient
from configuration import Configuration, ENDPOINT_GROUPS

BASE_URL = "https://api.rosnet.com"


class RosnetClient:
    """Client for Rosnet API"""

    def __init__(self, config: Configuration, http_client: HttpClient):
        self.config = config
        self.http_client = http_client
        self.auth_header = {
            "Authorization": f"Basic {config.authentication.get_auth_token}"
        }

    def build_query_params(
        self,
        group_name: str,
        endpoint_name: str
    ) -> list[dict]:
        """Constructs query parameters dynamically based on user config"""
        group = ENDPOINT_GROUPS.get(group_name)
        if not group:
            raise UserException(f"Unknown group: {group_name}")

        endpoint = group.get(endpoint_name)
        if not endpoint:
            raise UserException(
                f"Unknown endpoint: {endpoint_name} in group: {group_name}"
            )

        base_params = {
            key: str(getattr(self.config.sync_options, value))
            for key, value in endpoint.query_params.items()
            if not isinstance(getattr(self.config.sync_options, value, None), list)
        }
        multi_requests = []

        for key, value in endpoint.query_params.items():
            param_value = getattr(self.config.sync_options, value, None)

            if isinstance(param_value, list):
                for single_value in param_value:
                    request_params = base_params.copy()
                    request_params[key] = str(single_value)
                    multi_requests.append(request_params)
            elif param_value:
                base_params[key] = str(param_value)

        return multi_requests if multi_requests else ([base_params] if base_params else [{}])

    def fetch_paginated_data(
        self,
        group: str,
        endpoint: str
    ) -> list[dict[str, Any]]:
        """Fetches paginated data from Rosnet API"""
        url = f"{ENDPOINT_GROUPS[group][endpoint].path}"
        all_data = []

        for request_params in self.build_query_params(group, endpoint):
            if not isinstance(request_params, dict):
                raise UserException(f"Query parameters should be a dictionary, got {type(request_params)}")

            cursor = None
            while True:
                params = request_params.copy()
                if cursor:
                    params["cursor"] = str(cursor)

                params["limit"] = self.config.sync_options.api_limit

                response = self.http_client.get_raw(
                    url,
                    params=params,
                    headers=self.auth_header
                )

                try:
                    response_data = response.json()
                except ValueError:
                    raise UserException(f"Failed to parse JSON response from {url}")

                if not isinstance(response_data, list):
                    raise UserException(
                        f"Unexpected response format from {url}: Expected list, got {type(response_data)}"
                    )

                all_data.extend(response_data)
                cursor = response.headers.get("cursor", None)  # Explicit None handling

                if not cursor:  # Ensure pagination stops correctly
                    break

        return all_data

    def extract_and_save(self, group: str, endpoint: str, file_path: str):
        """Fetches data from an API endpoint and writes it to CSV"""
        logging.info(f"Fetching {endpoint} from {group} dataset")
        data = self.fetch_paginated_data(group, endpoint)

        if not data:
            logging.info(f"No data found for {group}/{endpoint}")
            return

        logging.info(f"Saving {len(data)} records to {file_path}")
        self._save_to_csv(file_path, data)

    @staticmethod
    def _save_to_csv(file_path: str, data: list[dict]):
        """Helper method to write data to CSV file"""
        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
