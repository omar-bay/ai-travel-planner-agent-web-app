import { Navigate, useLocation } from "react-router-dom";
import { isTokenValid } from "../utils/auth";

export default function RequireAuth({ children }) {
  const location = useLocation();
  if (!isTokenValid()) {
    // send to root login; keep location for future redirect if desired
    return <Navigate to="/auth" replace state={{ from: location }} />;
    }
  return children;
}
