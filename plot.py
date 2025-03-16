import plotly.express as px
import plotly.io as pio
import pandas as pd
import math
import colorsys

import worldbank
import norway_migration

def minimal_scatter(df, html_path=None, hover_data=None, hover_name=None):
    fig = px.scatter(
        df, 
        x=df.columns[0], 
        y=df.columns[1], 
        size=df.columns[2], 
        color=df.columns[3],
        hover_name=hover_name, 
        hover_data=hover_data,
        log_x=True
    )
    fig.update_traces(
        mode='markers', 
        marker=dict(
            sizemode='area', 
            sizeref=2.*max(df[df.columns[2]])/(100**2), 
            showscale=False, 
            line=dict(width=0),
        )
    )

    fig.update_layout(
        xaxis=dict(visible=False, showgrid=False, zeroline=False),
        yaxis=dict(visible=False, showgrid=False, zeroline=False),
        showlegend=False,  # Hide legend if not needed
        margin=dict(l=0, r=0, t=0, b=0),  # Remove padding/margins
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )
    fig.update_coloraxes(showscale=False)

    fig.show()
    if html_path:
        pio.write_html(fig, html_path, full_html=True)


def world_bank_data():
    indicators = ['NY.GDP.PCAP.CD', 'SP.DYN.TFRT.IN', 'SP.POP.TOTL','SP.DYN.LE00.IN']
    df = worldbank.get_indicators(countries=['all'], indicators=indicators, years=['2022'])
    df = df[df['iso2code'].isin(open('data/country_codes.csv').read().strip().split(','))] # filter for only countries, not regions
    df = df[indicators + ['country']] # reorder columns and remove useless ones
    # make columns more readable
    df.rename(columns={"NY.GDP.PCAP.CD":'GDP Per Capita', "SP.DYN.TFRT.IN":'Fertility Rate', 'SP.POP.TOTL': 'Population', 'SP.DYN.LE00.IN': 'Life Expectancy'}, inplace=True)

    minimal_scatter(
        df, 
        html_path='outputs/worldbank.html', 
        hover_data={
            'GDP Per Capita':':.2e', # customize hover for column of y attribute
            'Fertility Rate':':.2f', # add other column, customized formatting
            'Population':':.2e',
        }, 
        hover_name='country'
    )

# world_bank_data()

df = norway_migration.merged_data()

df_melted = df.melt(
    id_vars=['sub-region', 'region', 'Country'],
    value_vars=['3rd gen', '1st gen', '2nd gen', 'foreign-born to 1 native parent', 
                'local-born to 1 foreign parent', 'foreign-born to 2 native parents'],
    var_name='Category',
    value_name='Population'
)
df_melted.sort_values(by=['Category', 'Population'], ascending=False)

# df_melted.append('sub-region', 'region', 'Country', 'Category', 'Population')

region_hues = {
    'Oceania': 150,
    'Americas': 250,
    'Africa': 200,
    'Asia': 175,
    'Europe': 225,
}

def letter_to_value(letter, scale=255):
    """Maps the first letter (A-Z) to a value between 0 and scale."""
    if isinstance(letter, str) and letter:
        return (ord(letter.upper()) - ord('A')) / 26  # Normalize A-Z to [0, scale]
    print('invalid')
    return 0  # Default if invalid

def hsv_to_hex(h, s, v):
    """Convert HSV values to HEX."""
    rgb = colorsys.hsv_to_rgb(h, s, v)  # Normalize H to [0,1]
    return f"#{int(rgb[0] * 255):02x}{int(rgb[1] * 255):02x}{int(rgb[2] * 255):02x}"

color_map = {
    row['Country']: hsv_to_hex(
        region_hues[row['region']]/360,  # Hue based on region
        letter_to_value(row['sub-region'][0])*0.5 + 0.5,  # Saturation based on subregion
        letter_to_value(row['Country'][0])*0.5 + 0.5,  # Brightness based on country
    )
    for _, row in df_melted.iterrows()
} | {
    k: hsv_to_hex(
        v/360,
        0.5,
        0.5,
    )
    for k, v in region_hues.items()
} | { # subregion is a bit hacky for now, but it's not really a performance issue
    row['sub-region']: hsv_to_hex(
        region_hues[row['region']]/360,
        letter_to_value(row['sub-region'][0])*0.5 + 0.5,
        0.5,
    )
    for _, row in df_melted.iterrows()
} | {
    'foreign-born to 2 native parents' : 'aliceblue',
    'local-born to 1 foreign parent': 'azure',
    'foreign-born to 1 native parent': 'lavender',
    '3rd gen' : 'aquamarine',
    '2nd gen' : 'aqua',
    '1st gen' : 'cornflowerblue',
}

print(df_melted)
fig = px.sunburst(
    df_melted,
    path=['region', 'sub-region', 'Country', 'Category'],
    values='Population',
    # title='Migration Statistics (Sunburst)'
    color='Country',
    # color_continuous_midpoint=5,
    color_discrete_map=color_map,
    # color_continuous_scale=px.colors.sequential.Magma
)
all_labels = fig.data[0].labels
fig.update_traces(
    insidetextorientation='radial',
    # marker_colors=['#000000']*2
    marker=dict(
        colors=[color_map.get(label, 'beige') for label in all_labels]
    )

)
fig.update_layout(margin=dict(t=40, l=0, r=0, b=0))
fig.update_layout(
    # xaxis=dict(visible=False, showgrid=False, zeroline=False),
    # yaxis=dict(visible=False, showgrid=False, zeroline=False),
    showlegend=False,  # Hide legend if not needed
    # margin=dict(l=0, r=0, t=0, b=0),  # Remove padding/margins
    template='plotly_dark',
    plot_bgcolor='rgba(0, 0, 0, 0)',
    paper_bgcolor='rgba(0, 0, 0, 0)',
)

print(fig.data[0])
fig.show()

pio.write_html(fig, 'outputs/norway_migration.html', full_html=True)