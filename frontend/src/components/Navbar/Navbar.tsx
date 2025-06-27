import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "../../app/store";
import { logout } from "../../features/user/userSlice";
import { TokenManager } from "../../utils/tokenManager";
import "./Navbar.css";

const Navbar: React.FC = () => {
  const isAuthenticated = useSelector((state: RootState) => state.user.isAuthenticated);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogout = () => {
    TokenManager.clearTokens();
    dispatch(logout());
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <NavLink to="/" className="nav-item">首页</NavLink>
      <NavLink to="/search" className="nav-item">标签</NavLink>
      {isAuthenticated && <NavLink to="/edit/new" className="nav-item">写文章</NavLink>}
      {isAuthenticated && <NavLink to="/profile" className="nav-item">我的</NavLink>}
      {!isAuthenticated ? (
        <NavLink to="/login" className="nav-item">登录</NavLink>
      ) : (
        <span className="nav-item" onClick={handleLogout} style={{ cursor: "pointer" }}>登出</span>
      )}
    </nav>
  );
};

export default Navbar; 