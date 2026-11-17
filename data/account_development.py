import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

CMS_EMAIL = os.environ.get("SGS_CMS_EMAIL", "auto@test.id")
CMS_PASSWORD = os.environ.get("SGS_CMS_PASSWORD", "")
