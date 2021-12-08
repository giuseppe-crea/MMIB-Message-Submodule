FROM python:3-alpine

WORKDIR /code
ADD . /code

COPY requirements.txt /code

ENV DOCKER=yes
ENV TZ=Europe/Rome

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apk add build-base
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /code

EXPOSE 5002

ENTRYPOINT ["python3"]

CMD ["-m", "message_server"]
