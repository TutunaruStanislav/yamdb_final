FROM python:3.7-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY api_yamdb/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files (preserve existing files)
RUN python api_yamdb/manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run gunicorn from api_yamdb directory
WORKDIR /app/api_yamdb
CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0.0.0.0:8000"]
