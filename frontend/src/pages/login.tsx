import { useEffect } from "react";
import { getToken, isTokenExpired } from "../lib/auth";
import logo from "../assets/SonicAnalytics Logo.png";

export default function Login() {
  useEffect(() => {
    const token = getToken();
    if (token && !isTokenExpired(token)) {
      window.location.href = "/dashboard";
    }
  }, []);

  const handleLogin = () => {
    window.location.href = `${import.meta.env.VITE_API_URL}/v1/auth/login`;
  };

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center">
      {/* Logo */}
      <div className="mb-4 flex items-center justify-center w-20 h-20 rounded-full border border-green-500/40 bg-transparent">
        <img src={logo} alt="Logo" className="w-full h-full object-contain" />
      </div>

      <h1 className="text-white text-3xl font-bold mb-1">SoundPulse</h1>
      <p className="text-gray-400 text-sm mb-8">Spotify Analytics</p>

      {/* Card */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 w-full max-w-sm">
        <p className="text-gray-500 text-xs uppercase tracking-widest mb-1">Gateway</p>
        <p className="text-white text-base font-medium mb-6">Experience High-Fidelity Data</p>

        <button
          onClick={handleLogin}
          className="w-full flex items-center justify-center gap-2 bg-green-500 hover:bg-green-400 text-black font-semibold py-3 rounded-md transition-colors"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 3a9 9 0 100 18A9 9 0 0012 3zm4.13 12.96a.56.56 0 01-.77.19c-2.12-1.3-4.78-1.59-7.92-.87a.56.56 0 01-.25-1.09c3.43-.78 6.38-.45 8.75 1.01.27.16.35.5.19.76zm1.1-2.44a.7.7 0 01-.96.23C13.84 12.1 11 11.74 7.57 12.7a.7.7 0 01-.36-1.35c3.84-1.04 7.07-.59 9.65.94.33.2.44.62.23.96v-.03zm.1-2.54C14.5 9.2 10.37 9.08 7.04 10.06a.84.84 0 01-.48-1.61C10.17 7.4 14.72 7.55 18 9.4a.84.84 0 01-.77 1.5v.08z"/>
          </svg>
          Connect with Spotify
        </button>

        <div className="flex items-center gap-2 my-4">
          <div className="flex-1 h-px bg-zinc-700" />
          <span className="text-zinc-500 text-xs">Secure Authentication</span>
          <div className="flex-1 h-px bg-zinc-700" />
        </div>

        <p className="text-zinc-500 text-xs text-center">
          By connecting, you agree to our{" "}
          <span className="text-green-500 cursor-pointer hover:underline">Terms of Service</span>{" "}
          and{" "}
          <span className="text-green-500 cursor-pointer hover:underline">Privacy Policy</span>
        </p>
      </div>

      {/* Footer */}
      <p className="text-zinc-700 text-xs mt-8">© 2026 SOUNDPULSE. ALL RIGHTS RESERVED.</p>
    </div>
  );
}