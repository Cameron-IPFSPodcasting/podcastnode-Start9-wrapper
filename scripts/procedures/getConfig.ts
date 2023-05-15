import { compat, types as T } from "../deps.ts";

export const getConfig: T.ExpectedExports.getConfig = compat.getConfig({
/*
  "ipfs-id": {
    "name": "gc IPFS ID",
    "description": "gc Your IPFS Node ID on the IPFS Network.",
    "type": "pointer",
    "subtype": "package",
    "package-id": "ipfs-podcasting",
    "target": "ipfs-id",
    "interface": "main"
  },
  "peer-count": {
    "name": "gc Peer Count",
    "description": "gc Number of IPFS peers connected to your node. More nodes mean [better performance](https://ipfspodcasting.net/Help/Network).",
    "type": "pointer",
    "subtype": "package",
    "package-id": "ipfs-podcasting",
    "target": "peer-count",
    "interface": "main"
  },
  "disk-usage": {
    "name": "gc Disk Usage",
    "description": "gc Disk used by IPFS. This is the size of your IPFS Datastore which may contain files not used for IPFS Podcasting. To clean up your datastore, select `Clean Up` from the `Actions` menu.",
    "type": "pointer",
    "subtype": "package",
    "package-id": "ipfs-podcasting",
    "target": "disk-usage",
    "interface": "main"
  },
*/
  "email-address": {
    "type": "string",
    "name": "E-Mail (optional)",
    "description": "Enter an email to manage your node from IPFSPodcasting.net",
    "nullable": true,
    "pattern": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$",
    "pattern-description": "Must be a valid email address",
  },
});
