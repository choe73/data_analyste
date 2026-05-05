from sqlalchemy import Column, String, Integer, DateTime, JSON, Boolean, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class APIType(str, enum.Enum):
    REST = "rest"
    CKAN = "ckan"
    GRAPHQL = "graphql"
    CSV = "csv"
    EXCEL = "excel"
    SATELLITE = "satellite"
    IOT = "iot"
    CUSTOM = "custom"


class AuthType(str, enum.Enum):
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC = "basic"
    OAUTH2 = "oauth2"
    CUSTOM = "custom"


class SourceStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Identité de la source
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text)
    category = Column(String(100), index=True)  # agriculture, health, energy, etc.
    country = Column(String(100), index=True)   # Pays d'origine
    
    # Configuration API
    url = Column(String(500), nullable=False)
    api_type = Column(Enum(APIType), default=APIType.REST, nullable=False)
    api_version = Column(String(50))
    
    # Authentification
    auth_type = Column(Enum(AuthType), default=AuthType.NONE, nullable=False)
    auth_credentials = Column(JSON)  # {api_key, token, username, password, etc.}
    
    # Schéma et mapping
    schema_mapping = Column(JSON)  # Mapping des champs source → format unifié
    data_format = Column(String(50))  # json, csv, xml, etc.
    
    # Collecte
    collection_frequency = Column(String(100))  # cron expression: "0 0 * * *"
    last_collected = Column(DateTime, nullable=True)
    next_collection = Column(DateTime, nullable=True)
    
    # Pagination
    supports_pagination = Column(Boolean, default=True)
    pagination_type = Column(String(50))  # offset, cursor, page
    pagination_param = Column(String(100))  # param name: "offset", "page", etc.
    page_size = Column(Integer, default=100)
    
    # Rate limiting
    rate_limit = Column(Integer)  # requests per minute
    rate_limit_window = Column(Integer, default=60)  # seconds
    
    # Status
    status = Column(Enum(SourceStatus), default=SourceStatus.TESTING, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Métadonnées
    total_records = Column(Integer, default=0)
    last_error = Column(Text)
    error_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="data_sources")
    collection_logs = relationship("CollectionLog", back_populates="data_source", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DataSource {self.name} ({self.api_type})>"


class CollectionLog(Base):
    __tablename__ = "collection_logs"

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False, index=True)
    
    # Résultats
    status = Column(String(50))  # success, error, partial
    records_fetched = Column(Integer, default=0)
    records_stored = Column(Integer, default=0)
    
    # Détails
    error_message = Column(Text)
    execution_time = Column(Integer)  # secondes
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)
    
    # Relations
    data_source = relationship("DataSource", back_populates="collection_logs")
    
    def __repr__(self):
        return f"<CollectionLog {self.data_source_id} - {self.status}>"
