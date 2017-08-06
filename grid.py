from database import *

class Grid(Base):

    #SETUP TABLE COLUMNS
    __tablename__ = 'grids'
    id    = Column(types.Integer, primary_key=True)

    quality = Column(types.Integer)
    rows = relationship("Row")
    #END TABLE SETUP


    class Row(Base):

    #SETUP TABLE COLUMNS
    __tablename__ = 'rows'
    id    = Column(types.Integer, primary_key=True)
    grid  = Column(types.Integer, ForeignKey('Grid.id'))
    latitude = Column(types.Float)
    points = relationship("Point")
    #END TABLE SETUP



    class Point(Base):
    #SETUP TABLE COLUMNS
    __tablename__ = 'points'
    id        = Column(types.Integer, primary_key=True)
    latitude  = Column(types.Float)
    longitude = Column(types.Float)
    elevation = Column(types.Float)
    resolution
    row = Column(types.Integer, ForeignKey('Row.id'))
    #END COLUMN SETUP

    def __repr__(self):
        return '%s' % self.elevation