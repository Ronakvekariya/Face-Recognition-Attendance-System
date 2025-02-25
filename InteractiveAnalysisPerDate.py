from Analysis import AnalysisResult
import json
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table, Input, Output

# Fetch Data
_, _, data = AnalysisResult()

# Validate if data is a dictionary
if not isinstance(data, dict):
    raise ValueError("Error: Data extracted from AnalysisResult() is not in the expected dictionary format.")

# Convert JSON data to DataFrame
attendance_records = []
for date, records in data.items():
    for emp_id, record in records.items():
        if isinstance(record, str):
            record_data = json.loads(record)  # Convert JSON string to dict
            attendance_records.append({
                "Date": date,
                "EmployeeId": emp_id,
                "InTime": record_data.get("InTime"),
                "OutTime": record_data.get("OutTime"),
                "NumberOfTime": record_data.get("NumberOfTime")
            })

df = pd.DataFrame(attendance_records)
df["Date"] = pd.to_datetime(df["Date"])  # Convert to datetime
df["Month"] = df["Date"].dt.strftime("%Y-%m")  # Extract month (YYYY-MM format)

# Group by month for dropdown
monthly_attendance = df.groupby("Month").size().reset_index(name="Employees Present")

# Initialize Dash App with Bootstrap
app = dash.Dash(__name__, external_stylesheets=["https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"])

app.layout = html.Div([
    html.H1("📊 Employee Attendance Dashboard", className="text-center mt-4 mb-3"),
    
    # Month selector
    html.Div([
        html.Label("Select a Month:", className="fw-bold"),
        dcc.Dropdown(
            id="month-selector",
            options=[{"label": month, "value": month} for month in monthly_attendance["Month"]],
            placeholder="📅 Choose a Month",
            className="mb-4"
        )
    ], className="container w-50"),

    # Daily attendance chart
    html.Div([
        dcc.Graph(id="daily-attendance-bar-chart")
    ], className="container"),

    # Employee details
    html.Div(id="employee-day-info", className="container mt-4")
])

# Callback to update daily attendance chart based on selected month
@app.callback(
    Output("daily-attendance-bar-chart", "figure"),
    Input("month-selector", "value")
)
def update_daily_chart(selected_month):
    if not selected_month:
        return px.bar(title="Select a month to see daily data.")
    
    daily_data = df[df["Month"] == selected_month].groupby("Date").size().reset_index(name="Employees Present")

    # Styled bar chart
    fig = px.bar(
        daily_data, x="Date", y="Employees Present",
        title=f"📅 Daily Attendance in {selected_month}",
        color="Employees Present",
        color_continuous_scale="blues",
        labels={"Employees Present": "Number of Employees"},
        hover_data={"Date": "|%Y-%m-%d"}
    )
    
    fig.update_layout(
        plot_bgcolor="white",
        xaxis=dict(title="Date", tickangle=-45),
        yaxis=dict(title="Employees Present"),
        margin=dict(l=40, r=40, t=50, b=40),
        hovermode="x"
    )
    
    return fig

# Callback to show employee details for selected day
@app.callback(
    Output("employee-day-info", "children"),
    Input("daily-attendance-bar-chart", "clickData")
)
def display_daily_employee_details(clickData):
    if clickData is None:
        return html.Div("🔍 Click on a bar to see employee details.", className="alert alert-info text-center")

    try:
        selected_date = pd.to_datetime(clickData["points"][0]["x"]).strftime("%Y-%m-%d")
    except Exception as e:
        return html.Div(f"⚠️ Error processing date: {str(e)}", className="alert alert-danger")

    daily_data = df[df["Date"] == selected_date]
    
    if daily_data.empty:
        return html.Div("❌ No data available for this date.", className="alert alert-warning text-center")

    # Styled table for employee details
    return html.Div([
        html.H3(f"👥 Employee Details for {selected_date}", className="text-center mt-4"),
        dash_table.DataTable(
            data=daily_data.to_dict("records"),
            columns=[
                {"name": "Employee ID", "id": "EmployeeId"},
                {"name": "In Time", "id": "InTime"},
                {"name": "Out Time", "id": "OutTime"},
                {"name": "Number of Times", "id": "NumberOfTime"}
            ],
            style_table={"overflowX": "auto"},
            style_header={"backgroundColor": "#007bff", "color": "white", "fontWeight": "bold"},
            style_cell={"textAlign": "center", "padding": "10px"},
            style_data={"border": "1px solid #ddd"},
            page_size=10
        )
    ], className="container mt-3")

if __name__ == "__main__":
    app.run_server(debug=True)
