import React from "react";
import PhysicsDiagram from "../../components/Banner/PhysicsDiagram";

const PhysicsDiagramTest: React.FC = () => (
  <div style={{ width: "100vw", height: "100vh", background: "#fff", display: "flex", alignItems: "center", justifyContent: "center" }}>
    <div style={{ width: "90vw", height: "90vh", border: "1px solid #ccc", background: "#fff" }}>
      <PhysicsDiagram />
    </div>
  </div>
);

export default PhysicsDiagramTest; 