import psutil
import psycopg
from datetime import datetime, date, time
import time

# PostgreSQL database configuration
db_host = 'localhost'
db_port = '5432'
db_name = 'temperature_data'
db_user = 'postgres'
db_password = 'password'

# Connect to the default database
conn = psycopg.connect(
    host=db_host,
    port=db_port,
    user=db_user,
    password=db_password
)

# Create the temperature_data database if it doesn't exist
cursor = conn.cursor()
cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
exists = cursor.fetchone()
if not exists:
    cursor.execute(f"CREATE DATABASE {db_name}")
conn.close()

# Connect to the temperature_data database
conn = psycopg.connect(
    host=db_host,
    port=db_port,
    dbname=db_name,
    user=db_user,
    password=db_password
)

# Create the temperature table if it doesn't exist
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS temperature (
        id SERIAL PRIMARY KEY,
        core_id INTEGER NOT NULL,
        temperature REAL NOT NULL,
        frequency REAL NOT NULL,
        date_value DATE NOT NULL,
        time_value TIME NOT NULL,
        timestamp TIMESTAMP NOT NULL
    );
""")
conn.commit()

# Loop with 1-second interval to retrieve the CPU temperature and frequency per core and insert them into the database
while True:
    # Retrieve the CPU temperature and frequency per core
    core_temps = psutil.sensors_temperatures()['coretemp']
    cpu_freqs = psutil.cpu_freq(percpu=True)

    # Insert the temperature, frequency, date, and timestamp into the database for each core
    cursor = conn.cursor()
    for i, (core_temp, cpu_freq) in enumerate(zip(core_temps, cpu_freqs)):
        temperature = core_temp.current
        frequency = cpu_freq.current
        now = datetime.now()
        date_value = now.date()
        time_value = now.time()
        cursor.execute('INSERT INTO temperature (core_id, temperature, frequency, date_value, time_value, timestamp) VALUES (%s, %s, %s, %s, %s, %s)', (i, temperature, frequency, date_value, time_value, now))
    conn.commit()

    # Wait for 1 second before the next loop
    time.sleep(1)

# Close the database connection
conn.close()
