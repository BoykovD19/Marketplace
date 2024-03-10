FROM python:3.10.0
WORKDIR /usr/src/app
RUN pip install -U pip && pip install pipenv
ADD ./marketplace /usr/src/app
COPY Pipfile Pipfile.lock /usr/src/app/
RUN pipenv install --system --deploy
COPY . /usr/src/app
