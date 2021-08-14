import os

import click
from flask_migrate import Migrate
from main import create_app, db


app = create_app(os.getenv("APP_SETTINGS"))
migrate = Migrate(app, db)

@app.after_request
def after_request(response):
    try:
        name_file = response.response.file.name[13:]
        os.remove(name_file)
    except:
        pass
    return response


@app.shell_context_processor
def make_shell_context():
    return _import_payment_models()


if __name__ == "__main__":
    app.cli()


def _import_payment_models():
    from main.models.models import (
        EntryImages,
        ClassificationResult,
    )

    return dict(
        db=db,
        EntryImages=EntryImages,
        ClassificationResult=ClassificationResult,
    )
