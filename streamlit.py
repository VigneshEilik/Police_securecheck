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
query = "SELECT * FROM logs"
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
    "Time of day with most traffic stops",
    "Gender distribution of drivers stopped in each country",
    "Average stop duration for different violations",
    "Most common violations among young drivers (<25)",
    "Countries with highest rate of drug-related stops",
    "Country with most stops where search was conducted",
    "Time period analysis of stops",
    "Top 5 violation with highest arrest rate",
    "Violations with High Search and Arrest Rates",
    "Yearly Breakdown of Stops and Arrests by Country",
    "Arrest rate by country and violation",
    "Violation rarely resulting in search or arrest",
    "Driver demographics by country",
    "Number of stops by year, month, hour of day",
    "Violation trends by age & race",
    "Yearly breakdown of stops and arrests by country",
    "Are stops during night more likely to lead to arrests",
    "Race & gender combo with highest search rate"
])

query_map = {
  "Top 10 vehicle numbers involved in drug-related stops": "SELECT vehicle_number, COUNT(*) AS drug_related_stops FROM logs WHERE drugs_related_stop = TRUE GROUP BY vehicle_number ORDER BY drug_related_stops DESC LIMIT 10;",
  "Vehicle most frequantly searched": "SELECT vehicle_number, COUNT(*) AS search_count FROM logs WHERE search_conducted = TRUE GROUP BY vehicle_number ORDER BY search_count DESC LIMIT 10;",
  "Time of day with most traffic stops": "SELECT HOUR(TIME(stop_time)) AS stop_hour, COUNT(*) AS stop_count FROM traffic_data GROUP BY stop_hour ORDER BY stop_count DESC;",
  "Gender distribution of drivers stopped in each country": "SELECT country_name, driver_gender, COUNT(*) AS stop_count FROM logs GROUP BY country_name, driver_gender ORDER BY country_name, stop_count DESC;",
  "Average stop duration for different violations": "SELECT violation, AVG( CASE stop_duration WHEN '0-15 Min' THEN 10 WHEN '16-30 Min' THEN 23 WHEN '30+ Min' THEN 40 ELSE 0 END ) AS avg_duration_minutes FROM logs GROUP BY violation ORDER BY avg_duration_minutes DESC;",
  "Most common violations among young drivers (<25)": "SELECT violation, COUNT(*) AS count FROM logs WHERE driver_age < 25 GROUP BY violation ORDER BY count DESC;",
  "Countries with highest rate of drug-related stops": "SELECT country_name, ROUND(SUM(CASE WHEN drugs_related_stop THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS drug_stop_rate FROM logs GROUP BY country_name ORDER BY drug_stop_rate DESC;",
  "Country with most stops where search was conducted": "SELECT country_name, COUNT(*) AS search_count FROM logs WHERE search_conducted = TRUE GROUP BY country_name ORDER BY search_count DESC LIMIT 1;",
  "Time period analysis of stops": "SELECT YEAR(DATE(stop_date)) AS year, MONTH(DATE(stop_date)) AS month, HOUR(TIME(stop_time)) AS hour, COUNT(*) AS stop_count FROM traffic_data GROUP BY year, month, hour ORDER BY stop_count DESC;",
  "Top 5 violation with highest arrest rate": "SELECT violation, COUNT(*) AS total, SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS arrests, ROUND(SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate FROM logs GROUP BY violation ORDER BY arrest_rate DESC LIMIT 5;",
  "Violations with High Search and Arrest Rates": "SELECT violation, COUNT(*) AS total_stops, SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) AS total_searches, SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS total_arrests, ROUND(SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS search_rate, ROUND(SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate, RANK() OVER (ORDER BY SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) * 1.0 / COUNT(*) DESC) AS arrest_rank FROM logs GROUP BY violation;",
  "Yearly Breakdown of Stops and Arrests by Country": "SELECT DISTINCT stop_year, country_name,  COUNT(*) OVER (PARTITION BY stop_year, country_name) AS total_stops, SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) OVER (PARTITION BY stop_year, country_name) AS total_arrests FROM ( SELECT *, YEAR(DATE(stop_date)) AS stop_year FROM traffic_data) AS sub;",
  "Arrest rate by country and violation": "SELECT country_name, violation, ROUND(SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate FROM logs GROUP BY country_name, violation ORDER BY arrest_rate DESC;",
  "Violation rarely resulting in search or arrest": "SELECT violation, ROUND(SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS search_rate, ROUND(SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate FROM logs GROUP BY violation;",
  "Driver demographics by country": "SELECT country_name, AVG(driver_age) AS avg_age, COUNT(DISTINCT driver_gender) AS gender_variety, COUNT(DISTINCT driver_race) AS race_variety FROM logs GROUP BY country_name;",
  "Number of stops by year, month, hour of day": "SELECT YEAR(DATE(stop_date)) AS year, MONTH(DATE(stop_date)) AS month, HOUR(TIME(stop_time)) AS hour, COUNT(*) AS stop_count FROM logs GROUP BY year, month, hour ORDER BY stop_count DESC;",
  "Violation trends by age & race": "SELECT t.driver_age, t.driver_race, t.violation, COUNT(*) AS count FROM logs t JOIN (SELECT driver_age, driver_race FROM logs WHERE driver_age BETWEEN 18 AND 40 GROUP BY driver_age, driver_race) AS demo ON t.driver_age = demo.driver_age AND t.driver_race = demo.driver_race GROUP BY t.driver_age, t.driver_race, t.violation ORDER BY count DESC;",
  "Yearly breakdown of stops and arrests by country": "SELECT DISTINCT stop_year, country_name, COUNT(*) OVER (PARTITION BY stop_year, country_name) AS total_stops, SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) OVER (PARTITION BY stop_year, country_name) AS total_arrests FROM (SELECT *, YEAR(DATE(stop_date)) AS stop_year FROM logs) AS sub;",
  "Are stops during night more likely to lead to arrests": "SELECT CASE WHEN HOUR(TIME(stop_time)) BETWEEN 6 AND 18 THEN 'Day' ELSE 'Night' END AS time_period, ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS arrest_rate FROM logs GROUP BY time_period;",
  "Race & gender combo with highest search rate": "SELECT driver_race, driver_gender, ROUND(SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS search_rate FROM logs GROUP BY driver_race, driver_gender ORDER BY search_rate DESC LIMIT 1;"

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
    timestamp = datetime.now()

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
