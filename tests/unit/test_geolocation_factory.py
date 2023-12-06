from unittest import TestCase, mock

from app.geolocation.factory import Factory


class TestGeoLocationFactory(TestCase):
    @mock.patch("boto3.session.Session")
    def test_s3(self, MockSession):
        f = Factory()

        assert MockSession.called
        assert f.storage_provider == "S3"

    @mock.patch("google.cloud.storage.Client")
    def test_gcs(self, MockClient):
        with mock.patch.dict("os.environ", {"GEOIP_GCS_BUCKET": "acme"}):
            f = Factory()

            assert MockClient.called
            assert f.storage_provider == "GCS"
