#SETUP SQLALCHEMY AND DATABASE
from sqlalchemy import Table, Column, types, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
 
Base = declarative_base()

from sqlalchemy import create_engine
engine = create_engine('mysql://surveyuser:surveyuser@localhost/surveydb')
 
from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)
db = session()
#END SQLALCHEMY