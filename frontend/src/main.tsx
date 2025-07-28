import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "./app/App";
import store from "./app/store";
import "antd/dist/reset.css";
import "./styles/global.css";
import "katex/dist/katex.min.css";
import { HelmetProvider } from "react-helmet-async";

// import { useLocation } from "react-router-dom";
// const location = useLocation();
// console.log("当前路由状态:",location.pathname);

const router = createBrowserRouter([
  {
    path: "*",
    element: <App />,
    // children: [
      // { path: "home", element: <Home /> },
      // { path: "about", element: <About /> },
    // ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <HelmetProvider>
      <Provider store={store}>
        <RouterProvider
          router={router}
          future={{
            v7_startTransition: true,
          }}
        />
      </Provider>
    </HelmetProvider>
  </React.StrictMode>
); 