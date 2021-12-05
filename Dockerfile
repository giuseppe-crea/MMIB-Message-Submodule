FROM python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

ENV DOCKER=yes
ENV TZ=Europe/Rome

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apk add build-base
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

# EXPOSE 5007

CMD ["python3", "-m", "message_server"]
