import base64
import google.cloud.logging
import gzip
import json
import logging
import os
import random
import time
import urllib.request
from datetime import datetime, timezone
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
                record_metrics(text_metrics["pocket.spoc_shim"], submission_timestamp, namespace, user_agent_version)
    elif "firefox-desktop" == namespace and "spoc" == doctype:  # Desktop/Glean
        if user_agent_version is not None and int(user_agent_version) >= 122:
            if "metrics" in telemetry:
                text_metrics = telemetry["metrics"].get("text", {})
                if "pocket.shim" in text_metrics:
                    ping_adzerk(text_metrics["pocket.shim"])
                    record_metrics(text_metrics["pocket.shim"], submission_timestamp, namespace, user_agent_version)
    elif "activity-stream" == namespace and "impression-stats" == doctype:
        if user_agent_version is not None and int(user_agent_version) < 122:  # Desktop/Legacy
            if "tiles" in telemetry:
                for tile in telemetry["tiles"]:
                    if "shim" in tile:
                        ping_adzerk(tile["shim"])
                        record_metrics(tile["shim"], submission_timestamp, namespace, user_agent_version)


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


def record_metrics(shim, submission_timestamp, namespace, user_agent_version):
    """If METRICS_SAMPLE_RATE is set and greater than 0, then log metrics for the event.
        The metrics are logged in a structured event to enable google cloud log-based metrics to aggregate them

        metrics sampled:
            time from adserver generating the impression to now
            time from telemetry submission to now
    """
    try:
        # range of 0-1000, to sample in increments of 1/1000
        metrics_sample_rate = os.environ.get("METRICS_SAMPLE_RATE", "0")

        if not metrics_sample_rate.isdecimal():
            return

        if int(metrics_sample_rate) <= 0 or random.randrange(0, 1000) >= int(metrics_sample_rate):
            return

        log_client = google.cloud.logging.Client()
        log_client.setup_logging()

        submission_timestamp = datetime.fromisoformat(submission_timestamp)

        _, encoded_data, _ = shim.split(",")
        padded_data = encoded_data + '=' * (-len(encoded_data)%4)
        kevel_json = json.loads(base64.b64decode(padded_data))
        kevel_timestamp_millis = kevel_json['ts']

        now = get_now()

        glean_latency = now - submission_timestamp
        glean_latency_millis = int(glean_latency.total_seconds() * 1000)
        adserver_latency_millis = int(now.timestamp() * 1000) - kevel_timestamp_millis

        json_fields = {
            "glean_latency": glean_latency_millis,
            "adserver_latency": adserver_latency_millis,
            "namespace": namespace,
            "user_agent_version": user_agent_version,
        }
        logging.info("metrics", extra={"json_fields": json_fields})

        return
    except:
        return


def get_now():
    return datetime.now(timezone.utc)