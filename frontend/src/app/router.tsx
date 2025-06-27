import React, { Suspense, lazy } from "react";
import { Routes, Route, Outlet } from "react-router-dom";
import RequireAuth from "../components/Auth/RequireAuth";
import MainLayout from "../layouts/MainLayout";

const Home = lazy(() => import("../pages/Home/Home"));
const Login = lazy(() => import("../pages/Auth/Login"));
const Register = lazy(() => import("../pages/Auth/Register"));
const ArticleDetail = lazy(() => import("../pages/Article/ArticleDetail"));
const ArticleEdit = lazy(() => import("../pages/Article/ArticleEdit"));
const Profile = lazy(() => import("../pages/Profile/Profile"));
const Admin = lazy(() => import("../pages/Admin/Admin"));
const Search = lazy(() => import("../pages/Search/Search"));
const Debug = lazy(() => import("../pages/Debug/Debug"));
const LaTeXTest = lazy(() => import("../pages/Test/LaTeXTest"));
const CommentTest = lazy(() => import("../pages/Test/CommentTest"));
const NotFound = lazy(() => import("../pages/NotFound"));

const AppRouter: React.FC = () => (
  <Suspense fallback={<div>加载中...</div>}>
    <Routes>
      <Route element={<MainLayout><Outlet /></MainLayout>}>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/debug" element={<Debug />} />
        <Route path="/latex-test" element={<LaTeXTest />} />
        <Route path="/comment-test" element={<CommentTest />} />
        <Route path="/search" element={<Search />} />
        <Route path="/article/:id" element={<ArticleDetail />} />
        <Route path="/edit/:id" element={<RequireAuth><ArticleEdit /></RequireAuth>} />
        <Route path="/profile" element={<RequireAuth><Profile /></RequireAuth>} />
        <Route path="/admin" element={<RequireAuth role="admin"><Admin /></RequireAuth>} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  </Suspense>
);

export default AppRouter; 