export function scrapeGreenhouse(): string | null {
  return document.querySelector(".job-description")?.textContent?.trim() ?? null;
}
