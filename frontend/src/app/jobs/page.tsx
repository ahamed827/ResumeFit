"use client";

import React, { useEffect, useState, useRef } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";
import { Job, StructuredJobRequirements } from "@/types";
import { formatDate } from "@/lib/utils";
import {
  Briefcase,
  Plus,
  Upload,
  RefreshCw,
  Trash2,
  Edit3,
  CheckCircle2,
  AlertCircle,
  Loader2,
  ChevronRight,
  X,
  FileText
} from "lucide-react";

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newCompany, setNewCompany] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [statusMessage, setStatusMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchJobs = async () => {
    try {
      const res = await api.get("/jobs");
      setJobs(res.data.items);
      if (res.data.items.length > 0 && !selectedJob) {
        setSelectedJob(res.data.items[0]);
      }
    } catch (err) {
      console.error("Failed to fetch jobs:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleCreatePastedJob = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle || !newDescription) return;

    setIsSubmitting(true);
    setStatusMessage(null);

    try {
      const res = await api.post("/jobs", {
        title: newTitle,
        company_name: newCompany || undefined,
        raw_description: newDescription,
      });
      setStatusMessage({ type: "success", text: "Job specification created and analyzed!" });
      setShowAddModal(false);
      setNewTitle("");
      setNewCompany("");
      setNewDescription("");
      await fetchJobs();
      setSelectedJob(res.data);
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || "Failed to create job.";
      setStatusMessage({ type: "error", text: msg });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsSubmitting(true);
    setStatusMessage(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await api.post("/jobs/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setStatusMessage({ type: "success", text: "Job file uploaded and analyzed!" });
      await fetchJobs();
      setSelectedJob(res.data);
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || "Failed to upload job file.";
      setStatusMessage({ type: "error", text: msg });
    } finally {
      setIsSubmitting(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this job?")) return;
    try {
      await api.delete(`/jobs/${id}`);
      setStatusMessage({ type: "success", text: "Job description removed." });
      if (selectedJob?.id === id) setSelectedJob(null);
      await fetchJobs();
    } catch (err) {
      setStatusMessage({ type: "error", text: "Failed to delete job." });
    }
  };

  const handleReanalyze = async (id: string) => {
    try {
      const res = await api.post(`/jobs/${id}/analyze`);
      setStatusMessage({ type: "success", text: "Job re-analyzed successfully!" });
      await fetchJobs();
      if (selectedJob?.id === id) setSelectedJob(res.data);
    } catch (err) {
      setStatusMessage({ type: "error", text: "Failed to re-analyze job." });
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Job Library</h1>
            <p className="text-sm text-slate-400 mt-1">
              Store target job postings, analyze required vs nice-to-have skills, and prepare for matching.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".txt,.pdf,.docx"
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isSubmitting}
              className="flex items-center gap-2 px-3.5 py-2.5 rounded-lg border border-slate-700 bg-slate-850 hover:bg-slate-800 font-semibold text-xs text-slate-200 transition"
            >
              <Upload className="h-4 w-4" />
              <span>Upload Posting</span>
            </button>
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 font-semibold text-sm text-white shadow-md shadow-indigo-600/30 transition"
            >
              <Plus className="h-4 w-4" />
              <span>Paste Job Text</span>
            </button>
          </div>
        </div>

        {statusMessage && (
          <div
            className={`p-4 rounded-xl flex items-center justify-between gap-3 text-sm border ${
              statusMessage.type === "success"
                ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                : "bg-rose-500/10 border-rose-500/30 text-rose-300"
            }`}
          >
            <div className="flex items-center gap-2">
              {statusMessage.type === "success" ? (
                <CheckCircle2 className="h-5 w-5 shrink-0" />
              ) : (
                <AlertCircle className="h-5 w-5 shrink-0" />
              )}
              <span>{statusMessage.text}</span>
            </div>
            <button onClick={() => setStatusMessage(null)}>
              <X className="h-4 w-4 text-slate-400 hover:text-white" />
            </button>
          </div>
        )}

        {/* Master List & Detail View */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Job List */}
          <div className="lg:col-span-4 space-y-3">
            <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
              Saved Roles ({jobs.length})
            </h2>

            {isLoading ? (
              <div className="p-8 text-center bg-slate-900 border border-slate-800 rounded-xl">
                <Loader2 className="h-6 w-6 text-indigo-500 animate-spin mx-auto mb-2" />
                <p className="text-xs text-slate-400">Loading jobs...</p>
              </div>
            ) : jobs.length === 0 ? (
              <div className="p-8 text-center bg-slate-900 border border-dashed border-slate-800 rounded-xl">
                <Briefcase className="h-10 w-10 text-slate-600 mx-auto mb-2" />
                <p className="text-sm font-medium text-slate-300">No jobs saved yet</p>
                <p className="text-xs text-slate-500 mt-1">Paste a job posting or upload a file to extract requirements.</p>
              </div>
            ) : (
              jobs.map((job) => {
                const isSelected = selectedJob?.id === job.id;
                return (
                  <div
                    key={job.id}
                    onClick={() => setSelectedJob(job)}
                    className={`p-4 rounded-xl border cursor-pointer transition flex items-start justify-between gap-3 ${
                      isSelected
                        ? "bg-slate-800/80 border-indigo-500/60 shadow-md ring-1 ring-indigo-500/30"
                        : "bg-slate-900 border-slate-800 hover:border-slate-700 hover:bg-slate-850"
                    }`}
                  >
                    <div className="flex items-start gap-3 min-w-0">
                      <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 shrink-0 mt-0.5">
                        <Briefcase className="h-5 w-5" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-white truncate">{job.title}</p>
                        <p className="text-xs text-slate-400 mt-0.5">{job.company_name || "Company not specified"}</p>
                        <span
                          className={`inline-block mt-2 text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase ${
                            job.analysis_status === "completed"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : job.analysis_status === "processing"
                              ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                              : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                          }`}
                        >
                          {job.analysis_status}
                        </span>
                      </div>
                    </div>
                    <ChevronRight className={`h-4 w-4 shrink-0 mt-1 ${isSelected ? "text-indigo-400" : "text-slate-600"}`} />
                  </div>
                );
              })
            )}
          </div>

          {/* Job Requirements View */}
          <div className="lg:col-span-8">
            {selectedJob ? (
              <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900 shadow-sm space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                  <div>
                    <h3 className="text-lg font-bold text-white">{selectedJob.title}</h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {selectedJob.company_name || "Company Unspecified"} • Added {formatDate(selectedJob.created_at)}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleReanalyze(selectedJob.id)}
                      title="Re-run AI analysis"
                      className="p-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-200 transition"
                    >
                      <RefreshCw className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(selectedJob.id)}
                      title="Delete Job"
                      className="p-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-rose-500/20 hover:text-rose-400 text-slate-400 transition"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {selectedJob.structured_requirements ? (
                  <div className="space-y-6">
                    {/* Meta info */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs">
                      <div>
                        <span className="text-slate-400">Seniority</span>
                        <p className="font-semibold text-white mt-0.5">
                          {selectedJob.structured_requirements.seniority_level || "Not specified"}
                        </p>
                      </div>
                      <div>
                        <span className="text-slate-400">Employment</span>
                        <p className="font-semibold text-white mt-0.5">
                          {selectedJob.structured_requirements.employment_type || "Full-time"}
                        </p>
                      </div>
                      <div>
                        <span className="text-slate-400">Experience</span>
                        <p className="font-semibold text-white mt-0.5">
                          {selectedJob.structured_requirements.years_of_experience
                            ? `${selectedJob.structured_requirements.years_of_experience}+ Years`
                            : "Entry / Fresher"}
                        </p>
                      </div>
                      <div>
                        <span className="text-slate-400">Location</span>
                        <p className="font-semibold text-white mt-0.5 truncate">
                          {selectedJob.structured_requirements.location || "Remote / Flexible"}
                        </p>
                      </div>
                    </div>

                    {/* Must-have skills */}
                    <div>
                      <h4 className="text-xs font-semibold text-rose-400 uppercase tracking-wider mb-2">
                        Must-Have Required Skills ({selectedJob.structured_requirements.must_have_skills?.length || 0})
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedJob.structured_requirements.must_have_skills?.map((s, idx) => (
                          <span
                            key={idx}
                            className="px-2.5 py-1 rounded-md text-xs font-semibold bg-rose-500/10 border border-rose-500/20 text-rose-300"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Nice-to-have skills */}
                    {selectedJob.structured_requirements.nice_to_have_skills?.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-2">
                          Nice-to-Have / Preferred Skills
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {selectedJob.structured_requirements.nice_to_have_skills.map((s, idx) => (
                            <span
                              key={idx}
                              className="px-2.5 py-1 rounded-md text-xs font-semibold bg-indigo-500/10 border border-indigo-500/20 text-indigo-300"
                            >
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Responsibilities */}
                    {selectedJob.structured_requirements.responsibilities?.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                          Key Responsibilities
                        </h4>
                        <ul className="space-y-1.5 list-disc list-inside text-xs text-slate-300">
                          {selectedJob.structured_requirements.responsibilities.map((r, idx) => (
                            <li key={idx}>{r}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-400 whitespace-pre-wrap">
                    {selectedJob.raw_description}
                  </div>
                )}
              </div>
            ) : (
              <div className="p-12 text-center bg-slate-900 border border-dashed border-slate-800 rounded-2xl">
                <Briefcase className="h-12 w-12 text-slate-600 mx-auto mb-3" />
                <h3 className="text-base font-semibold text-white">Select a Job</h3>
                <p className="text-sm text-slate-400 mt-1 max-w-sm mx-auto">
                  Click on any target job from the list on the left to inspect required skills and requirements.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Add Job Modal */}
        {showAddModal && (
          <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-xl w-full p-6 shadow-2xl">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <h3 className="text-base font-bold text-white">Add Job Description</h3>
                <button onClick={() => setShowAddModal(false)}>
                  <X className="h-5 w-5 text-slate-400 hover:text-white" />
                </button>
              </div>

              <form onSubmit={handleCreatePastedJob} className="py-4 space-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300">Job Title</label>
                  <input
                    type="text"
                    required
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    placeholder="e.g. Junior Full-Stack Developer"
                    className="mt-1 w-full px-3.5 py-2 rounded-lg border border-slate-700 bg-slate-950 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300">Company Name (Optional)</label>
                  <input
                    type="text"
                    value={newCompany}
                    onChange={(e) => setNewCompany(e.target.value)}
                    placeholder="e.g. Stripe, Google, or Startup"
                    className="mt-1 w-full px-3.5 py-2 rounded-lg border border-slate-700 bg-slate-950 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300">Job Description Text</label>
                  <textarea
                    required
                    rows={6}
                    value={newDescription}
                    onChange={(e) => setNewDescription(e.target.value)}
                    placeholder="Paste the full job posting text here including responsibilities and technical requirements..."
                    className="mt-1 w-full px-3.5 py-2 rounded-lg border border-slate-700 bg-slate-950 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="px-4 py-2 rounded-lg border border-slate-700 bg-slate-800 text-xs font-semibold text-slate-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white flex items-center gap-2"
                  >
                    {isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
                    <span>Analyze Job</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
