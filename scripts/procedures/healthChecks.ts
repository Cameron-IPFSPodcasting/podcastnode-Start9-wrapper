import { types as T, healthUtil } from "../deps.ts";

export const health: T.ExpectedExports.health = {
  async "web-ui"(effects, duration) {
    return healthUtil.checkWebUrl("http://ipfs-podcasting.embassy:5001/webui")(effects, duration).catch(healthUtil.catchError(effects))
  },
};
