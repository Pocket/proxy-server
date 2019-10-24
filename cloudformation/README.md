Notes:

- Log groups are not created by ecs-fargate.yaml. Including log groups in the templates proved to cause stack update reliability problems. You must manually create them before deploying.
- You must manually create the GeoIP S3 bucket and upload GeoIP2-City.mmdb
- You must manually create a secret called `prod/adzerk` that stores the AdZerk API key in a JSON object: `{"ADZERK_API_KEY":"<api key goes here>"`. If you use the AWS Console it will have the correct JSON format.
