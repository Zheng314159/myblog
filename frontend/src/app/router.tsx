import React, { Suspense, lazy } from "react";
import { Routes, Route, Outlet } from "react-router-dom";
import RequireAuth from "../components/Auth/RequireAuth";
import MainLayout from "../layouts/MainLayout";
import Media from '../pages/Media/Media';
import DonationResult from '../pages/Donation/DonationResult';

const Home = lazy(() => import("../pages/Home/Home"));
const Login = lazy(() => import("../pages/Auth/Login"));
const Register = lazy(() => import("../pages/Auth/Register"));
const ForgotPassword = lazy(() => import("../pages/Auth/ForgotPassword"));
const ResetPassword = lazy(() => import("../pages/Auth/ResetPassword"));
const OAuthCallback = lazy(() => import("../pages/Auth/OAuthCallback"));
const ArticleDetail = lazy(() => import("../pages/Article/ArticleDetail"));
const ArticleEdit = lazy(() => import("../pages/Article/ArticleEdit"));
const Profile = lazy(() => import("../pages/Profile/Profile"));
const Admin = lazy(() => import("../pages/Admin/Admin"));
const Search = lazy(() => import("../pages/Search/Search"));
const Debug = lazy(() => import("../pages/Debug/Debug"));
const LaTeXTest = lazy(() => import("../pages/Test/LaTeXTest"));
const CommentTest = lazy(() => import("../pages/Test/CommentTest"));
const OAuthTest = lazy(() => import("../pages/Test/OAuthTest"));
const ConfigTest = lazy(() => import("../pages/Test/ConfigTest"));
const DonationPage = lazy(() => import("../pages/Donation/DonationPage"));
const NotFound = lazy(() => import("../pages/NotFound"));
const PhysicsDiagramTest = lazy(() => import("../pages/Test/PhysicsDiagramTest"));

const AppRouter: React.FC = () => (
  <Suspense fallback={<div>加载中...</div>}>
    <Routes>
      <Route element={<MainLayout><Outlet /></MainLayout>}>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/oauth/callback" element={<OAuthCallback />} />
        <Route path="/debug" element={<Debug />} />
        <Route path="/latex-test" element={<LaTeXTest />} />
        <Route path="/comment-test" element={<CommentTest />} />
        <Route path="/oauth-test" element={<OAuthTest />} />
        <Route path="/config-test" element={<ConfigTest />} />
        <Route path="/physics-diagram-test" element={<PhysicsDiagramTest />} />
        <Route path="/search" element={<Search />} />
        <Route path="/article/:id" element={<ArticleDetail />} />
        <Route path="/edit/:id" element={<RequireAuth><ArticleEdit /></RequireAuth>} />
        <Route path="/profile" element={<RequireAuth><Profile /></RequireAuth>} />
        <Route path="/admin" element={<RequireAuth role="ADMIN"><Admin /></RequireAuth>} />
        <Route path="/media" element={<Media />} />
        <Route path="/donation" element={<DonationPage />} />
        <Route path="/donation/result" element={<DonationResult />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  </Suspense>
);

export default AppRouter; 