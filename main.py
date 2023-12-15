import datetime
import os

import psycopg2
from fastapi import FastAPI, Depends
from pydantic import BaseModel

app = FastAPI()


class Input(BaseModel):
    org_name: str
    start: datetime.datetime
    end: datetime.datetime


db_host = os.environ["PG_HOST"]
db_port = os.environ["PG_PORT"]
db_name = os.environ["PG_DB"]
db_user = os.environ["PG_USER"]
db_password = os.environ["PG_PASSWORD"]


class Response(BaseModel):
    datetime: datetime.datetime
    org_name: str
    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    packets_count: int
    bytes_count: int


@app.get("/api/v1/{table_name}")
def data(table_name: str, input_form: Input = Depends()):
    connection = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Assuming 'data' table has the same structure as the Response model
    query = f"SELECT datetime, org_name, src_ip, src_port, dst_ip, dst_port, packets_count, bytes_count FROM {table_name} WHERE org_name = %s AND datetime >= %s AND datetime <= %s"

    # Execute the query with parameters
    cursor.execute(query, (input_form.org_name, input_form.start, input_form.end))

    # Fetch all the results
    rows = cursor.fetchall()

    # Close the database connection
    cursor.close()
    connection.close()

    # Convert the result to a list of dictionaries
    result = [dict(zip([desc[0] for desc in cursor.description], row)) for row in rows]

    # Return the result
    return result
