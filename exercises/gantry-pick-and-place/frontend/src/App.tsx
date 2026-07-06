import "./App.css";
import { Controls } from "./components/Controls";
import { Footprint } from "./components/Footprint";
import { Dashboard } from "./components/Dashboard";
import { useTelemetry } from "./useTelemetry";

function App() {
  const { status, connected } = useTelemetry();

  const state = status?.state ?? "ready";

  return (
    <div className="layout">
      <section className="panel">
        <h2>Workspace</h2>
        <Footprint status={status} fault={state === "fault"} />
      </section>

      <section className="panel">
        <h2>Telemetry</h2>
        <Dashboard status={status} connected={connected} />
        <Controls cube={status?.cube} dest={status?.dest} state={state} connected={connected} />
      </section>
    </div>
  );
}

export default App
