// src/router/coreRoutes.ts
import { lazy } from "react";

const Home = lazy(() => import("../pages/Home/Home.tsx"));
const Login = lazy(() => import("../pages/Auth/Login.tsx"));
const Register = lazy(() => import("../pages/Auth/Register.tsx"));
const ForgotPassword = lazy(() => import("../pages/Auth/ForgotPassword.tsx"));
const ResetPassword = lazy(() => import("../pages/Auth/ResetPassword.tsx"));
const OAuthCallback = lazy(() => import("../pages/Auth/OAuthCallback.tsx"));
const ArticleDetail = lazy(() => import("../pages/Article/ArticleDetail.tsx"));
const ArticleEdit = lazy(() => import("../pages/Article/ArticleEdit.tsx"));
const Profile = lazy(() => import("../pages/Profile/Profile.tsx"));
const Admin = lazy(() => import("../pages/Admin/Admin.tsx"));
const Search = lazy(() => import("../pages/Search/Search.tsx"));
const Media = lazy(() => import("../pages/Media/Media.tsx"));
const DonationPage = lazy(() => import("../pages/Donation/DonationPage.tsx"));
const DonationResult = lazy(() => import("../pages/Donation/DonationResult.tsx"));
const NotFound = lazy(() => import("../pages/NotFound.tsx"));

export interface RouteConfig {
  path: string;
  component: React.LazyExoticComponent<React.FC>;
  auth?: boolean;
  role?: string;
}

const coreRoutes: RouteConfig[] = [
  { path: "/", component: Home },
  { path: "/login", component: Login },
  { path: "/register", component: Register },
  { path: "/forgot-password", component: ForgotPassword },
  { path: "/reset-password", component: ResetPassword },
  { path: "/oauth/callback", component: OAuthCallback },
  { path: "/search", component: Search },
  { path: "/article/:id", component: ArticleDetail },
  { path: "/edit/:id", component: ArticleEdit, auth: true },
  { path: "/profile", component: Profile, auth: true },
  { path: "/admin", component: Admin, auth: true, role: "ADMIN" },
  { path: "/media", component: Media },
  { path: "/donation", component: DonationPage },
  { path: "/donation/result", component: DonationResult },
  { path: "*", component: NotFound },
];

export default coreRoutes;
