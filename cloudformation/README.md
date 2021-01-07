Notes:

- Log groups are not created by ecs-fargate.yaml. Including log groups in the templates proved to cause stack update reliability problems. You must manually create them before deploying.
- You must manually create the GeoIP S3 bucket and upload GeoIP2-City.mmdb
- You must manually create two secrets in a JSON object, which the SecretsManager AWS Console uses by default.
   - `prod/adzerk` that stores the AdZerk API key: `{"ADZERK_API_KEY":"<api key goes here>"}`
   - `prod/sentry_dsn` that stores the Sentry DSN API key: `{"SENTRY_DSN":"<DSN goes here>"}`
