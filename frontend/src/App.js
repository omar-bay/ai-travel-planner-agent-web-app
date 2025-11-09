import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./Layout";
import Home from "./pages/Home";
import Trips from "./pages/Trips";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="trips" element={<Trips />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
