import plotly.express as px
import worldbank

indicators = ['NY.GDP.PCAP.CD', 'SP.DYN.TFRT.IN', 'SP.POP.TOTL','SP.DYN.LE00.IN']
df = worldbank.get_indicators(countries=['all'], indicators=indicators, years=['2022'])
country_codes = open('data/country_codes.csv').read().strip().split(',')
df = df[df['iso2code'].isin(country_codes)]
print(country_codes)
print(df)

fig = px.scatter(
    df, 
    x=indicators[0], 
    y=indicators[1], 
    size=indicators[2], 
    color=indicators[3], 
    hover_name="country",
    log_x=True
)
fig.update_traces(mode='markers', marker=dict(sizemode='area', sizeref=1.*max(df['SP.POP.TOTL'])/(100**2), showscale=False))
fig.update_layout(
                                template='plotly_dark',
                                # plot_bgcolor='rgba(0, 0, 0, 0)',
                                # paper_bgcolor='rgba(0, 0, 0, 0)',
                            )
fig.show()