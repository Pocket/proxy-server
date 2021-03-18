from app.telemetry.handler import TELEMETRY_PATH_IDS

network_id = 10250
div_name = "spocs"
domain = "https://e-{0}.adzerk.net".format(str(network_id))

production = staging = development = test = {
    "network_id": network_id,
    "div_name": div_name,
    "telemetry_endpoint_ids": TELEMETRY_PATH_IDS,
    "forget_endpoint": "{0}/udb/{1}/".format(domain, str(network_id)),
    "decision": {
        "url": "{0}/api/v2".format(domain),
        "body": {
            "placements": [{
                "divName": div_name,
                "networkId": network_id,
                "siteId": 1070098,
                "adTypes": [2401, 3617],
                "zoneIds": [217995],
                "count": 10,
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
