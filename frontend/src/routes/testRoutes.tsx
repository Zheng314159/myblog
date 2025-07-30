import { lazy } from "react";

const Debug = lazy(() => import("../pages/Debug/Debug.tsx"));
const LaTeXTest = lazy(() => import("../pages/Test/LaTeXTest.tsx"));
const CommentTest = lazy(() => import("../pages/Test/CommentTest.tsx"));
const OAuthTest = lazy(() => import("../pages/Test/OAuthTest.tsx"));
const ConfigTest = lazy(() => import("../pages/Test/ConfigTest.tsx"));
const PhysicsDiagramTest = lazy(
  () => import("../pages/Test/PhysicsDiagramTest.tsx")
);

const testRoutes = [
  { path: "/debug", element: <Debug /> },
  { path: "/latex-test", element: <LaTeXTest /> },
  { path: "/comment-test", element: <CommentTest /> },
  { path: "/oauth-test", element: <OAuthTest /> },
  { path: "/config-test", element: <ConfigTest /> },
  { path: "/physics-diagram-test", element: <PhysicsDiagramTest /> },
];

export default testRoutes;
