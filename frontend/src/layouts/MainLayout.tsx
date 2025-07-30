import React from "react";
import { Banner } from "../components/Banner/Banner.tsx";
import Navbar from "../components/Navbar/Navbar.tsx";
import "./MainLayout.css";

const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <>
    <header>
      <Banner />
      <nav>
        <Navbar />
      </nav>
    </header>
    <main>
      <div className="main-content">
        {children}
      </div>
    </main>
  </>
);

export default MainLayout; 