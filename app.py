import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# User database connection
user_conn = sqlite3.connect('user_data.db', check_same_thread=False)
user_c = user_conn.cursor()

# Lorry repair database connection
lorry_conn = sqlite3.connect('lorry_repair.db', check_same_thread=False)
lorry_c = lorry_conn.cursor()

# Create user table if not exists
def create_user_table():
    user_c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT
        )
    ''')
    user_conn.commit()

# Create lorry repairs table if not exists
def create_lorry_table():
    lorry_c.execute('''
        CREATE TABLE IF NOT EXISTS lorry_repairs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_no TEXT,
            part_name TEXT,
            km_reading INTEGER,
            repair_date TEXT,
            repair_type TEXT
        )
    ''')
    lorry_conn.commit()

# Insert user data into the user database
def insert_user(phone_number):
    user_c.execute('INSERT INTO users (phone_number) VALUES (?)', (phone_number,))
    user_conn.commit()

# Check if the phone number exists in the user database
def validate_user(phone_number):
    user_c.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,))
    return user_c.fetchone()

# Function to insert data into the lorry database
def insert_lorry_data(vehicle_no, part_name, km_reading, repair_date, repair_type):
    lorry_c.execute('''
        INSERT INTO lorry_repairs (vehicle_no, part_name, km_reading, repair_date, repair_type)
        VALUES (?, ?, ?, ?, ?)
    ''', (vehicle_no, part_name, km_reading, repair_date, repair_type))
    lorry_conn.commit()

# Function to upload Excel data
def upload_excel(file):
    df = pd.read_excel(file)
    for _, row in df.iterrows():
        vehicle_no = row['Vehicle Number']
        part_name = row['Part Name']
        km_reading = row['KM Reading']
        repair_date = row['Repair Date']
        repair_type = row['Repair Type']
        insert_lorry_data(vehicle_no, part_name, km_reading, repair_date, repair_type)

# Initialize database
create_user_table()
create_lorry_table()

# Login system
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Login")
    phone_number = st.text_input("Enter your phone number", max_chars=10)
    
    if st.button("Login"):
        # Check phone number length
        if len(phone_number) != 10 or not phone_number.isdigit():
            st.error("Invalid phone number. Please enter a 10-digit number.")
        else:
            # Check if the user is already registered
            if validate_user(phone_number):
                st.session_state.logged_in = True
                st.session_state.phone_number = phone_number
                st.success("Login successful!")
            else:
                # Register the user if not already registered
                insert_user(phone_number)
                st.session_state.logged_in = True
                st.session_state.phone_number = phone_number
                st.success("Login successful! You are now registered.")
else:
    st.sidebar.title(f"Welcome, {st.session_state.phone_number}")
    
    # Navigation after login
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Add Data One by One", "Upload Excel File", "Search Vehicle History"])

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
                insert_lorry_data(vehicle_no, part_name, km_reading, repair_date.strftime('%Y-%m-%d'), repair_type)
                st.success(f"Data added for Vehicle {vehicle_no} - {part_name} ({repair_type})")
    
    elif page == "Upload Excel File":
        st.title("Upload Repair Data from Excel")
        uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])
        if uploaded_file:
            upload_excel(uploaded_file)
            st.success("Data uploaded successfully!")
    
    elif page == "Search Vehicle History":
        st.title("Search Vehicle History")
        search_vehicle = st.text_input("Enter Vehicle Number to Search")
        if st.button("Search"):
            lorry_c.execute('SELECT * FROM lorry_repairs WHERE vehicle_no = ?', (search_vehicle,))
            history = lorry_c.fetchall()
            if history:
                st.write(f"Repair history for vehicle: {search_vehicle}")
                for record in history:
                    st.write(f"Part: {record[2]}, KM: {record[3]}, Date: {record[4]}, Type: {record[5]}")
            else:
                st.write(f"No records found for vehicle: {search_vehicle}")

# Close connections
user_conn.close()
lorry_conn.close()
