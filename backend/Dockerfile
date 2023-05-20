FROM python:3.11-slim-buster

RUN pip install poetry
COPY app /application
WORKDIR /application
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]
