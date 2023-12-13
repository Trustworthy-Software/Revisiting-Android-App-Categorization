# Use a base image with Python
FROM python:3.9

# Set a working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire current directory into the container
COPY . /app

# Expose the Jupyter port
EXPOSE 8888

# Set the command to run Jupyter Notebook when the container starts
CMD ["jupyter", "notebook", "--ip='*'", "--port=8888", "--no-browser", "--allow-root"]
