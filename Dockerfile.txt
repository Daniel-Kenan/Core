# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install PostgreSQL client and development files
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install system dependencies for face_recognition (CMake and dlib dependencies)
# RUN apt-get install -y \
#     build-essential \
#     cmake \
#     gfortran \
#     libboost-python-dev \
#     libboost-thread-dev \
#     libopenblas-dev \
#     liblapack-dev \
#     libx11-dev \
#     libgtk-3-dev \
#     libjpeg-dev \
#     libpng-dev \
#     libtiff-dev \
#     libavcodec-dev \
#     libavformat-dev \
#     libswscale-dev \
#     pkg-config \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# RUN apt-get install -y wkhtmltopdf



# Copy the requirements file and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && pip install --upgrade pymongo

# Copy the application code
COPY . .

# Set environment variables
ENV FLASK_APP=server.py  

# Expose the port
EXPOSE 8765 

# Command to run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=8765"]

