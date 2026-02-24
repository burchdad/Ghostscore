from sqlalchemy import Column, String, Float, Integer
from models.database import Base
class ProfileCalibration(Base):
    __tablename__ = "profile_calibration"
    profile_id = Column(String, primary_key=True)
    offset = Column(Float, nullable=False)
    actual_score = Column(Integer)
    estimated_score = Column(Integer)
