FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD python manage.py migrate && \
    python manage.py loaddata fixtures/pharmacy_fixtures_final.json && \
    python manage.py collectstatic --noinput && \
    gunicorn PharmacyApp.wsgi:application --bind 0.0.0.0:$PORT