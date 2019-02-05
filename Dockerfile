FROM ubuntu:bionic-20181112

ENV DEBIAN_FRONTEND noninteractive

# locales
RUN apt-get update && apt-get install -y locales rsync
RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

RUN groupadd -r postgres --gid=999 && useradd -r -g postgres --uid=999 postgres

# postgres
ENV PG_MAJOR 10
RUN apt-get update && apt-get install -y postgresql-common
RUN sed -ri 's/#(create_main_cluster) .*$/\1 = false/' /etc/postgresql-common/createcluster.conf
RUN apt-get update && apt-get install -y postgresql-$PG_MAJOR
ENV PGDATA /data/postgres

# python
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y python3.6 python3-pip python3-venv
RUN pip3 install pipenv
ENV PIPENV_VENV_IN_PROJECT 1
# Should be ENV PIPENV_CACHE_DIR /tmp/.cache
ENV XDG_CACHE_HOME /tmp/.cache

ENV PATH $PATH:/usr/lib/postgresql/$PG_MAJOR/bin:/src/.venv/bin
WORKDIR /src
