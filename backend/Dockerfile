FROM python:3.7-slim
COPY ./ /app
RUN pip install --upgrade pip && pip install -r /app/requirements.txt --no-cache-dir
WORKDIR /app/
# CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
CMD ["python", "manage.py", "runserver", "0:8000"]