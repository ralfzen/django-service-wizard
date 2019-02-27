FROM python:3.7-alpine

WORKDIR /code

COPY ./requirements/base.txt requirements/base.txt
RUN pip install --upgrade pip && pip install -r requirements/base.txt

ADD . /code

ENTRYPOINT ["python", "/code/setup.py"]
