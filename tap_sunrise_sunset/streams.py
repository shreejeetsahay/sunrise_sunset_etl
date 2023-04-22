"""Stream type classes for tap-sunrise-sunset."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable, cast
import requests
from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_sunrise_sunset.client import sunrise_sunsetStream

from datetime import timedelta, date
import copy

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class dataStream(sunrise_sunsetStream):
    """Sunrise Sunset data stream."""
    name = "sunrise_sunset"
    path = "/json"
    primary_keys = []
    replication_key = None
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    schema_filepath = SCHEMAS_DIR / "sunrise_sunset.json"

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        params["lat"] = self.config["lat"]
        params["lng"] = self.config["lng"]
        params["formatted"] = 0
        return params
    
    def prepare_request(
        self, context: Optional[dict], next_page_token: Optional[Any], date1
    ) -> requests.PreparedRequest:
        """Prepare a request object.

        If partitioning is supported, the `context` object will contain the partition
        definitions. Pagination information can be parsed from `next_page_token` if
        `next_page_token` is not None.

        Args:
            context: Stream partition or context dictionary.
            next_page_token: Token, page number or any request argument to request the
                next page of data.

        Returns:
            Build a request with the stream's URL, path, query parameters,
            HTTP headers and authenticator.
        """
        http_method = self.rest_method
        url: str = self.get_url(context)
        params: dict = self.get_url_params(context, next_page_token)
        request_data = self.prepare_request_payload(context, next_page_token)
        headers = self.http_headers
        params["date"] = date1

        authenticator = self.authenticator
        if authenticator:
            headers.update(authenticator.auth_headers or {})
            params.update(authenticator.auth_params or {})

        request = cast(
            requests.PreparedRequest,
            self.requests_session.prepare_request(
                requests.Request(
                    method=http_method,
                    url=url,
                    params=params,
                    headers=headers,
                    json=request_data,
                ),
            ),
        )
        return request

    def request_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Request records from REST endpoint(s), returning response records.

        If pagination is detected, pages will be recursed automatically.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            An item for every record in the response.

        Raises:
            RuntimeError: If a loop in pagination is detected. That is, when two
                consecutive pagination tokens are identical.
        """
        next_page_token: Any = None
        finished = False
        decorated_request = self.request_decorator(self._request)
        sd = self.config.get("start_date").split("-")
        ed = self.config.get("end_date").split("-")
        start_dt = date(int(sd[0]), int(sd[1]), int(sd[2]))
        end_dt = date(int(ed[0]), int(ed[1]), int(ed[2]))
        for dt in daterange(start_dt, end_dt):
            date1 = dt.strftime("%Y-%m-%d")
            prepared_request = self.prepare_request(
                context, next_page_token=next_page_token,date1 = date1
            )
            resp = decorated_request(prepared_request, context)
            yield from self.parse_response(resp)
            
            
