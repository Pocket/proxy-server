from urllib import parse
import logging

import conf


def to_spoc(decision):
    if not decision:
        return {}
    custom_data = decision['contents'][0]['data']

    events_map = {e["id"]: tracking_url_to_shim(e["url"]) for e in decision["events"]}

    spoc = {
        'id':                decision['adId'],
        'flight_id':         decision['flightId'],
        'campaign_id':       decision['campaignId'],
        'title':             custom_data['ctTitle'],
        'url':               custom_data['ctUrl'],
        'domain':            custom_data['ctDomain'],
        'excerpt':           custom_data['ctExcerpt'],
        'sponsor':           custom_data['ctSponsor'],
        'context':           __get_context(custom_data['ctSponsor']),
        'raw_image_src':     custom_data['ctFullimagepath'],
        'image_src':         __get_cdn_image(custom_data['ctFullimagepath']),
        'shim': {
            'click':         tracking_url_to_shim(decision['clickUrl']),
            'impression':    tracking_url_to_shim(decision['impressionUrl']),
            'delete':        events_map[17],
            'save':          events_map[20],
        },
        'parameter_set':     'default',
        'caps':              conf.spocs['caps'],
        'domain_affinities': __get_domain_affinities(custom_data.get('ctDomain_affinities')),
    }
    
    if 'ctCta' in custom_data and custom_data['ctCta']:
        spoc['cta'] = custom_data['ctCta']

    try:
        spoc['min_score']  = float(custom_data['ctMin_score'])
        spoc['item_score'] = float(custom_data['ctItem_score'])
    except (KeyError, ValueError) as e:
        logging.warning(str(e))

    return spoc


def tracking_url_to_shim(url):
    components = parse.urlsplit(url)

    path_id = conf.adzerk['telemetry_endpoint_ids'].get(components.path)
    if path_id is None:
        raise Exception('Not a known telemetry path: {0}'.format(components.path))

    params = parse.parse_qs(components.query)
    e = params['e'][0]
    s = params['s'][0]
    return ','.join([path_id,e,s])


def __get_cdn_image(raw_image_url):
    escaped = parse.quote(raw_image_url)
    return 'https://img-getpocket.cdn.mozilla.net/direct?url={0}&resize=w618-h310'.format(escaped)


def __get_context(sponsor):
    return 'Sponsored by {0}'.format(sponsor)


def __get_domain_affinities(name):
    if name is None:
        return {}
    else:
        return conf.domain_affinities.get(str(name).lower(), dict())
