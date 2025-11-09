import axios from "axios";
import { useCallback, useState } from "react";

// You can refactor to share this instance across hooks later.
const API = axios.create({
  baseURL: "http://localhost:8000/api",
  timeout: 30000,
});
API.interceptors.request.use((config) => {
  config.headers = config.headers || {};
  config.headers.Authorization =
    "Bearer " +
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzYyODAzMzUxfQ.QfJ13R4hHMURN70t4ZPihkCj3LAAtlZEeYRal0RS55Y";
  return config;
});

export function useSavedTrips() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setErr] = useState(null);

  const refetch = useCallback(async () => {
    setLoading(true);
    setErr(null);
    try {
      // Backend returns an array
      const res = await API.get("/saved-trips");
      setData(res.data || []);
    } catch (e) {
      setErr(e);
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, setData, loading, error, refetch };
}

export function useDeleteTrip() {
  const [loading, setLoading] = useState(false);

  const del = useCallback(async (id) => {
    setLoading(true);
    try {
      await API.delete(`/saved-trips/${id}`);
      return true;
    } catch (e) {
      console.error(e);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  return { del, loading };
}
