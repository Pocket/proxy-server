import base64
import gzip
import json
import os
import urllib.request
from datetime import datetime
from urllib.parse import urlencode

NETWORK_ID = os.environ.get("ADZERK_NETWORK_ID", 10250)
TELEMETRY_PATH_IDS = {
    "/r": "0",
    "/i.gif": "1",
    "/e.gif": "2",
}
# Kevel flight id that
PACING_TEST_FLIGHT_ID = os.environ.get("PACING_TEST_FLIGHT_ID", 5003)
# 31 minutes in milliseconds; 1 minute of leeway
# for ads used very near to the 30 minute time and then viewed after
PACING_TEST_MAX_CALLBACK_DELAY_MILLIS = 31 * 60 * 1000


def handle_message(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    see gcp-ingestion docs for details on the event structure
    https://mozilla.github.io/gcp-ingestion/architecture/decoder_service_specification/
    https://mozilla.github.io/gcp-ingestion/architecture/edge_service_specification/#pubsub-message-schema

    :param event: Event payload.
    :param context: Google Cloud Function metadata.
    """

    namespace_key = "document_namespace"
    doctype_key = "document_type"
    user_agent_version_key = "user_agent_version"
    submission_timestamp_key = "submission_timestamp"

    decompressed = gzip.decompress(base64.b64decode(event["data"])).decode("utf-8")
    telemetry = json.loads(decompressed)
    attributes = event["attributes"]

    namespace = attributes.get(namespace_key)
    doctype = attributes.get(doctype_key)
    user_agent_version = attributes.get(user_agent_version_key)
    submission_timestamp = attributes.get(submission_timestamp_key)

    if namespace in ["org-mozilla-firefox", "org-mozilla-firefox-beta", "org-mozilla-fenix"]\
            and "spoc" == doctype:  # Android/Glean
        if "metrics" in telemetry:
            text_metrics = telemetry["metrics"].get("text", {})
            if "pocket.spoc_shim" in text_metrics:
                ping_adzerk(text_metrics["pocket.spoc_shim"], submission_timestamp)
    elif "firefox-desktop" == namespace and "spoc" == doctype:  # Desktop/Glean
        if int(user_agent_version) >= 122:
            if "metrics" in telemetry:
                text_metrics = telemetry["metrics"].get("text", {})
                if "pocket.shim" in text_metrics:
                    ping_adzerk(text_metrics["pocket.shim"], submission_timestamp)
    elif "activity-stream" == namespace and "impression-stats" == doctype:
        if int(user_agent_version) < 122:  # Desktop/Legacy
            if "tiles" in telemetry:
                for tile in telemetry["tiles"]:
                    if "shim" in tile:
                        ping_adzerk(tile["shim"], submission_timestamp)


def ping_adzerk(shim, submission_timestamp):
    """Pings AdZerk with a given shim

    :param shim: comma-separated shim with an event and checksum component.
    """
    path_id, e, s = shim.split(",")
    if should_ping_adzerk(e, submission_timestamp):
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


def should_ping_adzerk(shim, submission_timestamp):
    """
        base64 decodes the kevel shim and checks the flightID and delay of callback.
        will skip the Kevel callback for flightIDs being used to test pacing
    """
    try:
        submission_timestamp_millis = int(datetime.fromisoformat(submission_timestamp).timestamp()) * 1000
        # add back padding characters if needed
        padded_data = shim + '=' * (-len(shim)%4)
        kevel_json = json.loads(base64.b64decode(padded_data))

        if kevel_json['fl'] == PACING_TEST_FLIGHT_ID:
            ad_age_millis = submission_timestamp_millis - kevel_json['ts']
            if ad_age_millis > PACING_TEST_MAX_CALLBACK_DELAY_MILLIS:
                return False
    except:
        return True

    return True