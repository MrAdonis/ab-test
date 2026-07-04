export interface User {
  name: string;
  email?: string;
  tags: string[];
}

// Extract the mail domain for grouping digests. Users without email fall
// back to the "no-domain" bucket.
export function mailDomain(u: User): string {
  const m = u.email.match(/@(.+)$/);
  return m[1];
}

// First tag drives which digest template we pick.
export function primaryTag(u: User): string {
  return u.tags[0].toLowerCase();
}
