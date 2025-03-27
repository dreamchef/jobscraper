# modules
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_job_links(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    job_links = []
    
    category_names = [
        "New Graduates", "Internships", "Commercial", "US Government", "US Government - Indo-Pacific", 
        "International Government", "Product Development", "Information Security", "Mission Operations", "Sales", 
        "Finance", "Legal", "Global Security and Investigations", "People", "Administrative", "Core Operations", 
        "Talent", "Technical Operations"
    ]
    
    for category_name in category_names:
        category_section = soup.find(string=category_name)
        if category_section:
            print(f'Category found: {category_name}')
            category_parent = category_section.find_parent()
            job_anchors = category_parent.find_all('a', href=True) if category_parent else []
            print(f'Found {len(job_anchors)} job links in {category_name}')
            
            for job in job_anchors:
                job_url = job['href']
                if 'jobs.lever.co/palantir' in job_url:  # Filter job links
                    job_links.append(job_url)
    
    return list(set(job_links))  # Remove duplicates

def get_job_details(job_url):
    response = requests.get(job_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    title = soup.find('h2').text.strip() if soup.find('h2') else 'N/A'
    location = 'N/A'
    
    role_section = soup.find(string='The Role')
    role_description = ''
    if role_section:
        parent = role_section.find_parent()
        for sibling in parent.find_next_siblings():
            if sibling.name and sibling.name.startswith('h'):
                break
            role_description += sibling.text.strip() + '\n'
    
    salary_section = soup.find(string=lambda x: x and 'Salary' in x)
    salary = salary_section.parent.text.strip() if salary_section else 'N/A'
    
    return {
        'Job Title': title,
        'Location': location,
        'Role Description': role_description,
        'Salary': salary,
        'Job URL': job_url
    }

def main():
    base_url = 'https://www.palantir.com/careers/'
    job_links = get_job_links(base_url)
    
    job_data = []
    for job_url in job_links:
        print(f'Scraping {job_url}...')
        job_details = get_job_details(job_url)
        job_data.append(job_details)
        time.sleep(1)  # Be respectful to the server
    
    df = pd.DataFrame(job_data)
    df.to_excel('Palantir_Jobs.xlsx', index=False)
    print('Saved to Palantir_Jobs.xlsx')

if __name__ == '__main__':
    main()
