import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "./app/App";
import store from "./app/store";
import "antd/dist/reset.css";
import "./styles/global.css";
import "katex/dist/katex.min.css";

const router = createBrowserRouter([
  {
    path: "*",
    element: <App />,
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <Provider store={store}>
    <RouterProvider
      router={router}
      future={{
        v7_startTransition: true
      }}
    />
  </Provider>
); 