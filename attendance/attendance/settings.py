import json
import os
from collections import defaultdict

import matplotlib.pyplot as plt
import mysql.connector
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime


def get_db_config():
    missing = [
        name for name in ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME")
        if not os.getenv(name)
    ]
    if missing:
        raise RuntimeError(
            "Missing database environment variables: "
            + ", ".join(missing)
            + ". Copy .env.example to .env and configure the values."
        )

    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "port": int(os.getenv("DB_PORT", "3306")),
    }


class Database:
    def __init__(self):
        config = get_db_config()
        self.host = config["host"]
        self.user = config["user"]
        self.password = config["password"]
        self.database = config["database"]
        try:
            self.connection = mysql.connector.connect(**config)
            self.cursor = self.connection.cursor(buffered=True)
            print("Connected to database")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            print(self.connection)

    def Connection(self):
        return self.connection


def count_employees(data):
    attendance_count = {}
    for date, records in data.items():
        attendance_count[date] = len(records)
    return attendance_count


def AnalysisResult():
    db = Database()
    connection = db.Connection()
    cursor = connection.cursor(buffered=True)
    print("Connected to database")

    query = "select * from attendance_table"
    cursor.execute(query)
    result = cursor.fetchall()

    if len(result) > 0:
        attendance_count = defaultdict(int)
        per_day_emp_attendance = {}
        per_date_emp_attendance = {}
        for rows in result:
            emp_data = json.loads(rows[3])

            for date, details in emp_data.items():
                if details["InTime"]:
                    attendance_count[date] = attendance_count[date] + 1
                    if len(details["InTime"]) >= 1:
                        intime = details["InTime"][0]
                        NumberOfTime = len(details["InTime"])
                    else:
                        intime = None
                        NumberOfTime = None

                    if len(details["OutTime"]) >= 1:
                        outime = details["OutTime"][0]
                    else:
                        outime = None

                    json_temp = {"InTime": intime, "NumberOfTime": NumberOfTime, "OutTime": outime}
                    json_temp = json.dumps(json_temp)
                else:
                    json_temp = {"InTime": None, "NumberOfTime": None, "OutTime": None}
                    json_temp = json.dumps(json_temp)

                if str(rows[1]) not in per_day_emp_attendance.keys():
                    per_day_emp_attendance[str(rows[1])] = {}

                per_day_emp_attendance[str(rows[1])][date] = json_temp

            emp_data = json.loads(rows[3])

            for date, details in emp_data.items():
                if details["InTime"]:
                    if len(details["InTime"]) >= 1:
                        intime = details["InTime"][0]
                        NumberOfTime = len(details["InTime"])
                    else:
                        intime = None
                        NumberOfTime = None

                    if len(details["OutTime"]) >= 1:
                        outime = details["OutTime"][0]
                    else:
                        outime = None
                else:
                    intime = None
                    NumberOfTime = None
                    outime = None

                if str(rows[1]) not in per_date_emp_attendance.keys():
                    per_date_emp_attendance[str(rows[1])] = {}
                per_date_emp_attendance[str(rows[1])][date] = {
                    "InTime": intime,
                    "NumberOfTime": NumberOfTime,
                    "OutTime": outime,
                }
