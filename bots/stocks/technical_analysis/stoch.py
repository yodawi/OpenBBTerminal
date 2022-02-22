from datetime import datetime, timedelta

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots import helpers
from gamestonk_terminal.common.technical_analysis import momentum_model


def stoch_command(ticker="", fast_k="14", slow_d="3", slow_k="3", start="", end=""):
    """Displays chart with stochastic relative strength average [Yahoo Finance]"""

    # Debug
    if cfg.DEBUG:
        logger.debug(
            "ta-stoch %s %s %s %s %s %s",
            ticker,
            fast_k,
            slow_k,
            slow_d,
            start,
            end,
        )

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    if start == "":
        start = datetime.now() - timedelta(days=365)
    else:
        start = datetime.strptime(start, cfg.DATE_FORMAT)

    if end == "":
        end = datetime.now()
    else:
        end = datetime.strptime(end, cfg.DATE_FORMAT)

    if not fast_k.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    fast_k = int(fast_k)
    if not slow_k.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    slow_k = int(slow_k)
    if not slow_d.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    slow_d = int(slow_d)

    ticker = ticker.upper()
    df_stock = helpers.load(ticker, start)
    if df_stock.empty:
        raise Exception("Stock ticker is invalid")

    # Retrieve Data
    df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

    df_ta = momentum_model.stoch(
        df_stock["High"],
        df_stock["Low"],
        df_stock["Adj Close"],
        fast_k,
        slow_d,
        slow_k,
    )

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.07,
        row_width=[0.5, 0.7],
    )
    fig.add_trace(
        go.Scatter(
            x=df_stock.index,
            y=df_stock["Adj Close"].values,
            line=dict(color="#fdc708", width=2),
            opacity=1,
            showlegend=False,
        ),
        row=1,
        col=1,
    )
    K = df_ta.columns[0].replace("_", " ")
    D = df_ta.columns[1].replace("_", " ")
    fig.add_trace(
        go.Scatter(
            name=f"%K {K}",
            x=df_stock.index,
            y=df_ta.iloc[:, 0].values,
            line=dict(width=1.8),
            opacity=1,
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            name=f"%D {D}",
            x=df_stock.index,
            y=df_ta.iloc[:, 1].values,
            line=dict(width=1.8, dash="dash"),
            opacity=1,
        ),
        row=2,
        col=1,
    )
    fig.add_hrect(
        y0=80,
        y1=100,
        fillcolor="red",
        opacity=0.2,
        layer="below",
        line_width=0,
        row=2,
        col=1,
    )
    fig.add_hrect(
        y0=0,
        y1=20,
        fillcolor="green",
        opacity=0.2,
        layer="below",
        line_width=0,
        row=2,
        col=1,
    )
    fig.add_hline(
        y=80,
        fillcolor="green",
        opacity=1,
        layer="below",
        line_width=3,
        line=dict(color="red", dash="dash"),
        row=2,
        col=1,
    )
    fig.add_hline(
        y=20,
        fillcolor="green",
        opacity=1,
        layer="below",
        line_width=3,
        line=dict(color="green", dash="dash"),
        row=2,
        col=1,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=20),
        template=cfg.PLT_TA_STYLE_TEMPLATE,
        colorway=cfg.PLT_TA_COLORWAY,
        title=f"Stochastic Relative Strength Index (STOCH RSI) on {ticker}",
        title_x=0.5,
        yaxis_title="Stock Price ($)",
        yaxis=dict(
            fixedrange=False,
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
            type="date",
        ),
        dragmode="pan",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )
    config = dict({"scrollZoom": True})
    imagefile = "ta_stoch.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        html_ran = helpers.uuid_get()
        fig.write_html(f"in/stoch_{html_ran}.html", config=config)
        plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/stoch_{html_ran}.html)"

    fig.update_layout(
        width=800,
        height=500,
    )

    imagefile = helpers.image_border(imagefile, fig=fig)

    return {
        "title": f"Stocks: Stochastic-Relative-Strength-Index {ticker}",
        "description": plt_link,
        "imagefile": imagefile,
    }