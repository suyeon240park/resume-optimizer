const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

class ApiClient {
  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  /** One refresh attempt; returns true if new access token is stored. */
  private async tryRefresh(): Promise<boolean> {
    if (typeof window === "undefined") return false;
    const refresh = localStorage.getItem("refresh_token");
    if (!refresh) return false;
    try {
      const res = await fetch(`${API_URL}/api/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
      });
      if (!res.ok) return false;
      const data = (await res.json()) as {
        access_token: string;
        refresh_token: string;
      };
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      return true;
    } catch {
      return false;
    }
  }

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    return this.requestWithOptionalRefresh<T>(path, init, true);
  }

  private async requestWithOptionalRefresh<T>(
    path: string,
    init: RequestInit | undefined,
    allowRefresh: boolean
  ): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(init?.headers as Record<string, string>),
    };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_URL}${path}`, { ...init, headers });

    if (res.status === 401 && allowRefresh) {
      const refreshed = await this.tryRefresh();
      if (refreshed) {
        return this.requestWithOptionalRefresh<T>(path, init, false);
      }
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      window.location.href = "/login";
      throw new Error("Unauthorized");
    }

    if (res.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      window.location.href = "/login";
      throw new Error("Unauthorized");
    }

    if (!res.ok) {
      throw new Error(`API error ${res.status}`);
    }

    if (res.status === 204) return undefined as T;
    return res.json();
  }

  // Resumes
  listResumes() {
    return this.request<import("./types").ResumeOut[]>("/api/resumes");
  }
  getResume(id: string) {
    return this.request<import("./types").ResumeDetail>(`/api/resumes/${id}`);
  }
  createResume(data: { name: string; latex_source: string; preset_type?: string }) {
    return this.request<import("./types").ResumeOut>("/api/resumes", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }
  deleteResume(id: string) {
    return this.request<void>(`/api/resumes/${id}`, { method: "DELETE" });
  }

  // Applications
  listApplications(status?: string) {
    const params = status ? `?status=${status}` : "";
    return this.request<import("./types").ApplicationOut[]>(`/api/applications${params}`);
  }
  getApplication(id: string) {
    return this.request<import("./types").ApplicationDetail>(`/api/applications/${id}`);
  }
  createApplication(data: { company: string; role_title: string; jd_snapshot: string; portal_url?: string }) {
    return this.request<import("./types").ApplicationOut>("/api/applications", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }
  updateApplication(id: string, data: { status?: string; applied_at?: string }) {
    return this.request<import("./types").ApplicationOut>(`/api/applications/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }
  deleteApplication(id: string) {
    return this.request<void>(`/api/applications/${id}`, { method: "DELETE" });
  }

  // Versions
  listVersions(appId: string) {
    return this.request<import("./types").VersionOut[]>(`/api/applications/${appId}/versions`);
  }
  downloadPdf(versionId: string): string {
    return `${API_URL}/api/versions/${versionId}/pdf`;
  }

  // Optimization
  optimize(appId: string, baseResumeId: string) {
    return this.request<import("./types").OptimizeResponse>(
      `/api/applications/${appId}/optimize`,
      { method: "POST", body: JSON.stringify({ base_resume_id: baseResumeId }) }
    );
  }
  applyMutations(appId: string, baseResumeId: string, mutations: import("./types").MutationItem[]) {
    return this.request<import("./types").ApplyResponse>(
      `/api/applications/${appId}/apply`,
      { method: "POST", body: JSON.stringify({ base_resume_id: baseResumeId, mutations }) }
    );
  }

  // Scrape
  analyzeJD(jdText: string) {
    return this.request<{ jd_analysis: import("./types").JDAnalysis }>("/api/scrape", {
      method: "POST",
      body: JSON.stringify({ jd_text: jdText }),
    });
  }
}

export const api = new ApiClient();
