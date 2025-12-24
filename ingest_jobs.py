import os
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from database import init_db, SessionLocal, Job

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_json_file(filepath):
    """Load JSON file and return data, or empty list if file doesn't exist"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} jobs from {filepath}")
                return data
        else:
            logger.warning(f"File not found: {filepath}")
            return []
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return []

def parse_date(date_str):
    """Parse date string to Python date object. Returns None if parsing fails."""
    if not date_str:
        return None
    try:
        # Assumes date format 'YYYY-MM-DD' from scraper
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None 
    except Exception:
        return None

def ingest_data():
    """Ingest data from JSON files into the database"""
    
    # 1. Initialize Tables
    logger.info("Initializing database tables...")
    init_db()
    
    # 2. Load Data
    seek_file = "output/seek/seek_jobs.json"
    jobsearch_file = "output/jobsearch/jobsearch_jobs.json"
    
    seek_data = load_json_file(seek_file)
    jobsearch_data = load_json_file(jobsearch_file)
    
    # Add source tag
    for job in seek_data:
        job['source'] = 'seek'
    for job in jobsearch_data:
        job['source'] = 'jobsearch'
        
    all_jobs = seek_data + jobsearch_data
    
    if not all_jobs:
        logger.warning("No jobs found to ingest.")
        return

    db = SessionLocal()
    try:
        total_processed = 0
        total_inserted = 0
        total_updated = 0
        
        for job_data in all_jobs:
            total_processed += 1
            
            # Extract fields
            url = job_data.get('url')
            if not url:
                continue # Skip jobs without URL
            
            # Check if exists
            existing_job = db.query(Job).filter(Job.url == url).first()
            
            # Parse numeric fields
            min_salary = job_data.get('min_annual_salary')
            max_salary = job_data.get('max_annual_salary')
            
            # Prepare data
            job_dict = {
                'source': job_data.get('source'),
                'job_title': job_data.get('job_title'),
                'company_name': job_data.get('company_name'),
                'location': job_data.get('location'),
                'city': job_data.get('city'),
                'state': job_data.get('state'),
                'country': job_data.get('country'),
                'is_remote': job_data.get('is_remote', False),
                'is_hybrid': job_data.get('is_hybrid', False),
                # 'classification': job_data.get('classification'), # REMOVED
                'work_type': job_data.get('work_type'),
                'salary_range': job_data.get('salary_range'),
                'min_annual_salary': float(min_salary) if min_salary else None,
                'max_annual_salary': float(max_salary) if max_salary else None,
                # 'posting_time': job_data.get('posting_time'),
                'posted_date': parse_date(job_data.get('posted_date')),
                'job_description': job_data.get('job_description'),
                'url': url
            }
            
            if existing_job:
                # Update existing
                for key, value in job_dict.items():
                    setattr(existing_job, key, value)
                total_updated += 1
            else:
                # Create new
                new_job = Job(**job_dict)
                db.add(new_job)
                total_inserted += 1
                
        db.commit()
        logger.info(f"Ingestion complete. Processed: {total_processed}, Inserted: {total_inserted}, Updated: {total_updated}")
        
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    ingest_data()
