import logging

import requests
import aiohttp
from copy import deepcopy

from app.adzerk import validation
from app import conf


class AdZerkException(Exception):
    pass


class Api:

    def __init__(self, pocket_id, country=None, region=None, site=None, placements=None, api_key: str = None):
        self.pocket_id = pocket_id
        self.country = country
        self.region = region
        self.site = site
        self.placements = placements
        self.api_key = api_key

    async def get_decisions(self):
        """
        Calls Adzerk API with request body
        :return: A map of decisions, previously
        a list of decisions for one div/placement.
        """
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(limit=None)
        # Wrap the request in a try/catch block to log timeout errors.
        try:
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                async with session.post(conf.adzerk['decision']['url'], json=self.get_decision_body()) as r:
                    if r.status == 400:
                        text = await r.text()
                        # This occurs when there is no site with the requested id from adzerk.
                        # So instead we send back no results but log an error
                        logging.error(text)
                        return dict()
                    response = await r.json()

            decisions = response['decisions']
            if not decisions or len(decisions) == 0:
                return dict()
            for _, dec in decisions.items():
                if dec:
                    map(validation.validate_decision, dec)
            return decisions
        except Exception as e:
            # Log the exact parameters sent to Kevel
            logging.error(repr(self.get_decision_body()))
            return dict()

    def get_decision_body(self):
        body = deepcopy(conf.adzerk['decision']['body'])
        self.__add_targeting(body)
        self.__add_placements(body)
        self.__add_site(body)
        logging.debug(body)
        return body

    def __add_targeting(self, body):
        if self.pocket_id is not None:
            body['user'] = {'key': self.pocket_id}
        keywords = []
        if self.country:
            keywords.append(self.country)
            if self.region:
                keywords.append(self.country + '-' + self.region)
        if keywords:
            body['keywords'] = keywords

    def __add_site(self, body):
        if self.site is not None:
            for placement in body['placements']:
                placement['siteId'] = self.site

    def __add_placements(self, body):
        # if placement exists, we need to replace default values with placements from client
        if self.placements and len(self.placements) > 0:
            default_placement = body['placements'].pop(0)  # remove default
            for place in self.placements:
                copy_place = deepcopy(default_placement)
                if 'ad_types' in place:
                    copy_place['adTypes'] = place['ad_types']
                if 'zone_ids' in place:
                    copy_place['zoneIds'] = place['zone_ids']
                copy_place['divName'] = place['name']
                body['placements'].append(copy_place)

    def delete_user(self):
        response = requests.delete(
            url=conf.adzerk['forget_endpoint'],
            params={'userKey': self.pocket_id},
            headers={'X-Adzerk-ApiKey': self.api_key},
            timeout=30
        )
        response.raise_for_status()
        return response
