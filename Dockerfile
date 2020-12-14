FROM python:3-alpine

RUN apk update && apk upgrade && apk add git

WORKDIR /usr/src/app

COPY . .
RUN pip install -r requirements.txt

CMD [ "python", "-u", "./dc.py"]