from sqlalchemy import Column, Integer, String

try:
    from app.database import Base
except ImportError:
    try:
        from app.database.database import Base
    except ImportError:
        from ..database import Base

class AwsAccount(Base):
    __tablename__ = "aws_accounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account_name = Column(String, nullable=False)
    account_id = Column(String, nullable=False)
    role_arn = Column(String, nullable=False)
    external_id = Column(String, nullable=True)
