import { compat, types as T } from "../deps.ts";

export const getConfig: T.ExpectedExports.getConfig = compat.getConfig({
  "email-address": {
    "type": "string",
    "name": "E-Mail (optional)",
    "description": "Enter an email to manage your node from IPFSPodcasting.net",
    "nullable": true,
    "pattern": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$",
    "pattern-description": "Must be a valid email address",
  },
});
