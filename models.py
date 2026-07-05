from sqlalchemy import Column, Integer, String, Boolean, Text, UniqueConstraint
from database import Base

class GraduateJob(Base):
    __tablename__ = "graduate_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    company_breakdown = Column(String, nullable=True)
    cover_letter_snippet = Column(String, nullable=True)
    has_ml_team = Column(Boolean, default=False)
    status = Column(String, default="Not Applied")
    source_url = Column(Text, nullable=True)

    # Ensure no duplicate title & company combinations exist in database
    __table_args = (
        UniqueConstraint('job_title', 'company', name='_job_company_uc')
    )
