from Analysis import AnalysisResult
import json
import pandas as pd
import dash
from dash import dcc, html, dash_table, Input, Output

# Fetch Data
_, attendance_data , _ = AnalysisResult()

# Convert JSON Data to DataFrame
def get_employee_attendance(employee_id):
    if employee_id not in attendance_data:
        return pd.DataFrame()  # Return empty DataFrame if employee not found
    
    records = []
    for date, record in attendance_data[employee_id].items():
        record_data = json.loads(record)  # Convert JSON string to dictionary
        records.append({
            "Date": date,
            "In Time": record_data.get("InTime"),
            "Out Time": record_data.get("OutTime") if record_data.get("OutTime") else "N/A",
            "Number of Entries": record_data.get("NumberOfTime")
        })
    
    return pd.DataFrame(records)

# Initialize Dash App with Bootstrap
app = dash.Dash(__name__, external_stylesheets=["https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"])

# Define App Layout
app.layout = html.Div([
    html.H1("🔍 Employee Attendance Search", className="text-center mt-4 mb-3"),
    
    # Employee ID Search Bar
    html.Div([
        html.Label("Enter Employee ID:", className="fw-bold"),
        dcc.Input(id="employee-id", type="text", placeholder="Enter Employee ID...", className="form-control mb-3"),
        html.Button("Search", id="search-btn", n_clicks=0, className="btn btn-primary")
    ], className="container w-50"),
    
    # Display Employee Attendance
    html.Div(id="attendance-details", className="container mt-4")
])

# Callback to fetch and display attendance records
@app.callback(
    Output("attendance-details", "children"),
    Input("search-btn", "n_clicks"),
    Input("employee-id", "value")
)
def display_attendance(n_clicks, employee_id):
    if not employee_id:
        return html.Div("🔎 Enter an Employee ID and click Search.", className="alert alert-info text-center")
    
    df = get_employee_attendance(employee_id.strip())
    
    if df.empty:
        return html.Div(f"❌ No records found for Employee ID: {employee_id}", className="alert alert-warning text-center")

    # Create a styled table with employee attendance
    return html.Div([
        html.H3(f"📅 Attendance for Employee {employee_id}", className="text-center mt-4"),
        dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[
                {"name": "Date", "id": "Date"},
                {"name": "In Time", "id": "In Time"},
                {"name": "Out Time", "id": "Out Time"},
                {"name": "Number of Entries", "id": "Number of Entries"}
            ],
            style_table={"overflowX": "auto"},
            style_header={"backgroundColor": "#007bff", "color": "white", "fontWeight": "bold"},
            style_cell={"textAlign": "center", "padding": "10px"},
            style_data={"border": "1px solid #ddd"},
            page_size=10
        )
    ], className="container mt-3")

# Run the Dash App
if __name__ == "__main__":
    app.run_server(debug=True)
