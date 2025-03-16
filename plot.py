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

def styled_suburst(df, path, values, html_path=None, color_map=None):
    fig = px.sunburst(
    df,
    path=path,
    values=values
    )
    all_labels = fig.data[0].labels
    fig.update_traces(
        insidetextorientation='radial',
        marker=dict(
            colors=[color_map.get(label, 'beige') for label in all_labels]
        ),
        opacity=1
    )
    fig.update_layout(margin=dict(t=40, l=0, r=0, b=0))
    fig.update_layout(
        showlegend=False,  # Hide legend if not needed
        template='plotly_dark',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )

    # print(fig.data[0])
    fig.show()

    pio.write_html(fig, html_path, full_html=True)

def norway_migration_sunburst():
    df = norway_migration.melted()
    path = ['region', 'sub-region', 'country', 'category']
    values = 'population'

    region_hues = {
        'Oceania': 150/360,
        'Asia': 175/360,
        'Africa': 200/360,
        'Europe': 225/360,
        'Americas': 250/360,
    }

    def hsv_to_hex(h, s=0.7, v=0.7):
        """Convert HSV values to HEX."""
        rgb = colorsys.hsv_to_rgb(h, s, v)  # Normalize H to [0,1]
        return f"#{int(rgb[0] * 255):02x}{int(rgb[1] * 255):02x}{int(rgb[2] * 255):02x}"

    def hierarchy_norm(key, row):
        '''Normalize the value of an index with regards to the parent category'''
        lookup = path[:-1]
        assert key in lookup[1:]
        i = lookup.index(key)
        return df[df[lookup[i]]==row[lookup[i]]]['population'].sum()/df[df[lookup[i-1]]==row[lookup[i-1]]]['population'].sum()

    color_map =  {
        k: hsv_to_hex( # region
            v,
            0.8,
            0.8,
        )
        for k, v in region_hues.items()
    } | { # subregion; a bit hacky, computes multiple times
        row['sub-region']: hsv_to_hex(
            region_hues.get(row['region'],0), # Hue based on region
            0.74,   # gradient of saturations for each layer of sunburst
            hierarchy_norm('sub-region', row)*0.7+0.3,  # Brightness based on proportion of subregion in region
        )
        for _, row in df.iterrows()
    } | {
        row['country']: hsv_to_hex(
            region_hues.get(row['region'],0),
            0.68,
            hierarchy_norm('country', row)*0.6+0.4,
        )
        for _, row in df.iterrows()
    } | {
        k : hsv_to_hex((i*20+150)/360) # Category hues
        for i, k in  enumerate([
            '1st gen',
            '2nd gen',
            '3rd gen',
            'foreign-born to 2 native parents',
            'local-born to 1 foreign parent',
            'foreign-born to 1 native parent',
        ])
    }

    styled_suburst(
        df, 
        path, 
        values, 
        html_path='outputs/norway_migration.html', 
        color_map=color_map
    )

# world_bank_data()
norway_migration_sunburst()