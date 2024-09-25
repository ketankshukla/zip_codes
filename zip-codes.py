from pyzipcode import ZipCodeDatabase

zips = ZipCodeDatabase()

zip_code = input('enter zip code: ')
monthly_payment = int(input('monthly payment amount: '))
zip_info = zips[zip_code]

CA_sales_tax = .0725
SD_county = .0005
el_cajon_extra = .005

state_tax = monthly_payment * CA_sales_tax
san_diego_tax = monthly_payment * SD_county
el_cajon = monthly_payment * el_cajon_extra


if zip_info.city == 'San Diego':
    print(f'\nGargaged location: {zip_code}')
    print(f'Payment amount: ${monthly_payment}')
    print(f'County: {zip_info.city} County')
    print(f'Remittance amount to county: ${san_diego_tax}')
    print(f'City: {zip_info.city}')
    print(f'State: {zip_info.state}\nRemittance amount to state: ${state_tax}')
elif zip_info.city == 'El Cajon':
    print(f'Gargaged location: {zip_code}\n')
    print(f'Payment amount: ${monthly_payment}')
    print(f'County: {zip_info.city.replace('El Cajon', 'San Diego')} County')
    print(f'Remittance amount to county: ${san_diego_tax}')
    print(f'Remittance amount to El Cajon: ${el_cajon}')
    print(f'City: {zip_info.city}')
    print(f'State: {zip_info.state}\nRemittance amount to state: {state_tax}')
else:
    print('Invalid entry, input a valid zipcode.')