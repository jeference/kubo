FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY pyproject.toml ./
COPY . .
RUN pip install --no-cache-dir .

USER nobody
EXPOSE 8000

# Um processo por contêiner. O `command` do compose escolhe entre web, worker e scheduler.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]
