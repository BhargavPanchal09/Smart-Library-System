"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Library, ArrowRight, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { signInWithPopup, OAuthProvider, signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "@/lib/firebase";
import AuroraShaders from "@/components/ui/aurora";

export default function LoginPage() {
  const router = useRouter();
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  
  // States for your existing inputs
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const handleStandardLogin = async () => {
  setIsAuthenticating(true);
    try {
      const result = await signInWithEmailAndPassword(auth, email, password);
      const token = await result.user.getIdToken();
      sessionStorage.setItem("library_auth_token", token);
      router.push("/dashboard");
    } catch (error) {
      console.error("Login failed:", error);
    } finally {
      setIsAuthenticating(false);
    }
  };

  const handleMicrosoftLogin = async () => {
    setIsAuthenticating(true);
    try {
      const provider = new OAuthProvider('microsoft.com');
      provider.setCustomParameters({ tenant: 'd1b99a31-59dc-4039-b9c4-f6166b6bf0a4' });
      const result = await signInWithPopup(auth, provider);
      const token = await result.user.getIdToken();
      sessionStorage.setItem("library_auth_token", token);
      router.push("/dashboard");
    } catch (error) {
      console.error("SSO failed:", error);
    } finally {
      setIsAuthenticating(false);
    }
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-slate-50">
      <div className="absolute inset-0 z-0 opacity-40">
        {isMounted && (
          <AuroraShaders 
            speed={0.5} intensity={0.8} vibrancy={0.6} stretch={1.5}
            className="w-full h-full"
          />
        )}
      </div>

      <div className="relative z-10 flex min-h-screen w-full items-center justify-center px-4 font-sans text-slate-900">
        <motion.div 
          initial={{ opacity: 0, y: 40, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ type: "spring", stiffness: 260, damping: 20 }}
          className="w-full max-w-md bg-white/70 backdrop-blur-3xl border border-white/80 rounded-3xl p-8 md:p-10 shadow-[0_20px_60px_-15px_rgba(0,0,0,0.1)]"
        >
          <div className="flex flex-col items-center mb-10 text-center">
            <div className="w-14 h-14 bg-slate-900 text-white rounded-2xl flex items-center justify-center mb-6 shadow-xl shadow-slate-900/20">
              <Library className="w-7 h-7" />
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 mb-2">Welcome back</h1>
            <p className="text-sm font-medium text-slate-500">Enter your credentials to access the archives.</p>
          </div>

          <div className="space-y-5">
            <div className="space-y-4">
              <div className="relative">
                <input 
                  type="text" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  id="identifier" 
                  className="block px-4 pb-2.5 pt-6 w-full text-sm text-slate-900 bg-white/60 rounded-xl border border-slate-200 appearance-none focus:outline-none focus:ring-0 focus:border-slate-900 focus:bg-white peer transition-colors shadow-sm" 
                  placeholder=" " 
                />
                <label htmlFor="identifier" className="absolute text-sm text-slate-400 duration-300 transform -translate-y-3 scale-75 top-4 z-10 origin-[0] left-4 peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-3 font-medium cursor-text">
                  Student ID or Email
                </label>
              </div>

              <div className="relative">
                <input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  id="password" 
                  className="block px-4 pb-2.5 pt-6 w-full text-sm text-slate-900 bg-white/60 rounded-xl border border-slate-200 appearance-none focus:outline-none focus:ring-0 focus:border-slate-900 focus:bg-white peer transition-colors shadow-sm" 
                  placeholder=" " 
                />
                <label htmlFor="password" className="absolute text-sm text-slate-400 duration-300 transform -translate-y-3 scale-75 top-4 z-10 origin-[0] left-4 peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-3 font-medium cursor-text">
                  Password
                </label>
              </div>
            </div>

            <div className="flex items-center justify-between text-sm mt-2 mb-6">
              <label className="flex items-center gap-2 cursor-pointer group">
                <input type="checkbox" className="w-4 h-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900" />
                <span className="text-slate-500 font-medium group-hover:text-slate-700 transition-colors">Remember me</span>
              </label>
              <a href="#" className="font-semibold text-slate-900 hover:text-slate-600 transition-colors">Forgot password?</a>
            </div>

            <button 
              onClick={handleStandardLogin}
              disabled={isAuthenticating}
              className="w-full flex items-center justify-center gap-2 py-4 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-semibold tracking-wide transition-all active:scale-[0.98] shadow-lg shadow-slate-900/20"
            >
              {isAuthenticating ? <Loader2 className="w-5 h-5 animate-spin" /> : <>Sign In <ArrowRight className="w-4 h-4" /></>}
            </button>

            <div className="relative flex items-center py-6">
              <div className="grow border-t border-slate-200"></div>
              <span className="shrink-0 mx-4 text-xs font-semibold text-slate-400 uppercase tracking-widest">or</span>
              <div className="grow border-t border-slate-200"></div>
            </div>

            <button 
              onClick={handleMicrosoftLogin}
              disabled={isAuthenticating}
              className="w-full flex items-center justify-center gap-3 py-3.5 bg-white hover:bg-slate-50 border border-slate-200 rounded-xl font-semibold text-sm text-slate-700 transition-colors shadow-sm active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {!isAuthenticating && (
                <svg className="w-5 h-5" viewBox="0 0 21 21" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M10 0H0V10H10V0Z" fill="#F25022"/><path d="M21 0H11V10H21V0Z" fill="#7FBA00"/><path d="M10 11H0V21H10V11Z" fill="#00A4EF"/><path d="M21 11H11V21H21V11Z" fill="#FFB900"/>
                </svg>
              )}
              {isAuthenticating ? <Loader2 className="w-5 h-5 animate-spin" /> : "Continue with University SSO"}
            </button>
          </div>

          <p className="text-center text-sm text-slate-500 font-medium mt-10">
            Don't have an account? <a href="#" className="font-bold text-slate-900 hover:underline">Request access</a>
          </p>
        </motion.div>
      </div>
    </div>
  );
}