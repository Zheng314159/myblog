import { lazy } from "react";

const Debug = lazy(() => import("../pages/Debug/Debug"));
const LaTeXTest = lazy(() => import("../pages/Test/LaTeXTest"));
const CommentTest = lazy(() => import("../pages/Test/CommentTest"));
const OAuthTest = lazy(() => import("../pages/Test/OAuthTest"));
const ConfigTest = lazy(() => import("../pages/Test/ConfigTest"));
const PhysicsDiagramTest = lazy(
  () => import("../pages/Test/PhysicsDiagramTest")
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
