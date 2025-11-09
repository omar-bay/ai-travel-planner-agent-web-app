import { useEffect, useMemo, useState } from "react";
import {
  Box, Card, CardActionArea, CardContent, CardMedia, Stack, Typography,
  Button, Dialog, DialogTitle, DialogContent, DialogActions, Chip,
  LinearProgress, Alert, Snackbar, Divider
} from "@mui/material";
import { useCities, useAskAgent, useSaveTrip } from "../../hooks/Home";

// a few fallback images (unsplash-like placeholders)
// replace with your own or serve from /public
const FALLBACK_IMAGES = [
  "https://images.unsplash.com/photo-1505764706515-aa95265c5abc?q=80&w=1600&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1505761671935-60b3a7427bad?q=80&w=1600&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1528909514045-2fa4ac7a08ba?q=80&w=1600&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1488646953014-85cb44e25828?q=80&w=1600&auto=format&fit=crop",
];

function CityCarousel({ items = [], onPick }) {
  return (
    <Box sx={{ overflowX: "auto", pb: 1 }}>
      <Stack direction="row" spacing={2} sx={{ minWidth: "100%", py: 1 }}>
        {items.map((item, idx) => {
          const img = FALLBACK_IMAGES[idx % FALLBACK_IMAGES.length];
          return (
            <Card key={`${item.city}-${idx}`} sx={{ minWidth: 280, flex: "0 0 auto" }}>
              <CardActionArea onClick={() => onPick(item.city)}>
                <CardMedia component="img" height="140" image={img} alt={item.title} />
                <CardContent>
                  <Typography variant="h6" sx={{ letterSpacing: 1.2 }}>
                    {String(item.title || item.city).toUpperCase()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Tap to plan a trip to {item.city}
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          );
        })}
      </Stack>
    </Box>
  );
}

function ResponseSection({ data }) {
  if (!data) return null;

  const { city, recommendations, forecast, itinerary, sources } = data;

  return (
    <Stack spacing={2}>
      <Typography variant="subtitle2" color="text.secondary">
        City: <strong>{city}</strong>
      </Typography>

      {Array.isArray(recommendations) && recommendations.length > 0 && (
        <Box>
          <Typography variant="h6" gutterBottom>Recommendations</Typography>
          <Stack spacing={1}>
            {recommendations.map((line, i) => (
              <Typography key={i} variant="body1">• {line}</Typography>
            ))}
          </Stack>
        </Box>
      )}

      {forecast && (
        <Box>
          <Typography variant="h6" gutterBottom>Forecast</Typography>
          <Typography variant="body1" sx={{ mb: 1 }}>
            {forecast.summary}
          </Typography>
          {forecast.advisories?.length ? (
            <Box sx={{ mb: 1 }}>
              <Typography variant="subtitle2">Advisories</Typography>
              <Stack spacing={0.5}>
                {forecast.advisories.map((a, i) => (
                  <Typography key={i} variant="body2">- {a}</Typography>
                ))}
              </Stack>
            </Box>
          ) : null}
          {forecast.pack_tips?.length ? (
            <Box>
              <Typography variant="subtitle2">Pack Tips</Typography>
              <Stack spacing={0.5}>
                {forecast.pack_tips.map((p, i) => (
                  <Typography key={i} variant="body2">- {p}</Typography>
                ))}
              </Stack>
            </Box>
          ) : null}
        </Box>
      )}

      {Array.isArray(itinerary) && itinerary.length > 0 && (
        <Box>
          <Typography variant="h6" gutterBottom>Itinerary</Typography>
          <Stack spacing={1.5}>
            {itinerary.map((d) => (
              <Card key={d.day} variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" sx={{ mb: 1 }}>Day {d.day}</Typography>
                  <Stack spacing={0.5}>
                    {d.morning && <Typography>Morning: {d.morning}</Typography>}
                    {d.afternoon && <Typography>Afternoon: {d.afternoon}</Typography>}
                    {d.evening && <Typography>Evening: {d.evening}</Typography>}
                  </Stack>
                </CardContent>
              </Card>
            ))}
          </Stack>
        </Box>
      )}

      {sources && (
        <>
          <Divider />
          <Box>
            <Typography variant="overline" display="block" gutterBottom>Sources</Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {sources.rag?.map((t, i) => <Chip key={`rag-${i}`} label={t} size="small" />)}
              {sources.weather?.map((t, i) => <Chip key={`wx-${i}`} label={t} size="small" color="info" />)}
            </Stack>
          </Box>
        </>
      )}
    </Stack>
  );
}

export default function Home() {
  const { data: cities, error: citiesError, loading: citiesLoading, refetch: refetchCities } = useCities();
  const { ask, loading: askLoading, error: askError, data: askData, clear: clearAsk } = useAskAgent();
  const { save, loading: saveLoading } = useSaveTrip();

  const [open, setOpen] = useState(false);
  const [toast, setToast] = useState({ open: false, message: "", severity: "success" });

  useEffect(() => {
    if (askData) setOpen(true);
  }, [askData]);

  const carouselItems = useMemo(() => {
    // expecting objects like { city: "barcelona", title: "Barcelona" }
    return (cities?.items || []).map((d) => ({
      city: String(d.city || "").toLowerCase(),
      title: d.title || d.city || "CITY",
    }));
  }, [cities]);

  const handlePickCity = (city) => {
    // your fixed example prompt + days=3
    ask({
      question: "Plan 3 days with food + must-see architecture, and tell me what to pack this week.",
      city,
      days: 3,
    });
  };

  const handleSave = async () => {
    if (!askData?.city) return;
    // the backend expects strings: city & recommendation
    // join recommendations array into a single string
    const recommendation =
      Array.isArray(askData.recommendations) && askData.recommendations.length
        ? askData.recommendations.join("\n")
        : JSON.stringify(askData);

    const ok = await save({ city: askData.city, recommendation });
    if (ok) {
      setToast({ open: true, message: "Trip saved successfully!", severity: "success" });
    } else {
      setToast({ open: true, message: "Couldn’t save the trip. Try again.", severity: "error" });
    }
  };

  return (
    <Box>
      <Stack spacing={2} sx={{ mb: 2 }}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>
          Home & Ask
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Pick a city from the carousel to generate a 3-day plan with food, architecture, and packing tips.
        </Typography>
      </Stack>

      {citiesLoading && <LinearProgress sx={{ mb: 2 }} />}
      {citiesError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to load cities. <Button onClick={refetchCities}>Retry</Button>
        </Alert>
      )}

      <CityCarousel items={carouselItems} onPick={handlePickCity} />

      {/* Response Modal */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>AI Recommendation</DialogTitle>
        <DialogContent dividers>
          {askLoading && <LinearProgress sx={{ mb: 2 }} />}
          {askError && <Alert severity="error">Failed to load recommendation. Try again.</Alert>}
          {!askLoading && !askError && <ResponseSection data={askData} />}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setOpen(false); clearAsk(); }} color="inherit">
            Close
          </Button>
          <Button onClick={handleSave} disabled={saveLoading} variant="contained">
            {saveLoading ? "Saving..." : "Save Trip"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Toasts */}
      <Snackbar
        open={toast.open}
        autoHideDuration={3500}
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
