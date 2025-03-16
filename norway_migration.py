import pandas as pd

def read_norsk_demographics():
    df = pd.read_csv('data/norway_migration_background.csv', sep=';')
    for col in df.columns[1:]:
        df[col] = df[col].str.replace(' ', '').astype(int)
    df = df[df['Country'] != 'Total']
    df = df[df['Country'] != 'Norway']
    # 3rd gen;1st gen;2nd gen;foreign-born to 1 native parent;local-born to 1 foreign parent;foreign-born to 2 native parents
    df['total'] = df[['3rd gen', '1st gen', '2nd gen', 'foreign-born to 1 native parent', 'local-born to 1 foreign parent', 'foreign-born to 2 native parents']].sum(axis=1)
    df.sort_values(by='total', inplace=True, ascending=False)
    return df

def merged_data():
    df = read_norsk_demographics()
    df_region = pd.read_csv('data/countries_by_region.csv')[['name', 'region', 'sub-region']]
    df = pd.merge(df, df_region, left_on='Country', right_on='name')
    return df

# print(df)
# print(df_melted)