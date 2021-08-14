"""App functions"""
from os.path import isfile

from flask import current_app, render_template, make_response, url_for
from main.models.payments_db import Provider, Payment, Site
from main.util.common_utils import plugin_split, str_split
from main.util.connectors.connector_factory import ConnectorFactory
from main.util.crypting.encryptor_utils import EncryptionUtils

import json, sys


class AppController:
    def __init__(
        self,
        site=None,
        site_code=None,
        site_id=None,
        data=None,
        use_detokenizer=False,
        uses=True,
        view=None,
        auto_render=True,
        auto_layouts=True,
    ):
        self.site = site
        self.site_code = site_code
        self.site_id = site_id
        self.data = data
        self.use_detokenizer = use_detokenizer
        self.regexSiteId = "/.{0}^[A-Za-z]{2}$.{0}/"

        self.layout = url_for("static", filename="css/default.css")
        self.uses = uses
        self.view_path = "templates/"
        self.layouts_path = "templates/layouts"
        self.view = view
        self.auto_render = auto_render
        self.auto_layouts = auto_layouts

        self.css = url_for("static", filename="css/default.css")
        self.params = []
        self.layout_html = ""
        self.data_layouts = {}

    @staticmethod
    def load_connector(self, provider_id):
        provider = Provider.get_by_id(provider_id)
        connector_id = provider.connector_id
        
        site = Site.query.filter_by(id=provider.site_id).first()
        provider_country = site.country
        provider_site = site.name

        if connector_id:
            try:
                connector = ConnectorFactory.create(
                    connector_id, provider_country, provider_site
                )
                if connector:
                    return connector
                else:
                    return "Connector not found: {}".format(connector_id), 404
            except Exception as exc:
                return "Connector not found error: {}".format(exc), 404
        else:
            return "Can't get connector_id for provider id: {}".format(provider_id), 404

    def decrypt_from_checkout(self, request_data, site_country):
        if current_app.config["SECURITY_USE_ENCRYPTION"]:
            decrypted_data = EncryptionUtils.decrypt_form_parameters_to_payments(
                request_data, site_country
            )
            return decrypted_data
        return request_data

    def recaptcha(self, data, options, site_id=None):
        defaults = {
            "title": "",
            "message": "",
        }

        style_url = url_for("static", filename="css/default.css")

        options = {**options, **defaults}

        if "custom_js" in data:
            data["custom_js"] = f"{data['custom_js']}/{data['custom_js']}.js?v=1"

        render_data = {}
        render_data["data"] = data
        render_data["style"] = style_url
        render_data["title_for_layour"] = options["title"]
        render_data["message"] = options["message"]
        render_data["type"] = options["title"]
        render_data["card_digits"] = list(
            str_split(data["UserOneclick"]["last4CardDigits"].rjust(4, "0"))
        )

        return render_template("elements/require_validation.html", **render_data)

    def config_redir(self, redirect_data, options=None, side_id=None):

        if options is None:
            options = {
                "title": "",
                "message": "",
            }

        style = ""

        if side_id:
            site_name = Site.get_name_by_id(id=side_id)
            style = f"/css/{site_name.lower()}.css"
        else:
            if self.site_id is not None:
                if "Side" in self.site_id:
                    style = url_for(
                        "static",
                        filename=f"css/{(self.site['Side']['name']).lower()}.css",
                    )

        style_file_css = f"{current_app.config.get('CSS_PAYMENTS')}{style}"

        if isfile(style_file_css):
            self.css = style
            print("ok path exist")

        if "custom_js" in redirect_data:
            redirect_data[
                "coustom_js"
            ] = f"{redirect_data['custom_js']}/{redirect_data['coustom_js']}.js?v=1"

        redirect_data["style"] = self.css
        redirect_data["type"] = options["type"] if "type" in options else ""
        redirect_data["message"] = options["message"]
        redirect_data["title_for_layout"] = options["title"]

        self.data_layouts = redirect_data
        if current_app.config.get("DEBUG"):
            # self.data_layouts['style'] = url_for('static', filename="css/debug.css")
            self.data_layouts["debug"] = True

    def redir(self, redirect_data, options=None, side_id=None):
        self.config_redir(redirect_data, options, side_id)
        self.layouts_path = "layouts/redirect.html"
        self.view_path = "elements/redirect.html"
        html_render = self.render()

        return html_render

    def simple_redir(self, redirect_data, options=None, side_id=None):
        self.config_redir(redirect_data, options, side_id)
        self.layouts_path = "layouts/simple_redirect.html"
        self.view_path = f"elements/{redirect_data['form_data']['render']}.html"
        html_render = self.render()
        return html_render

    def render(self):
        if self.uses and type(self.uses) is list:
            for model in self.uses:
                data = plugin_split(model)
                plugin = data[0]
                class_name = data[1]
                self.params = {"plugin": plugin, "className": class_name}

        self.auto_render = False

        self.data_layouts["extended"] = self.layouts_path

        # if current_app.config.get("DEBUG"):
        #     self.data_layouts["debug"] = True
        #     self.data_layouts["url"] = "https://www.youtube.com/watch?v=qoBIyxWEiOw"
        #     self.data_layouts["type"] = "redirigiendo al proveedor de pagos..."
        #     self.data_layouts["message"] = "REDIRIGIENDO A UN VIAJE INTERDIMENCIONAL"
        #     self.data_layouts[
        #         "title_for_layout"
        #     ] = "ESTAMOS REDIRIGIENDO A LUGAR DE DESTINO"

        elements_html = render_template(self.view_path, data=self.data_layouts)
        resp = make_response(elements_html)
        resp.headers["Content-Type"] = "text/html"
        return resp

    def return_to_site(self, site_id, url, data_to_encode, options):
        data = {
            "method": "POST",
            "enctype": "multipart/form-data",
            "url": url,
            "form_data": {},
        }

        (
            data["form_data"]["encdata"],
            data["form_data"]["signature"],
        ) = self.site.encrypt_data(site_id, json.dumps(data_to_encode))

        self.redir(data, options)
