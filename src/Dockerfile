# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas-base-dev \
    libffi-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements.txt file from the host to the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
# Install required Python libraries
RUN pip install \
    fastapi \
    uvicorn \
    pandas \
    numpy==1.21.6 \
    scikit-learn==1.0.2 \
    scikit-surprise \
    joblib \
    gdown

# Copy the rest of the application code into the container
COPY . /app

# Run the application when the container starts
CMD ["python", "train.py"]
