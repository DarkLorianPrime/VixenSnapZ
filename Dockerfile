FROM python:3.11-buster
COPY ./project /project
WORKDIR /project
RUN pip install -r requirements.txt

CMD ["bash", "run.sh"]
