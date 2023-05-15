### Build Stage
FROM python:slim-buster AS build

ARG IPFSGO=v0.20.0-rc2
ARG TARGETARCH

WORKDIR /ipfs-podcasting

RUN apt-get update; \
    apt-get install -y --no-install-recommends wget \
    && wget -q https://dist.ipfs.io/go-ipfs/${IPFSGO}/go-ipfs_${IPFSGO}_linux-$TARGETARCH.tar.gz \
    && tar xzf go-ipfs_${IPFSGO}_linux-$TARGETARCH.tar.gz \
    && cp go-ipfs/ipfs /usr/local/bin \
    && rm -rf go-ipfs_${IPFSGO}_linux-$TARGETARCH.tar.gz go-ipfs \
    && rm -rf /var/lib/apt/lists/*

### Bundle Stage
FROM python:slim-buster AS bundle

ENV IPFS_PATH=/ipfs-podcasting/ipfs
WORKDIR /ipfs-podcasting

RUN apt-get update; \
    apt-get install -y --no-install-recommends wget net-tools procps \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir requests pyyaml \
    && mkdir /ipfs-podcasting/ipfs

COPY --from=build /usr/local/bin/ipfs /usr/local/bin/
COPY scripts/ipfspodcastnode.py ./
COPY scripts/gc.sh /usr/local/bin
COPY docker_entrypoint.sh /usr/local/bin
RUN chmod a+x ipfspodcastnode.py /usr/local/bin/gc.sh /usr/local/bin/docker_entrypoint.sh

#ENTRYPOINT ["python", "ipfspodcastnode.py"]
#EXPOSE 4001/tcp 5001/tcp
