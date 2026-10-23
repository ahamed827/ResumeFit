"use client";

import React, { useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { api } from "@/lib/api";
import { Sparkles, Loader2, CheckCircle2, AlertCircle } from "lucide-react";

const resetSchema = z.object({
  newPassword: z.string().min(8, "Password must be at least 8 characters long"),
  confirmPassword: z.string(),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"],
});

type ResetFormData = z.infer<typeof resetSchema>;

function ResetPasswordContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "";

  const [success, setSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetFormData>({
    resolver: zodResolver(resetSchema),
  });

  const onSubmit = async (data: ResetFormData) => {
    if (!token) {
      setErrorMsg("Reset token is missing from URL.");
      return;
    }
    setErrorMsg(null);
    try {
      await api.post("/auth/reset-password", {
        token: token,
        new_password: data.newPassword,
      });
      setSuccess(true);
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || "Failed to reset password. The link may have expired.";
      setErrorMsg(msg);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link href="/" className="inline-flex items-center gap-2 font-bold text-2xl text-white mb-2">
          <div className="h-9 w-9 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-600/30">
            <Sparkles className="h-5 w-5" />
          </div>
          <span>Resume<span className="text-indigo-400">Fit</span></span>
        </Link>
        <h2 className="text-xl font-bold tracking-tight text-white mt-4">Create New Password</h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-slate-900 py-8 px-6 shadow-xl border border-slate-800 rounded-xl sm:px-10">
          {success ? (
            <div className="text-center py-4">
              <CheckCircle2 className="h-12 w-12 text-emerald-400 mx-auto mb-3" />
              <h3 className="text-base font-semibold text-white">Password Updated</h3>
              <p className="mt-2 text-sm text-slate-400">Your password has been changed successfully.</p>
              <Link
                href="/login"
                className="mt-6 inline-block text-sm font-semibold text-indigo-400 hover:text-indigo-300"
              >
                Sign In With New Password
              </Link>
            </div>
          ) : (
            <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
              {errorMsg && (
                <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-rose-400 shrink-0 mt-0.5" />
                  <p className="text-sm text-rose-300">{errorMsg}</p>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-slate-200">New Password</label>
                <div className="mt-1">
                  <input
                    type="password"
                    {...register("newPassword")}
                    className="w-full px-3.5 py-2.5 rounded-lg border border-slate-700 bg-slate-950 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                    placeholder="••••••••"
                  />
                  {errors.newPassword && (
                    <p className="mt-1.5 text-xs text-rose-400">{errors.newPassword.message}</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-200">Confirm Password</label>
                <div className="mt-1">
                  <input
                    type="password"
                    {...register("confirmPassword")}
                    className="w-full px-3.5 py-2.5 rounded-lg border border-slate-700 bg-slate-950 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                    placeholder="••••••••"
                  />
                  {errors.confirmPassword && (
                    <p className="mt-1.5 text-xs text-rose-400">{errors.confirmPassword.message}</p>
                  )}
                </div>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full flex justify-center items-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 transition"
              >
                {isSubmitting ? <Loader2 className="h-5 w-5 animate-spin" /> : "Set New Password"}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400">Loading...</div>}>
      <ResetPasswordContent />
    </Suspense>
  );
}
