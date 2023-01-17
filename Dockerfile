FROM python:3.10

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

# Creating working directory
RUN mkdir /app
WORKDIR /app

# Set timezone
RUN echo "Asia/Dhaka" > /etc/timezone

# Install project dependencies
COPY ./requirements.txt ./

RUN apt-get update \
    && apt-get install build-essential tzdata -y \
    && apt-get install gdal-bin libgdal-dev -y \
    && apt-get install python3-gdal -y \
    && apt-get install postgis -y \
    && python3 -m pip install --upgrade pip\
    && python3 -m pip install -r requirements.txt gunicorn uvicorn\
    && apt-get remove build-essential -y \
    && apt-get autoremove -y

# Copy project files
COPY . .

EXPOSE $PORT
CMD python manage.py migrate; python manage.py collectstatic --noinput; gunicorn amarshohor_backend.asgi:application -w 1 -k uvicorn.workers.UvicornH11Worker -b [::]:$PORT
