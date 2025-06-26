import React, { Suspense, lazy } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import RequireAuth from "../components/Auth/RequireAuth";

const Home = lazy(() => import("../pages/Home/Home"));
const Login = lazy(() => import("../pages/Auth/Login"));
const Register = lazy(() => import("../pages/Auth/Register"));
const ArticleDetail = lazy(() => import("../pages/Article/ArticleDetail"));
const ArticleEdit = lazy(() => import("../pages/Article/ArticleEdit"));
const Profile = lazy(() => import("../pages/Profile/Profile"));
const Admin = lazy(() => import("../pages/Admin/Admin"));
const NotFound = lazy(() => import("../pages/NotFound"));

const AppRouter: React.FC = () => (
  <Suspense fallback={<div>加载中...</div>}>
    <Routes>
      <Route path="/" element={<RequireAuth><Home /></RequireAuth>} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/article/:id" element={<ArticleDetail />} />
      <Route path="/edit/:id" element={<RequireAuth><ArticleEdit /></RequireAuth>} />
      <Route path="/profile" element={<RequireAuth><Profile /></RequireAuth>} />
      <Route path="/admin" element={<RequireAuth role="admin"><Admin /></RequireAuth>} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  </Suspense>
);

export default AppRouter; 