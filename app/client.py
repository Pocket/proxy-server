import conf
from adzerk.api import Api as AdZerk
import adzerk.transform
import logging


class Client:

    def __init__(self, version, consumer_key, pocket_id, ip, geolocation_provider,
                 site=None, placements=None):
        self.version = int(version)
        self.consumer_key = consumer_key
        self.pocket_id = pocket_id
        self.ip = ip
        if not geolocation_provider:
            logging.error('Need geolocation object')
        else:
            self.geolocation = geolocation_provider
        self.site = site
        self.placements = placements

    def get_spocs(self):
        targeting = {"site": self.site}     # setting site here by default so it's picked up by API

        try:
            geo = self.geolocation.get_city(self.ip)
            targeting['country'] = self.geolocation.get_country(geo)
            targeting['region'] = self.geolocation.get_region(geo)
        except Exception as e:
            logging.warning("Could not target based on geolocation. {0}".format(str(e)))

        if self.pocket_id:
            targeting['pocket_id'] = self.pocket_id
        else:
            logging.warning("Could not target based on pocket_id because it's missing.")

        targeting['placements'] = self.placements

        adzerk_api = AdZerk(**targeting)
        decisions = adzerk_api.get_decisions()

        response = {
            'settings': conf.spocs['settings'],
        }
        self.__transform_spocs(response, decisions)

        if conf.env in ('development', 'staging'):
            response['__debug__'] = adzerk_api.get_decision_body()

        return response

    def __transform_spocs(self, response, spocs_raw):
        # spocs is a dict from multiple decisions
        # so we add its elements to final response directly
        for div, spocs in spocs_raw.items():
            if spocs:
                transformed_spocs = [adzerk.transform.to_spoc(s) for s in spocs]
                if self.version >= 2 and adzerk.transform.is_collection(transformed_spocs):
                    response[div] = adzerk.transform.to_collection(transformed_spocs)
                else:
                    response[div] = transformed_spocs
            else:
                response[div] = []
