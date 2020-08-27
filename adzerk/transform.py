from urllib import parse
import json
import re
import logging
import distutils.util

import conf


def to_spoc(decision):
    if not decision:
        return {}
    custom_data = decision['contents'][0]['data']
    body = decision['contents'][0].get('body')
    if body:
        body = json.loads(body)

    events_map = {e["id"]: tracking_url_to_shim(e["url"]) for e in decision["events"]}

    spoc = {
        'id':                     decision['adId'],
        'flight_id':              decision['flightId'],
        'campaign_id':            decision['campaignId'],
        'title':                  custom_data['ctTitle'],
        'url':                    custom_data['ctUrl'],
        'domain':                 custom_data['ctDomain'],
        'excerpt':                custom_data['ctExcerpt'],
        'context':                __get_context(custom_data.get('ctSponsor')),
        'raw_image_src':          custom_data['ctFullimagepath'],
        'image_src':              __get_cdn_image(custom_data['ctFullimagepath']),
        'shim':      {
            'click':              tracking_url_to_shim(decision['clickUrl']),
            'impression':         tracking_url_to_shim(decision['impressionUrl']),
            'delete':             events_map[17],
            'save':               events_map[20],
        },
        'parameter_set':          'default',
        'caps':                   conf.spocs['caps'],
        'domain_affinities':      __get_domain_affinities(custom_data.get('ctDomain_affinities')),
        'personalization_models': get_personalization_models(body),
    }

    optional_fields = {
        'ctCta':                 'cta',
        'ctCollectionTitle':     'collection_title',
        'ctSponsor':             'sponsor',
        'ctSponsoredByOverride': 'sponsored_by_override',
    }
    for adzerk_key, spoc_key in optional_fields.items():
        if adzerk_key in custom_data and custom_data[adzerk_key]:
            spoc[spoc_key] = custom_data[adzerk_key]

    if 'sponsored_by_override' in spoc:
        spoc['sponsored_by_override'] = __clean_sponsored_by_override(spoc['sponsored_by_override'])

    try:
        spoc['min_score']  = float(custom_data['ctMin_score'])
        spoc['item_score'] = float(custom_data['ctItem_score'])
    except (KeyError, ValueError) as e:
        logging.warning(str(e))

    try:
        spoc['is_video'] = bool(distutils.util.strtobool(custom_data['ctIsVideo'].strip()))
    except (KeyError, ValueError):
        # Don't set is_video if ctIsVideo is not present or not a boolean (e.g. an empty string)
        pass

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


def is_collection(spocs):
    """
    :param spocs: A list of spocs
    :return: True if the list of spocs is a sponsored collection; spocs that should be featured together.
    """
    return all(spoc.get('collection_title') for spoc in spocs)


def to_collection(spocs):
    """
    Transforms a list of spocs to a sponsored collection dictionary.
    AdZerk does not support fields for a collection. We set them on all creatives and get them from an arbitrary one.
    :param spocs: A list of spocs
    :return: A dictionary with collection fields (title, flight_id, and sponsor) and a list of spocs.
    """
    collection = {
        'title':     spocs[0]['collection_title'],
        'flight_id': spocs[0]['flight_id'],
        'sponsor':   spocs[0]['sponsor'],
        'context':   __get_context(spocs[0]['sponsor']),
    }

    if 'sponsored_by_override' in spocs[0]:
        collection['sponsored_by_override'] = spocs[0]['sponsored_by_override']

    for spoc in spocs:
        del spoc['collection_title']
        spoc.pop('sponsored_by_override', None)

    collection['items'] = spocs
    return collection


def get_personalization_models(body):
    if body is None:
        return {}
    else:
        # Topics in AdZerk prefixed with topic_ correspond with models in Firefox prefixed with nb_model_.
        p = re.compile('^topic_')
        return {k: 1 for k in [p.sub('', t) for t, v in body.items() if p.match(t) and v in ('true', True)]}



def __get_cdn_image(raw_image_url):
    escaped = parse.quote(raw_image_url)
    return 'https://img-getpocket.cdn.mozilla.net/direct?url={0}&resize=w618-h310'.format(escaped)


def __get_context(sponsor):
    return 'Sponsored by {0}'.format(sponsor) if sponsor else ''


def __get_domain_affinities(name):
    if name is None:
        return {}
    else:
        return conf.domain_affinities.get(str(name).lower(), dict())


def __clean_sponsored_by_override(sponsored_by_override):
    """
    Return an empty string for 'sponsored_by_override' if the value in AdZerk is set to "blank" or "empty".
    @type sponsored_by_override: str
    """
    return re.sub(r'^(blank|empty)$', '', sponsored_by_override.strip(), flags=re.IGNORECASE)
