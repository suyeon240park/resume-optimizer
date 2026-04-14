export function scrapeLever(): string | null {
  return (
    document.querySelector(".posting-page .content")?.textContent?.trim() ?? null
  );
}
