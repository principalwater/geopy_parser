import pandas as pd
from geopy.geocoders import Nominatim
from pandas import DataFrame

# Creating the dummy data and dataframe within
city_tuple = {'regioncity': ['Moscow', 'Bryansk', 'Saint-Petersburg', 'Ryazan'],
              'regioncountry': ['Russian Federation', 'Russia', 'Russia', None]}

city_df = DataFrame(data=city_tuple)
print(city_df)  # Checking the initial source dataframe

geolocator = Nominatim(timeout=3, user_agent="region-city-mapper")

if city_df['regioncity'] is not None:
    # Parsing full location regarding the city and country names
    city_df['location'] = city_df.apply(
        lambda row: geolocator.geocode(
            f"{row['regioncity']}, {row['regioncountry']}" if pd.notna(row['regioncountry']) else row['regioncity'],
            language='ru', addressdetails=True), axis=1)


    # Parsing the exact city, country and region in exact locale
    def split_region_city(x):
        if x is not None and 'name' in x.raw.keys():
            regioncity_row = list(x.raw['name'].split(" "))
            return regioncity_row[len(regioncity_row) - 1]
        return None


    city_df['regioncity_ru'] = city_df['location'].apply(split_region_city)
    city_df['regioncountry_ru'] = city_df['location'].apply(
        lambda x: x.raw['address']['country'] if x and 'address' in x.raw and 'country' in x.raw['address'] else None
    )


    def extract_region_state(x):
        if x is not None and 'address' in x.raw:
            address = x.raw['address']
            if 'region' in address:
                return address['region']
            elif 'state' in address:
                return address['state']
        return None


    city_df['region_ru'] = city_df['location'].apply(extract_region_state)

    # Fill 'None' values with city names
    city_df['region_ru'] = city_df['region_ru'].fillna(city_df['regioncity_ru'])

# Enriching the initial dataframe with parsed attribute values
# and filling the other 'None' values as 'Undefined'
columns_to_merge = ['regioncity_ru', 'regioncountry_ru', 'region_ru']
city_df[columns_to_merge] = city_df[columns_to_merge].fillna('Undefined')

# Checking the result
print(city_df.to_string())