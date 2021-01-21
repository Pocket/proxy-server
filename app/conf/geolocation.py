import os

production = development = {
    's3_bucket': os.environ.get('GEOIP_S3_BUCKET', 'GEOIP_S3_BUCKET'),
    's3_key': 'GeoIP2-City.mmdb',
}
