// Strong keywords — highly specific to job descriptions
const PRIMARY_KEYWORDS = [
  "responsibilities",
  "qualifications",
  "what you'll do",
  "what we're looking for",
  "minimum qualifications",
  "preferred qualifications",
  "about the role",
  "about this role",
  "job requirements",
  "who you are",
];

// Weak keywords — appear on many non-job pages too
const SECONDARY_KEYWORDS = ["requirements", "experience", "skills"];

const JOB_URL_PATTERNS = [
  /\/jobs?\//i,
  /\/careers?\//i,
  /\/openings?\//i,
  /\/positions?\//i,
  /\/postings?\//i,
  /\/apply\//i,
  /\/join\//i,
];

function looksLikeJobUrl(): boolean {
  return JOB_URL_PATTERNS.some((re) => re.test(window.location.pathname));
}

function countMatches(text: string, keywords: string[]): number {
  return keywords.filter((kw) => text.includes(kw)).length;
}

export function scrapeGeneric(): string | null {
  // Gate: only run the expensive DOM scan on pages whose URL looks job-related
  if (!looksLikeJobUrl()) return null;

  const candidates = Array.from(
    document.querySelectorAll("div, section, article, main")
  )
    .map((el) => ({
      el,
      text: (el as HTMLElement).innerText ?? "",
    }))
    .filter(({ text }) => {
      if (text.length < 300) return false;
      const lower = text.toLowerCase();
      // Accept if any primary keyword matches, or 2+ secondary keywords
      return (
        countMatches(lower, PRIMARY_KEYWORDS) >= 1 ||
        countMatches(lower, SECONDARY_KEYWORDS) >= 2
      );
    })
    .sort((a, b) => b.text.length - a.text.length);

  return candidates[0]?.text.trim() ?? null;
}
