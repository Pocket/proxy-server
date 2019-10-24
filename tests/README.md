# Tests

## Unit Testing

Run all test cases:
```bash
python -m unittest discover tests/
```
Or run a specific test case:
```bash
python -m unittest tests.test_adzerk_transform.test_to_spoc
```

## Load Testing

[Serverless Artillery](https://github.com/Nordstrom/serverless-artillery) is used for load testing this service.

### Installation
1. `cd tests/load`
2. Follow the [Serverless Artillery installation instructions](https://github.com/Nordstrom/serverless-artillery#installation).
    1. `npm install serverless`
    2. `npm install serverless-artillery`
    3. Check that the installation succeeded: `slsart --version`
3. `npm install artillery-plugin-cloudwatch`

### Run test
1. `cd tests/load`
2. `aws-vault exec <aws profile> -- slsart deploy --stage <your-unique-stage-name>`
3. `aws-vault exec <aws profile> -- slsart invoke --stage <your-unique-stage-name>`

## Local speed test
Locally run 500 requests in parallel. This is useful to:
1. Verify whether the code is running asynchronously.
2. Do a performance test in a matter of seconds. Running a load test is still required to get an accurate result.
```shell script
 gunicorn -c ./tests/scripts/wsgi_profiler_conf.py "app.main:create_app()"
```

## Profiling
Measure which lines take up the most CPU time. This is useful to identify if any part of the code is taking much more time than it should. 
```shell script
 gunicorn -c ./tests/scripts/wsgi_profiler_conf.py "app.main:create_app()"
```
