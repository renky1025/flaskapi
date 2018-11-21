FROM ubuntu:latest
MAINTAINER Kangyao Ren "renky_1025@hotmail.com"
RUN apt-get update -y
RUN apt-get install -y python3 python3-dev python3-pip libmysqlclient-dev
#nginx
#RUN pip3 install uwsgi
#RUN pip3 install mysqlclient
RUN mkdir -p /mnt/services
COPY . /mnt/services/app
WORKDIR /mnt/services/app
#RUN mkdir -p ./static/images/
RUN pip3 install -r requirements.txt
EXPOSE 8080
ENTRYPOINT ["python3"]
CMD ["./app/mongoapp.py"]