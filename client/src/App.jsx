import React from "react";
import AppRoutes from "./routes";
import { ThemeProvider } from "./ThemeContext";
import { StoriesProvider } from "./StoriesContext";
import "./index.css";

function App() {
  return (
    <ThemeProvider>
      <StoriesProvider>
        <AppRoutes />
      </StoriesProvider>
    </ThemeProvider>
  );
}

export default App;