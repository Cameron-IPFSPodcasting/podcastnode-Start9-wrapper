#!/bin/bash

set -e

_term() { 
  echo "Caught SIGTERM signal!" 
  kill -TERM "$IPFSPOD" 2>/dev/null
}

/ipfs-podcasting/ipfspodcastnode.py &

IPFSPOD=$!

trap _term SIGTERM

wait "$IPFSPOD"
