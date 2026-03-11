
try:
    from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Text, JSON  # type: ignore
    from sqlalchemy.ext.declarative import declarative_base  # type: ignore
    from sqlalchemy.orm import relationship  # type: ignore
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

    # Fallback classes for when SQLAlchemy is not available
    class Column:
        def __init__(self, *args, **kwargs):
            pass

    Integer = String = DateTime = ForeignKey = Float = Boolean = Text = JSON = Column

    class declarative_base:
        def __init__(self):
            pass

        def __call__(self):
            return type('Base', (), {})

    class relationship:
        def __init__(self, *args, **kwargs):
            pass

from datetime import datetime

if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()
else:
    Base = declarative_base()

class IdentityCore(Base):
    __tablename__ = 'identity_core'
    identity_id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    national_id = Column(String, unique=True)
    postal_address = Column(String)
    phone = Column(String)
    email = Column(String)
    date_of_birth = Column(DateTime)
    assets = relationship("Asset", back_populates="identity")
    aliases = relationship("IdentityAlias", back_populates="aliases")
    links = relationship("IdentityLinks", back_populates="links")
    cluster_memberships = relationship("ClusterMembers", back_populates="identity")

class Asset(Base):
    __tablename__ = 'assets'
    asset_id = Column(Integer, primary_key=True)
    identity_id = Column(Integer, ForeignKey('identity_core.identity_id'))
    asset_type = Column(String, nullable=False)  # cash, shares, safe_deposit
    institution = Column(String, nullable=False)
    account_number = Column(String)
    amount = Column(Float)
    status = Column(String)
    identity = relationship("IdentityCore", back_populates="assets")

class IdentityAlias(Base):
    __tablename__ = 'identity_alias'
    alias_id = Column(Integer, primary_key=True)
    identity_id = Column(Integer, ForeignKey('identity_core.identity_id'))
    name_variations = Column(String)
    previous_addresses = Column(String)
    alternative_ids = Column(String)
    identity = relationship("IdentityCore", back_populates="aliases")

class IdentityLinks(Base):
    __tablename__ = 'identity_links'
    link_id = Column(Integer, primary_key=True)
    identity_id = Column(Integer, ForeignKey('identity_core.identity_id'))
    linked_identifier = Column(String, nullable=False)
    identifier_type = Column(String, nullable=False)  # e.g., phone, email, account
    confidence_score = Column(Float, default=1.0)
    identity = relationship("IdentityCore", back_populates="links")

# Identity Resolution Engine (IRE) Models
class IdentityClusters(Base):
    __tablename__ = 'identity_clusters'
    cluster_id = Column(Integer, primary_key=True)
    representative_name = Column(String, nullable=False)
    representative_address = Column(Text)
    cluster_size = Column(Integer, nullable=False, default=1)
    confidence_score = Column(Float, nullable=False, default=0.0)
    country = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    validated = Column(Boolean, default=False)
    members = relationship("ClusterMembers", back_populates="cluster")
    resolution_logs = relationship("IdentityResolutionLog", back_populates="cluster")

class ClusterMembers(Base):
    __tablename__ = 'cluster_members'
    member_id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, ForeignKey('identity_clusters.cluster_id'), nullable=False)
    identity_id = Column(Integer, ForeignKey('identity_core.identity_id'))
    source_table = Column(String, nullable=False)  # identity_core, identity_alias, etc.
    source_record_id = Column(Integer, nullable=False)
    similarity_score = Column(Float, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    cluster = relationship("IdentityClusters", back_populates="members")
    identity = relationship("IdentityCore", back_populates="cluster_memberships")

class IdentityResolutionLog(Base):
    __tablename__ = 'identity_resolution_log'
    log_id = Column(Integer, primary_key=True)
    query_hash = Column(String, nullable=False)
    query_params = Column(JSON)
    resolved_cluster_id = Column(Integer, ForeignKey('identity_clusters.cluster_id'))
    confidence_score = Column(Float)
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    cluster = relationship("IdentityClusters", back_populates="resolution_logs")