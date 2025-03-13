import requests
import pandas as pd
import utils

@utils.cache()
def get_indicators(countries=['all'], indicators=['SP.DYN.TFRT.IN','SP.POP.TOTL','NY.GDP.MKTP.CD','SP.DYN.LE00.IN'], years=['2020']):
  
    url = f'https://api.worldbank.org/v2/country/{';'.join(countries)}/indicator/{";".join(indicators)}?source=2&format=json&per_page=10000&date={";".join(years)}'
    print(url)
    response = requests.get(url).json()
    print(response)

    indicator_names = {entry["indicator"]["id"]: entry["indicator"]["value"] for entry in response[1]}

    data = pd.DataFrame([
        {
            'iso3code': entry['countryiso3code'],
            'iso2code': entry['country']['id'],
            'country': entry['country']['value'],
            'indicator': entry['indicator']['id'],
            'indicator_value': entry['value'],
            'date': entry['date']
        }
        for entry in response[1]                 
    ])
    # print(pd.DataFrame(response[1]))
    # print(data)
    df_grouped = data.pivot(index=["iso2code", "country", "date"], columns="indicator", values="indicator_value").reset_index().dropna(axis=0)
    # print(df_grouped)
    return df_grouped

if __name__ == '__main__':
    get_indicators(countries=['all'], indicators=['SP.DYN.TFRT.IN','SP.POP.TOTL','NY.GDP.MKTP.CD','SP.DYN.LE00.IN'], years=['2020'])