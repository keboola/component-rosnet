import base64
import logging
from datetime import date
from typing import Optional, List
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
        "accounts": EndpointConfig(
            path="/food/definitions/accounts",
            query_params={}
        ),
        "account_categories": EndpointConfig(
            path="/food/definitions/acctCategories",
            query_params={}
        ),
        "vendors": EndpointConfig(
            path="/food/definitions/vendors",
            query_params={}
        ),
        "transaction_types": EndpointConfig(
            path="/food/definitions/transactionTypes",
            query_params={}
        ),
        "inventory_status_types": EndpointConfig(
            path="/food/definitions/invStatusTypes",
            query_params={}
        ),
        "product_measure_units": EndpointConfig(
            path="/food/definitions/productUOMs",
            query_params={}
        ),
        "products": EndpointConfig(
            path="/food/products",
            query_params={}
        ),
        "inventory_status": EndpointConfig(
            path="/food/inventoryStatus",
            query_params={
                "locationId": "location_ids",
                "startDate": "start_date"
            }
        ),
        "inventory_products": EndpointConfig(
            path="/food/inventoryProducts",
            query_params={
                "locationId": "location_ids",
                "invPeriodDate": "start_date"
            }
        ),
        "period_qfactor": EndpointConfig(
            path="/food/periodQFactor",
            query_params={
                "locationId": "location_ids",
                "invPeriodDate": "start_date"
            }
        ),
        "product_purchases": EndpointConfig(
            path="/food/productPurchases",
            query_params={
                "locationId": "location_ids",
                "minPostDate": "start_date",
                "maxPostDate": "end_date"
            }
        ),
        "non_product_purchases": EndpointConfig(
            path="/food/nonProductPurchases",
            query_params={
                "locationId": "location_ids",
                "minPostDate": "start_date",
                "maxPostDate": "end_date"
            }
        ),
        "inventory_onhand_details": EndpointConfig(
            path="/food/inventoryOnhandDetails",
            query_params={
                "locationId": "location_ids",
                "businessDate": "start_date"
            }
        ),
        "plate_costs": EndpointConfig(
            path="/food/plateCosts",
            query_params={
                "locationId": "location_ids",
                "invPeriodDate": "start_date"
            }
        )
    },
    "sales": {
        "checks": EndpointConfig(
            path="/sales/checks",
            query_params={
                "locationId": "location_ids",
                "businessDate": "start_date"
            }
        ),
        "pos_departments": EndpointConfig(
            path="/sales/definitions/posDepartments",
            query_params={}
        ),
        "discount_categories": EndpointConfig(
            path="/sales/definitions/discountCategories",
            query_params={}
        ),
        "discounts": EndpointConfig(
            path="/sales/definitions/discounts",
            query_params={}
        ),
        # "drive_thru_stations": EndpointConfig(
        #     path="/sales/definitions/driveThruStations",
        #     query_params={}
        # ),
        # "items": EndpointConfig(
        #     path="/sales/definitions/items",
        #     query_params={
        #         "minSoldDate": "start_date",
        #     }
        # ),
        "major_categories": EndpointConfig(
            path="/sales/definitions/majorCategories",
            query_params={}
        ),
        "payment_categories": EndpointConfig(
            path="/sales/definitions/paymentCategories",
            query_params={}
        ),
        "pos_sources": EndpointConfig(
            path="/sales/definitions/posSources",
            query_params={}
        ),
        "revenue_centers": EndpointConfig(
            path="/sales/definitions/revenueCenters",
            query_params={}
        ),
        "sales_categories": EndpointConfig(
            path="/sales/definitions/salesCategories",
            query_params={}
        ),
        "tax_categories": EndpointConfig(
            path="/sales/definitions/taxCategories",
            query_params={}
        ),
        "void_categories": EndpointConfig(
            path="/sales/definitions/voidCategories",
            query_params={}
        ),
    },
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


class SyncOptions(BaseModel):
    datasets: list[str] = Field(
        default=[],
        description="List of datasets to fetch, e.g. ['general']"
    )
    date_from: str = Field(
        default="2020-01-01",
        description="Start date, defaults to '2020-01-01' if not provided"
    )
    date_to: str = Field(
        default_factory=lambda: str(date.today()),
        description="End date, defaults to today"
    )
    location_ids: Optional[List[int]] = Field(
        default=None,
        description="List of location IDs (Optional)"
    )
    generate_date_range: bool = Field(
        default=False,
        description="generate date range between date_from and date_to, (defaults to False uses just date_from)"
    )
    api_limit: int = Field(
        default=300,
        description=(
            "Number of records per request, "
            "defaults to 300 if not specified"
        )
    )

    @field_validator("datasets")
    def validate_datasets(cls, value: List[str]) -> List[str]:
        supported_values = {"general", "sales"}

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


class Configuration(BaseModel):
    authentication: Authentication
    sync_options: SyncOptions
    debug: bool = False


def __init__(self, **data):
    if self.debug:
        logging.debug("Component will run in Debug mode")
