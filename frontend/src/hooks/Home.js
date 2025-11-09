import { API } from "../lib/api";
import { useCallback, useEffect, useState } from "react";


// ===== Cities (title, city) from documents =====
export function useCities() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setErr] = useState(null);

  const fetchCities = useCallback(async () => {
    setLoading(true);
    setErr(null);
    try {
      // Expecting backend to return [{ city: "barcelona", title: "Barcelona" }, ...]
      // This could be backed by SELECT city, title FROM documents
      const res = await API.get("/cities", {
        params: { fields: "city,title" },
      });
      setData(res.data || []);
    } catch (e) {
      setErr(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCities();
  }, [fetchCities]);

  return { data, loading, error, refetch: fetchCities };
}

// ===== Ask Agent (POST /api/agent/query) =====
export function useAskAgent() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setErr] = useState(null);

  const ask = useCallback(async ({ question, city, days }) => {
    setLoading(true);
    setErr(null);
    setData(null);
    try {
      const res = await API.post("/agent/query", { question, city, days });
      setData(res.data);
    } catch (e) {
      setErr(e);
    } finally {
      setLoading(false);
    }
  }, []);

  const clear = useCallback(() => {
    setData(null);
    setErr(null);
  }, []);

  return { ask, data, loading, error, clear };
}

// ===== Save Trip (POST /api/save-trip) =====
export function useSaveTrip() {
  const [loading, setLoading] = useState(false);

  const save = useCallback(async ({ city, recommendation }) => {
    setLoading(true);
    try {
      await API.post("/save-trip", { city, recommendation });
      return true;
    } catch (e) {
      console.error(e);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  return { save, loading };
}
