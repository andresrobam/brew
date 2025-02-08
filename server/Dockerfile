FROM python:3.13.2-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY *.py .
RUN mkdir config

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000", "-w", "1"]