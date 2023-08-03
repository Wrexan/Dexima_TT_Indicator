from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd

from utils.indicator import CustomTradeIndicator

sources = {
    'file (long wait)': {
        'link': 'data//ohlcv.csv'
    },
    'web': {
        'link': 'https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv'
    }
}
background_color = '#050505'

app = Dash(__name__)

app.layout = html.Div([
    html.H4('Pythonic TradingView Indicators'),
    html.Div(className='six columns', children=[
        dcc.Checklist(
                id='toggle-activate-indicators',
                options=[{'label': 'Indicator', 'value': 'indicator'}],
                value=[False]
            ),
        dcc.RadioItems(
                id='select-source',
                value='web',
                options=[*sources.keys()],
                inline=True,
            ),
    ]),
    html.Div(className='six columns', children=[
        html.Span(children='Input candle range:'),
        dcc.Input(
            id='candle_range',
            type='number',
            placeholder='Candle Range',
            value=15,
            min=5,
            max=100,
            step=1,
        ),
        dcc.Checklist(
            id='toggle-activate-extras',
            options=[
                {'label': 'Show PDH/PDL', 'value': 'showPD'},
                {'label': 'Show Bearish BOS Lines', 'value': 'showBearishBOS'},
                {'label': 'Show Bullish BOS Lines', 'value': 'showBullishBOS'},
            ],
            value=['showPD', 'showBearishBOS', 'showBullishBOS'],
            inline=True,
        ),
    ]),
    dcc.Graph(
        id="graph",
        # config={'displayModeBar': True, 'scrollZoom': True}
    ),
])


@app.callback(
    Output("graph", "figure"),
    Input("toggle-activate-indicators", "value"),
    Input("select-source", "value"),
    Input("candle_range", "value"),
    Input("toggle-activate-extras", "value"),
)
def display_candlestick(indicators, source, candle_range, extras):
    df = pd.read_csv(sources[source]['link'])
    df.columns = df.columns.str.lower()
    df.columns = [column.split('.')[-1] for column in df.columns]
    fig = go.Figure(
        go.Candlestick(
            x=df['date'],
            open=df[f'open'],
            high=df[f'high'],
            low=df[f'low'],
            close=df[f'close'],
        )
    )

    fig.update_layout(
        # dragmode='pan',
        plot_bgcolor=background_color,
        paper_bgcolor=background_color,
        height=800
    )
    fig.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='#252525'
    )
    fig.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='#252525',
        side='right'
    )
    indicator = CustomTradeIndicator(fig, df)
    if 'indicator' in indicators:
        indicator.draw_indicator(candle_range, extras)

    return fig


app.run_server(debug=True)
