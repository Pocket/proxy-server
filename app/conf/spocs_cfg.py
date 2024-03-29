production = staging = development = test = {
    'caps': {
        'lifetime': 50,
        'campaign': {
            'count': 10,
            'period': 86400,
        },
        'flight': {
            'count': 10,
            'period': 86400,
        },
    },
    'settings': {
        "feature_flags": {
            "spoc_v2": True,
            # 'Collections' are stories that are run together, currently only used occasionally in Firefox.
            # If collections is True, the client can include a collection placement in the request.
            # If collections is False, the client will not include a collection placement, to reduce ad decisions.
            "collections": False,
        },
        "spocsPerNewTabs": 1,
        "domainAffinityParameterSets": {
            "default": {
                "recencyFactor": 0.5,
                "frequencyFactor": 0.5,
                "combinedDomainFactor": 0.5,
                "perfectFrequencyVisits": 10,
                "perfectCombinedDomainScore": 2,
                "multiDomainBoost": 0,
                "itemScoreFactor": 1
            },
            "fully-personalized": {
                "recencyFactor": 0.5,
                "frequencyFactor": 0.5,
                "combinedDomainFactor": 0.5,
                "perfectFrequencyVisits": 10,
                "perfectCombinedDomainScore": 2,
                "itemScoreFactor": 0.01,
                "multiDomainBoost": 0
            },
            "fully-personalized-domains": {
                "recencyFactor": 0.5,
                "frequencyFactor": 0.5,
                "combinedDomainFactor": 0.5,
                "perfectFrequencyVisits": 1,
                "perfectCombinedDomainScore": 10,
                "itemScoreFactor": 0.01,
                "multiDomainBoost": 0
            }
        },
        "timeSegments": [
            {
                "id": "week-1",
                "startTime": 432000,
                "endTime": 0,
                "weightPosition": 1
            },
            {
                "id": "week-2",
                "startTime": 864000,
                "endTime": 432000,
                "weightPosition": 1
            },
            {
                "id": "week-3",
                "startTime": 1296000,
                "endTime": 864000,
                "weightPosition": 1
            },
            {
                "id": "week-4",
                "startTime": 1728000,
                "endTime": 1296000,
                "weightPosition": 1
            },
            {
                "id": "week-5",
                "startTime": 2160000,
                "endTime": 1728000,
                "weightPosition": 1
            },
            {
                "id": "week-6",
                "startTime": 2592000,
                "endTime": 2160000,
                "weightPosition": 1
            }
        ]
    }
}
