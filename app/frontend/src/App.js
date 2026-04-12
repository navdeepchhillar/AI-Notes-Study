import { useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import Dashboard from "./pages/Dashboard";
import { Toaster } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  useEffect(() => {
    const helloWorldApi = async () => {
      try {
        const response = await axios.get(`${API}/`);
        console.log("Backend connected:", response.data.message);
      } catch (e) {
        console.error("Backend connection failed:", e);
      }
    };

    helloWorldApi();
  }, []);

  return (
    <div className="App">
      <Toaster position="top-right" />

      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;