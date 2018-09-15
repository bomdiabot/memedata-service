FROM ubuntu:latest

RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev locales

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app
#db dirs
RUN mkdir -p /db
RUN mkdir -p /tmp

#locale stuff
RUN locale-gen pt_BR.UTF-8
ENV LC_ALL=pt_BR.UTF-8
ENV LANG=pt_BR.UTF-8
ENV LANGUAGE=pt_BR.UTF-8

#env vars for app
RUN printf \
"#!/bin/bash\n\
export MEMEDATA_SECRET_KEY=$(openssl rand -hex 64)\n\
export MEMEDATA_JWT_SECRET_KEY=$(openssl rand -hex 64)\n" \
    > env.sh
RUN printf \
"#!/bin/bash\n\
source env.sh\n\
exec \"\$@\"\n" \
    > entrypoint.sh
RUN chmod +x entrypoint.sh

ENTRYPOINT ["bash", "entrypoint.sh"]

CMD ["/bin/bash"]
