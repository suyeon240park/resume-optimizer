import { scrapeGreenhouse } from "./greenhouse";
import { scrapeLever } from "./lever";
import { scrapeWorkday } from "./workday";
import { scrapeAshby } from "./ashby";
import { scrapeGeneric } from "./generic";

interface ScrapeResult {
  source: string;
  text: string;
}

const PORTAL_SCRAPERS: Record<string, () => string | null> = {
  "greenhouse.io": scrapeGreenhouse,
  "lever.co": scrapeLever,
  "myworkdayjobs.com": scrapeWorkday,
  "jobs.ashbyhq.com": scrapeAshby,
  "icims.com": () =>
    document.querySelector(".iCIMS_JobContent")?.textContent?.trim() ?? null,
  "bamboohr.com": () =>
    document.querySelector(".BambooHR-ATS-body")?.textContent?.trim() ?? null,
  "smartrecruiters.com": () =>
    document.querySelector(".job-sections")?.textContent?.trim() ?? null,
  "linkedin.com": () =>
    document.querySelector(".description__text")?.textContent?.trim() ?? null,
  "indeed.com": () =>
    document.querySelector("#jobDescriptionText")?.textContent?.trim() ?? null,
  "glassdoor.com": () =>
    document.querySelector(".jobDescriptionContent")?.textContent?.trim() ??
    null,
};

export function scrapeJobDescription(): ScrapeResult | null {
  const hostname = window.location.hostname;

  for (const [domain, scraper] of Object.entries(PORTAL_SCRAPERS)) {
    if (hostname.includes(domain)) {
      const text = scraper();
      if (text && text.length > 100) {
        return { source: domain, text };
      }
    }
  }

  // Generic fallback — only runs on pages with job-like URLs (see generic.ts)
  const text = scrapeGeneric();
  if (text && text.length > 500) {
    return { source: "heuristic", text };
  }

  return null;
}
