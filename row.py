from database import *

class Row(Base):

    #SETUP TABLE COLUMNS
    __tablename__ = 'rows'
    id    = Column(types.Integer, primary_key=True)
    grid  = Column(types.Float(precision=32))
    south = Column(types.Float(precision=32))
    east  = Column(types.Float(precision=32))
    west  = Column(types.Float(precision=32))
    #END TABLE SETUP