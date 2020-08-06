import os
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from singleton import SingletonMeta


class SessionManager(metaclass=SingletonMeta):
    def __init__(self):
        """ Get SQLAlchemy session """
        self._engine = create_engine(os.environ['DATABASE_URL'])        
        self._session = sessionmaker(autoflush=True)
        self._session.configure(bind=self._engine)

    def obtain_session(self):
        return self._session()


    
