from sqlalchemy import Column, String, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Wallet(Base):
    __tablename__ = 'wallets'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    balance = Column(Float, default=0.0)
