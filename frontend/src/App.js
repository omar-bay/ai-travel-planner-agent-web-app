import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./Layout";
import Home from "./pages/Home";
import Trips from "./pages/Trips";
import Auth from "./pages/Auth";
import RequireAuth from "./components/RequireAuth";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Login / Sign up at root */}
        <Route path="/" element={<Auth />} />

        {/* Protected app routes */}
        <Route
          element={
            <RequireAuth>
              <Layout />
            </RequireAuth>
          }
        >
          <Route path="/home" element={<Home />} />
          <Route path="/trips" element={<Trips />} />
          {/* optional redirect if user hits /app root */}
          <Route path="/app" element={<Navigate to="/home" replace />} />
        </Route>

        {/* Fallback: anything else -> login */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
