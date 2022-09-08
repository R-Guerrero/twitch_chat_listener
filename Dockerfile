# Pulling the base image.
FROM python:3.10-slim

# This instructs Python to run in UNBUFFERED mode, which is recommended when
# using Python inside a Docker container. The reason for this is that it does
# not allow Python to buffer outputs; instead, it prints output directly,avoiding
# some complications in the docker image when running your Python application.
ENV PYTHONUNBUFFERED 1

# Creating a folder and moving into it.
WORKDIR /usr/app/src

# Copying the dependency list into Docker the container.
COPY requirements.txt ./

# Copying the python script into the Docker container.
COPY  tcl_main.py tcl_consumer.py ./

# Copying the packages folder into the Docker container.
COPY  packages ./packages

# Create the output folder into the Docker container.
RUN mkdir output

# Copying the Kibana dashboard template into the Docker container.
COPY  kibana_dashboards ./

# Upgrade the Python package manager.
RUN pip install --upgrade pip

# Installing the required Python dependencies for the application.
RUN pip install --no-cache-dir -r requirements.txt