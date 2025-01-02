FROM python:3.12

ENV PYTHONUNBUFFERED=1

ARG WORKDIR=/wd
ARG USER=user

WORKDIR ${WORKDIR}

RUN useradd --system ${USER} && \
    chown --recursive ${USER} ${WORKDIR}

RUN apt update && apt upgrade --yes

COPY --chown=${USER} requirements.txt requirements.txt
COPY --chown=${USER} .env .env

RUN pip install --upgrade pip && \
    pip install --requirement requirements.txt

COPY --chown=${USER} start.sh start.sh
RUN chmod +x start.sh


COPY --chown=${USER} manage.py manage.py
COPY --chown=${USER} ./BaseApp BaseApp
COPY --chown=${USER} ./apps apps



USER ${USER}


EXPOSE 8000


CMD ["./start.sh"]
#CMD ["ls"]