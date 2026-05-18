import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/login";
import Callback from "./pages/callback";
import Dashboard from "./pages/dashboard";
import Profile from "./pages/profile";
import Etl from "./pages/etl";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/navbar";

function ProtectedLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-zinc-950">
      <Navbar />
      <main className="ml-40 flex-1 p-6">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/callback" element={<Callback />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <ProtectedLayout><Dashboard /></ProtectedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProtectedLayout><Profile /></ProtectedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/etl"
          element={
            <ProtectedRoute>
              <ProtectedLayout><Etl /></ProtectedLayout>
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}