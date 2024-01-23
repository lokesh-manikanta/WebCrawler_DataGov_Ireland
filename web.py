import os
import requests
import json
from bs4 import BeautifulSoup

# Define the base URL
base_url = 'https://data.gov.ie'
# Define the URL pattern for pagination
url_pattern = f'{base_url}/dataset?_theme_limit=0&theme=Education+and+Sport&q=education&_res_format_limit=0&sort=score+desc%2C+metadata_created+desc&page='

# Start with page 1
page_number = 1

# Create a directory to save the downloaded files
if not os.path.exists('downloaded_files'):
    os.makedirs('downloaded_files')

# Open a text file to save sublinks and JSON URLs
with open('failed_downloads.txt', 'w') as failed_downloads_file:

    while True:
        # Construct the source URL for the current page
        source_url = f'{url_pattern}{page_number}'

        # Send an HTTP GET request to the source URL
        response = requests.get(source_url)

        # Check the HTTP response status code
        if response.status_code == 200:
            # Retrieve the HTML content from the HTTP response
            html_content = response.text

            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Check if the page contains dataset entries
            dataset_entries = soup.select('div.dataset-content')
            if not dataset_entries:
                # No dataset entries on this page, end the loop
                break

            # Find all dataset sub-links on the source page
            sub_links = soup.select('a[href*="/dataset/"]')

            # Access each sub-link
            for link_tag in sub_links:
                # Construct the full URL by appending the relative URL to the base URL
                sub_link_url = f'{base_url}{link_tag["href"]}' if link_tag["href"].startswith('/') else f'{base_url}/{link_tag["href"]}'
                
                # Send an HTTP GET request to the sub-link URL
                sub_response = requests.get(sub_link_url)

                # Check the HTTP response status code for the sub-link
                if sub_response.status_code == 200:
                    # Parse the HTML content of the sub-link with BeautifulSoup
                    sub_soup = BeautifulSoup(sub_response.text, 'html.parser')
                    
                    # Extract the dataset title from the heading on the sub-link page
                    dataset_title = sub_soup.select_one('h1, h2').text.strip() if sub_soup.select_one('h1, h2') else "Unknown Title"
                    
                    # Extract the dataset ID from the HTML content
                    dataset_id_element = sub_soup.select_one('a.tag')
                    dataset_id = dataset_id_element.text if dataset_id_element else "Unknown ID"
                    
                    # Print the dataset ID
                    print(f'Dataset ID: {dataset_id}')

                    # Check for CSV, XLSX, and JSON-stat files
                    file_formats = [('CSV', 'text/csv'), ('XLSX', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'), ('JSON-stat', 'application/json')]
                    downloaded = False
                    for file_format, expected_content_type in file_formats:
                        try:
                            download_link = f"https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/{dataset_id}/{file_format}/1.0/en"
                            print(f'Trying to download from: {download_link}')  # Print the constructed download link
                            download_response = requests.get(download_link)
                            if download_response.status_code == 200 and download_response.headers['Content-Type'] == expected_content_type:
                                # Save the file
                                file_extension = 'json' if file_format == 'JSON-stat' else file_format.lower()
                                file_path = f'downloaded_files/{dataset_title}.{file_extension}'
                                with open(file_path, 'wb') as file:
                                    if file_format == 'JSON-stat':
                                        # Save JSON content to a file
                                        json_content = download_response.json()
                                        file.write(json.dumps(json_content).encode())
                                        # Save JSON URL to text file
                                        failed_downloads_file.write(f'JSON URL: {download_link}\n')
                                    else:
                                        # Save CSV or XLSX content to a file
                                        file.write(download_response.content)
                                print(f"File successfully downloaded: {file_path}")
                                downloaded = True
                                break
                            else:
                                print(f"{file_format} file not available for dataset: {dataset_title}")
                        except Exception as e:
                            print(f"Error downloading {file_format} file for dataset {dataset_title}: {e}")

                    # If dataset couldn't be downloaded, save the sublink to text file
                    if not downloaded:
                        failed_downloads_file.write(f'Sublink for manual download: {sub_link_url}\n')

            # Increment the page number for the next iteration
            page_number += 1

        else:
            print("Failed to retrieve the source webpage")
            break

print("Process completed")
