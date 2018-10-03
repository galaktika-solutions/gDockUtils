FROM alpine:3.8

RUN apk --update add python3 bash

# python
RUN python3 -m venv /python
ENV PATH /python/bin:$PATH
ENV PYTHONUNBUFFERED 1
RUN pip3 install --no-cache twine==1.11.0
RUN pip3 install --no-cache coverage==4.5.1
RUN pip3 install --no-cache Sphinx==1.7.5
RUN pip3 install --no-cache sphinx_rtd_theme==0.4.0

RUN apk --update add su-exec

RUN addgroup -g 1000 developer && adduser -D -H -u 1000 -G developer developer

ENTRYPOINT ["/src/entrypoint.sh"]
