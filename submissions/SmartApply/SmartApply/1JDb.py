import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse, parse_qs
import pandas as pd
from urllib.parse import urlparse


def get_apply_url(job_listing_url):
    response = requests.get(job_listing_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the <a> tag with the button text
    apply_link = soup.find('a', string=lambda s: s and 'Apply for this position' in s)
    
    # If not found, try by class (update class name if needed)
    if not apply_link:
        apply_link = soup.find('a', class_='tw-btn-primary')
    
    if apply_link and apply_link.has_attr('href'):
        return apply_link['href']
    else:
        return None


# Function to extract main job platform (domain without subdomains and TLDs)
def extract_job_platform(url):
    parsed = urlparse(url)
    domain_parts = parsed.netloc.split('.')

    # Remove 'www' or common subdomain prefixes
    domain_parts = [part for part in domain_parts if part not in ['www', 'jobs', 'job-boards', 'boards']]

    # Take the second-level domain (like 'lever' in 'jobs.lever.co')
    if len(domain_parts) >= 2:
        return domain_parts[-2]  # second last part
    elif domain_parts:
        return domain_parts[0]  # fallback
    else:
        return None

# Example: load your DataFrame (update this line with your actual data source)
df = pd.read_csv("JobsData.csv")
df["Apply_URL"] = df["Apply_URL"].apply(get_apply_url)

# Apply function to create 'via' column
df['Apply_Source'] = df['Apply_URL'].apply(extract_job_platform)

#print(df['Apply_URL'])
#print(df['Apply_Source'])

df = df[df['Apply_Source'] != 'greenhouse']

# Step 2: Define custom sort order
priority = ['ashbyhq', 'workable']

# Function to assign sort key
def sort_key(x):
    if x in priority:
        return (priority.index(x), x)
    else:
        return (len(priority), x)  # all others go after

# Step 3: Sort the filtered list using the custom key
df = df.sort_values(by='Apply_Source', key=lambda col: col.map(sort_key))

# Reset index if needed
df = df.reset_index(drop=True)
# Save the updated DataFrame
df.to_csv("JobsData.csv", index=False)
