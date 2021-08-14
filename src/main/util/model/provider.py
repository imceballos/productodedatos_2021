"""Business logic for /provider Model"""
from http import HTTPStatus

from main import db
from main.models.models import Provider
from main.util.app_controller import AppController


class ProviderControl(AppController):
    def __init__(self, site=None, data=None):
        AppController.__init__(self, site, data)

    def get(self):

        if self.site == None:
            return "No site set in App Controller", 404

        providers = Provider.get_for_site(str(self.site.id), True, False)

        if len(providers) == 0:
            return "Not provider for that site", 404

        providers = self.process_providers(providers, self.site.id)

        return providers

    def process_providers(self, providers, site_id, uid=None):
        providers_modified = providers
        for provider in providers:
            connector = AppController.load_connector(self, str(provider.id))
            # TODO: get_config from connector, process_get_provider from config of connector
            if connector and "get_config" in connector.__dict__:
                config = connnector.get_config()
                if (
                    config != None
                    and "process_get_provider" in connector.__dict__
                    and uid != None
                    and config.read("get_provider_need_action")
                ):
                    providers_modified[provider] = connector.process_get_provider(
                        uid, site_id, providers[provider]
                    )
        return providers_modified

    def get_field_mapping(self, provider):
        provider_id = Provider.get_id_by_short_name(provider)
        connector = AppController.load_connector(self, str(provider_id))
        response = None

        # TODO: get_field_map from connector
        if connector != None and "get_field_map" in connector.__dict__:
            response = connector.get_field_map()
        else:
            response = []

        return response

    def edit(self):
        if self.data == None:
            return "Not data found", 404

        response = Provider.edit(self.data)

        return response, 202

        return True
