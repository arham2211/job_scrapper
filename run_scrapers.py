"""
Parallel Job Scraper Runner

This script runs both seek.py and jobsearch.py in parallel using multiprocessing,
then combines their JSON outputs into a single CSV file.

Directory Structure:
- output/seek/seek_jobs.json
- output/jobsearch/jobsearch_jobs.json
- combined_jobs.csv (root directory)
"""

import multiprocessing
import subprocess
import json
import pandas as pd
import os
import sys
from pathlib import Path


def run_seek_scraper():
    """Run the Seek job scraper"""
    print("\n[SEEK] Starting Seek scraper...")
    try:
        result = subprocess.run(
            [sys.executable, "seek.py"],
            cwd=os.getcwd(),
            capture_output=True,
            text=True
        )
        print(f"[SEEK] {result.stdout}")
        if result.stderr:
            print(f"[SEEK ERROR] {result.stderr}")
        print("[SEEK] Completed!")
        return result.returncode == 0
    except Exception as e:
        print(f"[SEEK ERROR] Failed to run: {e}")
        return False


def run_jobsearch_scraper():
    """Run the JobSearch scraper"""
    print("\n[JOBSEARCH] Starting JobSearch scraper...")
    try:
        result = subprocess.run(
            [sys.executable, "jobsearch.py"],
            cwd=os.getcwd(),
            capture_output=True,
            text=True
        )
        print(f"[JOBSEARCH] {result.stdout}")
        if result.stderr:
            print(f"[JOBSEARCH ERROR] {result.stderr}")
        print("[JOBSEARCH] Completed!")
        return result.returncode == 0
    except Exception as e:
        print(f"[JOBSEARCH ERROR] Failed to run: {e}")
        return False


def load_json_file(filepath):
    """Load JSON file and return data, or empty list if file doesn't exist"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✓ Loaded {len(data)} jobs from {filepath}")
                return data
        else:
            print(f"⚠ File not found: {filepath}")
            return []
    except Exception as e:
        print(f"✗ Error loading {filepath}: {e}")
        return []


def combine_to_csv():
    """Combine JSON files from both scrapers into a single CSV"""
    print("\n" + "="*60)
    print("COMBINING RESULTS INTO CSV")
    print("="*60)
    
    # Load data from both sources
    seek_data = load_json_file("output/seek/seek_jobs.json")
    jobsearch_data = load_json_file("output/jobsearch/jobsearch_jobs.json")
    
    # Add source column to identify where each job came from
    for job in seek_data:
        job['source'] = 'seek'
    
    for job in jobsearch_data:
        job['source'] = 'jobsearch'
    
    # Combine all jobs
    all_jobs = seek_data + jobsearch_data
    
    if not all_jobs:
        print("⚠ No jobs found to combine!")
        return False
    
    print(f"\nTotal jobs collected: {len(all_jobs)}")
    print(f"  - Seek: {len(seek_data)}")
    print(f"  - JobSearch: {len(jobsearch_data)}")
    
    # Convert to DataFrame
    df = pd.DataFrame(all_jobs)
    
    # Reorder columns for better readability
    column_order = [
        'source',
        'job_title',
        'company_name',
        'location',
        'classification',
        'work_type',
        'salary_range',
        'posting_time',
        'job_description',
        'url'
    ]
    
    # Only include columns that exist in the data
    existing_columns = [col for col in column_order if col in df.columns]
    df = df[existing_columns]
    
    # Save to CSV
    output_file = "combined_jobs.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n✓ Successfully created {output_file}")
    print(f"  Columns: {', '.join(existing_columns)}")
    print(f"  Total rows: {len(df)}")
    
    return True


def main():
    """Main execution function"""
    print("="*60)
    print("PARALLEL JOB SCRAPER RUNNER")
    print("="*60)
    
    # Ensure output directories exist
    os.makedirs("output/seek", exist_ok=True)
    os.makedirs("output/jobsearch", exist_ok=True)
    
    # Create processes for parallel execution
    seek_process = multiprocessing.Process(target=run_seek_scraper)
    jobsearch_process = multiprocessing.Process(target=run_jobsearch_scraper)
    
    # Start both scrapers in parallel
    print("\nStarting both scrapers in parallel...")
    seek_process.start()
    jobsearch_process.start()
    
    # Wait for both to complete
    print("\nWaiting for scrapers to complete...")
    seek_process.join()
    jobsearch_process.join()
    
    print("\n" + "="*60)
    print("BOTH SCRAPERS COMPLETED")
    print("="*60)
    
    # Combine results into CSV
    success = combine_to_csv()
    
    if success:
        print("\n" + "="*60)
        print("✓ ALL DONE!")
        print("="*60)
        print("\nOutput files:")
        print("  - output/seek/seek_jobs.json")
        print("  - output/jobsearch/jobsearch_jobs.json")
        print("  - combined_jobs.csv")
    else:
        print("\n⚠ Warning: CSV generation had issues. Check the logs above.")


if __name__ == "__main__":
    main()
