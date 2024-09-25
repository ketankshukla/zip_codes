import pgeocode
from decimal import Decimal

# Constants
TAX_RATES = {
    'CA_sales_tax': Decimal('0.0725'),
    'SD_county': Decimal('0.0005'),
    'el_cajon_extra': Decimal('0.005')
}

def get_location_info(zip_code):
    nomi = pgeocode.Nominatim('US')
    result = nomi.query_postal_code(zip_code)

    if not result.empty:
        return {
            'city': result['place_name'],
            'county': result['county_name'],
            'state': result['state_name']
        }
    else:
        return None

def calculate_taxes(monthly_payment, city):
    state_tax = monthly_payment * TAX_RATES['CA_sales_tax']
    county_tax = monthly_payment * TAX_RATES['SD_county']

    taxes = {
        'state_tax': state_tax,
        'county_tax': county_tax
    }

    if city == 'El Cajon':
        taxes['city_tax'] = monthly_payment * TAX_RATES['el_cajon_extra']

    return taxes

def format_output(zip_code, monthly_payment, location_info, taxes):
    output = [
        f"Gargaged location: {zip_code}",
        f"Payment amount: ${monthly_payment:.2f}",
        f"City: {location_info['city']}",
        f"County: {location_info['county']}",
        f"State: {location_info['state']}",
        f"Remittance amount to county: ${taxes['county_tax']:.2f}",
        f"Remittance amount to state: ${taxes['state_tax']:.2f}"
    ]

    if 'city_tax' in taxes:
        output.insert(-1, f"Remittance amount to El Cajon: ${taxes['city_tax']:.2f}")

    return '\n'.join(output)

def main():
    while True:
        zip_code = input("Enter a ZIP code (or 'x' to exit): ").strip().lower()

        if zip_code == 'x':
            print("Exiting the program. Goodbye!")
            break

        location_info = get_location_info(zip_code)

        if location_info:
            if location_info['state'] != 'California':
                print(f"Sorry, this program only handles California zip codes. You entered a zip code for {location_info['state']}.")
                continue

            try:
                monthly_payment = Decimal(input("Enter monthly payment amount: $"))
            except ValueError:
                print("Invalid input for payment amount. Please enter a numeric value.")
                continue

            taxes = calculate_taxes(monthly_payment, location_info['city'])
            print("\n" + format_output(zip_code, monthly_payment, location_info, taxes) + "\n")
        else:
            print(f"No information found for ZIP code {zip_code}\n")

if __name__ == "__main__":
    main()