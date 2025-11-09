import { useEffect, useState, useCallback } from "react";
import {
  Box, Typography, Grid, Card, CardContent, CardActions, Button, Chip,
  Stack, Skeleton, Alert, Snackbar, Dialog, DialogTitle, DialogContent,
  DialogActions, Divider, IconButton
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import VisibilityIcon from "@mui/icons-material/Visibility";
import dayjs from "dayjs";
import { useSavedTrips, useDeleteTrip } from "../../hooks/Trips";

function TripCard({ trip, onView, onDelete }) {
  const snippet =
    (trip.recommendation || "").length > 160
      ? trip.recommendation.slice(0, 160) + "…"
      : trip.recommendation || "";

  return (
    <Card variant="outlined">
      <CardContent>
        <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 1 }}>
          <Typography variant="h6" sx={{ textTransform: "capitalize" }}>
            {trip.city || "custom"}
          </Typography>
          <Chip size="small" label={dayjs(trip.created_at).format("YYYY-MM-DD HH:mm")} />
        </Stack>
        <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: "pre-line" }}>
          {snippet}
        </Typography>
      </CardContent>
      <CardActions sx={{ justifyContent: "flex-end" }}>
        <Button startIcon={<VisibilityIcon />} onClick={() => onView(trip)}>
          View
        </Button>
        <Button color="error" startIcon={<DeleteIcon />} onClick={() => onDelete(trip)}>
          Delete
        </Button>
      </CardActions>
    </Card>
  );
}

export default function Trips() {
  const { data, loading, error, refetch, setData } = useSavedTrips();
  const { del, loading: deleting } = useDeleteTrip();

  const [toast, setToast] = useState({ open: false, message: "", severity: "success" });
  const [viewTrip, setViewTrip] = useState(null);
  const [confirmTrip, setConfirmTrip] = useState(null);

  useEffect(() => { refetch(); }, [refetch]);

  const handleConfirmDelete = useCallback(async () => {
    if (!confirmTrip) return;
    const id = confirmTrip.id;
    const ok = await del(id);
    if (ok) {
      setData((prev) => (prev || []).filter((t) => t.id !== id));
      setToast({ open: true, message: "Deleted.", severity: "success" });
    } else {
      setToast({ open: true, message: "Delete failed. Try again.", severity: "error" });
    }
    setConfirmTrip(null);
  }, [confirmTrip, del, setData]);

  return (
    <Box>
      <Stack spacing={1} sx={{ mb: 2 }}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>Trips</Typography>
        <Typography variant="body2" color="text.secondary">
          Browse your saved trips. View details or delete entries.
        </Typography>
      </Stack>

      {loading && (
        <Grid container spacing={2}>
          {Array.from({ length: 6 }).map((_, i) => (
            <Grid item xs={12} sm={6} md={4} key={i}>
              <Skeleton variant="rectangular" height={160} />
            </Grid>
          ))}
        </Grid>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to load trips. <Button onClick={refetch}>Retry</Button>
        </Alert>
      )}

      {!loading && !error && (!data || data.length === 0) && (
        <Alert severity="info">No trips saved yet.</Alert>
      )}

      {!loading && !error && data && data.length > 0 && (
        <Grid container spacing={2}>
          {data.map((trip) => (
            <Grid item xs={12} sm={6} md={4} key={trip.id}>
              <TripCard
                trip={trip}
                onView={setViewTrip}
                onDelete={setConfirmTrip}
              />
            </Grid>
          ))}
        </Grid>
      )}

      {/* View dialog */}
      <Dialog open={!!viewTrip} onClose={() => setViewTrip(null)} maxWidth="md" fullWidth>
        <DialogTitle>
          {viewTrip ? (viewTrip.city || "custom") : ""} — Recommendation
        </DialogTitle>
        <DialogContent dividers>
          <Typography variant="body1" sx={{ whiteSpace: "pre-line" }}>
            {viewTrip?.recommendation || ""}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewTrip(null)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Delete confirm */}
      <Dialog open={!!confirmTrip} onClose={() => setConfirmTrip(null)}>
        <DialogTitle>Delete this trip?</DialogTitle>
        <DialogContent dividers>
          <Typography variant="body2" color="text.secondary">
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmTrip(null)} color="inherit">Cancel</Button>
          <Button onClick={handleConfirmDelete} color="error" disabled={deleting}>
            {deleting ? "Deleting…" : "Delete"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Toast */}
      <Snackbar
        open={toast.open}
        autoHideDuration={3000}
        onClose={() => setToast((t) => ({ ...t, open: false }))}
        anchorOrigin={{ vertical: "top", horizontal: "right" }}
      >
        <Alert
          onClose={() => setToast((t) => ({ ...t, open: false }))}
          severity={toast.severity}
          variant="filled"
          sx={{ width: "100%" }}
        >
          {toast.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
