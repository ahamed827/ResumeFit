"use client";

import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";
import { Application, ApplicationStatus, Job } from "@/types";
import { formatDate } from "@/lib/utils";
import {
  CheckSquare,
  Plus,
  Search,
  Filter,
  Trash2,
  Calendar,
  Building,
  Loader2,
  ChevronRight,
  X,
  FileText
} from "lucide-react";

const STAGES: Array<{ key: ApplicationStatus; label: string; color: string }> = [
  { key: "saved", label: "Saved", color: "border-slate-700 bg-slate-800/40 text-slate-300" },
  { key: "applied", label: "Applied", color: "border-blue-500/30 bg-blue-500/10 text-blue-400" },
  { key: "screening", label: "Screening", color: "border-purple-500/30 bg-purple-500/10 text-purple-400" },
  { key: "interview", label: "Interview", color: "border-amber-500/30 bg-amber-500/10 text-amber-400" },
  { key: "technical_assessment", label: "Tech Assessment", color: "border-indigo-500/30 bg-indigo-500/10 text-indigo-400" },
  { key: "offer", label: "Offer", color: "border-emerald-500/30 bg-emerald-500/10 text-emerald-400" },
  { key: "rejected", label: "Rejected", color: "border-rose-500/30 bg-rose-500/10 text-rose-400" },
];

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedStatusFilter, setSelectedStatusFilter] = useState<string>("all");
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState("");
  const [newStatus, setNewStatus] = useState<ApplicationStatus>("saved");
  const [newNotes, setNewNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchApplications = async () => {
    try {
      const res = await api.get("/applications");
      setApplications(res.data.items);
    } catch (err) {
      console.error("Failed to load applications:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
    api.get("/jobs").then((res) => {
      setJobs(res.data.items);
      if (res.data.items.length > 0) setSelectedJobId(res.data.items[0].id);
    });
  }, []);

  const handleStatusChange = async (appId: string, status: ApplicationStatus) => {
    try {
      await api.patch(`/applications/${appId}`, { status });
      await fetchApplications();
    } catch (err) {
      console.error("Status update error:", err);
    }
  };

  const handleDelete = async (appId: string) => {
    if (!confirm("Remove application from tracker?")) return;
    try {
      await api.delete(`/applications/${appId}`);
      await fetchApplications();
    } catch (err) {
      console.error("Delete app error:", err);
    }
  };

  const handleCreateApplication = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedJobId) return;

    setIsSubmitting(true);
    try {
      await api.post("/applications", {
        job_id: selectedJobId,
        status: newStatus,
        notes: newNotes || undefined,
      });
      setShowAddModal(false);
      setNewNotes("");
      await fetchApplications();
    } catch (err) {
      console.error("Create application error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredApps = applications.filter((app) => {
    const matchesSearch =
      (app.job?.title || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
      (app.job?.company_name || "").toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = selectedStatusFilter === "all" || app.status === selectedStatusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Application Tracker</h1>
            <p className="text-sm text-slate-400 mt-1">
              Organize, update, and manage your job pipeline stages and interview notes.
            </p>
          </div>

          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 font-semibold text-sm text-white shadow-md shadow-indigo-600/30 transition self-start sm:self-auto"
          >
            <Plus className="h-4 w-4" />
            <span>Add Application</span>
          </button>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search by role or company..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-700 bg-slate-900 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <select
            value={selectedStatusFilter}
            onChange={(e) => setSelectedStatusFilter(e.target.value)}
            className="px-3.5 py-2 rounded-lg border border-slate-700 bg-slate-900 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">All Stages ({applications.length})</option>
            {STAGES.map((s) => (
              <option key={s.key} value={s.key}>
                {s.label}
              </option>
            ))}
          </select>
        </div>

        {/* Applications Grid / Board */}
        {isLoading ? (
          <div className="p-12 text-center bg-slate-900 border border-slate-800 rounded-2xl">
            <Loader2 className="h-8 w-8 text-indigo-500 animate-spin mx-auto mb-2" />
            <p className="text-sm text-slate-400">Loading applications...</p>
          </div>
        ) : filteredApps.length === 0 ? (
          <div className="p-12 text-center bg-slate-900 border border-dashed border-slate-800 rounded-2xl">
            <CheckSquare className="h-10 w-10 text-slate-600 mx-auto mb-2" />
            <p className="text-sm font-semibold text-white">No applications match your filter</p>
            <p className="text-xs text-slate-400 mt-1">Add target opportunities or adjust your search.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredApps.map((app) => (
              <div
                key={app.id}
                className="p-5 rounded-2xl border border-slate-800 bg-slate-900 shadow-sm flex flex-col justify-between space-y-4"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className="text-base font-bold text-white leading-snug">{app.job?.title || "Target Role"}</h3>
                      <p className="text-xs text-slate-400 flex items-center gap-1.5 mt-1">
                        <Building className="h-3.5 w-3.5 text-slate-500" />
                        <span>{app.job?.company_name || "Company Unspecified"}</span>
                      </p>
                    </div>

                    <button
                      onClick={() => handleDelete(app.id)}
                      title="Remove"
                      className="text-slate-500 hover:text-rose-400 p-1"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>

                  {app.notes && (
                    <div className="mt-3 p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300">
                      {app.notes}
                    </div>
                  )}
                </div>

                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1 text-slate-500">
                    <Calendar className="h-3.5 w-3.5" />
                    <span>{formatDate(app.created_at)}</span>
                  </div>

                  <select
                    value={app.status}
                    onChange={(e) => handleStatusChange(app.id, e.target.value as ApplicationStatus)}
                    className="px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-800 border border-slate-700 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 capitalize"
                  >
                    {STAGES.map((s) => (
                      <option key={s.key} value={s.key}>
                        {s.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Add Application Modal */}
        {showAddModal && (
          <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="text-base font-bold text-white">Track New Application</h3>
                <button onClick={() => setShowAddModal(false)}>
                  <X className="h-5 w-5 text-slate-400 hover:text-white" />
                </button>
              </div>

              {jobs.length === 0 ? (
                <div className="py-6 text-center text-xs text-slate-400">
                  Please add a job to your library first before tracking an application.
                </div>
              ) : (
                <form onSubmit={handleCreateApplication} className="py-4 space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-300">Select Job</label>
                    <select
                      value={selectedJobId}
                      onChange={(e) => setSelectedJobId(e.target.value)}
                      className="mt-1 w-full px-3.5 py-2 rounded-lg border border-slate-700 bg-slate-950 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      {jobs.map((j) => (
                        <option key={j.id} value={j.id}>
                          {j.title} {j.company_name ? `(${j.company_name})` : ""}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-300">Initial Stage</label>
                    <select
                      value={newStatus}
                      onChange={(e) => setNewStatus(e.target.value as ApplicationStatus)}
                      className="mt-1 w-full px-3.5 py-2 rounded-lg border border-slate-700 bg-slate-950 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      {STAGES.map((s) => (
                        <option key={s.key} value={s.key}>
                          {s.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-300">Notes / Deadlines (Optional)</label>
                    <textarea
                      rows={3}
                      value={newNotes}
                      onChange={(e) => setNewNotes(e.target.value)}
                      placeholder="e.g. Technical assessment link due on Friday; contacted recruiter on LinkedIn."
                      className="mt-1 w-full px-3.5 py-2 rounded-lg border border-slate-700 bg-slate-950 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>

                  <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
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
                      className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white"
                    >
                      {isSubmitting ? "Saving..." : "Save to Tracker"}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
