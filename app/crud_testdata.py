"""Optional helper to seed a few tasks.

Run:
  python -m app.crud_testdata
"""

import os
import sys

# Allow running as a script (python app/crud_testdata.py)
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from app.db import SessionLocal, engine
from app.models import Base, Task



def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for title, status in [
            ("Write PRD", "todo"),
            ("Implement API endpoints", "in_progress"),
            ("Ship v1 release", "done"),
        ]:
            db.add(Task(title=title, status=status))
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()

