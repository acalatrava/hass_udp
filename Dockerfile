ARG BUILD_FROM=python:3.11-alpine
FROM ${BUILD_FROM}
WORKDIR /app
COPY main.py /app/main.py
COPY run.sh /run.sh
RUN chmod +x /run.sh
CMD [ "/run.sh" ]
