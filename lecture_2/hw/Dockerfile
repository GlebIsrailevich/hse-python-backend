FROM python:3.12 AS base

WORKDIR /app

COPY ./shop_api .

RUN python -m pip install --upgrade pip
RUN pip install pdm

COPY ./pyproject.toml ./pdm.lock ./
RUN pdm install

EXPOSE 8080