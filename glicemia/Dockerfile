FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libncurses5-dev \
    libnss3-dev \
    libsqlite3-dev \
    libreadline-dev \
    libffi-dev \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Descargar Python 3.12
RUN wget https://www.python.org/ftp/python/3.12.3/Python-3.12.3.tgz \
    && tar -xvf Python-3.12.3.tgz

WORKDIR /app/Python-3.12.3

RUN ./configure --enable-optimizations \
    && make -j 4 \
    && make altinstall

WORKDIR /app

COPY requirements.txt .

RUN python3.12 -m ensurepip
RUN python3.12 -m pip install --upgrade pip
RUN python3.12 -m pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python3.12", "manage.py", "runserver", "0.0.0.0:8000"]