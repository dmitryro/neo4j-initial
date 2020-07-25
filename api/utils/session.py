import os
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker


def obtain_session():
    """ Get SQLAlchemy session """
    engine = create_engine(os.environ['DATABASE_URL'])
    session = sessionmaker(autoflush=True)
    # Bind the sessionmaker to engine
    session.configure(bind=engine)
    return session()
