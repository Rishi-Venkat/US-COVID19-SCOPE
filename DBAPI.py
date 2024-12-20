import pypyodbc as odbc
import pandas as pd
from admin import username, password, database, server, connection_string

QUERY = ""

QUERY1 = """
SELECT State, COUNT(*) AS death_count
FROM [dbo].[case_data]
WHERE Death = 'Yes'
GROUP BY State
ORDER BY death_count DESC;
"""

def request(conn,QUERY = QUERY1):

    cursor = conn.cursor()
    cursor.execute(QUERY)

    dataset = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    data = pd.DataFrame(data= dataset, columns= columns)

    return data