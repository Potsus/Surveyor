from database import *

class point(Base):
    #SETUP TABLE COLUMNS
    __tablename__ = 'points'
    id        = Column(types.Integer, primary_key=True)
    point     = Column(types.Float)
    elevation = Column(types.Float)
    row = 
    #END COLUMN SETUP

    def __repr__(self):
        return '%s' % self.elevation

class Point(Base):
    #SETUP TABLE COLUMNS
    __tablename__ = 'points'
    id        = Column(types.Integer, primary_key=True)
    point  = Column(Geometry('POINT'))
    elevation = Column(types.Float)
    resolution = Column(types.Float)
    row = Column(types.Integer, ForeignKey('Row.id'))
    #END COLUMN SETUP

    def __repr__(self):
        return '%s' % self.elevation