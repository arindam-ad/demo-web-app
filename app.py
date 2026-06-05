from __future__ import annotations

from datetime import date
import json
import os

# Avoid Click's Windows console helper in detached/background launches.
os.environ.setdefault("CLICK_DISABLE_WINCONSOLE", "1")

import plotly.graph_objects as go
import plotly.io as pio
from plotly.offline import get_plotlyjs
from flask import Flask, Response, render_template_string, request


app = Flask(__name__)


# ---------------------------------------------------------------------------
# Static demo data. This keeps the app client-demo friendly without a database.
# ---------------------------------------------------------------------------
HOSPITALS = ["Hospital A", "Hospital B", "Hospital C"]
DEFAULT_START_DATE = date(2026, 5, 1)
DEFAULT_END_DATE = date(2026, 5, 31)

HOSPITAL_METRICS = {
    "All Hospitals": {
        "revenue": 12.62,
        "patients": 4562,
        "occupancy": 78.6,
        "emergency": 186,
        "staff": 1248,
        "claims": 234,
        "claims_value": 2.45,
        "ratio": 18,
    },
    "Hospital A": {
        "revenue": 5.21,
        "patients": 1824,
        "occupancy": 82.2,
        "emergency": 74,
        "staff": 512,
        "claims": 93,
        "claims_value": 0.98,
        "ratio": 17,
    },
    "Hospital B": {
        "revenue": 4.35,
        "patients": 1575,
        "occupancy": 76.4,
        "emergency": 62,
        "staff": 421,
        "claims": 81,
        "claims_value": 0.86,
        "ratio": 18,
    },
    "Hospital C": {
        "revenue": 3.06,
        "patients": 1163,
        "occupancy": 73.8,
        "emergency": 50,
        "staff": 315,
        "claims": 60,
        "claims_value": 0.61,
        "ratio": 19,
    },
}

hospital_revenue_df = [
    {"Hospital": "Hospital A", "Revenue": 5.21},
    {"Hospital": "Hospital B", "Revenue": 4.35},
    {"Hospital": "Hospital C", "Revenue": 3.06},
]

department_revenue_df = [
    {"Department": "Radiology", "Revenue": 3.45},
    {"Department": "Pathology", "Revenue": 2.78},
    {"Department": "Surgery", "Revenue": 2.35},
    {"Department": "Pharmacy", "Revenue": 1.68},
    {"Department": "ICU", "Revenue": 1.25},
    {"Department": "Cardiology", "Revenue": 1.11},
]

monthly_df = [
    {"Month": "Jun", "Revenue": 6.35, "Expenses": 3.82},
    {"Month": "Jul", "Revenue": 7.18, "Expenses": 4.12},
    {"Month": "Aug", "Revenue": 8.06, "Expenses": 4.48},
    {"Month": "Sep", "Revenue": 8.92, "Expenses": 4.79},
    {"Month": "Oct", "Revenue": 9.34, "Expenses": 5.03},
    {"Month": "Nov", "Revenue": 9.82, "Expenses": 5.22},
    {"Month": "Dec", "Revenue": 10.25, "Expenses": 5.47},
    {"Month": "Jan", "Revenue": 10.91, "Expenses": 5.86},
    {"Month": "Feb", "Revenue": 11.38, "Expenses": 6.12},
    {"Month": "Mar", "Revenue": 11.86, "Expenses": 6.52},
    {"Month": "Apr", "Revenue": 12.21, "Expenses": 7.06},
    {"Month": "May", "Revenue": 12.62, "Expenses": 7.81},
]

staff_df = [
    {"Role": "Doctors", "On Duty": 342, "Total": 415},
    {"Role": "Nurses", "On Duty": 512, "Total": 620},
    {"Role": "Technicians", "On Duty": 128, "Total": 160},
    {"Role": "Admin Staff", "On Duty": 63, "Total": 80},
]

alerts_df = [
    {
        "Hospital": "Hospital A",
        "Title": "Low on oxygen cylinders",
        "Detail": "Stock remaining: 12 units",
        "Severity": "Critical",
        "Time": "5 min ago",
    },
    {
        "Hospital": "Hospital B",
        "Title": "ICU occupancy high",
        "Detail": "ICU occupancy: 95%",
        "Severity": "High",
        "Time": "12 min ago",
    },
    {
        "Hospital": "Hospital C",
        "Title": "MRI machine maintenance scheduled",
        "Detail": "Scheduled maintenance at 2:00 PM",
        "Severity": "Warning",
        "Time": "25 min ago",
    },
    {
        "Hospital": "Hospital A",
        "Title": "High emergency admissions",
        "Detail": "Admissions increased by 32%",
        "Severity": "High",
        "Time": "35 min ago",
    },
]

inventory_df = [
    {
        "Resource": "Oxygen Cylinders",
        "Hospital": "Hospital A",
        "Status": "Critical",
        "Detail": "12 units remaining",
    },
    {
        "Resource": "Medicine: Inj. Meropenem",
        "Hospital": "Hospital B",
        "Status": "Low",
        "Detail": "8 units remaining",
    },
    {
        "Resource": "ICU Beds",
        "Hospital": "Hospital C",
        "Status": "Critical",
        "Detail": "2 beds available",
    },
    {
        "Resource": "Blood Units",
        "Hospital": "All Hospitals",
        "Status": "Low",
        "Detail": "A+ve: 15 | O-ve: 10",
    },
]

BOTTOM_KPIS = {
    "All Hospitals": {
        "queue": (46, {"Hospital A": 18, "Hospital B": 16, "Hospital C": 12}),
        "ambulance": (24, {"On Route": 8, "Available": 12, "At Hospital": 4}),
        "admissions": (286, {"OPD": 198, "IPD": 68, "Emergency": 20}),
        "discharges": (142, {"Hospital A": 48, "Hospital B": 57, "Hospital C": 37}),
    },
    "Hospital A": {
        "queue": (18, {"High": 8, "Medium": 6, "Low": 4}),
        "ambulance": (9, {"On Route": 3, "Available": 4, "At Hospital": 2}),
        "admissions": (112, {"OPD": 78, "IPD": 26, "Emergency": 8}),
        "discharges": (48, {"OPD": 21, "IPD": 19, "Emergency": 8}),
    },
    "Hospital B": {
        "queue": (16, {"High": 6, "Medium": 7, "Low": 3}),
        "ambulance": (8, {"On Route": 2, "Available": 5, "At Hospital": 1}),
        "admissions": (96, {"OPD": 65, "IPD": 24, "Emergency": 7}),
        "discharges": (57, {"OPD": 26, "IPD": 24, "Emergency": 7}),
    },
    "Hospital C": {
        "queue": (12, {"High": 4, "Medium": 5, "Low": 3}),
        "ambulance": (7, {"On Route": 3, "Available": 3, "At Hospital": 1}),
        "admissions": (78, {"OPD": 55, "IPD": 18, "Emergency": 5}),
        "discharges": (37, {"OPD": 18, "IPD": 14, "Emergency": 5}),
    },
}

