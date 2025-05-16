import pandas as pd
import asyncio
from playwright.async_api import async_playwright
from serpapi import GoogleSearch
import logging
import json
from dotenv import load_dotenv, find_dotenv
# Load environment variables
_ = load_dotenv(find_dotenv())


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def extract_job_description(page, url):
    try:
        # Navigate to the URL
        await page.goto(url, wait_until='networkidle')
        await asyncio.sleep(2)  # Give extra time for content to load
        
        # Try different selectors for job descriptions
        selectors = [
            '.job-details',
            '.description__text',
            '#job-details',
            '[data-automation="job-description"]',
            '.job-description',
            '.description'
        ]
        
        description = ""
        for selector in selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=5000)
                if element:
                    description = await element.inner_text()
                    if description:
                        break
            except:
                continue
        
        return description.strip() if description else "No description found"
        
    except Exception as e:
        logger.error(f"Error extracting job description from {url}: {str(e)}")
        return "Error: Could not extract job description"

async def process_jobs(jobs_data):
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        for job in jobs_data:
            url = job.get('job_link', '')
            if not url:
                continue
                
            logger.info(f"Processing job: {job.get('title', 'Unknown')} at {job.get('company_name', 'Unknown')}")
            
            description = await extract_job_description(page, url)
            
            job_info = {
                'Title': job.get('title', ''),
                'Company': job.get('company_name', ''),
                'Location': job.get('location', ''),
                'URL': url,
                'Description': description,
                'Salary': job.get('salary', ''),
                'Source': job.get('via', '')
            }
            
            results.append(job_info)
            await asyncio.sleep(2)  # Delay between requests
        
        await browser.close()
    
    return results

def get_jobs_from_serpapi(query, location):
    """
    Get jobs from Google Jobs API via SerpAPI
    """
    params = {
        "engine": "google_jobs",
        "q": f"{query} {location}",
        "ltype": "1",
        "hl": "en",
        "api_key": "fd310304cec59413586436f0ff1afac95c18894784316e9c934b8273992a2a1d"
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        return results.get("jobs_results", [])
    except Exception as e:
        logger.error(f"Error fetching jobs from SerpAPI: {str(e)}")
        return []

def get_preferred_apply_link(apply_options):
    """
    Get the preferred apply link from multiple options.
    Priority: Direct company website > LinkedIn > Indeed > Others
    """
    if not apply_options:
        return None
        
    # Priority order of application sources
    priority_sources = ['workable', 'ashbyhq',       # Simple 1-page forms
        ]
    
    # First try to find a link matching priority sources
    for source in priority_sources:
        for option in apply_options:
            if source in option.get('link', '').lower():
                return {
                    'source': option.get('title', 'Unknown'),
                    'url': option.get('link', '')
                }
    
    # If no priority source found, return the first option
    return {
        'source': apply_options[0].get('title', 'Unknown'),
        'url': apply_options[0].get('link', '')
    }

def process_jobs(jobs_data):
    """
    Process jobs data and extract relevant information
    """
    processed_jobs = []
    
    for job in jobs_data:
        # Get the preferred apply link
        apply_info = get_preferred_apply_link(job.get('apply_options', []))
        
        # Create job entry
        job_info = {
            'Title': job.get('title', ''),
            'Company': job.get('company_name', ''),
            'Location': job.get('location', ''),
            'Description': job.get('description', ''),
            'Posted': job.get('detected_extensions', {}).get('posted_at', ''),
            'Job_Type': job.get('detected_extensions', {}).get('schedule_type', ''),
            'Apply_Source': apply_info['source'] if apply_info else '',
            'Apply_URL': apply_info['url'] if apply_info else '',
            'Via': job.get('via', ''),
            'Qualifications': job.get('detected_extensions', {}).get('qualifications', '')
        }
        
        processed_jobs.append(job_info)
    
    return processed_jobs

def main():
    try:
        # Get jobs from SerpAPI
        logger.info("Fetching jobs from Google Jobs API...")
        jobs_data = get_jobs_from_serpapi("Data Analyst", "Remote")
        logger.info(f"Found {len(jobs_data)} jobs")
        
        # Save raw data
        with open('raw_jobs_data.json', 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False)
        logger.info("Saved raw jobs data to raw_jobs_data.json")
        
        # Process jobs
        processed_jobs = process_jobs(jobs_data)
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(processed_jobs)
        df["Combined"] = (
    "title: " + df["Title"].astype(str) + "\n"
    + "company: " + df["Company"].astype(str) + "\n"
    + "location: " + df["Location"].astype(str) + "\n"
    + "description: " + df["Description"].astype(str)
)
        df["Coverletter"] = None
        df["recruiter_email"] = None
        df.to_csv('JobsData.csv', index=False, encoding='utf-8')
        logger.info(f"Successfully saved {len(df)} jobs to JobsData.csv")
        
        # Display summary
        print("\nSummary:")
        print(f"Total jobs processed: {len(df)}")
        print(f"Unique companies: {df['Company'].nunique()}")
        print(f"Locations: {df['Location'].unique()}")
        print("\nApplication sources distribution:")
        print(df['Apply_Source'].value_counts())
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 