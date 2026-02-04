import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App_test.jsx";
import RootProvider from "./context/RootProvider";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <RootProvider>
      <App />
    </RootProvider>
  </StrictMode>
);
