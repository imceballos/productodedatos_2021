from main import db


class Base(db.Model):
    __abstract__ = True

    def __repr__(self):
        mydict = vars(self)
        mydict.pop("_sa_instance_state")
        return mydict

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as exc:
            print("log exc {}".format(str(exc)))
            return False

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as exc:
            print("log exc {}".format(str(exc)))
            return False

    def update(self, props: dict):
        try:
            for key, value in props.items():
                setattr(self, key, value)

            db.session.commit()
            db.session.flush()
        except Exception as exc:
            print("log exc {}".format(str(exc)))
            return False
