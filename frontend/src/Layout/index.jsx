import { Outlet } from "react-router-dom";
import { Link, NavLink } from "react-router-dom";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Avatar from "@mui/material/Avatar";
import Container from "@mui/material/Container";
import PersonIcon from "@mui/icons-material/Person";
import Button from "@mui/material/Button";

export default function Layout() {
  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
      <AppBar position="static" color="primary" elevation={1}>
        <Toolbar sx={{ justifyContent: "space-between" }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <Typography
              variant="h6"
              sx={{ fontWeight: 700, textDecoration: "none", color: "inherit" }}
              component={Link}
              to="/"
            >
              AI Travel
            </Typography>
            {/* Nav */}
            <Box sx={{ display: { xs: "none", sm: "flex" }, gap: 1 }}>
              <Button
                component={NavLink}
                to="/"
                color="inherit"
                sx={({ isActive }) => ({ opacity: isActive ? 1 : 0.7 })}
              >
                Home
              </Button>
              <Button
                component={NavLink}
                to="/trips"
                color="inherit"
                sx={({ isActive }) => ({ opacity: isActive ? 1 : 0.7 })}
              >
                Trips
              </Button>
            </Box>
          </Box>

          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Typography variant="body1" sx={{ display: { xs: "none", sm: "block" } }}>
              Omar
            </Typography>
            <IconButton color="inherit">
              <Avatar sx={{ width: 32, height: 32 }}>
                <PersonIcon fontSize="small" />
              </Avatar>
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Outlet />
      </Container>
    </Box>
  );
}
