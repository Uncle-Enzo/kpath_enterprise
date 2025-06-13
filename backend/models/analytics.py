"""
Analytics tracking models for collecting usage statistics
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from backend.core.database import Base


class SearchQuery(Base):
    """Track search queries for analytics"""
    __tablename__ = "search_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    user_id = Column(Integer, nullable=True)  # Optional user tracking
    results_count = Column(Integer, default=0)
    response_time_ms = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SearchQuery(query='{self.query[:50]}', timestamp='{self.timestamp}')>"


class UserLoginLog(Base):
    """Track user login activities for analytics"""
    __tablename__ = "user_login_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    email = Column(String(255), nullable=False)
    login_timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<UserLoginLog(email='{self.email}', timestamp='{self.login_timestamp}')>"



class APIRequestLog(Base):
    """Track API requests for analytics"""
    __tablename__ = "api_request_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, nullable=True)  # Foreign key to APIKey
    endpoint = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, etc.
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<APIRequestLog(endpoint='{self.endpoint}', status='{self.status_code}')>"
