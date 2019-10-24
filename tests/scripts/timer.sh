#!/bin/bash
# \nocite{Tange2011a}

time seq 500 | parallel --jobs 500 "curl -s -X POST \
  http://localhost/spocs \
  -H 'Accept: */*' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	\"version\":1,
	\"consumer_key\":\"1234\",
	\"pocket_id\":\"5678\"
}' > /dev/null"
