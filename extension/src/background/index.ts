import { API_URL } from "../config";

interface ApiMessage {
  type: "API_CALL";
  method: string;
  path: string;
  body?: unknown;
}

interface AuthMessage {
  type: "SET_TOKEN";
  accessToken: string;
  refreshToken: string;
}

interface GetTokenMessage {
  type: "GET_TOKEN";
}

type Message = ApiMessage | AuthMessage | GetTokenMessage | { type: "JD_DETECTED"; payload: unknown };

const ALLOWED_METHODS = new Set(["GET", "POST", "PATCH", "DELETE"]);

const ALLOWED_PATH_PATTERNS = [
  /^\/api\/resumes(\/|$)/,
  /^\/api\/applications(\/|$)/,
  /^\/api\/scrape$/,
  /^\/api\/versions(\/|$)/,
  /^\/api\/auth\//,
];

function isAllowedPath(path: string): boolean {
  if (path.includes("..") || path.includes("//")) return false;
  return ALLOWED_PATH_PATTERNS.some((re) => re.test(path));
}

function isExtensionPage(sender: chrome.runtime.MessageSender): boolean {
  return sender.id === chrome.runtime.id && !sender.tab;
}

async function getToken(): Promise<string | null> {
  const result = await chrome.storage.local.get("access_token");
  return result.access_token ?? null;
}

async function handleApiCall(
  msg: ApiMessage
): Promise<{ ok: boolean; status: number; data: unknown }> {
  if (!ALLOWED_METHODS.has(msg.method) || !isAllowedPath(msg.path)) {
    return { ok: false, status: 403, data: { error: "Blocked by path policy" } };
  }

  const token = await getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const init: RequestInit = {
    method: msg.method,
    headers,
  };
  if (msg.body) init.body = JSON.stringify(msg.body);

  const res = await fetch(`${API_URL}${msg.path}`, init);
  let data: unknown = null;
  if (res.status !== 204) {
    const text = await res.text();
    if (text.length > 0) {
      try {
        data = JSON.parse(text) as unknown;
      } catch {
        data = { error: "Invalid response from server" };
      }
    }
  }

  return { ok: res.ok, status: res.status, data };
}

chrome.runtime.onMessage.addListener(
  (message: Message, sender, sendResponse) => {
    if (message.type === "API_CALL") {
      if (!isExtensionPage(sender)) {
        sendResponse({ ok: false, status: 403, data: { error: "Forbidden" } });
        return false;
      }
      handleApiCall(message as ApiMessage).then(sendResponse).catch((err) => {
        sendResponse({ ok: false, status: 0, data: { error: err.message } });
      });
      return true;
    }

    if (message.type === "SET_TOKEN") {
      if (!isExtensionPage(sender)) {
        sendResponse({ ok: false });
        return false;
      }
      const { accessToken, refreshToken } = message as AuthMessage;
      chrome.storage.local.set({
        access_token: accessToken,
        refresh_token: refreshToken,
      });
      sendResponse({ ok: true });
      return false;
    }

    if (message.type === "GET_TOKEN") {
      if (!isExtensionPage(sender)) {
        sendResponse({ token: null });
        return false;
      }
      getToken().then((token) => sendResponse({ token }));
      return true;
    }

    if (message.type === "JD_DETECTED") {
      const { payload } = message;
      chrome.storage.local.set({ last_jd: payload });
      return false;
    }

    return false;
  }
);
