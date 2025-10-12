import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App.tsx";
import { Provider } from "./provider.tsx";
import { Auth0ProviderWithHistory } from "./components/auth/Auth0ProviderWithHistory.tsx";
import "@/styles/globals.css";
import "@/styles/index.css";
import "./i18n/config";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Auth0ProviderWithHistory>
        <Provider>
          <App />
        </Provider>
      </Auth0ProviderWithHistory>
    </BrowserRouter>
  </React.StrictMode>,
);
