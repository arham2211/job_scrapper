"""
Parallel Job Scraper Runner

This script runs seek.py, jobsearch.py, jora.py, and career.py in parallel using multiprocessing,
then combines their JSON outputs into a single CSV file.

Directory Structure:
- output/seek/seek_jobs.json
- output/jobsearch/jobsearch_jobs.json
- output/jora/jora_jobs.json
- output/career/career_jobs.json
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


def run_jora_scraper():
    """Run the Jora scraper"""
    print("\n[JORA] Starting Jora scraper...")
    try:
        result = subprocess.run(
            [sys.executable, "jora.py"],
            cwd=os.getcwd(),
            capture_output=True,
            text=True
        )
        print(f"[JORA] {result.stdout}")
        if result.stderr:
            print(f"[JORA ERROR] {result.stderr}")
        print("[JORA] Completed!")
        return result.returncode == 0
    except Exception as e:
        print(f"[JORA ERROR] Failed to run: {e}")
        return False


def run_career_scraper():
    """Run the CareerOne scraper"""
    print("\n[CAREER] Starting CareerOne scraper...")
    try:
        result = subprocess.run(
            [sys.executable, "career.py"],
            cwd=os.getcwd(),
            capture_output=True,
            text=True
        )
        print(f"[CAREER] {result.stdout}")
        if result.stderr:
            print(f"[CAREER ERROR] {result.stderr}")
        print("[CAREER] Completed!")
        return result.returncode == 0
    except Exception as e:
        print(f"[CAREER ERROR] Failed to run: {e}")
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
    """Combine JSON files from all scrapers into a single CSV"""
    print("\n" + "="*60)
    print("COMBINING RESULTS INTO CSV")
    print("="*60)
    
    # Load data from all sources
    seek_data = load_json_file("output/seek/seek_jobs.json")
    jobsearch_data = load_json_file("output/jobsearch/jobsearch_jobs.json")
    jora_data = load_json_file("output/jora/jora_jobs.json")
    career_data = load_json_file("output/career/career_jobs.json")
    
    # Add source column to identify where each job came from
    for job in seek_data:
        job['source'] = 'seek'
    
    for job in jobsearch_data:
        job['source'] = 'jobsearch'

    for job in jora_data:
        job['source'] = 'jora'

    for job in career_data:
        job['source'] = 'careerone'
    
    # Combine all jobs
    all_jobs = seek_data + jobsearch_data + jora_data + career_data
    
    if not all_jobs:
        print("⚠ No jobs found to combine!")
        return False
    
    print(f"\nTotal jobs collected: {len(all_jobs)}")
    print(f"  - Seek: {len(seek_data)}")
    print(f"  - JobSearch: {len(jobsearch_data)}")
    print(f"  - Jora: {len(jora_data)}")
    print(f"  - CareerOne: {len(career_data)}")
    
    # Convert to DataFrame
    df = pd.DataFrame(all_jobs)
    
    print(f"\nTotal jobs before removing duplicates: {len(df)}")
    
    # Remove duplicates
    df_deduplicated = df.drop_duplicates(
        keep='first'
    )
    
    duplicates_removed = len(df) - len(df_deduplicated)
    print(f"Removed {duplicates_removed} duplicate jobs")
    print(f"Total unique jobs: {len(df_deduplicated)}")
    
    # Reorder columns for better readability
    column_order = [
        'source',
        'job_title',
        'company_name',
        'location',
        'city',
        'state',
        'country',
        'is_remote',
        'is_hybrid',
        # 'classification', # REMOVED
        'work_type',
        'salary_range',
        'min_annual_salary',
        'max_annual_salary',
        # 'posting_time',
        'posted_date',
        'job_description',
        'url'
    ]
    
    # Only include columns that exist in the data
    existing_columns = [col for col in column_order if col in df_deduplicated.columns]
    df_final = df_deduplicated[existing_columns]
    
    # Save to CSV
    output_file = "combined_jobs.csv"
    df_final.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n✓ Successfully created {output_file}")
    print(f"  Columns: {', '.join(existing_columns)}")
    print(f"  Total rows: {len(df_final)}")
    
    return True


def main():
    """Main execution function"""
    print("="*60)
    print("PARALLEL JOB SCRAPER RUNNER")
    print("="*60)
    
    # Ensure output directories exist
    os.makedirs("output/seek", exist_ok=True)
    os.makedirs("output/jobsearch", exist_ok=True)
    os.makedirs("output/jora", exist_ok=True)
    os.makedirs("output/career", exist_ok=True)
    
    # Create processes for parallel execution
    seek_process = multiprocessing.Process(target=run_seek_scraper)
    jobsearch_process = multiprocessing.Process(target=run_jobsearch_scraper)
    jora_process = multiprocessing.Process(target=run_jora_scraper)
    career_process = multiprocessing.Process(target=run_career_scraper)
    
    # Start all scrapers in parallel
    print("\nStarting all scrapers in parallel...")
    seek_process.start()
    jobsearch_process.start()
    jora_process.start()
    career_process.start()
    
    # Wait for all to complete
    print("\nWaiting for scrapers to complete...")
    seek_process.join()
    jobsearch_process.join()
    jora_process.join()
    career_process.join()
    
    print("\n" + "="*60)
    print("ALL SCRAPERS COMPLETED")
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
        print("  - output/jora/jora_jobs.json")
        print("  - output/career/career_jobs.json")
        print("  - combined_jobs.csv")
    else:
        print("\n⚠ Warning: CSV generation had issues. Check the logs above.")


if __name__ == "__main__":
    main()
