import pandas as pd
import requests
from bs4 import BeautifulSoup
import os


def collect_links_from_csv(csv_file):
    # Read the CSV file into a DataFrame
    data = pd.read_csv(csv_file)

    # Filter out rows where color is green
    data = data[data['Color'] == 'green']

    # Create a set to store all the links
    all_links = set()

    # Iterate over the rows of the DataFrame
    for row in data.itertuples(index=False):
        source_link = row[0]
        target = row[1]

        all_links.add(source_link)
        all_links.add(target)

    return all_links

# Function to check if a page has forms or user interaction
def check_page_security(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Check for login/password fields
    has_login_password_field = soup.find('input', {'type': 'password'}) is not None
    
    # Check for forms or user interaction
    has_forms_user_interaction = soup.find('form') is not None or soup.find('input', {'type': 'text'}) is not None
    
    return has_login_password_field, has_forms_user_interaction

# Function to calculate webpage sizes
def calculate_webpage_sizes(links):
    webpage_sizes = []
    links_with_sizes = {}
    
    for link in links:
        response = requests.get(link)
        size = len(response.content)
        webpage_sizes.append(size)
        links_with_sizes[size] = link
    
    max_size = max(webpage_sizes)
    min_size = min(webpage_sizes)
    average_size = sum(webpage_sizes) / len(webpage_sizes)
    
    return max_size, min_size, average_size, links_with_sizes

def write_results_to_csv(csv_file, pages_with_login_password_field, pages_with_forms_user_interaction, max_size):
    # Create a DataFrame with the results
    result_data = pd.DataFrame({
        'File Name': [csv_file],
        'Number of pages with a login/password field': [pages_with_login_password_field],
        'Number of pages with forms or user interaction': [pages_with_forms_user_interaction],
        'Maximum webpage size': [max_size]
    })

    # Write the DataFrame to a CSV file
    if not os.path.isfile('security_metrics.csv'):
        result_data.to_csv('security_metrics.csv', index=False)
    else:
        result_data.to_csv('security_metrics.csv', mode='a', header=False, index=False)


if __name__ == "__main__":
    # Specify the path to your CSV file
    file = 'database---tokiocity.csv'

    # Call the function to collect links from the CSV file
    all_links = collect_links_from_csv(file)

    # Crawl each link in the all_links set
    pages_with_login_password_field = 0
    pages_with_forms_user_interaction = 0

    for link in all_links:
        has_login_password_field, has_forms_user_interaction = check_page_security(link)

        if has_login_password_field:
            pages_with_login_password_field += 1

        if has_forms_user_interaction:
            pages_with_forms_user_interaction += 1

    # Calculate webpage sizes and get links with sizes
    max_size, min_size, average_size, links_with_sizes = calculate_webpage_sizes(all_links)

    # Write the results to a CSV file
    write_results_to_csv(file, pages_with_login_password_field, pages_with_forms_user_interaction, max_size)

    # Print the results
    print("Data written to security_metrics.csv file.")