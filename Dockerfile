#FROM python:3-alpine
FROM python:3.8-slim

LABEL org.opencontainers.image.source https://github.com/SENERGY-Platform/mgw-smart-meter-dc

#RUN apk --no-cache add git
RUN apt-get update && apt-get install -y git

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "-u", "./dc.py"]