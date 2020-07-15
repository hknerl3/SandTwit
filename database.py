
from sqlalchemy.ext.automap import automap_base 
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker

Base = automap_base()
engine = create_engine("sqlite:///db/sosyalmedya",
connect_args={'check_same_thread': False}) 
Base.prepare(engine, reflect=True)
Session = sessionmaker(bind=engine)

class Database:
    @staticmethod
    def startCon():
        return Base # database tablolarını getirir.

    @staticmethod
    def loadSession():  
        session = Session()
        return session # oturum açma