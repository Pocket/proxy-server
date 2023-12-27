from unittest.mock import patch

import responses
import schemathesis
from aioresponses import aioresponses

from tests.fixtures.mock_factory import get_mocked_geolocation_factory
from tests.fixtures.mock_decision import mock_decision_2

__FACTORY = get_mocked_geolocation_factory()
with patch("app.geolocation.factory.Factory.get_instance", return_value=__FACTORY):
    from app.main import app

schema = schemathesis.from_path("openapi/openapi.yml", app=app)


MOCK_DECISIONS_RESPONSE = {
    "user": {
        "key": "{12345678-8901-2345-aaaa-bbbbbbcccccc}",
    },
    "decisions": {
        "spocs": [mock_decision_2]
    }
}

@responses.activate
@schema.parametrize()
def test_api(case: schemathesis.Case) -> None:
    # Mock call to forget API
    responses.delete("https://e-10250.adzerk.net/udb/10250/")

    with aioresponses() as m:
        # Mock call to decisions API
        m.post("https://e-10250.adzerk.net/api/v2", payload=MOCK_DECISIONS_RESPONSE)

        # Call Pocket Proxy and validate response
        response = case.call_asgi()
        case.validate_response(response)
