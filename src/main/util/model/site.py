"""Business logic for /provider Model"""
from http import HTTPStatus
import requests

from flask import current_app
from main import db
from main.models.models import Provider, Site, Payment
from main.util.app_controller import AppController
from main.util.model.risk import RiskControl
from main.util.crypting.encryptor_utils import EncryptionUtils


class SiteControl(AppController):
    def __init__(self):
        AppController.__init__(self)
        self.failure_return_value = "failed"
        self.success_return_value = "confirmed"

    def hook_end(self, site_id, order_number, mock_site_response=False):
        current_app.logger.info(
            "[hookNotify] hookEnd:: {} with OrderNumber {}".format(
                site_id, order_number
            )
        )

        if not isinstance(site_id, int):
            current_app.logger.info(
                "[hookNotify] hookEnd:: called with non-numeric siteId:: {}".format(
                    site_id
                )
            )
            return self.failure_return_value

        site = Site.get_by_id(site_id)
        if not site:
            current_app.logger.info(
                "[hookNotify] hookEnd:: Invalid site! ID: {}, orderNumber: {}".format(
                    site_id, order_number
                )
            )
            return self.failure_return_value

        payment = Payment().find_by_siteid_order(site.id, order_number)
        if not payment:
            current_app.logger.info(
                "[hookNotify] hookEnd:: Can't find payment with order number {} for site {}".format(
                    order_number, site.display_name
                )
            )
            return self.failure_return_value

        current_app.logger.info(
            "[hookNotify] hookEnd:: Will Notify order number {} for site {}".format(
                order_number, site.display_name
            )
        )
        data = {"order_number": order_number}
        return self.request_confirmation(
            site,
            site.url_confirm,
            data,
            self.success_return_value,
            self.failure_return_value,
            mock_site_response,
        )

    def hook_confirm(self, site_id, order_number, mock_site_response=False):
        current_app.logger.info(
            "[hookNotify] hookConfirm:: {} with OrderNumber {}".format(
                site_id, order_number
            )
        )
        return self.hook_end(site_id, order_number, mock_site_response)

    def hook_notify(self, payment, final_status, multipart=False):
        site = Site.get_by_id(payment.site_id)

        if not site:
            current_app.logger.info("[hookNotify] Empty site! ID: {} for Payment ID: {}".format(payment.site_id, payment.id))
            return self.fail_return_value

        if not final_status:
            current_app.logger.info(
                "[hookNotify] Empty finalStatus ID: {}".format(payment.id)
            )
            return self.fail_return_value

        if not site.url_notify:
            current_app.logger.info(
                "[hookNotify] Empty url_notify for Payment ID: {}".format(
                    payment.id
                )
            )
            return self.success_return_value

        risk_data = RiskControl().get_by_payment_id(payment.id)
        risk_data_code = None
        if risk_data is not None:
            if risk_data.decision:
                risk_data_code = risk_data.decision
            else:
                risk_data_code = risk_data.recommendation_code

        data = {
            "order_number": payment.order_number,
            "amount": payment.amount,
            "status": final_status.lower(),
            "notify": 1,
            "risk_code": risk_data_code,
        }

        current_app.logger.info(
            "[hookNotify] Notify to: {} , Payment: {}, orderNumber: {}, contains Data:: {}".format(
                site.url_notify,
                payment.id,
                payment.order_number,
                data,
            )
        )
        return self.request_confirmation(
            site,
            site.url_notify,
            data,
            self.success_return_value,
            self.failure_return_value,
            False,
            multipart,
        )

    def request_confirmation(
        self,
        site,
        site_url,
        data,
        success_return_value,
        failure_return_value,
        mock=False,
        multipart=False,
    ):
        if mock:
            return self.success_return_value

        payload = EncryptionUtils.encrypt_data_from_payments(data, site.country)

        try:
            r = requests.post(url=site_url, data=payload)
        except Exception as exc:
            current_app.logger.info(
                "[hookNotify] Exception {} trying to Request Confirmation for Site ID {} - Site URL {}".format(
                    str(exc), site.id, site_url
                )
            )
            return False

        if r.status_code not in [200, 204]:
            current_app.logger.info(
                "[hookNotify] Response code error {} site {}: {}".format(
                    r.status_code, site.id, site_url
                )
            )
            return self.failure_return_value

        current_app.logger.info(
            "[hookNotify] Response code Success {} site {}: {}".format(
                r.status_code, site.id, site_url
            )
        )
        return self.success_return_value