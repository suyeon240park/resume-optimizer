import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    LargeBinary,
    Numeric,
    String,
    Text,
    Uuid,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    google_id = Column(String(255), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    base_resumes = relationship("BaseResume", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")


class BaseResume(Base):
    __tablename__ = "base_resumes"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    latex_source = Column(Text, nullable=False)
    preset_type = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="base_resumes")
    versions = relationship("ResumeVersion", back_populates="base_resume")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company = Column(String(255), nullable=False)
    role_title = Column(String(255), nullable=False)
    portal_url = Column(Text)
    jd_snapshot = Column(Text, nullable=False)
    jd_analysis = Column(JSON)
    status = Column(String(50), default="draft")
    applied_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="applications")
    versions = relationship("ResumeVersion", back_populates="application", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_applications_status", "user_id", "status"),
    )


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    application_id = Column(Uuid, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    base_resume_id = Column(Uuid, ForeignKey("base_resumes.id"), nullable=True)
    latex_source = Column(Text, nullable=False)
    compiled_pdf = Column(LargeBinary)
    changes_applied = Column(JSON, nullable=False)
    ats_score = Column(Numeric(5, 2))
    version_number = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    application = relationship("Application", back_populates="versions")
    base_resume = relationship("BaseResume", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("application_id", "version_number", name="uq_app_version"),
    )
