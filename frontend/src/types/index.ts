export type UserRole = "candidate" | "recruiter" | "admin";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
}

export type ExtractionStatus = "pending" | "processing" | "completed" | "failed";

export interface EducationItem {
  degree?: string | null;
  institution?: string | null;
  field_of_study?: string | null;
  graduation_year?: string | null;
  gpa?: string | null;
}

export interface WorkExperienceItem {
  title?: string | null;
  organization?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  duration?: string | null;
  location?: string | null;
  description?: string | null;
  technologies_used: string[];
  achievements: string[];
}

export interface ProjectItem {
  name?: string | null;
  description?: string | null;
  technologies_used: string[];
  url?: string | null;
  achievements: string[];
}

export interface StructuredResumeProfile {
  full_name?: string | null;
  email?: string | null;
  phone?: string | null;
  location?: string | null;
  linkedin?: string | null;
  github?: string | null;
  portfolio?: string | null;
  professional_summary?: string | null;
  skills: string[];
  education: EducationItem[];
  work_experience: WorkExperienceItem[];
  internships: WorkExperienceItem[];
  projects: ProjectItem[];
  certifications: any[];
  achievements: string[];
  languages: string[];
}

export interface Resume {
  id: string;
  user_id: string;
  original_filename: string;
  file_url: string;
  file_size_bytes: number;
  mime_type: string;
  extraction_status: ExtractionStatus;
  raw_text?: string | null;
  structured_profile?: StructuredResumeProfile | null;
  parsing_error?: string | null;
  created_at: string;
  updated_at: string;
}

export type JobSourceType = "pasted" | "uploaded";
export type AnalysisStatus = "pending" | "processing" | "completed" | "failed";

export interface StructuredJobRequirements {
  job_title: string;
  company_name?: string | null;
  seniority_level?: string | null;
  employment_type?: string | null;
  location?: string | null;
  must_have_skills: string[];
  nice_to_have_skills: string[];
  responsibilities: string[];
  education_requirements: string[];
  experience_requirements?: string | null;
  years_of_experience?: number | null;
  keywords: string[];
  red_flags: string[];
}

export interface Job {
  id: string;
  user_id: string;
  title: string;
  company_name?: string | null;
  source_type: JobSourceType;
  raw_description: string;
  file_url?: string | null;
  structured_requirements?: StructuredJobRequirements | null;
  analysis_status: AnalysisStatus;
  parsing_error?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ComponentScores {
  required_skills: number;
  experience_relevance: number;
  nice_to_have_skills: number;
  projects_and_practical: number;
  education_fit: number;
  seniority_alignment: number;
}

export interface MatchedSkillDetail {
  skill: string;
  resume_evidence: string;
  confidence: number;
  category?: string;
}

export interface MissingSkillDetail {
  skill: string;
  importance: "critical" | "important" | "nice_to_have";
  category?: string | null;
}

export interface PartialSkillDetail {
  skill: string;
  related_resume_skill: string;
  explanation: string;
}

export interface ProjectIdea {
  title: string;
  description: string;
  technologies: string[];
  key_features: string[];
}

export interface LearningResource {
  topic: string;
  resource_name: string;
  resource_type: string;
  url?: string | null;
}

export interface ImprovementPlan {
  missing_skills_ranked: MissingSkillDetail[];
  learning_resources: LearningResource[];
  project_ideas: ProjectIdea[];
  resume_improvements: string[];
  interview_topics: string[];
}

export interface Match {
  id: string;
  user_id: string;
  resume_id: string;
  job_id: string;
  overall_score?: number | null;
  component_scores?: ComponentScores | null;
  matched_skills: MatchedSkillDetail[];
  missing_skills: MissingSkillDetail[];
  partial_skills: PartialSkillDetail[];
  evidence: Record<string, any>;
  explanation?: string | null;
  strengths: string[];
  risks: string[];
  improvement_plan?: ImprovementPlan | null;
  model_name?: string | null;
  prompt_version?: string | null;
  status: "pending" | "processing" | "completed" | "failed";
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export type ApplicationStatus =
  | "saved"
  | "applied"
  | "screening"
  | "interview"
  | "technical_assessment"
  | "offer"
  | "rejected"
  | "withdrawn";

export interface Application {
  id: string;
  user_id: string;
  job_id: string;
  resume_id?: string | null;
  status: ApplicationStatus;
  applied_at?: string | null;
  deadline?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
  job?: Job;
}

export interface SummaryResponse {
  id: string;
  user_id: string;
  resume_id: string;
  job_id: string;
  generated_summary: string;
  supported_evidence: string[];
  unsupported_flags: string[];
  created_at: string;
}

export interface AdminMetrics {
  total_users: number;
  total_resumes_processed: number;
  total_jobs_analyzed: number;
  total_matches_generated: number;
  ai_success_rate: number;
  average_ai_latency_ms: number;
  average_processing_cost_usd: number;
  failed_jobs_by_error: Record<string, number>;
  most_common_missing_skills: Array<{ skill: string; count: number }>;
  most_common_target_roles: Array<{ role: string; count: number }>;
}
