import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
from datetime import datetime

# Database Connection 
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Vicky@143',
            database='securelogs'
        )
        return connection
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

def fetch_data(query):
    connection = create_connection()
    if connection:
        # st.write("Hello everyone")
        try:
                cursor = connection.cursor()
                cursor.execute(query)
                result = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(result, columns = columns)
                return df
        except :
            print("error")
    else:
        return pd.DataFrame()

# Streamlit UI
st.set_page_config(page_title="SecureCheck Police Dashboard", layout="wide")

st.title("🚔 SecureCheck: Police Check Post Digital Ledger")
st.markdown("**Real-time monitoring and insights for law enforcement 🛡️**")

# Show full table 
st.header("📋 Police Logs Overview")
query = "SELECT * FROM ledger"
data = fetch_data(query)
st.dataframe(data, use_container_width=True)


# Quick Metrics
st.header("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_stops = data.shape[0]
    st.metric("Total Police Stops", total_stops)
    # st.write(data.columns)

with col2:
    arrests = data[data['stop_outcome'].str.contains("arrest", case=False, na=False)].shape[0]
    st.metric("Total Arrests", arrests)

with col3:
    warnings = data[data['stop_outcome'].str.contains("warning", case=False, na=False)].shape[0]
    st.metric("Total Warnings", warnings)

with col4:
    drug_related = data[data['drugs_related_stop'] == 1].shape[0]
    st.metric("Drug Related Stops", drug_related)

# --- Charts ---
st.header("📈 Visual Insights")
tab1, tab2 = st.tabs(["Stops by Violation", "Driver Gender Distribution"])

with tab1:
    if not data.empty and 'violation' in data.columns:
        violation_data = data['violation'].value_counts().reset_index()
        violation_data.columns = ['Violation', 'Count']
        fig = px.bar(violation_data, x='Violation', y='Count', title='Stops by Violation Type', color='Violation')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for Violation chart.")

with tab2:
    if not data.empty and 'driver_gender' in data.columns:
        gender_data = data['driver_gender'].value_counts().reset_index()
        gender_data.columns = ['Gender', 'Count']
        fig = px.pie(gender_data, names='Gender', values='Count', title='Driver Gender Distribution')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for Driver Gender chart.")


# --- Advanced Queries ---
st.header("🧠 Advanced Insights")

selected_query = st.selectbox("Select a Query to Run", [
    "Top 10 vehicle numbers involved in drug-related stops",
    "Vehicle most frequantly searched",
    "Which driver age group had the highest arrest rate?",
    "What is the gender distribution of drivers stopped in each country?",
    "Which race and gender combination has the highest search rate?",
    "What time of day sees the most traffic stops?",
    "What is the average stop duration for different violations?",
    "Are stops during the night more likely to lead to arrests?",
    "Which violations are most associated with searches or arrests?",
    "Which violations are most common among younger drivers (<25)?",
    "Is there a violation that rarely results in search or arrest?",
    "Which countries report the highest rate of drug-related stops?",
    "What is the arrest rate by country and violation?",
    "Which country has the most stops with search conducted?",
    "Yearly Breakdown of Stops and Arrests by Country",
    "Driver Violation Trends Based on Age and Race",
    "Time Period Analysis of Stops (Year, Month, Hour)",
    "Violations with High Search and Arrest Rates",
    "Driver Demographics by Country (Age, Gender, and Race)",
    "Top 5 Violations with Highest Arrest Rates"
])

query_map = {
    "Top 10 vehicle numbers involved in drug-related stops":"SELECT vehicle_number, COUNT(*) AS drug_related_stops FROM ledger WHERE drugs_related_stop = TRUE GROUP BY vehicle_number ORDER BY drug_related_stops DESC LIMIT 10;",
    "Vehicle most frequantly searched":"SELECT vehicle_number, COUNT(*) AS search_count FROM ledger WHERE search_conducted = TRUE GROUP BY vehicle_number ORDER BY search_count DESC;",
    "Which driver age group had the highest arrest rate?":"SELECT driver_age, COUNT(*) AS arrest_count FROM ledger WHERE is_arrested = TRUE GROUP BY driver_age ORDER BY arrest_count DESC;",
    "What is the gender distribution of drivers stopped in each country?":"SELECT country_name, driver_gender, COUNT(*) AS total_stops FROM ledger GROUP BY country_name, driver_gender;",
    "Which race and gender combination has the highest search rate?":"SELECT driver_race, driver_gender,  COUNT(*) AS total_stops, SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS searches, ROUND(SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS search_rate FROM ledger GROUP BY driver_race, driver_gender ORDER BY search_rate DESC;",
    "What time of day sees the most traffic stops?":"SELECT HOUR(STR_TO_DATE(stop_time, '%H:%i:%s')) AS hour_of_day, COUNT(*) AS stop_count FROM ledger GROUP BY hour_of_day ORDER BY stop_count DESC;",
    "What is the average stop duration for different violations?":"SELECT violation, AVG(CASE stop_duration WHEN '0-15 Min' THEN 15 WHEN '16-30 Min' THEN 30 WHEN '30+ Min' THEN 45 END) AS avg_duration_minutes FROM ledger GROUP BY violation;",
    "Are stops during the night more likely to lead to arrests?":"SELECT CASE WHEN HOUR(STR_TO_DATE(stop_time, '%H:%i:%s')) BETWEEN 20 AND 23 OR HOUR(STR_TO_DATE(stop_time, '%H:%i:%s')) BETWEEN 0 AND 5 THEN 'Night' ELSE 'Day' END AS time_period, COUNT(*) AS total_stops, SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrests, ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate FROM ledger GROUP BY time_period;",
    "Which violations are most associated with searches or arrests?":"SELECT violation, COUNT(*) AS total_stops, SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS total_searches, SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests FROM ledger GROUP BY violation ORDER BY total_searches DESC, total_arrests DESC;",
    "Which violations are most common among younger drivers (<25)?":"SELECT violation, COUNT(*) AS count FROM ledger WHERE driver_age < 25 GROUP BY violation ORDER BY count DESC;",
    "Is there a violation that rarely results in search or arrest?":"SELECT violation, COUNT(*) AS total, SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS searches, SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrests FROM ledger GROUP BY violation HAVING searches = 0 AND arrests = 0;",
    "Which countries report the highest rate of drug-related stops?":"SELECT country_name, COUNT(*) AS total_stops, SUM(CASE WHEN drugs_related_stop = TRUE THEN 1 ELSE 0 END) AS drug_related, ROUND(SUM(CASE WHEN drugs_related_stop = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS drug_rate FROM ledger GROUP BY country_name ORDER BY drug_rate DESC;",
    "What is the arrest rate by country and violation?":"SELECT country_name, violation, COUNT(*) AS total, SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrests, ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate FROM ledger GROUP BY country_name, violation;",
    "Which country has the most stops with search conducted?":"SELECT country_name, COUNT(*) AS search_stops FROM ledger WHERE search_conducted = TRUE GROUP BY country_name ORDER BY search_stops DESC;",
    "Yearly Breakdown of Stops and Arrests by Country":"SELECT country_name, YEAR(STR_TO_DATE(stop_date, '%Y-%m-%d')) AS year, COUNT(*) AS total_stops, SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrests, RANK() OVER (PARTITION BY country_name ORDER BY YEAR(STR_TO_DATE(stop_date, '%Y-%m-%d'))) AS year_rank FROM ledger GROUP BY country_name, year;",
    "Driver Violation Trends Based on Age and Race":"SELECT driver_age, driver_race, violation, COUNT(*) AS total FROM ( SELECT driver_age, driver_race, violation FROM ledger WHERE driver_age IS NOT NULL AND driver_race IS NOT NULL) AS sub GROUP BY driver_age, driver_race, violation ORDER BY total DESC;",
    "Time Period Analysis of Stops (Year, Month, Hour)":"SELECT YEAR(STR_TO_DATE(stop_date, '%Y-%m-%d')) AS year, MONTH(STR_TO_DATE(stop_date, '%Y-%m-%d')) AS month, HOUR(STR_TO_DATE(stop_time, '%H:%i:%s')) AS hour, COUNT(*) AS stop_count FROM ledger GROUP BY year, month, hour ORDER BY year, month, hour;",
    "Violations with High Search and Arrest Rates":"SELECT violation, COUNT(*) AS total, SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS searches, SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrests, RANK() OVER (ORDER BY SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) DESC) AS search_rank, RANK() OVER (ORDER BY SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) DESC) AS arrest_rank FROM ledger GROUP BY violation;",
    "Driver Demographics by Country (Age, Gender, and Race)":"SELECT country_name, driver_age, driver_gender, driver_race, COUNT(*) AS count FROM ledger GROUP BY country_name, driver_age, driver_gender, driver_race;",
    "Top 5 Violations with Highest Arrest Rates":"SELECT violation, COUNT(*) AS total, SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrests, ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate FROM ledger GROUP BY violation ORDER BY arrest_rate DESC LIMIT 5;"
}

if st.button("Run"):
    # st.write(query_map[selected_query])
    result = fetch_data(query_map[selected_query])
    if result is not None and not result.empty:
        st.write(result)
    else:
        st.warning("No results found for the selected query.")

st.markdown("---")
st.markdown("Built with ❤️ for Law Enforcement by SecureCheck™")
st.header("🧠 Custom Natural Language Filter")

# --- Input Form ---
st.header("📝 Add New Police Log & Predict Outcome and Violation")

with st.form("new_log_form"):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    county_name = st.selectbox("County Name", ["canada", "usa", "india"])
    driver_gender = st.selectbox("Driver Gender", ["male", "female"])
    driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27)
    driver_race = st.selectbox("Driver Race", ["White", "Black", "Hispanic", "Asian", "Other"])
    search_conducted = st.selectbox("Was a Search Conducted?", ["0", "1"])
    search_type = st.text_input("Search Type")
    drugs_related_stop = st.selectbox("Was it Drug Related?", ["0", "1"])
    stop_duration = st.selectbox("Stop Duration", data['stop_duration'].dropna().unique())
    vehicle_number = st.text_input("Vehicle Number")

    submitted = st.form_submit_button("Predict Stop Outcome & Violation")

