FROM golang:1.23 AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y nodejs npm

COPY container_imgs/app/go.mod container_imgs/app/go.sum ./
COPY /aws_lib /aws_lib

ENV GOFLAGS="-tags=container"
RUN go mod download

COPY container_imgs/app/ .
RUN npm ci
RUN make build

FROM alpine:latest
WORKDIR /root/

RUN apk add --no-cache tzdata

COPY --from=builder /app/bin/main .

EXPOSE 8080
