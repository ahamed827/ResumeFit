"use client";

import React, { useEffect, useState, useRef } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";
import { Resume, StructuredResumeProfile } from "@/types";
import { formatDate } from "@/lib/utils";
import {
  FileText,
  Upload,
  RefreshCw,
  Trash2,
  Edit3,
  CheckCircle2,
  AlertCircle,
  Loader2,
  FileCheck,
  ChevronRight,
  X,
  Plus
} from "lucide-react";

export default function ResumesPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedResume, setSelectedResume] = useState<Resume | null>(null);
  const [editingResume, setEditingResume] = useState<Resume | null>(null);
  const [editSkillsInput, setEditSkillsInput] = useState("");
  const [statusMessage, setStatusMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchResumes = async () => {
    try {
      const res = await api.get("/resumes");
      setResumes(res.data.items);
      if (res.data.items.length > 0 && !selectedResume) {
        setSelectedResume(res.data.items[0]);
      }
    } catch (err) {
      console.error("Failed to fetch resumes:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchResumes();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      setStatusMessage({ type: "error", text: "File size exceeds maximum allowed 5 MB." });
      return;
    }

    setIsUploading(true);
    setStatusMessage(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await api.post("/resumes/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setStatusMessage({ type: "success", text: "Resume uploaded and processed successfully!" });
      await fetchResumes();
      setSelectedResume(res.data);
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || "Failed to upload and extract resume.";
      setStatusMessage({ type: "error", text: msg });
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleReparse = async (id: string) => {
    try {
      const res = await api.post(`/resumes/${id}/reparse`);
      setStatusMessage({ type: "success", text: "Resume re-parsed successfully!" });
      await fetchResumes();
      if (selectedResume?.id === id) setSelectedResume(res.data);
    } catch (err: any) {
      setStatusMessage({ type: "error", text: "Failed to re-parse resume." });
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this resume?")) return;
    try {
      await api.delete(`/resumes/${id}`);
      setStatusMessage({ type: "success", text: "Resume deleted." });
      if (selectedResume?.id === id) setSelectedResume(null);
      await fetchResumes();
    } catch (err: any) {
      setStatusMessage({ type: "error", text: "Failed to delete resume." });
    }
  };

  const openEditModal = (resume: Resume) => {
    setEditingResume(resume);
    setEditSkillsInput((resume.structured_profile?.skills || []).join(", "));
  };

  const handleSaveProfile = async () => {
    if (!editingResume || !editingResume.structured_profile) return;
    const updatedSkills = editSkillsInput
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    const updatedProfile: StructuredResumeProfile = {
      ...editingResume.structured_profile,
      skills: updatedSkills,
    };

    try {
      const res = await api.patch(`/resumes/${editingResume.id}`, {
        structured_profile: updatedProfile,
      });
      setStatusMessage({ type: "success", text: "Resume profile updated!" });
      setEditingResume(null);
      await fetchResumes();
      if (selectedResume?.id === editingResume.id) setSelectedResume(res.data);
    } catch (err) {
      setStatusMessage({ type: "error", text: "Failed to update resume profile." });
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header and Upload Action */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Resume Library</h1>
            <p className="text-sm text-slate-400 mt-1">
              Upload PDF or DOCX resumes (up to 5MB). View extracted profiles and structured skills.
            </p>
          </div>

          <div>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".pdf,.docx,.doc"
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 font-semibold text-sm text-white shadow-md shadow-indigo-600/30 disabled:opacity-50 transition"
            >
              {isUploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
              <span>{isUploading ? "Extracting Profile..." : "Upload Resume"}</span>
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

        {/* Layout: Master List and Detail View */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* List of resumes */}
          <div className="lg:col-span-4 space-y-3">
            <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
              Uploaded Documents ({resumes.length})
            </h2>

            {isLoading ? (
              <div className="p-8 text-center bg-slate-900 border border-slate-800 rounded-xl">
                <Loader2 className="h-6 w-6 text-indigo-500 animate-spin mx-auto mb-2" />
                <p className="text-xs text-slate-400">Loading documents...</p>
              </div>
            ) : resumes.length === 0 ? (
              <div className="p-8 text-center bg-slate-900 border border-dashed border-slate-800 rounded-xl">
                <FileText className="h-10 w-10 text-slate-600 mx-auto mb-2" />
                <p className="text-sm font-medium text-slate-300">No resumes uploaded yet</p>
                <p className="text-xs text-slate-500 mt-1">Upload a PDF or DOCX to see parsed skills.</p>
              </div>
            ) : (
              resumes.map((resume) => {
                const isSelected = selectedResume?.id === resume.id;
                return (
                  <div
                    key={resume.id}
                    onClick={() => setSelectedResume(resume)}
                    className={`p-4 rounded-xl border cursor-pointer transition flex items-start justify-between gap-3 ${
                      isSelected
                        ? "bg-slate-800/80 border-indigo-500/60 shadow-md ring-1 ring-indigo-500/30"
                        : "bg-slate-900 border-slate-800 hover:border-slate-700 hover:bg-slate-850"
                    }`}
                  >
                    <div className="flex items-start gap-3 min-w-0">
                      <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 shrink-0 mt-0.5">
                        <FileText className="h-5 w-5" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-white truncate">{resume.original_filename}</p>
                        <p className="text-xs text-slate-400 mt-0.5">Uploaded {formatDate(resume.created_at)}</p>
                        <div className="mt-2 flex items-center gap-2">
                          <span
                            className={`text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase ${
                              resume.extraction_status === "completed"
                                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                : resume.extraction_status === "processing"
                                ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                                : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                            }`}
                          >
                            {resume.extraction_status}
                          </span>
                        </div>
                      </div>
                    </div>

                    <ChevronRight className={`h-4 w-4 shrink-0 mt-1 ${isSelected ? "text-indigo-400" : "text-slate-600"}`} />
                  </div>
                );
              })
            )}
          </div>

          {/* Detailed view of selected resume */}
          <div className="lg:col-span-8">
            {selectedResume ? (
              <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900 shadow-sm space-y-6">
                {/* Header Controls */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                  <div>
                    <h3 className="text-lg font-bold text-white">{selectedResume.original_filename}</h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      File size: {(selectedResume.file_size_bytes / 1024).toFixed(1)} KB • MIME: {selectedResume.mime_type}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => openEditModal(selectedResume)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition"
                    >
                      <Edit3 className="h-3.5 w-3.5" />
                      <span>Edit Skills</span>
                    </button>
                    <button
                      onClick={() => handleReparse(selectedResume.id)}
                      title="Re-run AI extraction"
                      className="p-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-200 transition"
                    >
                      <RefreshCw className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(selectedResume.id)}
                      title="Delete Resume"
                      className="p-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-rose-500/20 hover:text-rose-400 text-slate-400 transition"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {selectedResume.parsing_error && (
                  <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-start gap-2">
                    <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold">Extraction Notice</p>
                      <p className="text-xs mt-0.5">{selectedResume.parsing_error}</p>
                    </div>
                  </div>
                )}

                {selectedResume.structured_profile ? (
                  <div className="space-y-6">
                    {/* Candidate Basic Info */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 rounded-xl bg-slate-950 border border-slate-800">
                      <div>
                        <span className="text-xs text-slate-400">Full Name</span>
                        <p className="text-sm font-semibold text-white">{selectedResume.structured_profile.full_name || "N/A"}</p>
                      </div>
                      <div>
                        <span className="text-xs text-slate-400">Email Address</span>
                        <p className="text-sm font-semibold text-white">{selectedResume.structured_profile.email || "N/A"}</p>
                      </div>
                      <div>
                        <span className="text-xs text-slate-400">LinkedIn</span>
                        <p className="text-sm font-semibold text-indigo-400 truncate">
                          {selectedResume.structured_profile.linkedin || "N/A"}
                        </p>
                      </div>
                      <div>
                        <span className="text-xs text-slate-400">GitHub</span>
                        <p className="text-sm font-semibold text-indigo-400 truncate">
                          {selectedResume.structured_profile.github || "N/A"}
                        </p>
                      </div>
                    </div>

                    {/* Extracted Skills Badges */}
                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                        Extracted Skills ({selectedResume.structured_profile.skills?.length || 0})
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedResume.structured_profile.skills?.length ? (
                          selectedResume.structured_profile.skills.map((skill, idx) => (
                            <span
                              key={idx}
                              className="px-2.5 py-1 rounded-md text-xs font-semibold bg-indigo-500/10 border border-indigo-500/20 text-indigo-300"
                            >
                              {skill}
                            </span>
                          ))
                        ) : (
                          <span className="text-xs text-slate-500">No skills identified.</span>
                        )}
                      </div>
                    </div>

                    {/* Featured Projects */}
                    {selectedResume.structured_profile.projects?.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                          Extracted Projects
                        </h4>
                        <div className="space-y-3">
                          {selectedResume.structured_profile.projects.map((proj, idx) => (
                            <div key={idx} className="p-3.5 rounded-lg bg-slate-950 border border-slate-800">
                              <p className="text-sm font-semibold text-white">{proj.name}</p>
                              {proj.description && <p className="text-xs text-slate-400 mt-1">{proj.description}</p>}
                              {proj.technologies_used?.length > 0 && (
                                <div className="mt-2 flex flex-wrap gap-1.5">
                                  {proj.technologies_used.map((t, i) => (
                                    <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                                      {t}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Education */}
                    {selectedResume.structured_profile.education?.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Education</h4>
                        <div className="space-y-2">
                          {selectedResume.structured_profile.education.map((edu, idx) => (
                            <div key={idx} className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex justify-between text-xs">
                              <div>
                                <span className="font-semibold text-white">{edu.degree} in {edu.field_of_study}</span>
                                <p className="text-slate-400">{edu.institution}</p>
                              </div>
                              <span className="text-slate-400">{edu.graduation_year}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="py-8 text-center text-slate-500 text-sm">
                    No structured profile available for this document.
                  </div>
                )}
              </div>
            ) : (
              <div className="p-12 text-center bg-slate-900 border border-dashed border-slate-800 rounded-2xl">
                <FileCheck className="h-12 w-12 text-slate-600 mx-auto mb-3" />
                <h3 className="text-base font-semibold text-white">Select a Resume</h3>
                <p className="text-sm text-slate-400 mt-1 max-w-sm mx-auto">
                  Click on an uploaded resume from the left pane to view verified extraction details.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Edit Skills Modal */}
        {editingResume && (
          <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <h3 className="text-base font-bold text-white">Edit Extracted Skills</h3>
                <button onClick={() => setEditingResume(null)}>
                  <X className="h-5 w-5 text-slate-400 hover:text-white" />
                </button>
              </div>
              <div className="py-4 space-y-3">
                <label className="text-xs text-slate-400">Comma-separated list of technical skills:</label>
                <textarea
                  value={editSkillsInput}
                  onChange={(e) => setEditSkillsInput(e.target.value)}
                  rows={4}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-700 bg-slate-950 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  onClick={() => setEditingResume(null)}
                  className="px-4 py-2 rounded-lg border border-slate-700 bg-slate-800 text-xs font-semibold text-slate-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveProfile}
                  className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
