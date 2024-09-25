import requests
from bs4 import BeautifulSoup

# URL of the CDTFA tax rates page
url = 'https://www.cdtfa.ca.gov/taxes-and-fees/rates.aspx'

# Send a request to the website
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the section containing the tax rates
    # The tags and class names would depend on the actual structure of the page
    tables = soup.find_all('table')

    if tables:
        for table in tables:
            # Get all rows from the table
            rows = table.find_all('tr')

            # Loop through the rows to extract the data
            for row in rows:
                cells = row.find_all('td')
                if len(cells) > 1:
                    # Extract the relevant information, e.g., location and tax rate
                    location = cells[0].get_text(strip=True)
                    rate = cells[1].get_text(strip=True)
                    county = cells[2].get_text(strip=True)
                    print(f'Location: {location}, County: {county}, Rate: {rate}')
    else:
        print("No tables found on the page.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