MENU_ITEMS = [
    "Dashboard",
    "Patients",
    "Doctors",
    "Radiology",
    "Pathology",
    "Pharmacy",
    "Billing",
    "Insurance",
    "Inventory",
    "Staff Management",
    "Analytics",
    "Reports",
    "Settings",
]

MODULE_DEMOS = {
    "Patients": {
        "subtitle": "Registration, OPD, IPD, emergency, discharge and follow-up overview",
        "accent": "#1f6feb",
        "chart_title": "Patient Flow by Service",
        "categories": ["OPD", "IPD", "Emergency", "Follow-up", "Discharge"],
        "values": [198, 68, 20, 142, 87],
        "metrics": [("New Registrations", "286"), ("Avg Wait Time", "18 min"), ("Critical Patients", "34"), ("Discharges", "142")],
        "columns": ["Patient ID", "Name", "Hospital", "Type", "Department", "Status"],
        "rows": [
            ["UHMS-10231", "Amit Rao", "Hospital A", "IPD", "Cardiology", "Admitted"],
            ["UHMS-10232", "Neha Sharma", "Hospital B", "OPD", "Orthopedics", "Waiting"],
            ["UHMS-10233", "Ravi Menon", "Hospital C", "Emergency", "ICU", "Critical"],
            ["UHMS-10234", "Priya Nair", "Hospital A", "OPD", "Dermatology", "Consulted"],
        ],
    },
    "Doctors": {
        "subtitle": "Doctor availability, specialty coverage and consultation workload",
        "accent": "#12a864",
        "chart_title": "Consultations by Specialty",
        "categories": ["Cardiology", "Radiology", "Surgery", "Pediatrics", "ICU"],
        "values": [84, 68, 52, 76, 41],
        "metrics": [("Total Doctors", "415"), ("On Duty", "342"), ("Avg Consults", "22/day"), ("Utilization", "82%")],
        "columns": ["Doctor", "Specialty", "Hospital", "Queue", "Availability", "Rating"],
        "rows": [
            ["Dr. Meera Iyer", "Cardiology", "Hospital A", "14", "On Duty", "4.8"],
            ["Dr. Arjun Das", "Radiology", "Hospital B", "9", "In Procedure", "4.7"],
            ["Dr. Sara Khan", "ICU", "Hospital C", "6", "On Duty", "4.9"],
            ["Dr. Vikram Sen", "Surgery", "Hospital A", "11", "On Call", "4.6"],
        ],
    },
    "Radiology": {
        "subtitle": "Scan volumes, modality utilization, turnaround time and machine status",
        "accent": "#2f9de0",
        "chart_title": "Radiology Volume by Modality",
        "categories": ["X-Ray", "CT", "MRI", "USG", "Mammography"],
        "values": [420, 172, 96, 238, 54],
        "metrics": [("Revenue", "₹3.45 Cr"), ("Scans Today", "312"), ("TAT", "42 min"), ("Pending Reports", "28")],
        "columns": ["Order ID", "Modality", "Hospital", "Priority", "Status", "Radiologist"],
        "rows": [
            ["RAD-9001", "MRI Brain", "Hospital C", "Routine", "Scheduled", "Dr. Arjun"],
            ["RAD-9002", "CT Chest", "Hospital B", "Urgent", "Reporting", "Dr. Reema"],
            ["RAD-9003", "X-Ray AP", "Hospital A", "STAT", "Completed", "Dr. Kunal"],
            ["RAD-9004", "USG Abdomen", "Hospital B", "Routine", "In Scan", "Dr. Shalini"],
        ],
    },
    "Pathology": {
        "subtitle": "Lab orders, sample collection, report status and analyzer workload",
        "accent": "#12a6a6",
        "chart_title": "Lab Tests by Category",
        "categories": ["Hematology", "Biochemistry", "Microbiology", "Serology", "Histopath"],
        "values": [510, 438, 122, 186, 74],
        "metrics": [("Revenue", "₹2.78 Cr"), ("Samples Today", "1,330"), ("Reports Ready", "1,108"), ("Pending", "222")],
        "columns": ["Lab ID", "Test", "Hospital", "Sample", "Status", "TAT"],
        "rows": [
            ["LAB-7601", "CBC", "Hospital A", "Blood", "Ready", "28 min"],
            ["LAB-7602", "LFT", "Hospital B", "Serum", "Processing", "42 min"],
            ["LAB-7603", "Culture", "Hospital C", "Urine", "Incubation", "24 hr"],
            ["LAB-7604", "CRP", "Hospital A", "Blood", "Validated", "35 min"],
        ],
    },
    "Pharmacy": {
        "subtitle": "Prescription fulfillment, stock alerts, sales and expiry tracking",
        "accent": "#22c55e",
        "chart_title": "Pharmacy Sales by Category",
        "categories": ["Antibiotics", "Analgesics", "Cardiac", "Diabetes", "Consumables"],
        "values": [34, 22, 28, 19, 31],
        "metrics": [("Revenue", "₹1.68 Cr"), ("Orders", "1,942"), ("Low Stock", "18"), ("Fill Rate", "96%")],
        "columns": ["Item", "Hospital", "Stock", "Reorder Level", "Status", "Value"],
        "rows": [
            ["Inj. Meropenem", "Hospital B", "8", "25", "Low", "₹62,400"],
            ["Normal Saline", "Hospital A", "420", "160", "Healthy", "₹38,200"],
            ["Insulin Glargine", "Hospital C", "54", "40", "Healthy", "₹74,600"],
            ["Surgical Gloves", "Hospital A", "190", "240", "Reorder", "₹21,900"],
        ],
    },
    "Billing": {
        "subtitle": "Revenue collection, outstanding dues, refunds and package billing",
        "accent": "#f59e0b",
        "chart_title": "Collections by Payment Mode",
        "categories": ["Cash", "UPI", "Card", "Insurance", "Corporate"],
        "values": [1.42, 2.26, 1.84, 4.1, 3.0],
        "metrics": [("Collected", "₹12.62 Cr"), ("Outstanding", "₹1.04 Cr"), ("Refunds", "₹18.6 L"), ("Invoices", "3,846")],
        "columns": ["Invoice", "Patient", "Hospital", "Amount", "Mode", "Status"],
        "rows": [
            ["INV-2401", "Amit Rao", "Hospital A", "₹84,300", "Insurance", "Submitted"],
            ["INV-2402", "Neha Sharma", "Hospital B", "₹6,200", "UPI", "Paid"],
            ["INV-2403", "Ravi Menon", "Hospital C", "₹2,18,900", "Corporate", "Part Paid"],
            ["INV-2404", "Priya Nair", "Hospital A", "₹12,400", "Card", "Paid"],
        ],
    },
    "Insurance": {
        "subtitle": "Claim submission, pre-auth, settlement and rejection monitoring",
        "accent": "#6d5dfc",
        "chart_title": "Insurance Claim Pipeline",
        "categories": ["Pre-auth", "Submitted", "Under Review", "Approved", "Rejected"],
        "values": [82, 234, 118, 174, 21],
        "metrics": [("Pending Claims", "234"), ("Claim Value", "₹2.45 Cr"), ("Approved", "174"), ("Rejection Rate", "5.2%")],
        "columns": ["Claim ID", "Payer", "Hospital", "Value", "Stage", "Aging"],
        "rows": [
            ["CLM-6501", "Star Health", "Hospital A", "₹1,24,000", "Under Review", "4 days"],
            ["CLM-6502", "HDFC Ergo", "Hospital B", "₹86,500", "Pre-auth", "1 day"],
            ["CLM-6503", "Corporate TPA", "Hospital C", "₹2,42,800", "Approved", "6 days"],
            ["CLM-6504", "ICICI Lombard", "Hospital A", "₹54,300", "Submitted", "2 days"],
        ],
    },
    "Inventory": {
        "subtitle": "Central stock visibility across medicine, oxygen, ICU beds and consumables",
        "accent": "#ef4444",
        "chart_title": "Critical Resource Availability",
        "categories": ["Oxygen", "ICU Beds", "Blood", "Ventilators", "Antibiotics"],
        "values": [12, 2, 25, 14, 8],
        "metrics": [("Critical Items", "3"), ("Low Items", "2"), ("Stock Value", "₹4.8 Cr"), ("PO Pending", "37")],
        "columns": ["Resource", "Hospital", "Available", "Threshold", "Status", "Owner"],
        "rows": [
            ["Oxygen Cylinders", "Hospital A", "12", "40", "Critical", "Stores"],
            ["ICU Beds", "Hospital C", "2", "8", "Critical", "Operations"],
            ["Blood Units", "All Hospitals", "25", "50", "Low", "Blood Bank"],
            ["Ventilators", "Hospital B", "14", "10", "Healthy", "Biomedical"],
        ],
    },
    "Staff Management": {
        "subtitle": "Shift coverage, attendance, leave, roster and role utilization",
        "accent": "#0f9f9f",
        "chart_title": "Workforce by Role",
        "categories": ["Doctors", "Nurses", "Technicians", "Admin", "Support"],
        "values": [415, 620, 160, 80, 210],
        "metrics": [("Total Staff", "1,485"), ("On Duty", "1,248"), ("Leave", "86"), ("Attendance", "91%")],
        "columns": ["Employee", "Role", "Hospital", "Shift", "Attendance", "Status"],
        "rows": [
            ["EMP-1401", "Nurse", "Hospital A", "Morning", "Present", "On Duty"],
            ["EMP-1402", "Technician", "Hospital B", "Night", "Present", "Lab"],
            ["EMP-1403", "Doctor", "Hospital C", "Evening", "Present", "ICU"],
            ["EMP-1404", "Admin", "Hospital A", "Morning", "Leave", "Approved"],
        ],
    },
    "Analytics": {
        "subtitle": "Executive analytics, trends, operational health and forecast signals",
        "accent": "#1f6feb",
        "chart_title": "Operational KPI Score",
        "categories": ["Revenue", "Occupancy", "TAT", "Claims", "Inventory"],
        "values": [92, 79, 84, 76, 68],
        "metrics": [("KPI Score", "84/100"), ("Growth", "+18.6%"), ("Risk Alerts", "6"), ("Forecast", "Positive")],
        "columns": ["KPI", "Current", "Target", "Variance", "Owner", "Status"],
        "rows": [
            ["Revenue", "₹12.62 Cr", "₹11.8 Cr", "+7.0%", "Finance", "Ahead"],
            ["Occupancy", "78.6%", "80%", "-1.4%", "Operations", "Monitor"],
            ["Report TAT", "42 min", "45 min", "+3 min", "Diagnostics", "Good"],
            ["Claims Aging", "4.1 days", "3.5 days", "-0.6", "Insurance", "Watch"],
        ],
    },
    "Reports": {
        "subtitle": "Daily MIS, financial reports, clinical reports and compliance exports",
        "accent": "#64748b",
        "chart_title": "Reports Generated by Type",
        "categories": ["Finance", "Clinical", "Inventory", "HR", "Compliance"],
        "values": [48, 76, 32, 24, 18],
        "metrics": [("Reports Today", "198"), ("Scheduled", "42"), ("Downloaded", "127"), ("Pending", "9")],
        "columns": ["Report", "Module", "Hospital", "Frequency", "Format", "Status"],
        "rows": [
            ["Daily Revenue MIS", "Billing", "All Hospitals", "Daily", "PDF", "Ready"],
            ["Doctor Utilization", "Doctors", "All Hospitals", "Weekly", "XLSX", "Ready"],
            ["Stock Exception", "Inventory", "Hospital A", "Daily", "PDF", "Queued"],
            ["Claims Aging", "Insurance", "Hospital B", "Daily", "XLSX", "Ready"],
        ],
    },
    "Settings": {
        "subtitle": "Hospital configuration, access control, notifications and audit controls",
        "accent": "#475569",
        "chart_title": "Configuration Completion",
        "categories": ["Users", "Roles", "Hospitals", "Alerts", "Integrations"],
        "values": [96, 92, 100, 88, 78],
        "metrics": [("Hospitals", "3"), ("Active Users", "286"), ("Roles", "18"), ("Audit Logs", "12.4k")],
        "columns": ["Setting", "Scope", "Owner", "Updated", "Status", "Action"],
        "rows": [
            ["Role Permissions", "All Hospitals", "Admin", "Today", "Active", "Review"],
            ["Notification Rules", "Operations", "Admin", "Yesterday", "Active", "Edit"],
            ["Billing Codes", "Finance", "CFO Office", "2 days ago", "Active", "Review"],
            ["Integration Keys", "IT", "System Admin", "5 days ago", "Secured", "Rotate"],
        ],
    },
}


TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>UHMS Super Admin Dashboard</title>
    <script src="/plotly.js"></script>
    <style>
        :root {
            --blue: #1f6feb;
            --teal: #12a6a6;
            --green: #12a864;
            --orange: #f59e0b;
            --red: #ef4444;
            --ink: #0f1f3d;
            --muted: #66758f;
            --line: #dde7f3;
            --soft: #f6f9fd;
            --panel: #ffffff;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            background: #ffffff;
            color: var(--ink);
            font-family: Inter, Segoe UI, Roboto, Arial, sans-serif;
            letter-spacing: 0;
        }

        .app-shell {
            display: grid;
            grid-template-columns: 274px minmax(0, 1fr);
            min-height: 100vh;
        }

        .sidebar {
            border-right: 1px solid #e8eef7;
            background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
            padding: 24px 18px;
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 13px;
            padding-bottom: 20px;
            border-bottom: 1px solid #edf2f7;
            margin-bottom: 18px;
        }

        .logo-mark {
            width: 46px;
            height: 46px;
            border-radius: 8px;
            background:
                linear-gradient(135deg, #34c6e8 0 44%, transparent 45%),
                linear-gradient(225deg, #2f80ed 0 44%, transparent 45%),
                linear-gradient(315deg, #36d399 0 44%, transparent 45%),
                linear-gradient(45deg, #6d5dfc 0 44%, transparent 45%);
            box-shadow: 0 12px 22px rgba(31, 111, 235, 0.18);
            flex: 0 0 auto;
        }

        .brand-title {
            font-size: 27px;
            line-height: 1;
            font-weight: 850;
        }

        .brand-subtitle {
            margin-top: 5px;
            color: var(--muted);
            font-size: 12px;
            line-height: 1.25;
            font-weight: 650;
        }

        .nav-list {
            display: grid;
            gap: 4px;
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: 11px;
            padding: 11px 12px;
            border-radius: 8px;
            color: #263956;
            font-size: 14px;
            font-weight: 750;
            text-decoration: none;
            transition: background 140ms ease, color 140ms ease, transform 140ms ease;
        }

        .nav-item:hover {
            background: #eef5ff;
            color: var(--blue);
            transform: translateX(2px);
        }

        .nav-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #9ab0cf;
        }

        .nav-item.active {
            color: #ffffff;
            background: linear-gradient(135deg, #1f6feb, #2f80ed);
            box-shadow: 0 10px 18px rgba(31, 111, 235, 0.24);
        }

        .nav-item.active .nav-dot {
            background: #ffffff;
        }

        .sidebar-card {
            margin-top: 16px;
            padding: 14px;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 10px 28px rgba(15, 31, 61, 0.05);
        }

        .content {
            min-width: 0;
            background: linear-gradient(180deg, #ffffff 0%, #fbfdff 38%, #ffffff 100%);
        }

        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            padding: 24px 24px 18px;
            border-bottom: 1px solid #edf2f7;
            background: rgba(255, 255, 255, 0.94);
            position: sticky;
            top: 0;
            z-index: 3;
            backdrop-filter: blur(12px);
        }

        .page-title h1 {
            margin: 0;
            font-size: 26px;
            line-height: 1.15;
            font-weight: 850;
        }

        .page-title p {
            margin: 5px 0 0;
            color: var(--muted);
            font-size: 14px;
            font-weight: 650;
        }

        .filters {
            display: flex;
            align-items: end;
            gap: 12px;
            flex-wrap: wrap;
            justify-content: flex-end;
        }

        .filter-control {
            display: grid;
            gap: 6px;
        }

        label {
            color: #344766;
            font-size: 12px;
            font-weight: 800;
        }

        select,
        input[type="date"] {
            width: 180px;
            height: 42px;
            border: 1px solid #d8e4f2;
            border-radius: 8px;
            background: #ffffff;
            color: var(--ink);
            padding: 0 12px;
            font: inherit;
            font-size: 13px;
            font-weight: 700;
            box-shadow: 0 8px 18px rgba(15, 31, 61, 0.04);
        }

        .filter-button {
            height: 42px;
            padding: 0 16px;
            border: 0;
            border-radius: 8px;
            background: var(--blue);
            color: #ffffff;
            font-size: 13px;
            font-weight: 850;
            cursor: pointer;
            box-shadow: 0 10px 20px rgba(31, 111, 235, 0.2);
        }

        .dashboard {
            padding: 20px 24px 26px;
            max-width: 1500px;
            margin: 0 auto;
        }

        .context-line {
            color: var(--muted);
            font-size: 13px;
            font-weight: 650;
            margin-bottom: 14px;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(6, minmax(160px, 1fr));
            gap: 16px;
            margin-bottom: 18px;
        }

        .metric-card,
        .panel {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--panel);
            box-shadow: 0 12px 30px rgba(15, 31, 61, 0.07);
        }

        .metric-card {
            position: relative;
            min-height: 126px;
            padding: 17px 16px;
            overflow: hidden;
        }

        .metric-card::after {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, var(--accent-bg), transparent 60%);
            pointer-events: none;
        }

        .metric-title,
        .metric-value,
        .metric-foot {
            position: relative;
            z-index: 1;
        }

        .metric-title {
            color: #1e3153;
            font-size: 13px;
            font-weight: 800;
            min-height: 30px;
        }

        .metric-value {
            margin-top: 4px;
            font-size: 29px;
            line-height: 1.05;
            font-weight: 850;
        }

        .metric-foot {
            margin-top: 12px;
            color: var(--muted);
            font-size: 12px;
            font-weight: 650;
        }

        .metric-foot strong {
            color: var(--accent);
        }

        .chart-grid {
            display: grid;
            grid-template-columns: 1.05fr 1.05fr 1.35fr;
            gap: 16px;
            margin-bottom: 16px;
        }

        .ops-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 16px;
            margin-bottom: 16px;
        }

        .bottom-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 16px;
        }

        .panel {
            padding: 17px;
            min-width: 0;
            min-height: 100%;
            position: relative;
            overflow: hidden;
        }

        .panel.chart-panel::before {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            top: 0;
            height: 4px;
            background: linear-gradient(90deg, #1f6feb, #12a6a6, #22c55e, #f59e0b);
        }

        .panel-title {
            margin: 0;
            color: var(--ink);
            font-size: 17px;
            line-height: 1.2;
            font-weight: 850;
        }

        .panel-subtitle {
            margin: 6px 0 10px;
            color: var(--muted);
            font-size: 12px;
            font-weight: 700;
        }

        .chart {
            width: 100%;
            height: 315px;
        }

        .module-hero {
            display: grid;
            grid-template-columns: minmax(0, 1.3fr) minmax(300px, 0.7fr);
            gap: 16px;
            margin-bottom: 16px;
        }

        .module-title {
            margin: 0;
            font-size: 28px;
            font-weight: 850;
            line-height: 1.1;
        }

        .module-copy {
            color: var(--muted);
            font-size: 14px;
            line-height: 1.5;
            font-weight: 650;
            max-width: 760px;
        }

        .module-metric-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(150px, 1fr));
            gap: 14px;
            margin-top: 18px;
        }

        .module-metric {
            border: 1px solid #e5edf7;
            border-radius: 8px;
            padding: 14px;
            background: linear-gradient(135deg, rgba(31, 111, 235, 0.08), #ffffff 70%);
        }

        .module-table {
            width: 100%;
            border-collapse: collapse;
            overflow: hidden;
            border-radius: 8px;
            font-size: 13px;
        }

        .module-table th {
            color: #334765;
            background: #f4f8fd;
            text-align: left;
            padding: 12px 14px;
            font-size: 12px;
            font-weight: 850;
            border-bottom: 1px solid #dfe8f3;
        }

        .module-table td {
            padding: 13px 14px;
            border-bottom: 1px solid #edf2f7;
            font-weight: 700;
            color: #253754;
        }

        .module-table tr:last-child td {
            border-bottom: 0;
        }

        .module-insights {
            display: grid;
            gap: 12px;
        }

        .insight-card {
            border: 1px solid #e5edf7;
            border-radius: 8px;
            padding: 14px;
            background: #ffffff;
        }
        }

        .alert-row,
        .inventory-row {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 12px;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #edf2f7;
        }

        .alert-row:last-child,
        .inventory-row:last-child {
            border-bottom: 0;
        }

        .item-title {
            color: var(--ink);
            font-size: 13px;
            font-weight: 850;
            line-height: 1.25;
        }

        .item-detail {
            margin-top: 4px;
            color: var(--muted);
            font-size: 12px;
            line-height: 1.25;
            font-weight: 650;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 62px;
            border-radius: 8px;
            padding: 6px 8px;
            font-size: 11px;
            line-height: 1;
            font-weight: 850;
            white-space: nowrap;
        }

        .badge.critical {
            background: #ffe6e6;
            color: var(--red);
        }

        .badge.high {
            background: #fff0db;
            color: #d97706;
        }

        .badge.warning,
        .badge.low {
            background: #fff6dd;
            color: #c97700;
        }

        .progress-summary {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
            margin: 10px 0 14px;
        }

        .small-label {
            color: var(--muted);
            font-size: 12px;
            font-weight: 750;
        }

        .summary-value {
            margin-top: 4px;
            color: var(--blue);
            font-size: 23px;
            font-weight: 850;
        }

        .progress-row {
            display: grid;
            grid-template-columns: 92px 1fr 72px;
            gap: 10px;
            align-items: center;
            margin: 15px 0;
        }

        .progress-label,
        .progress-value {
            color: #253754;
            font-size: 12px;
            font-weight: 800;
        }

        .progress-value {
            text-align: right;
        }

        .bar-track {
            height: 8px;
            border-radius: 8px;
            background: #e8eef5;
            overflow: hidden;
        }

        .bar-fill {
            height: 100%;
            border-radius: 8px;
            background: linear-gradient(90deg, #12a864, #11b5a4);
        }

        .kpi-total {
            margin-top: 10px;
            color: var(--blue);
            font-size: 27px;
            line-height: 1;
            font-weight: 850;
        }

        .mini-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
            margin-top: 18px;
        }

        .mini-value {
            margin-top: 5px;
            font-size: 21px;
            line-height: 1;
            font-weight: 850;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            color: var(--green);
            font-size: 12px;
            font-weight: 850;
        }

        .status-pill::before {
            content: "";
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--green);
        }

        @media (max-width: 1280px) {
            .metric-grid {
                grid-template-columns: repeat(3, minmax(180px, 1fr));
            }

            .chart-grid,
            .ops-grid,
            .bottom-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .module-hero,
            .module-metric-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 860px) {
            .app-shell {
                grid-template-columns: 1fr;
            }

            .sidebar {
                position: relative;
                height: auto;
            }

            .topbar {
                position: relative;
                display: block;
            }

            .filters {
                margin-top: 16px;
                justify-content: flex-start;
            }

            .metric-grid,
            .chart-grid,
            .ops-grid,
            .bottom-grid,
            .module-hero,
            .module-metric-grid {
                grid-template-columns: 1fr;
            }

            select,
            input[type="date"] {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="app-shell">
        <aside class="sidebar">
            <div class="brand">
                <div class="logo-mark"></div>
                <div>
                    <div class="brand-title">UHMS</div>
                    <div class="brand-subtitle">Unified Hospital<br>Management System</div>
                </div>
            </div>

            <nav class="nav-list" aria-label="Primary navigation">
                {% for item in menu_items %}
                <a class="nav-item {% if item == current_page %}active{% endif %}" href="/?page={{ item|urlencode }}&hospital={{ selected_hospital|urlencode }}&start={{ start_date }}&end={{ end_date }}">
                    <span class="nav-dot"></span>
                    <span>{{ item }}</span>
                </a>
                {% endfor %}
            </nav>

            <div class="sidebar-card">
                <div class="item-title">Super Admin</div>
                <div class="item-detail">superadmin@uhms.com</div>
            </div>
            <div class="sidebar-card">
                <div class="item-title">System Status</div>
                <div class="item-detail"><span class="status-pill">All systems operational</span></div>
            </div>
            <div class="item-detail" style="margin:18px 4px 0;">2026 UHMS. Demo data only.</div>
        </aside>

        <main class="content">
            <header class="topbar">
                <div class="page-title">
                    <h1>{{ page_heading }}</h1>
                    <p>{{ page_subtitle }}</p>
                </div>

                <form class="filters" method="get">
                    <div class="filter-control">
                        <label for="hospital">Hospital</label>
                        <select id="hospital" name="hospital" onchange="this.form.submit()">
                            {% for hospital in hospital_options %}
                            <option value="{{ hospital }}" {% if hospital == selected_hospital %}selected{% endif %}>{{ hospital }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="filter-control">
                        <label for="start">Start date</label>
                        <input id="start" type="date" name="start" value="{{ start_date }}">
                    </div>
                    <div class="filter-control">
                        <label for="end">End date</label>
                        <input id="end" type="date" name="end" value="{{ end_date }}">
                    </div>
                    <button class="filter-button" type="submit">Apply</button>
                </form>
            </header>

            <section class="dashboard">
                <div class="context-line">
                    Viewing {{ selected_hospital }} from {{ display_start }} to {{ display_end }}
                </div>

                {% if current_page == 'Dashboard' %}

                <section class="metric-grid">
                    {% for card in metric_cards %}
                    <article class="metric-card" style="--accent:{{ card.accent }};--accent-bg:{{ card.accent_bg }};">
                        <div class="metric-title">{{ card.title }}</div>
                        <div class="metric-value">{{ card.value }}</div>
                        <div class="metric-foot">{{ card.foot | safe }}</div>
                    </article>
                    {% endfor %}
                </section>

                <section class="chart-grid">
                    <article class="panel chart-panel">
                        <h2 class="panel-title">Revenue by Hospital</h2>
                        <div class="panel-subtitle">Total Revenue: {{ total_revenue }}</div>
                        <div id="revenueHospital" class="chart"></div>
                    </article>
                    <article class="panel chart-panel">
                        <h2 class="panel-title">Revenue by Department</h2>
                        <div class="panel-subtitle">Department contribution this month</div>
                        <div id="revenueDepartment" class="chart"></div>
                    </article>
                    <article class="panel chart-panel">
                        <h2 class="panel-title">Revenue vs Expenses Trend</h2>
                        <div class="panel-subtitle">Last 12 months</div>
                        <div id="revenueExpenses" class="chart"></div>
                    </article>
                </section>

                <section class="ops-grid">
                    <article class="panel chart-panel">
                        <h2 class="panel-title">Doctor to Patient Ratio</h2>
                        <div class="panel-subtitle">Current ratio: 1:{{ metrics.ratio }} | Recommended: 1:20</div>
                        <div id="doctorRatio" class="chart"></div>
                        <div style="text-align:center;"><span class="status-pill">Good staffing level</span></div>
                    </article>

                    <article class="panel">
                        <h2 class="panel-title">Live Alerts</h2>
                        <div class="panel-subtitle">{{ alerts|length }} new operational alerts</div>
                        {% for alert in alerts %}
                        <div class="alert-row">
                            <div>
                                <div class="item-title">{{ alert.Hospital }}: {{ alert.Title }}</div>
                                <div class="item-detail">{{ alert.Detail }}</div>
                            </div>
                            <div style="text-align:right;">
                                <span class="badge {{ alert.Severity|lower }}">{{ alert.Severity }}</span>
                                <div class="item-detail">{{ alert.Time }}</div>
                            </div>
                        </div>
                        {% endfor %}
                    </article>

                    <article class="panel">
                        <h2 class="panel-title">Staff On Duty</h2>
                        <div class="panel-subtitle">Live workforce availability</div>
                        <div class="progress-summary">
                            <div>
                                <div class="small-label">Total Staff</div>
                                <div class="summary-value">{{ staff_summary.total }}</div>
                            </div>
                            <div>
                                <div class="small-label">On Duty</div>
                                <div class="summary-value" style="color:var(--green);">{{ staff_summary.on_duty }} <span style="font-size:13px;">({{ staff_summary.percent }}%)</span></div>
                            </div>
                        </div>
                        {% for row in staff_rows %}
                        <div class="progress-row">
                            <div class="progress-label">{{ row.Role }}</div>
                            <div class="bar-track"><div class="bar-fill" style="width:{{ row.Percent }}%;"></div></div>
                            <div class="progress-value">{{ row.OnDuty }} / {{ row.Total }}</div>
                        </div>
                        {% endfor %}
                    </article>

                    <article class="panel">
                        <h2 class="panel-title">Inventory & Resource Alerts</h2>
                        <div class="panel-subtitle">Critical and low-stock items</div>
                        {% for item in inventory %}
                        <div class="inventory-row">
                            <div>
                                <div class="item-title">{{ item.Resource }} ({{ item.Hospital }})</div>
                                <div class="item-detail">{{ item.Detail }}</div>
                            </div>
                            <span class="badge {{ item.Status|lower }}">{{ item.Status }}</span>
                        </div>
                        {% endfor %}
                    </article>
                </section>

                <section class="bottom-grid">
                    {% for card in bottom_cards %}
                    <article class="panel">
                        <h2 class="panel-title">{{ card.title }}</h2>
                        <div class="small-label">Total</div>
                        <div class="kpi-total" style="color:{{ card.accent }};">{{ card.total }}</div>
                        <div class="mini-grid">
                            {% for label, value in card.details.items() %}
                            <div>
                                <div class="small-label">{{ label }}</div>
                                <div class="mini-value" style="color:{{ card.accent }};">{{ value }}</div>
                            </div>
                            {% endfor %}
                        </div>
                    </article>
                    {% endfor %}
                </section>
                {% else %}
                <section class="module-hero">
                    <article class="panel">
                        <h2 class="module-title">{{ module.title }}</h2>
                        <p class="module-copy">{{ module.subtitle }}</p>
                        <div class="module-metric-grid">
                            {% for label, value in module.metrics %}
                            <div class="module-metric">
                                <div class="small-label">{{ label }}</div>
                                <div class="summary-value" style="color:{{ module.accent }};">{{ value }}</div>
                            </div>
                            {% endfor %}
                        </div>
                    </article>
                    <article class="panel chart-panel">
                        <h2 class="panel-title">{{ module.chart_title }}</h2>
                        <div class="panel-subtitle">Demo view for {{ selected_hospital }}</div>
                        <div id="moduleChart" class="chart"></div>
                    </article>
                </section>

                <section class="chart-grid" style="grid-template-columns:1.2fr .8fr;">
                    <article class="panel">
                        <h2 class="panel-title">{{ module.title }} Worklist</h2>
                        <div class="panel-subtitle">Representative records for client walkthrough</div>
                        <table class="module-table">
                            <thead>
                                <tr>
                                    {% for column in module.columns %}
                                    <th>{{ column }}</th>
                                    {% endfor %}
                                </tr>
                            </thead>
                            <tbody>
                                {% for row in module.rows %}
                                <tr>
                                    {% for cell in row %}
                                    <td>{{ cell }}</td>
                                    {% endfor %}
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </article>
                    <article class="panel">
                        <h2 class="panel-title">Client Demo Talking Points</h2>
                        <div class="module-insights">
                            <div class="insight-card">
                                <div class="item-title">Unified hospital filter</div>
                                <div class="item-detail">Owners can switch between all hospitals or a single hospital without changing modules.</div>
                            </div>
                            <div class="insight-card">
                                <div class="item-title">Operational drill-down</div>
                                <div class="item-detail">Each module can later connect to real workflows, approvals, reports and audit logs.</div>
                            </div>
                            <div class="insight-card">
                                <div class="item-title">Static demo data today</div>
                                <div class="item-detail">The layout is ready for API/database integration when the actual UHMS backend is available.</div>
                            </div>
                        </div>
                    </article>
                </section>
                {% endif %}
            </section>
        </main>
    </div>

    <script>
        const chartSpecs = {{ charts_json | safe }};
        const chartConfig = { displayModeBar: false, responsive: true };

        Object.entries(chartSpecs).forEach(([id, spec]) => {
            if (document.getElementById(id)) {
                Plotly.newPlot(id, spec.data, spec.layout, chartConfig);
            }
        });

        window.addEventListener("resize", () => {
            Object.keys(chartSpecs).forEach((id) => {
                if (document.getElementById(id)) {
                    Plotly.Plots.resize(id);
                }
            });
        });
    </script>
</body>
</html>
"""


def currency_cr(value: float) -> str:
    return f"₹ {value:.2f} Cr"


def clean_hospital(value: str | None) -> str:
    if value in HOSPITAL_METRICS:
        return value
    return "All Hospitals"


def clean_page(value: str | None) -> str:
    if value in MENU_ITEMS:
        return value
    return "Dashboard"


def parse_date(value: str | None, fallback: date) -> date:
    try:
        return date.fromisoformat(value) if value else fallback
    except ValueError:
        return fallback


def scaled_department_data(selected_hospital: str) -> list[dict]:
    total = HOSPITAL_METRICS[selected_hospital]["revenue"]
    scale = total / HOSPITAL_METRICS["All Hospitals"]["revenue"]
    return [
        {"Department": row["Department"], "Revenue": row["Revenue"] * scale}
        for row in department_revenue_df
    ]


def scaled_monthly_data(selected_hospital: str) -> list[dict]:
    if selected_hospital == "All Hospitals":
        return [dict(row) for row in monthly_df]

    scale = HOSPITAL_METRICS[selected_hospital]["revenue"] / HOSPITAL_METRICS["All Hospitals"]["revenue"]
    return [
        {
            "Month": row["Month"],
            "Revenue": row["Revenue"] * scale,
            "Expenses": row["Expenses"] * scale * 0.96,
        }
        for row in monthly_df
    ]


def scaled_staff_data(selected_hospital: str) -> list[dict]:
    if selected_hospital == "All Hospitals":
        return [dict(row) for row in staff_df]

    scale = HOSPITAL_METRICS[selected_hospital]["staff"] / HOSPITAL_METRICS["All Hospitals"]["staff"]
    return [
        {
            "Role": row["Role"],
            "On Duty": round(row["On Duty"] * scale),
            "Total": round(row["Total"] * scale),
        }
        for row in staff_df
    ]


def selected_alerts(selected_hospital: str) -> list[dict]:
    if selected_hospital == "All Hospitals":
        return [dict(row) for row in alerts_df]
    return [dict(row) for row in alerts_df if row["Hospital"] == selected_hospital]


def selected_inventory(selected_hospital: str) -> list[dict]:
    if selected_hospital == "All Hospitals":
        return [dict(row) for row in inventory_df]
    return [
        dict(row)
        for row in inventory_df
        if row["Hospital"] in {selected_hospital, "All Hospitals"}
    ]


def base_layout(height: int = 292) -> dict:
    return {
        "height": height,
        "margin": {"l": 12, "r": 12, "t": 24, "b": 12},
        "paper_bgcolor": "#ffffff",
        "plot_bgcolor": "rgba(246, 249, 253, 0.55)",
        "font": {"color": "#0f1f3d", "family": "Inter, Segoe UI, Arial", "size": 12},
        "xaxis": {"showgrid": False, "zeroline": False},
        "yaxis": {"gridcolor": "#e8eef7", "zeroline": False},
        "hoverlabel": {"bgcolor": "#0f1f3d", "font": {"color": "#ffffff"}},
    }


def revenue_hospital_chart(selected_hospital: str) -> go.Figure:
    data = [dict(row) for row in hospital_revenue_df]
    colors = ["#1f6feb", "#12a6a6", "#6d5dfc"]
    if selected_hospital != "All Hospitals":
        data = [row for row in data if row["Hospital"] == selected_hospital]
        colors = ["#1f6feb"]
    labels = [row["Hospital"] for row in data]
    values = [row["Revenue"] for row in data]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker={
                "color": values,
                "colorscale": [[0, colors[-1]], [0.5, colors[1 if len(colors) > 1 else 0]], [1, colors[0]]],
                "line": {"color": "#ffffff", "width": 2},
            },
            width=0.48,
            text=[currency_cr(value) for value in values],
            textposition="outside",
            hovertemplate="%{x}<br>Revenue: ₹%{y:.2f} Cr<extra></extra>",
        )
    )
    fig.update_layout(**base_layout())
    fig.update_yaxes(title_text="Revenue in Cr", ticksuffix=" Cr")
    return fig


def department_chart(selected_hospital: str) -> go.Figure:
    data = scaled_department_data(selected_hospital)
    colors = ["#1f6feb", "#12a6a6", "#22c55e", "#2f9de0", "#6d5dfc", "#f6b34b"]
    labels = [row["Department"] for row in data]
    values = [row["Revenue"] for row in data]
    total = sum(values)

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            textinfo="percent",
            textfont={"color": "#ffffff", "size": 12},
            marker={"colors": colors, "line": {"color": "#ffffff", "width": 2}},
            hovertemplate="%{label}<br>₹%{value:.2f} Cr (%{percent})<extra></extra>",
        )
    )
    fig.update_layout(
        height=315,
        margin={"l": 0, "r": 0, "t": 10, "b": 0},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font={"color": "#0f1f3d", "family": "Inter, Segoe UI, Arial", "size": 12},
        legend={"orientation": "v", "yanchor": "middle", "y": 0.5, "xanchor": "left", "x": 0.92, "font": {"size": 11}},
        annotations=[
            {
                "text": f"<b>{currency_cr(total)}</b><br><span style='font-size:12px'>Total</span>",
                "x": 0.38,
                "y": 0.5,
                "showarrow": False,
                "font": {"color": "#0f1f3d", "size": 16},
            }
        ],
    )
    return fig


def revenue_expense_chart(selected_hospital: str) -> go.Figure:
    data = scaled_monthly_data(selected_hospital)
    months = [row["Month"] for row in data]
    revenue = [row["Revenue"] for row in data]
    expenses = [row["Expenses"] for row in data]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=months,
            y=revenue,
            name="Revenue (Cr)",
            mode="lines+markers+text",
            line={"color": "#0f9f9f", "width": 3},
            marker={"size": 8},
            fill="tozeroy",
            fillcolor="rgba(18, 166, 166, 0.10)",
            text=["" for _ in range(len(data) - 1)] + [currency_cr(revenue[-1])],
            textposition="top center",
            hovertemplate="%{x}<br>Revenue: ₹%{y:.2f} Cr<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=months,
            y=expenses,
            name="Expenses (Cr)",
            mode="lines+markers+text",
            line={"color": "#ef4444", "width": 3},
            marker={"size": 8},
            fill="tozeroy",
            fillcolor="rgba(239, 68, 68, 0.08)",
            text=["" for _ in range(len(data) - 1)] + [currency_cr(expenses[-1])],
            textposition="bottom center",
            hovertemplate="%{x}<br>Expenses: ₹%{y:.2f} Cr<extra></extra>",
        )
    )
    fig.update_layout(**base_layout())
    fig.update_layout(legend={"orientation": "h", "y": 1.14, "x": 0})
    return fig


def doctor_ratio_chart(selected_hospital: str) -> go.Figure:
    ratio = HOSPITAL_METRICS[selected_hospital]["ratio"]
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=ratio,
            number={"prefix": "1:", "font": {"size": 32, "color": "#1f6feb"}},
            gauge={
                "axis": {
                    "range": [0, 40],
                    "tickvals": [0, 10, 20, 30, 40],
                    "ticktext": ["1:0", "1:10", "1:20", "1:30", "1:40"],
                },
                "bar": {"color": "#0f1f3d", "thickness": 0.18},
                "bgcolor": "#ffffff",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 20], "color": "#14b8a6"},
                    {"range": [20, 30], "color": "#f59e0b"},
                    {"range": [30, 40], "color": "#ef4444"},
                ],
                "threshold": {"line": {"color": "#0f1f3d", "width": 3}, "thickness": 0.75, "value": ratio},
            },
        )
    )
    fig.update_layout(height=285, margin={"l": 8, "r": 8, "t": 8, "b": 0}, paper_bgcolor="#ffffff")
    return fig


def module_chart(current_page: str) -> go.Figure:
    module = MODULE_DEMOS[current_page]
    fig = go.Figure(
        go.Bar(
            x=module["categories"],
            y=module["values"],
            marker={
                "color": module["values"],
                "colorscale": [[0, "#dbeafe"], [0.45, module["accent"]], [1, "#0f1f3d"]],
                "line": {"color": "#ffffff", "width": 2},
            },
            text=module["values"],
            textposition="outside",
            hovertemplate="%{x}<br>Value: %{y}<extra></extra>",
        )
    )
    fig.update_layout(**base_layout(315))
    return fig


def chart_payload(selected_hospital: str, current_page: str) -> str:
    charts = {
        "revenueHospital": json.loads(pio.to_json(revenue_hospital_chart(selected_hospital), validate=False)),
        "revenueDepartment": json.loads(pio.to_json(department_chart(selected_hospital), validate=False)),
        "revenueExpenses": json.loads(pio.to_json(revenue_expense_chart(selected_hospital), validate=False)),
        "doctorRatio": json.loads(pio.to_json(doctor_ratio_chart(selected_hospital), validate=False)),
    }
    if current_page != "Dashboard":
        charts = {
            "moduleChart": json.loads(pio.to_json(module_chart(current_page), validate=False)),
        }
    return json.dumps(charts)


def metric_cards(selected_hospital: str) -> list[dict]:
    metrics = HOSPITAL_METRICS[selected_hospital]
    return [
        {
            "title": "Total Revenue This Month",
            "value": currency_cr(metrics["revenue"]),
            "foot": "<strong>+18.6%</strong> vs last month",
            "accent": "#1f6feb",
            "accent_bg": "rgba(31,111,235,0.13)",
        },
        {
            "title": "Active Patients",
            "value": f"{metrics['patients']:,}",
            "foot": "<strong>+12.4%</strong> vs last month",
            "accent": "#12a864",
            "accent_bg": "rgba(18,168,100,0.12)",
        },
        {
            "title": "Bed Occupancy Rate",
            "value": f"{metrics['occupancy']:.1f}%",
            "foot": "<strong>+5.3%</strong> vs last month",
            "accent": "#6d5dfc",
            "accent_bg": "rgba(109,93,252,0.12)",
        },
        {
            "title": "Emergency Admissions",
            "value": f"{metrics['emergency']:,}",
            "foot": "<strong>+15.7%</strong> vs last month",
            "accent": "#ef4444",
            "accent_bg": "rgba(239,68,68,0.10)",
        },
        {
            "title": "Staff On Duty",
            "value": f"{metrics['staff']:,}",
            "foot": "<strong>Live</strong> shift tracking",
            "accent": "#12a6a6",
            "accent_bg": "rgba(18,166,166,0.12)",
        },
        {
            "title": "Pending Insurance Claims",
            "value": f"{metrics['claims']:,}",
            "foot": f"₹ {metrics['claims_value']:.2f} Cr",
            "accent": "#f59e0b",
            "accent_bg": "rgba(245,158,11,0.13)",
        },
    ]


def staff_payload(selected_hospital: str) -> tuple[list[dict], dict]:
    data = scaled_staff_data(selected_hospital)
    rows = [
        {
            "Role": row["Role"],
            "OnDuty": f"{row['On Duty']:,}",
            "Total": f"{row['Total']:,}",
            "Percent": round(row["On Duty"] / row["Total"] * 100, 1),
        }
        for row in data
    ]
    total = sum(row["Total"] for row in data)
    on_duty = sum(row["On Duty"] for row in data)
    summary = {
        "total": f"{total:,}",
        "on_duty": f"{on_duty:,}",
        "percent": f"{on_duty / total * 100:.1f}",
    }
    return rows, summary


def bottom_cards(selected_hospital: str) -> list[dict]:
    data = BOTTOM_KPIS[selected_hospital]
    return [
        {"title": "Emergency Queue", "total": data["queue"][0], "details": data["queue"][1], "accent": "#ef4444"},
        {"title": "Ambulance Tracking", "total": data["ambulance"][0], "details": data["ambulance"][1], "accent": "#1f6feb"},
        {"title": "Patient Admissions Today", "total": data["admissions"][0], "details": data["admissions"][1], "accent": "#12a864"},
        {"title": "Discharge Summary Today", "total": data["discharges"][0], "details": data["discharges"][1], "accent": "#6d5dfc"},
    ]


def module_payload(current_page: str) -> dict:
    data = dict(MODULE_DEMOS[current_page])
    data["title"] = current_page
    return data


@app.route("/plotly.js")
def plotly_js() -> Response:
    # Serve Plotly from the installed Python package so the app runs without CDN access.
    return Response(get_plotlyjs(), mimetype="text/javascript")


@app.route("/")
def dashboard() -> str:
    selected_hospital = clean_hospital(request.args.get("hospital"))
    current_page = clean_page(request.args.get("page"))
    start_date = parse_date(request.args.get("start"), DEFAULT_START_DATE)
    end_date = parse_date(request.args.get("end"), DEFAULT_END_DATE)
    metrics = HOSPITAL_METRICS[selected_hospital]
    staff_rows, staff_summary = staff_payload(selected_hospital)
    page_heading = "Super Admin Dashboard" if current_page == "Dashboard" else f"{current_page} Module"
    page_subtitle = (
        "Owner-level operational overview across Hospital A, Hospital B, and Hospital C"
        if current_page == "Dashboard"
        else MODULE_DEMOS[current_page]["subtitle"]
    )

    return render_template_string(
        TEMPLATE,
        menu_items=MENU_ITEMS,
        current_page=current_page,
        page_heading=page_heading,
        page_subtitle=page_subtitle,
        hospital_options=["All Hospitals", *HOSPITALS],
        selected_hospital=selected_hospital,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        display_start=start_date.strftime("%d %b %Y"),
        display_end=end_date.strftime("%d %b %Y"),
        metrics=metrics,
        metric_cards=metric_cards(selected_hospital),
        total_revenue=currency_cr(metrics["revenue"]),
        alerts=selected_alerts(selected_hospital),
        inventory=selected_inventory(selected_hospital),
        staff_rows=staff_rows,
        staff_summary=staff_summary,
        bottom_cards=bottom_cards(selected_hospital),
        module=module_payload(current_page) if current_page != "Dashboard" else {},
        charts_json=chart_payload(selected_hospital, current_page),
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8001"))
    app.run(host="0.0.0.0", port=port, debug=False)
