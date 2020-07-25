import logging
from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import engine_from_config, pool, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
import pathlib
from alembic import context
import sys
import os

current_path = os.path.dirname(os.path.abspath(__file__))

ROOT_PATH = os.path.join(current_path, '..')
sys.path.append(ROOT_PATH)

meta_list = list()
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


# Interpret the config file for Python logging.
# This line sets up loggers basically.
logger = logging.getLogger('alembic.env')

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
def combine_metadata(*args):
    m = MetaData()
    for metadata_temp in args:
        for metadata in metadata_temp:
            for t in metadata.tables.values():
                t.tometadata(m)
    return m


#target_metadata = combine_metadata(meta_list)
#target_metadata = combine_metadata(meta_list)

#target_metadata = combine_metadata(meta_list)

#target_metadata = current_app.extensions['migrate'].db.metadata

for file in [file for file in
os.listdir(str(pathlib.Path(__file__).parent.parent) + "/models/") if file !=
'__pycache__' and file != '__init__.py']:
    p, m = file.rsplit('.', 1)
    module_in_file = __import__("models." + str(p))
    files_module_in_directory = getattr(module_in_file, p)

    new_model = []
    for item in files_module_in_directory.__dict__:
        try:
            files_module = getattr(files_module_in_directory, item)
            if isinstance(files_module, Table) is True:
                meta_list.append(files_module.metadata)
        except Exception as e:
            print(e)

target_metadata = combine_metadata(meta_list)

def get_url():
    url = config.get_main_option("sqlalchemy.url")
    return url



def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    #url = config.get_main_option("sqlalchemy.url")
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()



def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(get_url())
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
