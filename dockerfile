FROM python:3.9

#instalar un cliente ssh
RUN apt-get update && apt-get install -y openssh-cliente

# la salida se escribe en la consola de forma inmediata
ENV PYTHONUNBUFFERED 1

#crea directorio app
WORKDIR /app

#copiar lo requirements
COPY requirements.txt /app/requirements.txt

#instalar requirements
RUN pip install -r requirements.txt

#copiar la aplicaion de trabajo en el directorio
COPY . /app

#arrancar django el ssh 
CMD python manage.py runserver 0.0.0.0:8000