#!/bin/sh
echo 'version: 2
data:
  IPFS ID:
    type: string
    value: N/A,
    description: Your IPFS Node ID on the IPFS Network.
    copyable: true
    qr: false
    masked: false
  Peer Count:
    type: string
    value: N/A,
    description: Number of IPFS peers connected to your node. More nodes mean [better performance](https://ipfspodcasting.net/Help/Network).
    copyable: true
    qr: false
    masked: false
  Disk Usage:
    type: string
    value: N/A,
    description: Disk used by IPFS. This is the size of your IPFS Datastore which may contain files not used for IPFS Podcasting. To clean up your datastore, select `Clean Up` from the `Actions` menu.
    copyable: true
    qr: false
    masked: false' >> /ipfs-podcasting/ipfs/start9/stats.yaml

exec /ipfs-podcasting/ipfspodcastnode.py
