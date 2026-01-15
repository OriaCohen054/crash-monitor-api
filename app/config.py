import os

# .env will be used locally. On Koyeb we will set env vars in the dashboard.
MONGODB_URI = os.getenv("MONGODB_URI", "")
DB_NAME = os.getenv("DB_NAME", "crash_monitor")
