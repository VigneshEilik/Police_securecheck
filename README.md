# Police_securecheck

# 🚨 Police SecureCheck

**Police SecureCheck** is a data analysis and visualization dashboard built using **Streamlit**, **MySQL**, and **Python (Pandas)** to monitor, analyze, and visualize police traffic stop records and related activities such as searches, arrests, and violations. It is designed to help law enforcement agencies or analysts ensure accountability, improve efficiency, and detect patterns in police stop-and-search behavior.

---

# Dataset

traffic_stops - traffic_stops_with_vehicle_number.csv - uncleaned_data

police_data.csv - cleaned_data


## 📁 Project Structure

Police_SecureCheck/
├── data_cleaning.ipynb # Jupyter notebook for data preprocessing
├── streamlit_app.py # Streamlit dashboard application
├── requirements.txt # List of Python dependencies
├── police_data.csv # Raw dataset (CSV format)
└── README.md # Project documentation
## Create virtual environment

python -m venv env
source env/bin/activate        # On Windows: env\Scripts\activate

## install dependencies

pip install -r requirements.txt

Set Up MySQL Database

## Create a database named Securelogs

Import the cleaned data using the provided .csv or from the Streamlit UI 


Update your MySQL credentials in streamlit_app.py:


engine = create_engine("mysql+mysqlconnector://root:<your_password>@localhost/Securelogs")

## Run the streamlit app

streamlit run streamlit_app.py

## Sample querirs
-- Top 10 vehicles involved in drug-related stops



SELECT vehicle_number, COUNT(*) AS drug_stops
FROM logs
WHERE drugs_related_stop = TRUE
GROUP BY vehicle_number
ORDER BY drug_stops DESC
LIMIT 10;

## 🙋‍♂️ Author
Vignesh

## 📜 License
This project is licensed under the MIT License.
