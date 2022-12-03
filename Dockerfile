FROM joyzoursky/python-chromedriver:3.9-alpine

WORKDIR /app

ADD . .
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
