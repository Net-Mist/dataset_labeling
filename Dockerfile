FROM yarnpkg/node-yarn:node7 AS builder

WORKDIR /opt/front
COPY front /opt/front/
RUN yarn && yarn build

FROM python:3.7
COPY --from=builder /opt/static .
