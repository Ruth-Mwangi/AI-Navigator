# Use an official Python runtime as a parent image
FROM python:3.10.12

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file from your local machine to the working directory in the container
COPY requirements.txt .

# Install the dependencies specified in the requirements file
RUN pip install -r requirements.txt

# Copy the rest of the application code from your local machine to the working directory in the container
COPY src/ .

# Expose the application port (8000 in this case)
EXPOSE 8000

# Define the command to run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]