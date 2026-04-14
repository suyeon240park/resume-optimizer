type Method = "GET" | "POST" | "PATCH" | "DELETE";

async function apiCall<T>(
  method: Method,
  path: string,
  body?: unknown
): Promise<T> {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage(
      { type: "API_CALL", method, path, body },
      (response) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
          return;
        }
        if (!response.ok) {
          reject(new Error(`API error ${response.status}`));
          return;
        }
        resolve(response.data as T);
      }
    );
  });
}

export const extApi = {
  listResumes: () => apiCall<ResumeOut[]>("GET", "/api/resumes"),
  listApplications: () => apiCall<ApplicationOut[]>("GET", "/api/applications"),
  createApplication: (data: {
    company: string;
    role_title: string;
    jd_snapshot: string;
    portal_url?: string;
  }) => apiCall<ApplicationOut>("POST", "/api/applications", data),
  optimize: (appId: string, baseResumeId: string) =>
    apiCall<OptimizeResponse>("POST", `/api/applications/${appId}/optimize`, {
      base_resume_id: baseResumeId,
    }),
  applyMutations: (
    appId: string,
    baseResumeId: string,
    mutations: MutationItem[]
  ) =>
    apiCall<ApplyResponse>("POST", `/api/applications/${appId}/apply`, {
      base_resume_id: baseResumeId,
      mutations,
    }),
};

// Inline types to avoid import issues in extension build
interface ResumeOut {
  id: string;
  name: string;
  preset_type: string | null;
  created_at: string;
  updated_at: string;
}

interface ApplicationOut {
  id: string;
  company: string;
  role_title: string;
  portal_url: string | null;
  status: string;
  jd_analysis: unknown;
  applied_at: string | null;
  created_at: string;
}

interface MutationItem {
  type: string;
  section: string;
  target: string | null;
  proposed: string | null;
  rationale: string;
  keywords_addressed: string[];
}

interface OptimizeResponse {
  jd_analysis: unknown;
  alignment: unknown;
  mutations: MutationItem[];
}

interface ApplyResponse {
  version_id: string;
  version_number: number;
  ats_score: number | null;
  latex_source: string;
}

export type {
  ResumeOut,
  ApplicationOut,
  MutationItem,
  OptimizeResponse,
  ApplyResponse,
};
