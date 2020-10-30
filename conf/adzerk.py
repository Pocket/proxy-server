import os
import logging
from botocore.exceptions import BotoCoreError
from copy import deepcopy


from telemetry.handler import TELEMETRY_PATH_IDS
import adzerk.secret
import adzerk.api
from conf import env

network_id = 10250
div_name = "spocs"
domain = "https://e-{0}.adzerk.net".format(str(network_id))

default = {
    "network_id": network_id,
    "div_name": div_name,
    "telemetry_endpoint_ids": TELEMETRY_PATH_IDS,
    "forget_endpoint": "{0}/udb/{1}/".format(domain, str(network_id)),
    "get_priority_endpoint": "https://api.adzerk.net/v1/priority",
    "decision": {
        "url": "{0}/api/v2".format(domain),
        "body": {
            "placements": [{
                "divName": div_name,
                "networkId": network_id,
                "siteId": 1070098,
                "adTypes": [2401, 3617],
                "zoneIds": [217995],
                "count": 20,
                "eventIds": [17, 20],
            }]
        }
    },
    # Default priory_id to weight mapping, used during task startup before they are fetched from AdZerk.
    "priority_id_to_weight": {
        147517: 1,
        180843: 2,
        147518: 3,
        160722: 9,
        147520: 10,
    }
}

production = deepcopy(default)
development = deepcopy(default)

try:
    api_key = adzerk.secret.get_api_key()
    development["api_key"] = production["api_key"] = api_key
except BotoCoreError as e:
    if env == 'development':
        logging.info('Failed to load api_key from Secret Manager.')
        development["api_key"] = os.environ.get("ADZERK_API_KEY")
    else:
        raise e
