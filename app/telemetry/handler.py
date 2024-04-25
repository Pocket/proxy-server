import base64
import google.cloud.logging
import gzip
import json
import logging
import os
import random
import time
import urllib.request
from datetime import datetime
from urllib.parse import urlencode

NETWORK_ID = os.environ.get("ADZERK_NETWORK_ID", 10250)
TELEMETRY_PATH_IDS = {
    "/r": "0",
    "/i.gif": "1",
    "/e.gif": "2",
}
# range of 0-1000, to sample in increments of 1/1000
METRIC_SAMPLE_RATE = os.environ.get("METRIC_SAMPLE_RATE", "0")


def handle_message(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.

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
                ping_adzerk(text_metrics["pocket.spoc_shim"])
                record_metrics(text_metrics["pocket.spoc_shim"], submission_timestamp)
    elif "firefox-desktop" == namespace and "spoc" == doctype:  # Desktop/Glean
        if int(user_agent_version) >= 122:
            if "metrics" in telemetry:
                text_metrics = telemetry["metrics"].get("text", {})
                if "pocket.shim" in text_metrics:
                    ping_adzerk(text_metrics["pocket.shim"])
                    record_metrics(text_metrics["pocket.shim"], submission_timestamp)
    elif "activity-stream" == namespace and "impression-stats" == doctype:
        if int(user_agent_version) < 122:  # Desktop/Legacy
            if "tiles" in telemetry:
                for tile in telemetry["tiles"]:
                    if "shim" in tile:
                        ping_adzerk(tile["shim"])
                        record_metrics(tile["shim"], submission_timestamp)


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


def record_metrics(shim, submission_timestamp):
    """If METRIC_SAMPLE_RATE is set and greater than 0, then log metrics for the event.
        The metrics are logged in a structured event to enable google cloud log-based metrics to aggregate them

        metrics sampled:
            time from adserver generating the impression to now
            time from telemetry submission to now
    """
    try:
        if not METRIC_SAMPLE_RATE.isdecimal():
            return

        if int(METRIC_SAMPLE_RATE) <= 0 or random.randrange(0, 1000) >= int(METRIC_SAMPLE_RATE):
            return

        log_client = google.cloud.logging.Client()
        log_client.setup_logging()

        submission_timestamp_millis = int(datetime.fromisoformat(submission_timestamp).timestamp() * 1000)

        padded_data = shim + '=' * (-len(shim)%4)
        kevel_json = json.loads(base64.b64decode(padded_data))

        kevel_timestamp = kevel_json['ts']

        now_millis = int(time.time() * 1000)

        glean_latency_millis = now_millis - submission_timestamp_millis
        adserver_latency_millis = now_millis - kevel_timestamp

        logging.info("metrics", extra={"json_fields": {"glean_latency": glean_latency_millis, "adserver_latency": adserver_latency_millis}})

        return
    except:
        return
