FROM    node:8.16.0-jessie AS builder

WORKDIR /opt/front
RUN     apt-get update && \
            apt-get install apt-transport-https && \
            curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
            echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list && \
            apt-get update && \
            apt-get install yarn
COPY    front /opt/front/
RUN     yarn && yarn build

FROM    python:3.7
WORKDIR /opt
RUN     pip3 install coloredlogs flask absl-py Pillow flask_cors
COPY    --from=builder /opt/static static
COPY    app.py app.py