# SQLAlchemy ORM models
# Defines database tables: evaluations, input_files, results, errors

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    model_name = Column(String, default="Default")
    mode = Column(String)  # "strict" or "lenient"
    
    # Relationships
    input_files = relationship("InputFile", back_populates="evaluation", cascade="all, delete-orphan")
    results = relationship("Result", back_populates="evaluation", cascade="all, delete-orphan")
    errors = relationship("Error", back_populates="evaluation", cascade="all, delete-orphan")


class InputFile(Base):
    __tablename__ = "input_files"
    
    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"))
    original_text = Column(Text)
    redacted_text = Column(Text)
    ground_truth = Column(Text)  # JSON string
    predictions = Column(Text)  # JSON string
    
    evaluation = relationship("Evaluation", back_populates="input_files")


class Result(Base):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"))
    
    # Overall metrics
    true_positives = Column(Integer)
    true_negatives = Column(Integer)
    false_positives = Column(Integer)
    false_negatives = Column(Integer)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    accuracy = Column(Float)
    
    # Additional data
    confusion_matrix = Column(Text)  # JSON string
    per_entity_metrics = Column(Text)  # JSON string
    redaction_analysis = Column(Text)  # JSON string
    diff_html = Column(Text)  # HTML content
    
    evaluation = relationship("Evaluation", back_populates="results")


class Error(Base):
    __tablename__ = "errors"
    
    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"))
    error_type = Column(String)  # "FP", "FN", "LEAK", "OVER", "UNDER", "SEMI"
    entity_type = Column(String)  # "EMAIL", "PAN", "PHONE", etc.
    position_start = Column(Integer)
    position_end = Column(Integer)
    text = Column(String)
    description = Column(Text)
    
    evaluation = relationship("Evaluation", back_populates="errors")

