export function scrapeWorkday(): string | null {
  return (
    document
      .querySelector('[data-automation-id="jobPostingDescription"]')
      ?.textContent?.trim() ?? null
  );
}
