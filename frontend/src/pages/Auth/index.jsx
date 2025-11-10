import { useState } from "react";
import { Box, Card, CardContent, CardHeader, TextField, Button, Stack, Typography, Alert, Link } from "@mui/material";
import { useNavigate, useLocation } from "react-router-dom";
import { API } from "../../lib/api";
import { setToken } from "../../utils/auth";

export default function Auth() {
  const [mode, setMode] = useState("login"); // "login" | "signup"
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setErr] = useState("");
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/";

  const onChange = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const onSubmit = async (e) => {
    e.preventDefault();
    setErr("");
    setLoading(true);
    try {
      if (mode === "signup") {
        const res = await API.post("/auth/signup", {
          name: form.name.trim(),
          email: form.email.trim(),
          password: form.password,
        });
        const token = res.data?.access_token;
        if (token) setToken(token);
        navigate(from, { replace: true });
      } else {
        const res = await API.post("/auth/login", {
          email: form.email.trim(),
          password: form.password,
        });
        const token = res.data?.access_token;
        if (token) setToken(token);
        navigate(from, { replace: true });
      }
    } catch (e) {
      setErr(e?.response?.data?.detail || "Authentication failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: "100vh", display: "grid", placeItems: "center", px: 2 }}>
      <Card sx={{ width: "100%", maxWidth: 420 }}>
        <CardHeader
          title={mode === "login" ? "Log in to AI Travel" : "Create your AI Travel account"}
          subheader="Plan smarter trips with an AI assistant"
        />
        <CardContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <Box component="form" onSubmit={onSubmit}>
            <Stack spacing={2}>
              {mode === "signup" && (
                <TextField label="Name" value={form.name} onChange={onChange("name")} required />
              )}
              <TextField type="email" label="Email" value={form.email} onChange={onChange("email")} required />
              <TextField type="password" label="Password" value={form.password} onChange={onChange("password")} required />
              <Button type="submit" variant="contained" disabled={loading}>
                {loading ? "Please wait…" : mode === "login" ? "Log In" : "Sign Up"}
              </Button>
            </Stack>
          </Box>

          <Typography variant="body2" sx={{ mt: 2 }}>
            {mode === "login" ? "Don’t have an account? " : "Already have an account? "}
            <Link
              component="button"
              onClick={() => { setErr(""); setMode(mode === "login" ? "signup" : "login"); }}
            >
              {mode === "login" ? "Sign up" : "Log in"}
            </Link>
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}
