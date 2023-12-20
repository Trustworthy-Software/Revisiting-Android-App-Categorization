# Use a base image with Python
FROM python:3.9

# Set a working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install apktool 
RUN apt-get update && apt-get install -y apktool

# Install libenchant-dev
RUN apt-get -y install enchant-2

# Install nltk
RUN pip install nltk
RUN python -m nltk.downloader punkt wordnet stopwords averaged_perceptron_tagger words

# Download and install Mallet
RUN wget http://mallet.cs.umass.edu/dist/mallet-2.0.8.tar.gz && \
    tar -xzf mallet-2.0.8.tar.gz && \
    rm mallet-2.0.8.tar.gz && \
    mv mallet-2.0.8 /app/Mallet

# Set permissions 
RUN chmod -R 777 /app/Mallet

# Copy the entire current directory into the container
COPY . /app

# Expose the Jupyter port
EXPOSE 8888

# Set the command to run Jupyter Notebook when the container starts
CMD ["jupyter", "notebook", "--ip='*'", "--port=8888", "--no-browser", "--allow-root"]
