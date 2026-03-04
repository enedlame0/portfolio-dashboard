from pathlib import Path
import sys

import plotly.express as px
import pandas as pd
from dash import Dash, dcc, html

# Allow running as `python app/app_dash.py` by adding project root to sys.path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.portfolio.ingest import load_holdings
from src.portfolio.pricing import fetch_prices_yfinance, fetch_ticker_regions_yfinance
from src.portfolio.analytics import portfolio_value, daily_returns, weights_latest
from src.portfolio.risk import max_drawdown, historical_var, historical_cvar

COLOR_BG = "#f4f2ec"
COLOR_SURFACE = "#ffffff"
COLOR_TEXT = "#14171f"
COLOR_MUTED = "#596579"
COLOR_PRIMARY = "#0f6b5f"
COLOR_SECONDARY = "#1860a7"
COLOR_ACCENT = "#b66a21"
COLOR_BORDER = "#d8ddd7"


def fmt_ccy(value: float) -> str:
    return f"${value:,.0f}"


def metric_card(title: str, value: str, hint: str) -> html.Div:
    return html.Div(
        style={
            "background": COLOR_SURFACE,
            "border": f"1px solid {COLOR_BORDER}",
            "borderRadius": "16px",
            "padding": "18px 20px",
            "boxShadow": "0 12px 28px rgba(16, 24, 40, 0.06)",
            "display": "flex",
            "flexDirection": "column",
            "gap": "6px",
            "minWidth": "220px",
            "flex": "1",
        },
        children=[
            html.Div(title, style={"fontSize": "0.8rem", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": COLOR_MUTED}),
            html.Div(value, style={"fontSize": "1.8rem", "fontWeight": "700", "lineHeight": "1.1", "color": COLOR_TEXT}),
            html.Div(hint, style={"fontSize": "0.85rem", "color": COLOR_MUTED}),
        ],
    )


def style_figure(fig):
    fig.update_layout(
        font={"family": "Space Grotesk, Segoe UI, sans-serif", "color": COLOR_TEXT},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#fafaf7",
        margin={"l": 50, "r": 20, "t": 65, "b": 45},
        title={"x": 0.02, "xanchor": "left", "font": {"size": 18}},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#e6e9e4", zeroline=False)
    return fig


holdings = load_holdings("data/holdings.csv")
tickers = sorted(holdings["ticker"].unique())
price_start = holdings["transaction_date"].min().strftime("%Y-%m-%d")
price_end = (pd.Timestamp.today().normalize() + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
prices = fetch_prices_yfinance(tickers, start=price_start, end=price_end)

pv = portfolio_value(holdings, prices)
rets = daily_returns(pv["portfolio_value"])

w = weights_latest(pv.filter(like="value_"))
w_df = w.reset_index()
w_df.columns = ["ticker", "weight"]
w_df["ticker"] = w_df["ticker"].str.replace("^value_", "", regex=True)

region_map = fetch_ticker_regions_yfinance(w_df["ticker"].tolist())
w_df["region"] = w_df["ticker"].map(region_map).fillna("Other")
geo_df = (
    w_df.groupby("region", as_index=False)["weight"]
    .sum()
    .sort_values("weight", ascending=False)
)

latest_value = float(pv["portfolio_value"].iloc[-1])
latest_external = float(pv["external_funding_cum"].iloc[-1])
pnl = latest_value - latest_external
roi_text = "N/A" if latest_external <= 0 else f"{(pnl / latest_external):.2%}"

fig_value = px.area(
    pv.reset_index(),
    x="Date",
    y="portfolio_value",
    title="Portfolio Value Trend",
)
fig_value.update_traces(line={"width": 2.5, "color": COLOR_PRIMARY}, fillcolor="rgba(15, 107, 95, 0.16)")
fig_value.update_yaxes(tickprefix="$", separatethousands=True, title="Portfolio Value")
fig_value.update_xaxes(title=None)
fig_value = style_figure(fig_value)

fig_dist = px.box(
    x=rets,
    points="outliers",
    title="Daily Returns Distribution",
)
fig_dist.update_traces(
    marker={"color": COLOR_SECONDARY},
    line={"color": COLOR_SECONDARY},
    fillcolor="rgba(24, 96, 167, 0.12)",
)
fig_dist.update_layout(showlegend=False)
fig_dist.update_xaxes(tickformat=".1%", title="Daily return")
fig_dist.update_yaxes(showgrid=False, showticklabels=False, title=None)
fig_dist = style_figure(fig_dist)

fig_weights_bar = px.bar(
    w_df.sort_values("weight", ascending=False),
    x="ticker",
    y="weight",
    title="Current Asset Weights",
)
fig_weights_bar.update_traces(marker={"color": COLOR_ACCENT}, texttemplate="%{y:.1%}", textposition="outside")
fig_weights_bar.update_yaxes(tickformat=".0%", title=None)
fig_weights_bar.update_xaxes(title=None)
fig_weights_bar = style_figure(fig_weights_bar)

fig_weights_pie = px.pie(
    w_df,
    names="ticker",
    values="weight",
    title="Portfolio Composition",
    hole=0.58,
)
fig_weights_pie.update_traces(textposition="inside", texttemplate="%{label}<br>%{percent}", sort=False)
fig_weights_pie = style_figure(fig_weights_pie)
fig_weights_pie.update_layout(
    legend={"orientation": "v", "yanchor": "middle", "y": 0.5, "xanchor": "left", "x": 1.02},
    margin={"l": 40, "r": 130, "t": 70, "b": 40},
)

fig_geo_pie = px.pie(
    geo_df,
    names="region",
    values="weight",
    title="Geographical Exposure",
    hole=0.58,
    color="region",
    color_discrete_map={
        "US": COLOR_PRIMARY,
        "Europe": COLOR_SECONDARY,
        "Asia": COLOR_ACCENT,
        "Cash": "#6f7b8f",
        "Other": "#9aa5b3",
    },
)
fig_geo_pie.update_traces(textposition="inside", texttemplate="%{label}<br>%{percent}", sort=False)
fig_geo_pie = style_figure(fig_geo_pie)
fig_geo_pie.update_layout(
    showlegend=False,
    margin={"l": 40, "r": 30, "t": 70, "b": 40},
)

app = Dash(
    __name__,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap"
    ],
)
app.layout = html.Div(
    style={
        "minHeight": "100vh",
        "background": "linear-gradient(145deg, #f8f6ef 0%, #eef3ef 50%, #f2f0ea 100%)",
        "padding": "28px 18px 36px",
        "fontFamily": "Space Grotesk, Segoe UI, sans-serif",
        "color": COLOR_TEXT,
    },
    children=[
        html.Div(
            style={
                "maxWidth": "1280px",
                "margin": "0 auto",
                "display": "flex",
                "flexDirection": "column",
                "gap": "20px",
            },
            children=[
                html.Div(
                    style={
                        "background": COLOR_SURFACE,
                        "border": f"1px solid {COLOR_BORDER}",
                        "borderRadius": "22px",
                        "padding": "26px 28px",
                        "boxShadow": "0 18px 45px rgba(20, 23, 31, 0.09)",
                    },
                    children=[
                        html.Div(
                            "Investor Snapshot",
                            style={
                                "fontSize": "0.82rem",
                                "fontWeight": "600",
                                "color": COLOR_MUTED,
                                "textTransform": "uppercase",
                                "letterSpacing": "0.13em",
                                "marginBottom": "8px",
                            },
                        ),
                        html.H1(
                            "Portfolio Performance Dashboard",
                            style={"margin": "0 0 6px 0", "fontSize": "2.05rem", "lineHeight": "1.1"},
                        ),
                        html.Div(
                            f"As of {pv.index[-1].strftime('%B %d, %Y')}",
                            style={"fontSize": "0.95rem", "color": COLOR_MUTED},
                        ),
                    ],
                ),
                html.Div(
                    style={"display": "flex", "gap": "14px", "flexWrap": "wrap"},
                    children=[
                        metric_card("Portfolio Value", fmt_ccy(latest_value), "Marked to last close"),
                        metric_card("P/L vs Contributions", fmt_ccy(pnl), f"Total invested: {fmt_ccy(latest_external)}"),
                        metric_card("Return on Invested Capital", roi_text, "Based on cumulative external funding"),
                        metric_card("Max Drawdown", f"{max_drawdown(pv['portfolio_value']):.2%}", "Peak-to-trough decline"),
                        metric_card("VaR 5%", f"{historical_var(rets, 0.05):.2%}", "One-day historical value at risk"),
                        metric_card("CVaR 5%", f"{historical_cvar(rets, 0.05):.2%}", "Average of worst 5% days"),
                    ],
                ),
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fit, minmax(360px, 1fr))",
                        "gap": "16px",
                    },
                    children=[
                        html.Div(
                            style={
                                "background": COLOR_SURFACE,
                                "border": f"1px solid {COLOR_BORDER}",
                                "borderRadius": "16px",
                                "padding": "10px",
                            },
                            children=[dcc.Graph(figure=fig_value, config={"displayModeBar": False})],
                        ),
                        html.Div(
                            style={
                                "background": COLOR_SURFACE,
                                "border": f"1px solid {COLOR_BORDER}",
                                "borderRadius": "16px",
                                "padding": "10px",
                            },
                            children=[dcc.Graph(figure=fig_dist, config={"displayModeBar": False})],
                        ),
                        html.Div(
                            style={
                                "background": COLOR_SURFACE,
                                "border": f"1px solid {COLOR_BORDER}",
                                "borderRadius": "16px",
                                "padding": "10px",
                            },
                            children=[dcc.Graph(figure=fig_weights_bar, config={"displayModeBar": False})],
                        ),
                        html.Div(
                            style={
                                "background": COLOR_SURFACE,
                                "border": f"1px solid {COLOR_BORDER}",
                                "borderRadius": "16px",
                                "padding": "10px",
                            },
                            children=[dcc.Graph(figure=fig_weights_pie, config={"displayModeBar": False})],
                        ),
                        html.Div(
                            style={
                                "background": COLOR_SURFACE,
                                "border": f"1px solid {COLOR_BORDER}",
                                "borderRadius": "16px",
                                "padding": "10px",
                            },
                            children=[dcc.Graph(figure=fig_geo_pie, config={"displayModeBar": False})],
                        ),
                    ],
                ),
            ],
        )
    ],
)

import os
import threading
import webbrowser

if __name__ == "__main__":
    url = "http://127.0.0.1:8050"
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, lambda: webbrowser.open_new(url)).start()
    app.run(debug=True)
