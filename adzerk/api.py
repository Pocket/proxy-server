import requests
import logging
from copy import deepcopy


import conf
import adzerk.validation
import adzerk.secret
import random
import time


class AdZerkException(Exception):
    pass


class Api:

    def __init__(self, pocket_id, country=None, region=None, site=None, placements=None):
        self.pocket_id = pocket_id
        self.country = country
        self.region = region
        self.site = site
        self.placements = placements

    def get_decisions(self):
        """
        Calls Adzerk API with request body
        :return: A map of decisions, previously
        a list of decisions for one div/placement.
        """
        # changelog decisions now returns a *map* response of placement -> decisions
        r = requests.post(conf.adzerk['decision']['url'], json=self.get_decision_body(),
                          timeout=0.5)
        response = r.json()

        decisions = response['decisions']
        if not decisions or len(decisions) == 0:
            return dict()
        for _,dec in decisions.items():
            if dec:
                map(adzerk.validation.validate_decision, dec)
        return decisions

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
            default_placement = body['placements'].pop(0)   # remove default
            for place in self.placements:
                copy_place = deepcopy(default_placement)
                if 'ad_types' in place:
                    copy_place['adTypes'] = place['ad_types']
                if 'zone_ids' in place:
                    copy_place['zoneIds'] = place['zone_ids']
                copy_place['divName'] = place['name']
                body['placements'].append(copy_place)

    def delete_user(self):
        response = self.__request_delete_user()
        if response.status_code == 401:
            self.__update_api_key()
            response = self.delete_user()
        if response.status_code != 200:
            logging.error("{0} delete_user: {1}".format(str(response.status_code), response.text))

        return response

    def __request_delete_user(self):
        return requests.delete(
            url=conf.adzerk['forget_endpoint'],
            params={'userKey': self.pocket_id},
            headers={'X-Adzerk-ApiKey': conf.adzerk['api_key']},
            timeout=30
        )

    def __update_api_key(self):
        conf.adzerk['api_key'] = adzerk.secret.get_api_key()
