from copy import deepcopy

mock_response = {
  "adId": 111,
  "creativeId": 222,
  "flightId": 333,
  "campaignId": 1000,
  "priorityId": 555,
  "clickUrl": "http://e-123.adzerk.net/r?e=12345&s=12345",
  "contents": [
    {
      "type": "html",
      "template": "image",
      "data": {
        "imageUrl": "http://static.adzerk.net/cat.jpg",
        "title": "ZOMG A CAT",
        "width": 350,
        "height": 350,
        "ctTitle": "title 1000",
        "ctUrl": "url",
        "ctDomain": "ctDOmain",
        "ctExcerpt": "excerpt",
        "ctSponsor": "sponsor",
        "ctFullimagepath": "blah",
        "ctMin_score": 0.01,
        "ctItem_score": 0.01,
        "ctDomain_affinities": "travel"
      }
    }
  ],
  "impressionUrl": "http://e-123.adzerk.net/i.gif?e=12345&s=12345",
  "events": [
    {
      "id": 12,
      "url": "http://e-123.adzerk.net/e.gif?e=12345&s=12345"
    },
    {
      "id": 13,
      "url": "http://e-123.adzerk.net/e.gif?e=12345&s=12345"
    },
    {
      "id": 20,
      "url": "http://e-123.adzerk.net/e.gif?e=12345&s=12345"
    },
    {
      "id": 17,
      "url": "http://e-123.adzerk.net/e.gif?e=12345&s=12345"
    }
  ],
  "pricing": {
    "price": 5,
    "clearPrice": 2.01,
    "revenue": 0.002,
    "rateType": 2,
    "eCPM": 5
  }
}

mock_response_900 = {
  "adId": 111,
  "creativeId": 222,
  "flightId": 333,
  "campaignId": 900,
  "priorityId": 555,
  "clickUrl": "http://e-123.adzerk.net/r?e=12345&s=12345",
  "contents": [
    {
      "type": "html",
      "template": "image",
      "data": {
        "imageUrl": "http://static.adzerk.net/cat.jpg",
        "title": "ZOMG A CAT",
        "width": 350,
        "height": 350,
        "ctTitle": "title 900",
        "ctUrl": "url",
        "ctDomain": "ctDOmain",
        "ctExcerpt": "excerpt",
        "ctSponsor": "sponsor",
        "ctFullimagepath": "blah",
        "ctMin_score": 0.01,
        "ctItem_score": 0.01,
        "ctDomain_affinities": "travel"
      }
    }
  ],
  "impressionUrl": "http://e-123.adzerk.net/i.gif?e=12345&s=12345",
  "events": [
    {
      "id": 12,
      "url": "http://e-123.adzerk.net/e.gif?e=12345&s=12345"
    },
    {
      "id": 13,
      "url": "http://e-123.adzerk.net/e.gif?e=12345&s=12345"
    },
    {
      "id": 20,
      "url": "http://e-123.adzerk.net/e.gif?e=12345&s=12345"
    },
    {
      "id": 17,
      "url": "http://e-123.adzerk.net/e.gif?e=12345&s=12345"
    }
  ],
  "pricing": {
    "price": 5,
    "clearPrice": 2.01,
    "revenue": 0.002,
    "rateType": 2,
    "eCPM": 5
  }
}

mock_decision_2 = {
  "adId": 2,
  "creativeId": 9142593,
  "flightId": 8525375,
  "campaignId": 887195,
  "priorityId": 155142,
  "clickUrl": "https://e-10250.adzerk.net/r?e=jq&s=s2",
  "impressionUrl": "https://e-10250.adzerk.net/i.gif?e=ke1&s=s3",
  "contents": [
    {
      "type": "raw",
      "data": {
        "ctUrl": "https://example.com/?key=foobar",
        "ctDomain_affinities": "publishers",
        "ctMin_score": "0.1",
        "ctDomain": "wallmarket.com",
        "ctItem_score": "0.11",
        "ctTitle": "Refresh Your Space for Spring",
        "ctExcerpt": "Get up to 50% off furniture, bedding, and more.",
        "ctFullimagepath": "https://cdn.net/25a.jpg",
        "ctSponsor": "WallMarket",
        "ctImage": "25a.jpg",
        "fileName": "25a.jpg"
      }
    }
  ],
  "events": [
    {
      "id": 17,
      "url": "https://e-10250.adzerk.net/e.gif?e=eyJ2&s=Y6"
    },
    {
      "id": 20,
      "url": "https://e-10250.adzerk.net/e.gif?e=wfQ&s=Rj-6"
    }
  ]
}

mock_decision_3_cta = deepcopy(mock_decision_2)
mock_decision_3_cta['adId'] = 3
mock_decision_3_cta['contents'][0]['data']['ctCta'] = "Learn more"

mock_collection_response = deepcopy(mock_response_900)
mock_collection_response['adId'] = 4
mock_collection_response['contents'][0]['data']['ctCollectionTitle'] = "Best of the Web"

mock_decision_5_topics = deepcopy(mock_decision_2)
mock_decision_5_topics['adId'] = 5
mock_decision_5_topics['contents'][0]['body'] = "{\"topic_arts_and_entertainment\":\"\",\"topic_autos_and_vehicles\":\"true\",\"topic_beauty_and_fitness\":\"true\"}"

mock_decision_6_no_sponsor = deepcopy(mock_decision_2)
mock_decision_6_no_sponsor['adId'] = 6
del mock_decision_6_no_sponsor['contents'][0]['data']['ctSponsor']
