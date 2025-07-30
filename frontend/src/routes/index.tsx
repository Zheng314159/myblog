import React, { Suspense } from "react";
import { Routes, Route, Outlet } from "react-router-dom";
import MainLayout from "../layouts/MainLayout.tsx";
import FullScreenLoader from "../components/Loader/FullScreenLoader.tsx";

import RequireAuth from "../components/Auth/RequireAuth.tsx";
import coreRoutes from "./coreRoutes.tsx";
import testRoutes from "./testRoutes.tsx";

const AppRouter: React.FC = () => (
  <Suspense fallback={<FullScreenLoader />}>
    <Routes>
      <Route element={<MainLayout><Outlet /></MainLayout>}>
        {coreRoutes.map(({ path, component: Component, auth, role }) => {
          const element = auth ? (
            <RequireAuth role={role}>
              <Component />
            </RequireAuth>
          ) : (
            <Component />
          );

          return <Route key={path} path={path} element={element} />;
        })}
      </Route>
      <Route
        element={
          <MainLayout>
            <Outlet />
          </MainLayout>
        }
      >
        {[...testRoutes].map(({ path, element }) => (
          <Route key={path} path={path} element={element} />
        ))}
      </Route>
    </Routes>
  </Suspense>
);

export default AppRouter;
