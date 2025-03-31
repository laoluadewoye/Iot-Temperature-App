FROM python:3.13-alpine

# Set environment variables to avoid interactive prompts during installation
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install dependencies required for psycopg2 and other utilities
RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev build-base python3-dev

# Add a user and give them control over app directory
RUN adduser -D -h /app app
RUN chown -R app:app /app

# Change working directory to app
WORKDIR /app

# Copy the application code into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the current user
USER app

# Command to run the application using Waitress
ENTRYPOINT ["python", "GenApp.py"]
