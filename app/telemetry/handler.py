import base64
import gzip
import json
import os
import urllib.request
from urllib.parse import urlencode

NETWORK_ID = os.environ.get("ADZERK_NETWORK_ID", 10250)
TELEMETRY_PATH_IDS = {
    "/r": "0",
    "/i.gif": "1",
    "/e.gif": "2",
}


def handle_message(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.

    :param event: Event payload.
    :param context: Google Cloud Function metadata.
    """

    namespace_key = "document_namespace"
    doctype_key = "document_type"
    user_agent_version_key = "user_agent_version"

    decompressed = gzip.decompress(base64.b64decode(event["data"])).decode("utf-8")
    telemetry = json.loads(decompressed)
    attributes = event["attributes"]

    namespace = attributes.get(namespace_key)
    doctype = attributes.get(doctype_key)
    user_agent_version = attributes.get(user_agent_version_key)

    if namespace in ["org-mozilla-firefox", "org-mozilla-firefox-beta", "org-mozilla-fenix"]\
            and "spoc" == doctype:  # Android/Glean
        if "metrics" in telemetry:
            text_metrics = telemetry["metrics"].get("text", {})
            if "pocket.spoc_shim" in text_metrics:
                ping_adzerk(text_metrics["pocket.spoc_shim"])
    elif "firefox-desktop" == namespace and "spoc" == doctype:  # Desktop/Glean
        if int(user_agent_version) >= 122:
            if "metrics" in telemetry:
                text_metrics = telemetry["metrics"].get("text", {})
                if "pocket.shim" in text_metrics:
                    ping_adzerk(text_metrics["pocket.shim"])
    elif "activity-stream" == namespace and "impression-stats" == doctype:
        if int(user_agent_version) < 122:  # Desktop/Legacy
            if "tiles" in telemetry:
                for tile in telemetry["tiles"]:
                    if "shim" in tile:
                        ping_adzerk(tile["shim"])


def ping_adzerk(shim):
    """Pings AdZerk with a given shim

    :param shim: comma-separated shim with an event and checksum component.
    """
    path_id, e, s = shim.split(",")
    path = get_path(path_id)
    query = urlencode({"e": e, "s": s})
    url = "https://e-{network_id}.adzerk.net{path}?{query}".format(
        network_id=NETWORK_ID, path=path, query=query
    )
    with urllib.request.urlopen(url) as response:
        response.read()


def get_path(path_id):
    for k, v in TELEMETRY_PATH_IDS.items():
        if v == path_id:
            return k
