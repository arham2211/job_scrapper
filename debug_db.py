from database import Job
from sqlalchemy import inspect

print("Inspecting Job model...")
mapper = inspect(Job)
print("Columns in Job model:")
for column in mapper.columns:
    print(f" - {column.key}")

print("\nAttempting to instantiate Job with posting_time...")
try:
    j = Job(posting_time="test", job_title="Debug Title")
    print("SUCCESS: Job instantiated.")
except Exception as e:
    print(f"FAILURE: {e}")
