FROM ubuntu:bionic-20180821

ENV DEBIAN_FRONTEND noninteractive

# locales
RUN apt-get update
RUN apt-get install -y locales build-essential rsync gettext
RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

# python
RUN apt-get install -y python3.6 python3-venv
RUN python3.6 -m venv /python
ENV PATH /python/bin:$PATH
ENV PYTHONUNBUFFERED 1

# COPY / /src
# RUN pip install -e /src

ENTRYPOINT ["/src/entrypoint.sh"]
