
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Institution(Base):
    __tablename__ = 'institutions'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    claims = relationship("Claim", back_populates="institution")

class Owner(Base):
    __tablename__ = 'owners'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    national_id = Column(String, unique=True)
    claims = relationship("Claim", back_populates="owner")

class Claim(Base):
    __tablename__ = 'claims'
    id = Column(Integer, primary_key=True)
    asset_type = Column(String, nullable=False)
    asset_id = Column(String, nullable=False)
    claimant_name = Column(String)
    created_at = Column(DateTime)
    owner_id = Column(Integer, ForeignKey('owners.id'))
    institution_id = Column(Integer, ForeignKey('institutions.id'))
    owner = relationship("Owner", back_populates="claims")
    institution = relationship("Institution", back_populates="claims")