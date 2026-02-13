FROM python:latest

WORKDIR /usr/local/app

RUN pip install flask

COPY . .

CMD ["python", "main.py"]

