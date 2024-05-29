# Use the official Python image as the base image
FROM python:3.10-slim AS base

# Set environment variable to prevent Python from writing .pyc files
ENV PYTHONUNBUFFERED 1

# Set up a virtual environment to cache dependencies
RUN python -m venv /opt/venv

# Ensure the virtualenv is activated when running any command
ENV PATH="/opt/venv/bin:$PATH"

# Set the working directory to /databot
WORKDIR /databot

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the dependencies in the virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# Install Terraform
RUN apt-get update && \
    apt-get install -y wget && \
    wget https://releases.hashicorp.com/terraform/1.1.0/terraform_1.1.0_linux_amd64.zip && \
    unzip terraform_1.1.0_linux_amd64.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform_1.1.0_linux_amd64.zip

# Use the official Python image as the base image for the final build
FROM python:3.10-slim

# Ensure the virtualenv is activated when running any command
ENV PATH="/opt/venv/bin:$PATH"

# Copy the virtual environment from the base image
COPY --from=base /opt/venv /opt/venv

# Set the working directory to /databot
WORKDIR /databot

# Copy the src and terraform directories to /databot
COPY src /databot/src
COPY terraform /databot/terraform

# Expose the port the app runs on
EXPOSE 8000

# Set the PYTHONPATH environment variable
ENV PYTHONPATH /databot/src/app:/databot/terraform

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
