from datetime import datetime, timedelta
from typing import List, Dict


def generate_date_location_matrix(
    date_from: str, 
    date_to: str, 
    location_ids: List[int], 
    generate_date_range: bool
) -> List[Dict[str, str]]:
    """Generates a matrix of location_id pairs with standard and timestamped date formats."""

    def to_iso_format(date_str: str) -> str:
        return f"{date_str}T12:00:00Z"

    if generate_date_range:
        start_date = datetime.strptime(date_from, "%Y-%m-%d")
        end_date = datetime.strptime(date_to, "%Y-%m-%d")

        date_list = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d")
                     for i in range((end_date - start_date).days + 1)]

        query_matrix = [
            {
                "selected_date": date,
                "selected_date_with_ts": to_iso_format(date),
                "location_id": str(location)
            }
            for date in date_list
            for location in location_ids
        ]

    else:
        query_matrix = [
            {
                "date_from": date_from,
                "date_from_with_ts": to_iso_format(date_from),
                "date_to": date_to,
                "date_to_with_ts": to_iso_format(date_to),
                "location_id": str(location)
            }
            for location in location_ids
        ]

    return query_matrix
