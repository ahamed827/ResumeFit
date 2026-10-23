"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useAuth } from "@/features/auth/AuthContext";
import { Sparkles, Loader2, AlertCircle } from "lucide-react";
import { UserRole } from "@/types";

const registerSchema = z.object({
  fullName: z.string().min(2, "Full name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  role: z.enum(["candidate", "recruiter"]),
});

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const { register: registerAuth } = useAuth();
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      role: "candidate",
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    setErrorMsg(null);
    try {
      await registerAuth(data.email, data.password, data.fullName, data.role as UserRole);
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || "Registration failed. Please try again.";
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
        <h2 className="text-xl font-bold tracking-tight text-white mt-4">Create your account</h2>
        <p className="mt-2 text-sm text-slate-400">
          Already registered?{" "}
          <Link href="/login" className="font-medium text-indigo-400 hover:text-indigo-300">
            Sign in here
          </Link>
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-slate-900 py-8 px-6 shadow-xl border border-slate-800 rounded-xl sm:px-10">
          {errorMsg && (
            <div className="mb-6 p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-rose-400 shrink-0 mt-0.5" />
              <p className="text-sm text-rose-300">{errorMsg}</p>
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit(onSubmit)}>
            <div>
              <label className="block text-sm font-medium text-slate-200">Full Name</label>
              <div className="mt-1">
                <input
                  type="text"
                  autoComplete="name"
                  {...register("fullName")}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-700 bg-slate-950 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                  placeholder="Alex Morgan"
                />
                {errors.fullName && (
                  <p className="mt-1.5 text-xs text-rose-400">{errors.fullName.message}</p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-200">Email address</label>
              <div className="mt-1">
                <input
                  type="email"
                  autoComplete="email"
                  {...register("email")}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-700 bg-slate-950 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                  placeholder="alex@example.com"
                />
                {errors.email && (
                  <p className="mt-1.5 text-xs text-rose-400">{errors.email.message}</p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-200">Password</label>
              <div className="mt-1">
                <input
                  type="password"
                  autoComplete="new-password"
                  {...register("password")}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-700 bg-slate-950 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                  placeholder="At least 8 characters"
                />
                {errors.password && (
                  <p className="mt-1.5 text-xs text-rose-400">{errors.password.message}</p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-200">I am a</label>
              <div className="mt-2 grid grid-cols-2 gap-3">
                <label className="flex items-center gap-2 p-3 rounded-lg border border-slate-700 bg-slate-950/60 cursor-pointer hover:border-indigo-500 transition">
                  <input
                    type="radio"
                    value="candidate"
                    {...register("role")}
                    className="text-indigo-600 focus:ring-indigo-500"
                  />
                  <span className="text-xs font-semibold text-slate-200">Job Seeker</span>
                </label>
                <label className="flex items-center gap-2 p-3 rounded-lg border border-slate-700 bg-slate-950/60 cursor-pointer hover:border-indigo-500 transition">
                  <input
                    type="radio"
                    value="recruiter"
                    {...register("role")}
                    className="text-indigo-600 focus:ring-indigo-500"
                  />
                  <span className="text-xs font-semibold text-slate-200">Recruiter</span>
                </label>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full mt-2 flex justify-center items-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition"
            >
              {isSubmitting ? <Loader2 className="h-5 w-5 animate-spin" /> : "Create Account"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
