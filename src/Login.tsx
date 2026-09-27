import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { AlertCircle, ArrowRight, Bus, ShieldCheck } from "lucide-react";
import api from "./api";

type Props = {
  onLogin: (token: string, user: { id: string | number; name: string; phone?: string; role: "ADMIN" | "COLLEGE" | "PARENT" | "STUDENT" | "DRIVER" }) => void;
};

export default function Login({ onLogin }: Props) {
  const location = useLocation();
  const routeState = location.state as { expired?: boolean; phone?: string } | null;
  const [phone, setPhone] = useState(routeState?.phone || "");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(routeState?.expired ? "Your session expired. Sign in again to continue." : "");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      const response = await api.post("/api/auth/login", {
        phone,
        password,
      });

      onLogin(response.data.access_token, response.data.user);
    } catch (err: any) {
      setError(
        err.response?.data?.error ||
          (err.response
            ? "Sign-in failed. Check your phone number and password."
            : "Unable to reach SmartBus. Check that the server is running.")
      );
    } finally {
      setLoading(false);
    }
  }

  return <main className="login-page">
    <section className="login-aside">
      <div className="login-brand"><span className="brand-mark"><Bus size={23} /></span><b>Smart<span>Bus</span></b></div>
      <div className="login-aside-copy"><span className="login-kicker">CAMPUS TRANSPORT, CONNECTED</span><h1>Every ride,<br />in view.</h1><p>Reliable campus mobility starts with clear information for the people who depend on it.</p></div>
      <div className="login-assurance"><ShieldCheck size={17} /> Private, role-based access</div>
    </section>
    <section className="login-main">
      <form className="login-card" onSubmit={handleLogin}>
        <div className="mobile-login-brand"><span className="brand-mark"><Bus size={20} /></span><b>Smart<span>Bus</span></b></div>
        <p className="eyebrow">ADMIN PORTAL</p>
        <h2>Welcome back</h2>
        <p className="login-intro">Sign in with your college admin credentials to manage buses, routes, students, drivers and parent links.</p>
        <label className="field"><span>Phone number</span><input type="tel" autoComplete="username" value={phone} onChange={(event) => setPhone(event.target.value)} placeholder="Enter your phone number" required /></label>
        <label className="field"><span>Password</span><input type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter your password" required /></label>
        {error && <div className="login-error"><AlertCircle size={17} /><span>{error}</span></div>}
        {success && <div className="login-success"><span>{success}</span></div>}
        <button className="button primary-button login-submit" type="submit" disabled={loading}>{loading ? "Signing in…" : "Sign in"}<ArrowRight size={17} /></button>
      </form>
      <span className="login-copyright">SMARTBUS · COLLEGE TRANSPORT SYSTEM</span>
    </section>
  </main>;
}