import plotly.express as px
import plotly.io as pio

import worldbank

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

world_bank_data()