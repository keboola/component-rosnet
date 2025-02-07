import base64
import logging
from typing import Optional, List
# from datetime import date
from pydantic import (
    BaseModel,
    Field,
    field_validator
)


class EndpointConfig(BaseModel):
    path: str
    query_params: dict[str, str] = {}


ENDPOINT_GROUPS = {
    "general": {
        "locations": EndpointConfig(
            path="/general/locations",
            query_params={"id": "location_ids"}
        ),
        "employees": EndpointConfig(
            path="/general/employees",
            query_params={"locationId": "location_ids"}
        ),
        "dayparts": EndpointConfig(
            path="/general/dayparts",
            query_params={}
        )
    },
    "food": {
        "products": EndpointConfig(
            path="/food/products",
            query_params={}
        )
    }
}


class Authentication(BaseModel):
    api_user: str
    api_password: str = Field(alias="#api_password")

    @field_validator("api_user", "api_password")
    def must_not_be_empty(cls, value: str, info) -> str:
        if not value.strip():
            raise ValueError(f"Field '{info.field_name}' cannot be empty")
        return value

    @property
    def get_auth_token(self) -> str:
        credentials = f"{self.api_user}:{self.api_password}"
        return base64.b64encode(credentials.encode()).decode()


class Location(BaseModel):
    location_ids: Optional[List[int]] = Field(
        None,
        description="List of location IDs (Optional)"
    )


class SyncOptions(BaseModel):
    datasets: list[str] = Field(
        default=[],
        description="List of datasets to fetch, e.g. ['general']"
    )
    # date_from: str = Field(
    #     default="2020-01-01",
    #     description="Start date, defaults to '2020-01-01' if not provided"
    # )
    # date_to: str = Field(
    #     default_factory=lambda: str(date.today()),
    #     description="End date, defaults to today"
    # )
    api_limit: int = Field(
        default=100,
        description=(
            "Number of records per request, "
            "defaults to 100 if not specified"
        )
    )

    @field_validator("datasets")
    def validate_datasets(cls, value: List[str]) -> List[str]:
        supported_values = {"general", "food"}

        if not isinstance(value, list):
            raise ValueError("datasets must be a list of strings")

        invalid_values = [
            dataset for dataset in value if dataset not in supported_values
        ]

        if invalid_values:
            raise ValueError(
                f"Invalid dataset(s) {invalid_values}. "
                f"Supported values: {supported_values}"
            )

        return value

    # @field_validator("date_from", "date_to")
    # def validate_dates(cls, value: str) -> str:
    #     try:
    #         date.fromisoformat(value)
    #     except ValueError:
    #         raise ValueError(
    #             f"Invalid date format for {value}, expected 'YYYY-MM-DD'"
    #         )
    #     return value


class Configuration(BaseModel):
    authentication: Authentication
    # location: Location
    sync_options: SyncOptions
    debug: bool = False


def __init__(self, **data):
    if self.debug:
        logging.debug("Component will run in Debug mode")
