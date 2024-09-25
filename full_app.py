import requests
from bs4 import BeautifulSoup
import pgeocode
import math  # Needed to check for NaN values

# Function to scrape tax rates data from the CDTFA page
def scrape_tax_rates():
    # URL of the CDTFA tax rates page
    url = 'https://www.cdtfa.ca.gov/taxes-and-fees/rates.aspx'

    # Send a request to the website
    response = requests.get(url)

    tax_data = []

    if response.status_code == 200:
        # Parse the content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table(s) containing the tax rates
        tables = soup.find_all('table')

        if tables:
            for table in tables:
                # Get all rows from the table
                rows = table.find_all('tr')

                # Loop through the rows to extract the data
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) > 1:
                        # Extract the relevant information: location (city), county, and tax rate
                        location = cells[0].get_text(strip=True).upper()
                        county = cells[2].get_text(strip=True).upper()
                        rate = cells[1].get_text(strip=True)
                        tax_data.append((location, county, rate))
        else:
            print("No tables found on the page.")
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

    return tax_data

# Function to get city and county using pgeocode
def get_location_from_zip(zip_code):
    nomi = pgeocode.Nominatim('us')
    location_info = nomi.query_postal_code(zip_code)

    # Handle NaN values (which can appear when pgeocode doesn't find a location)
    if isinstance(location_info.place_name, float) and math.isnan(location_info.place_name):
        city = None
    else:
        city = location_info.place_name.split(',')[0].upper() if location_info.place_name else None

    if isinstance(location_info.county_name, float) and math.isnan(location_info.county_name):
        county = None
    else:
        county = location_info.county_name.upper() if location_info.county_name else None

    return city, county

# Function to match city and county with tax rates
def get_tax_rate(city, county, tax_data):
    for entry in tax_data:
        location, county_name, rate = entry
        if city == location and county == county_name:
            return rate
    return None

# Function to calculate the tax based on monthly payment and tax rate
def calculate_tax(monthly_payment, tax_rate):
    try:
        # Convert tax rate from percentage to decimal (e.g., 7.75% -> 0.0775)
        tax_rate_decimal = float(tax_rate.strip('%')) / 100
        tax_amount = monthly_payment * tax_rate_decimal
        return round(tax_amount, 2)  # Round the result to 2 decimal places
    except ValueError:
        return None

# Function to validate the ZIP code input
def validate_zip_code(zip_code):
    if zip_code.isdigit() and len(zip_code) == 5:
        return True
    return False

# Function to validate the monthly payment input
def validate_monthly_payment(payment):
    try:
        payment = float(payment)
        if payment > 0:
            return True
        return False
    except ValueError:
        return False

# Main function
def main():
    # Step 1: Scrape tax rates from the website
    print("Scraping tax rates from CDTFA...")
    tax_data = scrape_tax_rates()

    if not tax_data:
        print("No tax data was extracted. Exiting...")
        return

    while True:
        # Step 2: Get ZIP code from user input
        user_zip = input("Enter ZIP code (or press 'x' to exit): ")

        # Exit the loop if user presses 'x'
        if user_zip.lower() == 'x':
            print("Exiting the program.")
            break

        # Validate the ZIP code input
        if not validate_zip_code(user_zip):
            print("Invalid input. Please enter a 5-digit ZIP code (numeric only).")
            continue

        # Step 3: Use pgeocode to find city and county from ZIP code
        city, county = get_location_from_zip(user_zip)
        if not city or not county:
            print(f"Could not find city and county for ZIP code {user_zip}.")
            continue

        print(f"City: {city}, County: {county}")

        # Step 4: Match city and county with tax rates
        tax_rate = get_tax_rate(city, county, tax_data)

        if not tax_rate:
            print(f"No tax rate found for {city}, {county}.")
            continue

        # Step 5: Get monthly payment from user input
        while True:
            user_payment = input("Enter your monthly payment: ")

            # Validate the monthly payment input
            if validate_monthly_payment(user_payment):
                user_payment = float(user_payment)  # Convert the input to a float
                break
            else:
                print("Invalid input. Please enter a valid numeric payment amount.")

        # Step 6: Calculate the tax amount
        tax_amount = calculate_tax(user_payment, tax_rate)

        if tax_amount is not None:
            print(f"The tax amount on your payment of ${user_payment} for {city}, {county} is: ${tax_amount}")
        else:
            print("Error calculating the tax. Please try again.")

if __name__ == "__main__":
    main()
