FROM tiangolo/uvicorn-gunicorn-fastapi:python3.6

ADD requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

ADD src /src

WORKDIR /src

CMD ["uvicorn", "--host",  "0.0.0.0", "app:api"]