from database import *

class point(Base):
    #SETUP TABLE COLUMNS
    __tablename__ = 'points'
    id        = Column(types.Integer, primary_key=True)
    latitude  = Column(types.Float)
    longitude = Column(types.Float)
    elevation = Column(types.Float)
    row = 
    #END COLUMN SETUP

    def __repr__(self):
        return '%s' % self.elevation