#!/bin/bash

set -e

_term() { 
  echo "Received STOP signal. Shutting Down." 
  kill -TERM "$IPFSPOD" 2>/dev/null
}

/ipfs-podcasting/ipfspodcastnode.py &

IPFSPOD=$!

trap _term SIGTERM

wait "$IPFSPOD"
