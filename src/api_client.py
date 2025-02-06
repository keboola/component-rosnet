import logging
import csv
import os

from keboola.component import UserException
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from keboola.http_client import HttpClient
from keboola.component.base import CommonInterface
from configuration import Configuration, ENDPOINT_GROUPS

BASE_URL = "https://api.rosnet.com"

class RosnetClient:
    """Client for Rosnet API"""

    def __init__(self, config: Configuration, http_client: HttpClient):
        self.config = config
        self.http_client = http_client
        self.auth_header = {"Authorization": f"Basic {config.authentication.get_auth_token}"}

    def build_query_params(self, group_name: str, endpoint_name: str) -> list[dict]:
        """Constructs query parameters dynamically based on user config"""
        group = ENDPOINT_GROUPS.get(group_name)
        if not group:
            raise UserException(f"Unknown group: {group_name}")

        endpoint = group.get(endpoint_name)
        if not endpoint:
            raise UserException(f"Unknown endpoint: {endpoint_name} in group: {group_name}")

        base_params = {}
        multi_requests = []

        for key, value in endpoint.query_params.items():
            param_value = getattr(self.config.sync_options, value, None)

            if param_value:
                if isinstance(param_value, list):
                    for single_value in param_value:
                        request_params = base_params.copy()
                        request_params[key] = str(single_value)
                        multi_requests.append(request_params)
                else:
                    base_params[key] = str(param_value)

        return multi_requests if multi_requests else [base_params]


    def fetch_paginated_data(self, group: str, endpoint: str) -> list[dict[str, Any]]:
        """Fetches paginated data from Rosnet API"""
        url = f"{ENDPOINT_GROUPS[group][endpoint].path}"
        all_data = []

        for params in self.build_query_params(group, endpoint):
            if not isinstance(params, dict):
                raise UserException(f"Query parameters should be a dictionary, got {type(params)}")

            cursor = None
            while True:
                if cursor:
                    params["cursor"] = str(cursor)

                params["limit"] = limit = self.config.sync_options.api_limit

                response = self.http_client.get_raw(url, params=params, headers=self.auth_header)

                try:
                    response_data = response.json()
                except ValueError:
                    raise UserException(f"Failed to parse JSON response from {url}")

                if not isinstance(response_data, list):
                    raise UserException(
                        f"Unexpected response format from {url}: Expected list, got {type(response_data)}")

                all_data.extend(response_data)

                cursor = response.headers.get("cursor")

                if not cursor:
                    break

        return all_data


    def extract_and_save(self, group: str, endpoint: str, output_dir: str):
        """Fetches data from an API endpoint and writes it to CSV"""
        logging.info(f"Fetching {endpoint} from {group} dataset")
        data = self.fetch_paginated_data(group, endpoint)

        if not data:
            logging.info(f"No data found for {group}/{endpoint}")
            return

        output_file = os.path.join(output_dir, f"{group}_{endpoint}.csv")
        logging.info(f"Saving {len(data)} records to {output_file}")

        with open(output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)