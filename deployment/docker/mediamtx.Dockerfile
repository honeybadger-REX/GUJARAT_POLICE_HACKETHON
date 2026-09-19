FROM alpine:3.20

ARG MTX_VERSION=1.21.0

RUN apk add --no-cache wget ca-certificates && \
    wget -q https://github.com/bluenviron/mediamtx/releases/download/v${MTX_VERSION}/mediamtx_v${MTX_VERSION}_linux_amd64.tar.gz && \
    tar -xzf mediamtx_v${MTX_VERSION}_linux_amd64.tar.gz && \
    mv mediamtx /usr/local/bin/mediamtx && \
    rm mediamtx_v${MTX_VERSION}_linux_amd64.tar.gz

COPY streaming/mediamtx_v1.21.0_windows_amd64/mediamtx.yml /mediamtx.yml

EXPOSE 8554/tcp
EXPOSE 8000/udp
EXPOSE 8001/udp
EXPOSE 1935/tcp
EXPOSE 8888/tcp
EXPOSE 8889/tcp
EXPOSE 8189/udp
EXPOSE 8890/udp
EXPOSE 8892/tcp
EXPOSE 8892/udp
EXPOSE 8893/udp

CMD ["/usr/local/bin/mediamtx", "/mediamtx.yml"]