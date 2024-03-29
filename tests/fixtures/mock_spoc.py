from copy import deepcopy

mock_spoc_2 = {
    "id": 2,
    "flight_id": 8525375,
    "campaign_id": 887195,
    "title": "Refresh Your Space for Spring",
    "url": "https://example.com/?key=foobar",
    "domain": "wallmarket.com",
    "excerpt": "Get up to 50% off furniture, bedding, and more.",
    "priority": 1,
    "context": "Sponsored by WallMarket",
    "sponsor": "WallMarket",
    "raw_image_src": "https://cdn.net/25a.jpg",
    "image_src": "https://img-getpocket.cdn.mozilla.net/direct?url=https%3A//cdn.net/25a.jpg&resize=w618-h310",
    "shim": {
        "click": "0,jq,s2",
        "impression": "1,ke1,s3",
        "delete": "2,eyJ2,Y6",
        "save": "2,wfQ,Rj-6"
    },
    "parameter_set": "default",
    "caps": {
        "lifetime": 50,
        "campaign": {
            "count": 10,
            "period": 86400
        },
        "flight": {
            "count": 10,
            "period": 86400
        }
    },
    "domain_affinities": {
        "example.com": 1
    },
    "personalization_models": {},
    "min_score": 0.1,
    "item_score": 0.2,
}

mock_spoc_3_cta = deepcopy(mock_spoc_2)
mock_spoc_3_cta["id"] = 3
mock_spoc_3_cta["cta"] = "Learn more"

mock_collection_spoc_2 = deepcopy(mock_spoc_2)
mock_collection_spoc_2["collection_title"] = "Best of the Web"
mock_collection_spoc_3 = deepcopy(mock_spoc_3_cta)
mock_collection_spoc_3["collection_title"] = "Best of the Web"

mock_collection = {
    "title": "Best of the Web",
    "sponsor": "WallMarket",
    "context": "Sponsored by WallMarket",
    "flight_id": 8525375,
    "items": [deepcopy(mock_spoc_2), deepcopy(mock_spoc_3_cta)]
}

mock_spoc_5_topics = deepcopy(mock_spoc_2)
mock_spoc_5_topics["id"] = 5
mock_spoc_5_topics["personalization_models"] = {"autos_and_vehicles":1, "beauty_and_fitness": 1}

mock_spoc_6_no_sponsor = deepcopy(mock_spoc_2)
mock_spoc_6_no_sponsor["id"] = 6
del mock_spoc_6_no_sponsor["sponsor"]
mock_spoc_6_no_sponsor["context"] = ""

mock_spoc_7_is_video = deepcopy(mock_spoc_2)
mock_spoc_7_is_video["id"] = 7
mock_spoc_7_is_video["is_video"] = True

mock_spoc_8_blank_sponsored_by_override = deepcopy(mock_spoc_2)
mock_spoc_8_blank_sponsored_by_override["id"] = 8
mock_spoc_8_blank_sponsored_by_override["sponsored_by_override"] = ""

mock_spoc_9_sponsored_by_override = deepcopy(mock_spoc_2)
mock_spoc_9_sponsored_by_override["id"] = 9
mock_spoc_9_sponsored_by_override["sponsored_by_override"] = "Brought by blank"

mock_spoc_10_missing_priority = deepcopy(mock_spoc_2)
mock_spoc_10_missing_priority["id"] = 10
mock_spoc_10_missing_priority["priority"] = 100
