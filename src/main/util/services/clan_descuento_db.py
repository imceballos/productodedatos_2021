from sqlalchemy import create_engine
from flask import current_app


class ClanDescuentoDatabase:
    def __init__(self):
        self.engine = create_engine(current_app.config["PEIXEURBANO_DATABASE_URI"])

    def get_payments(self, ids):
        query = f"select * from payments where id IN {ids}"
        try:
            with self.engine.connect() as con:
                rs = con.execute(query).fetchall()
                return rs
        except Exception:
            current_app.logger.info("Clan Descuento DB Error")