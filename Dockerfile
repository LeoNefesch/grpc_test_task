FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    wget \
    supervisor \
    jq

RUN python3 -m venv /app/venv

COPY requirements.txt /requirements.txt

RUN /app/venv/bin/pip install --upgrade pip
RUN /app/venv/bin/pip install -r /requirements.txt

COPY client.py /app/client.py
COPY server.py /app/server.py
COPY config.json /app/config.json
COPY protobufs/ /app/protobufs/

RUN /app/venv/bin/python -m grpc_tools.protoc -I /app/protobufs --python_out=/app \
           --grpc_python_out=/app /app/protobufs/grpc_test.proto

COPY init_db.sh /usr/local/bin/init_db.sh
RUN chmod +x /usr/local/bin/init_db.sh

USER postgres

RUN /usr/lib/postgresql/16/bin/initdb -D /var/lib/postgresql/data

RUN service postgresql start && \
    PG_USER=$(jq -r '.pg_user' /app/config.json) && \
    PG_PASSWORD=$(jq -r '.pg_password' /app/config.json) && \
    PG_DB=$(jq -r '.pg_database' /app/config.json) && \
    psql --command "CREATE USER $PG_USER WITH SUPERUSER PASSWORD '$PG_PASSWORD';" && \
    createdb -O $PG_USER $PG_DB

USER root

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN PG_PORT=$(jq -r '.pg_port' /app/config.json) && \
    GRPC_PORT=$(jq -r '.gRPCServerPort' /app/config.json) && \
    echo "Exposing PostgreSQL port: $PG_PORT and gRPC port: $GRPC_PORT"

EXPOSE $GRPC_PORT $PG_PORT

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
