import streamlit as st
import pyodbc as odbc
from admin import username, password, database, server, connection_string
from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report
import pandas as pd

st.set_page_config(layout="wide")

QUERY1 = """
SELECT TOP 10 *
FROM [dbo].[case_data];
"""

st.title("COVID SCOPE :microscope:")
#st.image("img/home.jpg")

# Establish Database connection
conn = odbc.connect(connection_string)

# Fetch initial data
try:
    cursor = conn.cursor()
    cursor.execute(QUERY1)
    data = pd.DataFrame.from_records(cursor.fetchall(), columns=[column[0] for column in cursor.description])
    st.subheader("Sample Data")
    st.dataframe(data)
except Exception as e:
    st.error(f"Database Connection Error: {e}")

# Selection inputs
col1, col2 = st.columns(2)

with col1:
    select_column = st.multiselect("SELECT :", ['ALL', 'State', 'Age_Group', 'Gender', 'Status', 'Hospitalized',
                                                'Intensive_Care', 'Death', 'Previous_Health_Condition', 'Month'])

with col2:
    select_groupby = st.selectbox("GROUP BY :", ['State', 'Age_Group', 'Gender', 'Status', 'Hospitalized',
                                                 'Intensive_Care', 'Death', 'Previous_Health_Condition', 'Month'])

count = st.checkbox('Count?')
fetch = st.button("Fetch Data")

# Query generation and execution
if fetch:
    with st.spinner("Fetching Data...."):
        try:
            if not select_column:
                st.error("Please select at least one column.")
            else:
                if 'ALL' in select_column:
                    selected_columns_str = '*'
                    groupby_columns_str = None
                else:
                    selected_columns_str = ", ".join(select_column)
                    groupby_columns_str = ", ".join(select_column)

                # Construct the query
                if count:
                    if groupby_columns_str:
                        QUERY = f"""
                        SELECT {selected_columns_str}, COUNT(*) AS record_count
                        FROM [dbo].[case_data]
                        GROUP BY {groupby_columns_str}
                        """
                    else:
                        st.error("GROUP BY is not valid with ALL columns.")
                        QUERY = None
                else:
                    QUERY = f"""
                    SELECT {selected_columns_str}
                    FROM [dbo].[case_data]
                    """
                    st.warning("Executing ungrouped query. Data may be large and slow to load.")

                if QUERY:
                    df = pd.DataFrame.from_records(cursor.execute(QUERY).fetchall(),
                                                   columns=[column[0] for column in cursor.description])
                    pr = ProfileReport(df, title="Report")
                    st_profile_report(pr)
                    st.dataframe(df)

                    st.success("Data Successfully Retrieved")

        except Exception as e:
            st.error(f"Query Execution Error: {e}")

# Custom Query Execution
st.subheader("For Custom Query Execution: Write Your Own SQL Query Below")

input_query = st.text_area(label='Write Your SQL QUERY Here!!!')
run = st.button('Execute Query & Generate Report')

if input_query and run:
    try:
        df = pd.DataFrame.from_records(cursor.execute(input_query).fetchall(),
                                       columns=[column[0] for column in cursor.description])
        st.dataframe(df)
        pr = ProfileReport(df, title="Report")
        st_profile_report(pr)
        st.success("Query Executed Successfully!")
    except Exception as e:
        st.error(f"Error: {e}")
