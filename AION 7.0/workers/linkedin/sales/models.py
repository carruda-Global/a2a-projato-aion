import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from .database import Base


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"
    CONVERTED = "converted"


class DealStage(str, enum.Enum):
    DISCOVERY = "discovery"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class LeadSource(str, enum.Enum):
    LINKEDIN = "linkedin"
    WEBSITE = "website"
    REFERRAL = "referral"
    EVENT = "event"
    COLD_OUTREACH = "cold_outreach"
    CROSS_SELL = "cross_sell"
    OTHER = "other"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    company = Column(String(255))
    title = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    linkedin_url = Column(String(500))
    linkedin_id = Column(String(100), unique=True)
    source = Column(String(50), default=LeadSource.OTHER.value)
    status = Column(String(50), default=LeadStatus.NEW.value)

    # BANT Scoring
    bant_budget = Column(Float, default=0)
    bant_authority = Column(Float, default=0)
    bant_need = Column(Float, default=0)
    bant_timeline = Column(Float, default=0)
    score = Column(Float, default=0)
    score_breakdown = Column(JSON)

    # Enrichment
    industry = Column(String(255))
    company_size = Column(String(50))
    location = Column(String(255))
    summary = Column(Text)
    skills = Column(JSON)
    recent_posts = Column(JSON)

    # Metadata
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contacted_at = Column(DateTime)

    deals = relationship("Deal", back_populates="lead", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="lead", cascade="all, delete-orphan")


class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    stage = Column(String(50), default=DealStage.DISCOVERY.value)
    value = Column(Float, default=0)
    probability = Column(Integer, default=10)
    expected_close_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lead = relationship("Lead", back_populates="deals")
    activities = relationship("Activity", back_populates="deal", cascade="all, delete-orphan")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True)
    type = Column(String(50))  # email, call, meeting, note, linkedin_message
    subject = Column(String(255))
    description = Column(Text)
    outcome = Column(String(50))  # positive, negative, pending
    scheduled_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="activities")
    deal = relationship("Deal", back_populates="activities")


class OutreachSequence(Base):
    __tablename__ = "outreach_sequences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    steps = Column(JSON)  # list of {day, subject, template, channel}
    trigger_conditions = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class OutreachStep(Base):
    __tablename__ = "outreach_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    sequence_id = Column(Integer, ForeignKey("outreach_sequences.id"))
    step_number = Column(Integer)
    channel = Column(String(50))  # email, linkedin, phone
    subject = Column(String(255))
    content = Column(Text)
    status = Column(String(50), default="pending")  # pending, sent, opened, replied, bounced
    sent_at = Column(DateTime)
    replied_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
