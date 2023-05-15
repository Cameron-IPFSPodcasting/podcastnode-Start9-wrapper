import { matches, types as T, util, YAML } from "../deps.ts";

const { shape, string } = matches;

const noPropertiesFound: T.ResultType<T.Properties> = {
  result: {
    version: 2,
    data: {
      "Not Ready": {
        type: "string",
        value: "Could not find properties. IPFS Podcasting might still be starting...",
        qr: false,
        copyable: false,
        masked: false,
        description: "Properties could not be found",
      },
    },
  },
} as const;

const configMatcher = shape({
  "ipfs-id": string,
  "peer-count": string,
  "disk-usage": string,
});

export const properties: T.ExpectedExports.properties = async (
  effects: T.Effects,
) => {
  if (
    await util.exists(effects, {
      volumeId: "main",
      path: "start9/config.yaml",
    }) === false
  ) {
    return noPropertiesFound;
  }
  const config = configMatcher.unsafeCast(YAML.parse(
    await effects.readFile({
      path: "start9/config.yaml",
      volumeId: "main",
    }),
  ));
  const properties: T.ResultType<T.Properties> = {
    result: {
      version: 2,
      data: {
//For IPFS - Show IPFS ID, Show Peers, Show Storage, Show Network? (HTTP, HTTPS, IPFS Health Check?)
        "IPFS ID": {
          type: "string",
          value: `${config["ipfs-id"]}`,
          description: "Your IPFS Node ID on the IPFS Network.",
          copyable: true,
          qr: false,
          masked: false,
        },
        "Peer Count": {
          type: "string",
          value: `${config["peer-count"]}`,
          description: "Number of IPFS peers connected to your node. More nodes mean [better performance](https://ipfspodcasting.net/Help/Network).",
          copyable: true,
          qr: false,
          masked: false,
        },
        "Disk Usage": {
          type: "string",
          value: `${config["disk-usage"]}`,
          description: "Disk used by IPFS. This is the size of your IPFS Datastore which may contain files not used for IPFS Podcasting. To clean up your datastore, select `Clean Up` from the `Actions` menu.",
          copyable: true,
          qr: false,
          masked: false,
        },
      },
    },
  } as const;
  return properties;
};
