// @vitest-environment jsdom
import { describe, it, expect, beforeEach, vi } from "vitest";
import { scrapeGeneric } from "./generic";

describe("generic scraper logic", () => {
  beforeEach(() => {
    document.body.innerHTML = "";
  });

  it("returns null when URL has no job-like path", () => {
    // Default jsdom location has no /jobs/ segment
    document.body.innerHTML =
      "<div>Responsibilities: do everything. Qualifications: be smart.</div>";
    const result = scrapeGeneric();
    expect(result).toBeNull();
  });

  it("returns null when URL looks like a job page but content has no JD keywords", () => {
    Object.defineProperty(window, "location", {
      value: { ...window.location, pathname: "/jobs/123" },
      writable: true,
    });
    document.body.innerHTML = "<div>Hello world, nothing here</div>";
    const result = scrapeGeneric();
    expect(result).toBeNull();
  });
});
