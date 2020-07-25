from flask import g
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from app import app
from werkzeug.local import LocalProxy

def connect_to_database():
    db = SQLAlchemy(app)
    return db


def get_db():
    if 'db' not in g:
        g.db = connect_to_database()

    return g.db

db = LocalProxy(get_db)

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@migrate.configure
def configure_alembic(config):
    # modify config object
    return config

if __name__ == '__main__':
    manager.run()
