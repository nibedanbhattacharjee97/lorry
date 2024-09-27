import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Database connection
conn = sqlite3.connect('lorry_repair.db', check_same_thread=False)
c = conn.cursor()

# Create table if it doesn't exist
def create_table():
    c.execute('''
        CREATE TABLE IF NOT EXISTS lorry_repairs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_no TEXT,
            part_name TEXT,
            km_reading INTEGER,
            repair_date TEXT,
            repair_type TEXT
        )
    ''')
    conn.commit()

# Function to insert data into the table
def insert_data(vehicle_no, part_name, km_reading, repair_date, repair_type):
    c.execute('''
        INSERT INTO lorry_repairs (vehicle_no, part_name, km_reading, repair_date, repair_type)
        VALUES (?, ?, ?, ?, ?)
    ''', (vehicle_no, part_name, km_reading, repair_date, repair_type))
    conn.commit()

# Function to display repair history
def display_history(vehicle_no):
    c.execute('SELECT * FROM lorry_repairs WHERE vehicle_no = ?', (vehicle_no,))
    data = c.fetchall()
    return data

# Function to upload Excel data
def upload_excel(file):
    df = pd.read_excel(file)
    for _, row in df.iterrows():
        # Extract data from Excel
        vehicle_no = row['Vehicle Number']
        part_name = row['Part Name']
        km_reading = row['KM Reading']
        repair_date = row['Repair Date']
        repair_type = row['Repair Type']
        
        # Insert into the database
        insert_data(vehicle_no, part_name, km_reading, repair_date, repair_type)

# Create the database table
create_table()

# Streamlit sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Add Data One by One", "Upload Excel File", "Search Vehicle History"])

# Page for manually adding data
if page == "Add Data One by One":
    st.title("Add Repair Data Manually")

    with st.form("repair_form"):
        vehicle_no = st.text_input("Vehicle Number")
        part_name = st.selectbox("Part", ["Air Filter", "Diesel Filter", "Gearbox", "Hub", "King Pin", "Adblue Filter", "Others"])
        km_reading = st.number_input("Kilometer Reading", min_value=0, step=1)
        repair_date = st.date_input("Repair/Change Date", datetime.now())
        repair_type = st.selectbox("Repair Type", ["Repair", "Replacement"])
        
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            insert_data(vehicle_no, part_name, km_reading, repair_date.strftime('%Y-%m-%d'), repair_type)
            st.success(f"Data added for Vehicle {vehicle_no} - {part_name} ({repair_type})")

# Page for uploading Excel file
elif page == "Upload Excel File":
    st.title("Upload Repair Data from Excel")
    
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])
    
    if uploaded_file:
        upload_excel(uploaded_file)
        st.success("Data uploaded successfully!")

# Search and display repair history in sidebar
elif page == "Search Vehicle History":
    st.sidebar.title("Search Vehicle History")
    search_vehicle = st.sidebar.text_input("Enter Vehicle Number to Search")

    if st.sidebar.button("Search"):
        history = display_history(search_vehicle)
        if history:
            st.write(f"Repair history for vehicle: {search_vehicle}")
            for record in history:
                st.write(f"Part: {record[2]}, KM: {record[3]}, Date: {record[4]}, Type: {record[5]}")
        else:
            st.write(f"No records found for vehicle: {search_vehicle}")

# Close database connection
conn.close()
