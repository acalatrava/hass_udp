# Usa la base oficial de add-ons de Home Assistant
ARG BUILD_FROM=ghcr.io/home-assistant/{arch}-base:3.19
FROM ${BUILD_FROM}

# Instala Python
RUN apk add --no-cache python3 py3-pip

WORKDIR /app
COPY main.py /app/main.py
COPY run.sh /run.sh
RUN chmod +x /run.sh

# Arranca el script
CMD [ "/run.sh" ]
