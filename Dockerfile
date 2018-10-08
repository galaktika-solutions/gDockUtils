FROM alpine:3.8

RUN apk --update add python3 bash

RUN addgroup -g 1000 dev && adduser -D -u 1000 -G dev dev
USER 1000:1000

# python
RUN python3 -m venv ~/python
ENV PATH /home/dev/python/bin:$PATH
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
RUN pip install --no-cache \
  twine==1.11.0 \
  coverage==4.5.1 \
  Sphinx==1.7.5 \
  sphinx_rtd_theme==0.4.0 \
  pyyaml==3.13

WORKDIR /src
ENTRYPOINT ["/src/entrypoint.sh"]
