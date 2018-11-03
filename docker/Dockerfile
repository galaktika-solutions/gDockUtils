FROM ubuntu:bionic-20181018

ENV UPDATE=2018-11-03
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update

# locales
RUN apt-get install -y locales rsync
RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

RUN groupadd -r postgres --gid=999 && useradd -r -g postgres --uid=999 postgres
RUN groupadd -r django --gid=8000 && useradd -r -g django --uid=8000 django
RUN groupadd -r nginx --gid=4430 && useradd -r -g nginx --uid=4430 nginx

# postgres
ENV PG_MAJOR 10
RUN apt-get install -y postgresql-common
RUN sed -ri 's/#(create_main_cluster) .*$/\1 = false/' /etc/postgresql-common/createcluster.conf
RUN apt-get install -y postgresql-$PG_MAJOR
ENV PATH $PATH:/usr/lib/postgresql/$PG_MAJOR/bin
ENV PGDATA /data/postgres

# python
RUN apt-get install -y python3.6 python3-venv
RUN python3.6 -m venv /python
ENV PATH /python/bin:$PATH
ENV PYTHONPATH /src/python_packages/:/src/frontend/
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
RUN pip install --no-cache-dir pyyaml

RUN pip install --no-cache-dir coverage
RUN pip install --no-cache-dir sphinx
RUN pip install --no-cache-dir sphinx_rtd_theme
RUN pip install --no-cache-dir twine

COPY / /src
WORKDIR /src

ENTRYPOINT ["/src/docker/entrypoint.sh"]
