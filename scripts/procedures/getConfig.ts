import { compat, types as T } from "../deps.ts";

export const getConfig: T.ExpectedExports.getConfig = compat.getConfig({
  "tor-address": {
    "name": "Tor Address",
    "description": "The Tor address for the IPFS WebUI",
    "type": "pointer",
    "subtype": "package",
    "package-id": "ipfs-podcasting",
    "target": "tor-address",
    "interface": "mgmt"
  },
  "lan-address": {
    "name": "Tor Address",
    "description": "The LAN address for the IPFS WebUI",
    "type": "pointer",
    "subtype": "package",
    "package-id": "ipfs-podcasting",
    "target": "lan-address",
    "interface": "mgmt"
  },
  "email-address": {
    "type": "string",
    "name": "E-Mail (optional)",
    "description": "Enter an email to manage your node from IPFSPodcasting.net",
    "nullable": true,
    "pattern": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$",
    "pattern-description": "Must be a valid email address",
  },
});
