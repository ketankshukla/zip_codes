import requests
from bs4 import BeautifulSoup
import pgeocode
from decimal import Decimal

# Function to scrape tax rates data from the CDTFA page
def scrape_tax_rates():
    url = 'https://www.cdtfa.ca.gov/taxes-and-fees/rates.aspx'
    response = requests.get(url)

    tax_data = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table')
        if tables:
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) > 1:
                        location = cells[0].get_text(strip=True).upper()
                        county = cells[2].get_text(strip=True).upper()
                        rate = cells[1].get_text(strip=True)
                        tax_data.append((location, county, rate))
    return tax_data

# Function to get city, county, state using pgeocode
def get_location_from_zip(zip_code):
    nomi = pgeocode.Nominatim('US')
    location_info = nomi.query_postal_code(zip_code)

    if isinstance(location_info.place_name, float) or isinstance(location_info.county_name, float):
        return None

    return {
        'city': location_info.place_name.split(',')[0].upper() if location_info.place_name else None,
        'county': location_info.county_name.upper() if location_info.county_name else None,
        'state': location_info.state_name.upper() if location_info.state_name else None
    }

# Function to match city and county with tax rates
def get_tax_rate(city, county, tax_data):
    for entry in tax_data:
        location, county_name, rate = entry
        if city == location and county == county_name:
            return rate
    return None

# Function to calculate taxes dynamically from the scraped tax rate
def calculate_taxes(monthly_payment, tax_rate):
    # Convert tax rate from percentage string to Decimal
    tax_rate_decimal = Decimal(tax_rate.strip('%')) / 100
    total_tax = monthly_payment * tax_rate_decimal
    return total_tax

# Function to calculate remittance amounts (state, county, and possibly city)
def calculate_remittance(total_tax):
    state_remittance = total_tax * Decimal('0.0725')  # Assumed standard CA state sales tax
    county_remittance = total_tax - state_remittance  # Rest goes to the county (simplified assumption)

    return state_remittance, county_remittance

# Function to format the output, including remittance details
def format_output(zip_code, monthly_payment, location_info, total_tax, tax_rate, state_remittance, county_remittance):
    output = [
        f"Location ZIP: {zip_code}",
        f"Payment amount: ${monthly_payment:.2f}",
        f"City: {location_info['city']}",
        f"County: {location_info['county']}",
        f"State: {location_info['state']}",
        f"Tax rate: {tax_rate}",
        f"Total tax to be paid: ${total_tax:.2f}",
        f"Remittance amount to state: ${state_remittance:.2f}",
        f"Remittance amount to county: ${county_remittance:.2f}"
    ]
    return '\n'.join(output)

# Function to validate the ZIP code input
def validate_zip_code(zip_code):
    return zip_code.isdigit() and len(zip_code) == 5

# Function to validate the monthly payment input
def validate_monthly_payment(payment):
    try:
        payment = Decimal(payment)
        return payment > 0
    except ValueError:
        return False

# Main function
def main():
    # Step 1: Scrape tax rates from the website
    print("Scraping tax rates from CDTFA website...")
    tax_data = scrape_tax_rates()

    if not tax_data:
        print("No tax data was extracted. Exiting...")
        return

    while True:
        # Step 2: Get ZIP code from user input
        user_zip = input("Enter ZIP code (or press 'x' to exit): ")

        if user_zip.lower() == 'x':
            print("Exiting the program.")
            break

        # Validate the ZIP code input
        if not validate_zip_code(user_zip):
            print("Invalid input. Please enter a 5-digit ZIP code (numeric only).")
            continue

        # Step 3: Get location information (city, county, state) using pgeocode
        location_info = get_location_from_zip(user_zip)
        if not location_info:
            print(f"No information found for ZIP code {user_zip}.")
            continue

        if location_info['state'] != 'CALIFORNIA':
            print(f"Sorry, this program only handles California ZIP codes.")
            continue

        print(f"City: {location_info['city']}, County: {location_info['county']}, State: {location_info['state']}")

        # Step 4: Match city and county with tax rates
        tax_rate = get_tax_rate(location_info['city'], location_info['county'], tax_data)
        if not tax_rate:
            print(f"No tax rate found for {location_info['city']}, {location_info['county']}.")
            continue

        # Step 5: Get monthly payment from user input
        while True:
            user_payment = input("Enter your monthly payment: ")
            if validate_monthly_payment(user_payment):
                user_payment = Decimal(user_payment)
                break
            else:
                print("Invalid input. Please enter a valid numeric payment amount.")

        # Step 6: Calculate total tax based on scraped tax rate and display results
        total_tax = calculate_taxes(user_payment, tax_rate)

        # Step 7: Calculate remittance amounts
        state_remittance, county_remittance = calculate_remittance(total_tax)

        # Step 8: Display the formatted output
        print("\n" + format_output(user_zip, user_payment, location_info, total_tax, tax_rate, state_remittance, county_remittance) + "\n")

if __name__ == "__main__":
    main()
