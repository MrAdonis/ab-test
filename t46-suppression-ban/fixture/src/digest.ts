import { User, mailDomain, primaryTag } from "./user";
import { resolve } from "./config";

export interface DigestLine {
  domain: string;
  tag: string;
  format: string;
}

export function buildDigest(users: User[], overrides: Record<string, string | undefined>): DigestLine[] {
  return users.map((u) => ({
    domain: mailDomain(u),
    tag: primaryTag(u),
    format: resolve(overrides, "format"),
  }));
}
