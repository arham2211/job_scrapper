# Job Scraper

Automated job scraping system that collects job listings from Seek and JobSearch Australia.

## Features

- 🔄 **Parallel Scraping**: Runs both scrapers simultaneously for faster execution
- 📄 **Multi-Page Collection**: Scrapes 20 pages from Seek and 30 pages from JobSearch
- 🔍 **Duplicate Removal**: Automatically removes duplicate job listings
- 📊 **Combined Output**: Generates a single CSV file with deduplicated results
- 🤖 **Automated CI/CD**: GitHub Actions workflow runs daily
- 📁 **Organized Structure**: Separate folders for each source

## Quick Start

### Local Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the scrapers
python run_scrapers.py
```

### Output Files

- `output/seek/seek_jobs.json` - Seek scraper results
- `output/jobsearch/jobsearch_jobs.json` - JobSearch scraper results
- `combined_jobs.csv` - Combined CSV file (ready for Excel)

## CI/CD Pipeline

The GitHub Actions workflow automatically:
- Runs daily at 9 AM UTC (2 PM Pakistan time)
- Scrapes 20 pages from Seek and 30 pages from JobSearch in parallel
- Combines results and removes duplicates
- Uploads CSV as downloadable artifact

### Manual Trigger

You can manually trigger the workflow from the GitHub Actions tab.

## Project Structure

```
Job-scraper/
├── .github/
│   └── workflows/
│       └── scrape-jobs.yml    # CI/CD workflow
├── output/
│   ├── seek/
│   │   └── seek_jobs.json
│   └── jobsearch/
│       └── jobsearch_jobs.json
├── seek.py                     # Seek scraper
├── jobsearch.py                # JobSearch scraper
├── run_scrapers.py             # Main runner script
├── combined_jobs.csv           # Combined results
└── requirements.txt            # Python dependencies
```

## CSV Columns

- `source` - Which website (seek/jobsearch)
- `job_title` - Job title
- `company_name` - Company name
- `location` - Job location
- `classification` - Job category
- `work_type` - Employment type (full-time, part-time, etc.)
- `salary_range` - Salary information
- `posting_time` - When the job was posted
- `job_description` - Full job description
- `url` - Link to the job posting

## Requirements

- Python 3.11+
- Chrome/Chromium browser
- Dependencies listed in `requirements.txt`

## License

This project is for educational purposes.
