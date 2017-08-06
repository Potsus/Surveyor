from sqlalchemy import Column, types, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
 
 
Base = declarative_base()
 
 
class Location(Base):
    __tablename__ = 'locations'
    id    = Column(types.Integer, primary_key=True)
    name  = Column(types.String(256))
    north = Column(types.Float(precision=32))
    south = Column(types.Float(precision=32))
    east  = Column(types.Float(precision=32))
    west  = Column(types.Float(precision=32))


 
 
from sqlalchemy import create_engine
engine = create_engine('mysql://surveyuser:surveyuser@localhost/surveydb')
 
from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)

connection = session()
tester = Location(name='Australia', north=-0.6911343999999999, south=-51.66332320000001, east=166.7429167, west=100.0911072)
connection.add(tester)
connection.commit()