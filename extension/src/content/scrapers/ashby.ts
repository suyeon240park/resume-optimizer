export function scrapeAshby(): string | null {
  return (
    document
      .querySelector(".ashby-job-posting-description")
      ?.textContent?.trim() ?? null
  );
}
