FROM python:3.8

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt 

COPY . .

EXPOSE 8000

CMD [ "python", "./manage.py", "runserver", "127.0.0.1:8000"]