# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Set the environment variable for Flask
ENV FLASK_APP=app.py
# Optionally set the environment variable to run in production mode
ENV FLASK_ENV=production

# Expose the port your app runs on
EXPOSE 80

# Command to run the Flask app
# If you use something like gunicorn, you can adapt accordingly:
# e.g., RUN pip install gunicorn and CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
