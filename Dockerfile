# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application into the container at /app
COPY . .

# Expose the port that Streamlit uses (8501 by default)
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "app.py"]