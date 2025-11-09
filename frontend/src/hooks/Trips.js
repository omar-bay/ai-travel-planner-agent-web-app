import { API } from "../lib/api";
import { useCallback, useState } from "react";


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
