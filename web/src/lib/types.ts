export interface ResumeOut {
  id: string;
  name: string;
  preset_type: string | null;
  created_at: string;
  updated_at: string;
}

export interface ResumeDetail extends ResumeOut {
  latex_source: string;
  sections: SectionNode[] | null;
}

export interface SectionNode {
  name: string;
  entries: ContentEntry[];
}

export interface ContentEntry {
  command: string;
  args: string[];
  source_range: [number, number];
  children?: ContentEntry[];
}

export interface ApplicationOut {
  id: string;
  company: string;
  role_title: string;
  portal_url: string | null;
  status: string;
  jd_analysis: JDAnalysis | null;
  applied_at: string | null;
  created_at: string;
}

export interface ApplicationDetail extends ApplicationOut {
  jd_snapshot: string;
}

export interface VersionOut {
  id: string;
  base_resume_id: string | null;
  version_number: number;
  ats_score: number | null;
  changes_applied: MutationItem[];
  created_at: string;
}

export interface JDAnalysis {
  role_title: string;
  seniority: string;
  team_function: string;
  required_skills: Skill[];
  domain_keywords: string[];
  soft_signals: string[];
  ats_keywords: string[];
}

export interface Skill {
  skill: string;
  category: string;
  importance: string;
}

export interface MutationItem {
  type: "edit" | "add" | "remove" | "reorder";
  section: string;
  target: string | null;
  proposed: string | null;
  rationale: string;
  keywords_addressed: string[];
}

export interface OptimizeResponse {
  jd_analysis: JDAnalysis;
  alignment: AlignmentResult;
  mutations: MutationItem[];
}

export interface AlignmentResult {
  bullet_scores: BulletScore[];
  gap_analysis: {
    missing_critical: string[];
    missing_preferred: string[];
    strongest_matches: string[];
  };
}

export interface BulletScore {
  section: string;
  bullet: string;
  relevance: number;
  matched_skills: string[];
  notes: string;
}

export interface ApplyResponse {
  version_id: string;
  version_number: number;
  ats_score: number | null;
  latex_source: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export type ApplicationStatus =
  | "draft"
  | "optimized"
  | "applied"
  | "interview"
  | "offer"
  | "rejected";

export const STATUS_COLUMNS: ApplicationStatus[] = [
  "draft",
  "optimized",
  "applied",
  "interview",
  "offer",
  "rejected",
];
