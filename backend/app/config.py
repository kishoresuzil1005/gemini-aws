import os
from dotenv import load_dotenv

# 1. Attempt to load standard local backend .env first
load_dotenv()

# 2. As an ultra-robust fallback, look for a root-level .env file up one directory 
# (useful if the user configured their credentials in the project root folder)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parent_env = os.path.join(base_dir, "..", ".env")
if os.path.exists(parent_env):
    load_dotenv(dotenv_path=parent_env)

# Database Configurations
DB_USER = os.getenv("DB_USER", "postgres")
# Default to "your_secure_password" to match our guide and local Docker setup, failing that default to "postgres"
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_secure_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "cloudops_db")

# Construct the URI dynamically so individual DB_* configurations work flawlessly
DEFAULT_DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# AWS Credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", os.getenv("AWS_REGION", "us-east-1"))

# Check if AWS credentials are configured
def is_aws_configured() -> bool:
    return bool(AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)
