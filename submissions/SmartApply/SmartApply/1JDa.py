import pandas as pd
import requests
import logging
from datetime import datetime
import json
import re
from bs4 import BeautifulSoup
import openai

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_html_content(html_content):
    """
    Clean HTML content and extract meaningful text
    """
    try:
        # First use BeautifulSoup to clean basic HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text and clean up whitespace
        text = soup.get_text(separator=' ')
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Use GPT to structure and clean the content
        prompt = f"""
        Clean and structure the following job description text, removing any remaining HTML artifacts or unwanted formatting.
        Organize it into clear sections if possible (e.g., About, Responsibilities, Requirements, Benefits).
        Keep only the essential information and format it in a clean, readable way.
        
        Text to clean:
        {text}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model= "gpt-4.1-nano", #"gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a job description cleaner. Clean and structure job descriptions while maintaining all important information."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            cleaned_text = response.choices[0].message.content.strip()
            return cleaned_text
        except Exception as e:
            logger.warning(f"GPT cleaning failed, falling back to basic cleaning: {str(e)}")
            return text
            
    except Exception as e:
        logger.error(f"Error cleaning HTML content: {str(e)}")
        return html_content

def get_jobs_from_remotive(category=None, search=None, limit=None):
    """
    Get jobs from Remotive API
    """
    base_url = "https://remotive.com/api/remote-jobs"
    params = {}
    
    if category:
        params['category'] = category
    if search:
        params['search'] = search
    if limit:
        params['limit'] = limit
        
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('jobs', [])
    except Exception as e:
        logger.error(f"Error fetching jobs from Remotive API: {str(e)}")
        return []

def process_jobs(jobs_data):
    """
    Process jobs data and extract relevant information
    """
    processed_jobs = []
    
    for job in jobs_data:
        # Clean the description
        cleaned_description = clean_html_content(job.get('description', ''))
        
        # Create job entry
        job_info = {
            'Title': job.get('title', ''),
            'Company': job.get('company_name', ''),
            'Location': job.get('candidate_required_location', ''),
            'Description': cleaned_description,
            'Posted': job.get('publication_date', ''),
            'Job_Type': job.get('job_type', ''),
            'Apply_Source': 'Remotive',
            'Apply_URL': job.get('url', ''),
            'Via': 'Remotive.com',
            'Qualifications': '',  # Remotive API doesn't provide this directly
            'Salary': job.get('salary', '')
        }
        
        processed_jobs.append(job_info)
    
    return processed_jobs

def main():
    try:
        # Set your OpenAI API key
        openai.api_key = 'your-api-key-here'  # Replace with your actual API key
        
        # Get jobs from Remotive API
        logger.info("Fetching jobs from Remotive API...")
        jobs_data = get_jobs_from_remotive(search="Data Analyst",limit=5)
        logger.info(f"Found {len(jobs_data)} jobs")
        
        # Save raw data
        with open('raw_remotive_jobs_data.json', 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False)
        logger.info("Saved raw jobs data to raw_remotive_jobs_data.json")
        
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
        df["score"] = None
        df["reason"] = None
        
        # Save to CSV
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