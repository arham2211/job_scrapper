from database import engine, Base, Job

def reset_db():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped.")

if __name__ == "__main__":
    reset_db()
