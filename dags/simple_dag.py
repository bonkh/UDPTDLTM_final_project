from datetime import datetime, timedelta, timezone
from airflow import DAG
from airflow.operators.python import PythonOperator

# Function to write "Hello World" with timestamp to a file
def write_hello_world():
    # Generate a timestamped filename
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    file_path = f'hello_world_{timestamp}.txt'
    
    # Write the message with current UTC date and time
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path, 'w') as f:
        f.write(f"Hello World! Current UTC Date and Time: {now}\n")

# Define default arguments for the DAG
default_args = {
    'owner': 'your_name',
    'retries': 1,
}

# Calculate the start date in UTC
start_date_utc = datetime.now(timezone.utc) - timedelta(hours=7)

# Define the DAG
with DAG(
    'hello_world_dag',
    default_args=default_args,
    description='A simple DAG that writes Hello World every 5 minutes with timestamped filenames',
    schedule_interval='*/5 * * * *',  # Every 5 minutes
    start_date=start_date_utc,
    catchup=False
) as dag:

    # Define the task
    write_task = PythonOperator(
        task_id='write_hello_world',
        python_callable=write_hello_world
    )

    write_task
