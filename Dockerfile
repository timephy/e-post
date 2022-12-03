FROM python:3.10.8-alpine

WORKDIR /app

ADD . .
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
