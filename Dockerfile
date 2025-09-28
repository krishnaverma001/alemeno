FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y postgresql-client
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy application and data
COPY . /app/
COPY data/ /app/data/

# Make startup script executable
RUN chmod +x /app/scripts/docker-start.sh

EXPOSE 8000
CMD ["/api/scripts/docker-start.sh"]