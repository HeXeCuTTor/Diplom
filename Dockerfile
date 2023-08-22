FROM python:3.8

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt 

COPY . .

CMD [ "python", "./manage.py", "runserver", "127.0.0.1:8000"]