# --- Prediction Logic (Simplified for Demo) ---
if submitted:
    filtered_data = data[
    (data['driver_gender'] == driver_gender) &
    (data['driver_age'] == driver_age) &
    (data['search_conducted'] == int(search_conducted)) &
    (data['stop_duration'] == stop_duration) &
    (data['drugs_related_stop'] == int(drugs_related_stop))
]

    if not filtered_data.empty:
        predicted_outcome = filtered_data['stop_outcome'].mode()[0]
        predicted_violation = filtered_data['violation'].mode()[0]
    else:
        predicted_outcome = "warning"
        predicted_violation = "speeding"

    # Natural Language Summary
    search_text = "a search was conducted" if int(search_conducted) else "no search was conducted"
    drug_text = "was drug-related" if int(drugs_related_stop) else "was not drug-related"


    st.markdown("### 🧾 Prediction Summary")
    st.write(f"**Predicted Violation:** {predicted_violation}")
    st.write(f"**Predicted Stop Outcome:** {predicted_outcome}")
    st.markdown(
        f"A {driver_age}-year-old {driver_gender} driver in {county_name} was stopped at "
        f"{stop_time.strftime('%I:%M %p')} on {stop_date}. "
        f"{search_text}, and the stop {drug_text}.  \n"
        f"**Stop Duration:** {stop_duration}  \n"
        f"**Vehicle Number:** {vehicle_number}"
    )
