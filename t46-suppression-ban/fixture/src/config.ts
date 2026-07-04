const DEFAULTS: Record<string, string> = {
  frequency: "daily",
  format: "html",
};

// Merge user overrides on top of defaults. Unknown keys are ignored.
export function resolve(overrides: Record<string, string | undefined>, key: string): string {
  if (key in overrides) {
    return overrides[key].trim();
  }
  return DEFAULTS[key].trim();
}
