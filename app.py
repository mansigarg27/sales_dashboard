import pandas as pd
import sqlite3
from dash import Dash, html, dcc, Input, Output
import plotly.express as px

# Load data
sales = pd.read_csv("sales.csv")
sales["Date"] = pd.to_datetime(sales["Date"])

emp = pd.read_csv("employees.csv")

# Create Database
conn = sqlite3.connect("company.db")
emp.to_sql("employees", conn, if_exists="replace", index=False)
employees = pd.read_sql("SELECT * FROM employees", conn)
conn.close()

# Create App
app = Dash(__name__)
app.title = "Sales Dashboard"

# Dropdown Options
region_list = ["All"] + sorted(sales["Region"].unique())
category_list = ["All"] + sorted(sales["Category"].unique())

# ---------- Card Style ----------

card_style = {
    "background":"white",
    "padding":"10px",
    "borderRadius":"8px",
    "boxShadow":"0 2px 5px lightgray",
    "width":"23%",
    "textAlign":"center"
}

app.layout = html.Div([

    html.H2(
        "Interactive Sales Dashboard",
        style={"textAlign": "center", "color": "#1565C0"}
    ),

    html.Div([

        dcc.Dropdown(
            id="region",
            options=[{"label": i, "value": i} for i in region_list],
            value="All",
            style={"width": "48%", "display": "inline-block"}
        ),

        dcc.Dropdown(
            id="category",
            options=[{"label": i, "value": i} for i in category_list],
            value="All",
            style={
                "width": "48%",
                "display": "inline-block",
                "float": "right"
            }
        )

    ]),

    html.Br(),

    html.Div(id="cards"),

    html.Div([

        dcc.Graph(id="line", style={"width":"49%"}),

        dcc.Graph(id="profit", style={"width":"49%"})

    ], style={"display":"flex","gap":"10px"}),

    html.Div([

        dcc.Graph(id="bar", style={"width":"49%"}),

        dcc.Graph(id="pie", style={"width":"49%"})

    ], style={"display":"flex","gap":"10px"})

], style={
    "padding":"10px",
    "backgroundColor":"#F5F5F5",
    "fontFamily":"Arial"
})

@app.callback(

[
    Output("cards","children"),
    Output("line","figure"),
    Output("profit","figure"),
    Output("bar","figure"),
    Output("pie","figure")
],

[
    Input("region","value"),
    Input("category","value")
]

)

def update(region, category):

    df = sales.copy()

    if region != "All":
        df = df[df["Region"] == region]

    if category != "All":
        df = df[df["Category"] == category]

    # ---------- KPI Cards ----------
    cards = html.Div([

        html.Div([
            html.H4("Total Sales"),
            html.H3(f"₹ {df['Sales'].sum():,}")
        ], style=card_style),

        html.Div([
            html.H4("Total Profit"),
            html.H3(f"₹ {df['Profit'].sum():,}")
        ], style=card_style),

        html.Div([
            html.H4("Orders"),
            html.H3(len(df))
        ], style=card_style),

        html.Div([
            html.H4("Employees"),
            html.H3(len(employees))
        ], style=card_style)

    ], style={"display":"flex","justifyContent":"space-between","margin":"15px 0"})


    # ---------- Charts ----------

    line = px.line(
        df,
        x="Date",
        y="Sales",
        markers=True,
        title="Sales Trend"
    )

    profit = px.bar(
        df.groupby("Product",as_index=False)["Profit"].sum(),
        x="Product",
        y="Profit",
        color="Product",
        title="Profit by Product"
    )

    bar = px.bar(
        df.groupby("Region",as_index=False)["Sales"].sum(),
        x="Region",
        y="Sales",
        color="Region",
        title="Sales by Region"
    )

    pie = px.pie(
        df,
        names="Category",
        values="Sales",
        hole=0.4,
        title="Category-wise Sales"
    )

    return cards, line, profit, bar, pie


# ---------- Card Style ----------

card_style = {
    "background":"white",
    "padding":"10px",
    "borderRadius":"8px",
    "boxShadow":"0 2px 5px lightgray",
    "width":"23%",
    "textAlign":"center"
}


# ---------- Run App ----------

if __name__ == "__main__":
    app.run(debug=True)