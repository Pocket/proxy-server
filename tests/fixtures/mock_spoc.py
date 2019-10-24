from copy import deepcopy

mock_spoc_2 = {
    "id": 2,
    "campaign_id": 887195,
    "title": "Refresh Your Space for Spring",
    "url": "https://example.com/?key=foobar",
    "domain": "wallmarket.com",
    "excerpt": "Get up to 50% off furniture, bedding, and more.",
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
        "lifetime": 10,
        "campaign": {
            "count": 10,
            "period": 86400
        }
    },
    "domain_affinities": {
        "example.com": 1
    },
    "min_score": 0.1,
    "item_score": 0.11,
}

mock_spoc_3_cta = deepcopy(mock_spoc_2)
mock_spoc_3_cta["id"] = 3
mock_spoc_3_cta["cta"] = "Learn more"
