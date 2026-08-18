import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";

import App from "./App.jsx";
import { Toast } from "./components/common/Toast.jsx";
import { store } from "./store/index.js";
import "./styles/index.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <Provider store={store}>
      <App />
      <Toast />
    </Provider>
  </StrictMode>
);
