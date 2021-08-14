"""Business logic for /blacklist model."""

from datetime import datetime, timedelta

from flask import current_app
from main import db
from main.models.models import Payment, Blacklist
from main.util.app_controller import AppController


class BlacklistControl(AppController):
    def __init__(self):
        AppController.__init__(self)

    def get_total_trx_by_ip(self, ip_adress):
        minutes = current_app.config.get("TRX_MINUTES_VALIDATE")
        from_time = datetime.now() - timedelta(minutes=minutes)
        from_time_string = from_time.strftime("%Y-%m-%d %H:%M:%S")
        return Payment.find_by_trx_ip(from_time_string, ip_adress)

    def validate_ip_by_last_minutes(self, site_id, ip_address):
        trx_to_add = current_app.config.get("TRX_TO_ADD")
        results = self.get_total_trx_by_ip(ip_address)

        if not results:
            return True

        if results > trx_to_add:
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            data = Blacklist(
                site_id=site_id,
                user_id=None,
                ip=ip_address,
                active=1,
                created_by=12050551,
                created=dt_string,
            )
            db.session.add(data)
            db.session.commit()

            return False
        return True

    def is_not_in_blacklist_user_site(self, user_id, site_id):
        results = Blacklist.is_notinblack_usersite(user_id, site_id)
        return not bool(results)

    def is_not_in_blacklist_ip_site(self, ip_address, site_id):
        results = Blacklist.is_notinblack_ipsite(ip_address, site_id)
        return not bool(results)

    def is_valid_buyer(self, site_id, user_id, ip_address):
        whitelist = current_app.config.get("TRX_WHITE_LIST")

        if ip_address in whitelist:
            return True

        is_valid = self.is_not_in_blacklist_ip_site(ip_address, site_id)
        if is_valid:
            if site_id in [21, 25]:
                is_valid = self.validate_ip_by_last_minutes(site_id, ip_address)
                return is_valid
            is_valid = self.is_not_in_blacklist_user_site(user_id, site_id)

        return is_valid
