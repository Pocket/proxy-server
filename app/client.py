from app import conf
from app.adzerk.api import Api as AdZerk
import app.adzerk.transform
import logging


class Client:

    def __init__(self, version, consumer_key, pocket_id, ip, geolocation_provider,
                 site=None, placements=None, country=None, region=None):
        """
        :param version: API version to provide backwards-compatibility to older clients
        :param consumer_key: Identifies the consumer (e.g. Firefox)
        :param pocket_id: Anonymous Pocket user id
        :param ip: Client IP-address
        :param geolocation_provider: GeoIP2 database that converts an IP to a geolocation.
        :param site: Override the site. Leave None to use the default Firefox Production site.
        :param placements: Override the default placements. Leave None to get spocs.
        :param country: Set the country for debugging purposes. Leave None for IP-based geolocation.
        :param region: Set the region for debugging purposes. Leave None for IP-based geolocation.
        """
        self.version = int(version)
        self.consumer_key = consumer_key
        self.pocket_id = pocket_id
        self.ip = ip
        self.country = country
        self.region = region
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

        if self.country:
            targeting['country'] = self.country
        if self.region:
            targeting['region'] = self.region

        if self.pocket_id:
            targeting['pocket_id'] = self.pocket_id
        else:
            logging.warning("Could not target based on pocket_id because it's missing.")

        targeting['placements'] = self.placements

        adzerk_api = AdZerk(**targeting)
        decisions = adzerk_api.get_decisions()

        response = {
            'settings': app.conf.spocs['settings'],
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
                transformed_spocs = [app.adzerk.transform.to_spoc(s) for s in spocs]
                if self.version >= 2 and app.adzerk.transform.is_collection(transformed_spocs):
                    response[div] = app.adzerk.transform.to_collection(transformed_spocs)
                else:
                    response[div] = transformed_spocs
            else:
                response[div] = []
