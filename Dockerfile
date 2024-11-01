# Use the official Airflow image as the base
FROM apache/airflow:2.10.2

# Set the working directory
WORKDIR /opt/airflow

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt
