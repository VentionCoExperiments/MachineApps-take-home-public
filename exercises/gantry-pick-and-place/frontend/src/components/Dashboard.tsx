import type { StatusResponse } from "../gen/app_pb";

function Card({ label, value }: { label: string; value: string }) {
  return (
    <div className="card">
      <span className="card-label">{label}</span>
      <span className="card-value">{value}</span>
    </div>
  );
}

function formatPositionValue(value?: number): string {
  return value === undefined ? "-" : value.toFixed(2);
}

function formatState(state: string): string {
  return state.charAt(0).toUpperCase() + state.slice(1);
}

// Dashboard for telemetry info
export function Dashboard({ status, connected }: { status: StatusResponse | null; connected: boolean }) {
  const state = status?.state ?? "ready";
  const pos = status?.position;
  const gripper = status?.gripper ?? "-";
  const moving = status?.moving ?? false;
  const error = status?.error ?? "";

  return (
    <>
      <div className="cards">
        <Card label="Position X" value={formatPositionValue(pos?.x)} />
        <Card label="Position Y" value={formatPositionValue(pos?.y)} />
        <Card label="Position Z" value={formatPositionValue(pos?.z)} />
        <Card label="Gripper" value={gripper} />
        <Card label="Motion" value={moving ? "Moving" : "Idle"} />
        <Card label="State" value={formatState(state)} />
        <Card label="Connected" value={connected ? "Yes" : "No"} />
        <Card label="Error" value={error} />
      </div>
      <div className="cards cards-config">
        <Card label="Cube start" value={`${formatPositionValue(status?.cube?.x)}, ${formatPositionValue(status?.cube?.y)}, ${formatPositionValue(status?.cube?.z)}`} />
        <Card label="Destination" value={`${formatPositionValue(status?.dest?.x)}, ${formatPositionValue(status?.dest?.y)}, ${formatPositionValue(status?.dest?.z)}`} />
      </div>
    </>
  );
}
