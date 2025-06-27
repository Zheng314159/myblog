import React from "react";
import Banner from "../components/Banner/Banner";
import Navbar from "../components/Navbar/Navbar";
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