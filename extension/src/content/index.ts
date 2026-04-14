import { scrapeJobDescription } from "./scrapers";

let sidebarIframe: HTMLIFrameElement | null = null;
let fabButton: HTMLButtonElement | null = null;

function createFAB() {
  if (fabButton) return;

  fabButton = document.createElement("button");
  fabButton.id = "resume-opt-fab";
  Object.assign(fabButton.style, {
    position: "fixed",
    bottom: "24px",
    right: "24px",
    zIndex: "2147483646",
    width: "48px",
    height: "48px",
    borderRadius: "50%",
    backgroundColor: "#18181b",
    color: "#fff",
    border: "none",
    cursor: "pointer",
    fontSize: "20px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontFamily: "system-ui, sans-serif",
  });
  fabButton.textContent = "R";
  fabButton.title = "Open Resume Optimizer";
  fabButton.setAttribute("aria-label", "Open Resume Optimizer");
  fabButton.addEventListener("click", toggleSidebar);
  document.body.appendChild(fabButton);
}

function toggleSidebar() {
  if (sidebarIframe) {
    sidebarIframe.remove();
    sidebarIframe = null;
    document.body.style.marginRight = "";
    return;
  }

  const sidebarUrl = chrome.runtime.getURL("sidebar/index.html");
  sidebarIframe = document.createElement("iframe");
  sidebarIframe.id = "resume-opt-sidebar";
  sidebarIframe.src = sidebarUrl;
  Object.assign(sidebarIframe.style, {
    position: "fixed",
    top: "0",
    right: "0",
    width: "400px",
    height: "100vh",
    zIndex: "2147483647",
    border: "none",
    borderLeft: "1px solid #e5e7eb",
    boxShadow: "-4px 0 16px rgba(0,0,0,0.1)",
    backgroundColor: "#fff",
  });

  document.body.appendChild(sidebarIframe);
  document.body.style.marginRight = "400px";

  // Send scraped JD to sidebar once it loads
  const extensionOrigin = new URL(chrome.runtime.getURL("/")).origin;
  sidebarIframe.addEventListener("load", () => {
    const result = scrapeJobDescription();
    sidebarIframe?.contentWindow?.postMessage(
      { type: "JD_SCRAPED", payload: result },
      extensionOrigin
    );
  });
}

function init() {
  // Only show the FAB if we detect a likely job description page
  const result = scrapeJobDescription();
  if (result) {
    createFAB();

    // Also notify background script about the scrape
    chrome.runtime.sendMessage({
      type: "JD_DETECTED",
      payload: {
        url: window.location.href,
        ...result,
      },
    });
  }
}

// Delay to let dynamic content load
if (document.readyState === "complete") {
  setTimeout(init, 1000);
} else {
  window.addEventListener("load", () => setTimeout(init, 1000));
}
