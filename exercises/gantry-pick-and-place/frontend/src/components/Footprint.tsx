import type { StatusResponse } from "../gen/app_pb";

const SIZE = 360;
const PAD = 30;
const PLOT = SIZE - PAD * 2;
const TABLE = 200;

interface Point {
  x: number;
  y: number;
  z: number;
}
const ORIGIN: Point = { x: 0, y: 0, z: 0 };
const DEFAULT_LIMITS: Point = { x: 1000, y: 1000, z: 1000 };

// Convert world coordinates (mm) into SVG pixel coordinates
const worldToSvgX = (xMm: number, xLimit: number) => PAD + (xMm / xLimit) * PLOT;
const worldToSvgY = (yMm: number, yLimit: number) => PAD + (1 - yMm / yLimit) * PLOT;
const worldToSvgLength = (lengthMm: number, limit: number) => (lengthMm / limit) * PLOT;


// Workspace rectangle and axes
function Workspace({ limits }: { limits: Point }) {
  return (
    <g>
      <rect x={PAD} y={PAD} width={PLOT} height={PLOT} fill="#f8fafc" stroke="#cbd5e1" strokeWidth={1.5} />
      <text x={PAD} y={SIZE - PAD + 16} fontSize={10} fill="#94a3b8">0</text>
      <text x={PAD + PLOT} y={SIZE - PAD + 16} fontSize={10} fill="#94a3b8" textAnchor="end">X {limits.x}</text>
      <text x={PAD} y={PAD - 8} fontSize={10} fill="#94a3b8">Y {limits.y}</text>
    </g>
  );
}

// Table marker and label
function Table({ at, label, limits }: { at: Point; label: string; limits: Point }) {
  const w = worldToSvgLength(TABLE, limits.x);
  const h = worldToSvgLength(TABLE, limits.y);
  return (
    <g>
      <rect
        x={worldToSvgX(at.x, limits.x) - w / 2}
        y={worldToSvgY(at.y, limits.y) - h / 2}
        width={w}
        height={h}
        rx={4}
        fill="#e2e8f0"
        stroke="#94a3b8"
        strokeWidth={1}
      />
      <text x={worldToSvgX(at.x, limits.x)} y={worldToSvgY(at.y, limits.y) - h / 2 - 4} textAnchor="middle" fontSize={12} fill="#475569">
        {label}
      </text>
    </g>
  );
}

function CubeMarker({ at, limits }: { at: Point; limits: Point }) {
  return (
    <g>
      <rect x={worldToSvgX(at.x, limits.x) - 7} y={worldToSvgY(at.y, limits.y) - 7} width={14} height={14} rx={2} fill="#f59e0b" stroke="#b45309" />
      <text x={worldToSvgX(at.x, limits.x)} y={worldToSvgY(at.y, limits.y) + 24} textAnchor="middle" fontSize={10} fill="#b45309">cube</text>
    </g>
  );
}

function DestMarker({ at, limits }: { at: Point; limits: Point }) {
  return (
    <g>
      <circle cx={worldToSvgX(at.x, limits.x)} cy={worldToSvgY(at.y, limits.y)} r={9} fill="none" stroke="#dc2626" strokeWidth={3} />
      <circle cx={worldToSvgX(at.x, limits.x)} cy={worldToSvgY(at.y, limits.y)} r={2} fill="#dc2626" />
      <text x={worldToSvgX(at.x, limits.x)} y={worldToSvgY(at.y, limits.y) + 24} textAnchor="middle" fontSize={10} fill="#dc2626">dest</text>
    </g>
  );
}

function RobotMarker({ at, color, limits }: { at: Point; color: string; limits: Point }) {
  const cx = worldToSvgX(at.x, limits.x);
  const cy = worldToSvgY(at.y, limits.y);
  return (
    <g>
      <line x1={cx - 12} y1={cy} x2={cx + 12} y2={cy} stroke={color} strokeWidth={2} />
      <line x1={cx} y1={cy - 12} x2={cx} y2={cy + 12} stroke={color} strokeWidth={2} />
      <circle cx={cx} cy={cy} r={6} fill={color} fillOpacity={0.85} />
    </g>
  );
}

// Vertical bar gauge showing the gantry's Z elevation
function ZGauge({ z, color, zLimit }: { z: number; color: string; zLimit: number }) {
  const fill = Math.max(0, Math.min(1, z / zLimit)) * PLOT;
  return (
    <g>
      <text x={SIZE + 35} y={PAD - 10} fontSize={10} fill="#94a3b8" textAnchor="middle">Z {zLimit}</text>
      <rect x={SIZE + 25} y={PAD} width={20} height={PLOT} fill="#f1f5f9" stroke="#cbd5e1" />
      <rect x={SIZE + 25} y={PAD + (PLOT - fill)} width={20} height={fill} fill={color} fillOpacity={0.7} />
      <text x={SIZE + 35} y={SIZE - PAD + 16} fontSize={10} fill="#475569" textAnchor="middle">
        {z.toFixed(0)}
      </text>
    </g>
  );
}

export function Footprint({ status, fault }: { status: StatusResponse | null; fault: boolean }) {
  const pos = (status?.position ?? ORIGIN) as Point;
  const cube = (status?.cube ?? ORIGIN) as Point;
  const dest = (status?.dest ?? ORIGIN) as Point;
  const raw = status?.robotLimits ?? [];
  const limits: Point = {
    x: raw[0] ?? DEFAULT_LIMITS.x,
    y: raw[1] ?? DEFAULT_LIMITS.y,
    z: raw[2] ?? DEFAULT_LIMITS.z,
  };

  const gantry = fault ? "#dc2626" : "#2563eb";

  return (
    <>
      <svg
        className="footprint"
        viewBox={`0 0 ${SIZE + 70} ${SIZE}`}
        role="img"
        aria-label="Top-down gantry workspace"
      >
        <Workspace limits={limits} />
        <Table at={cube} label="Table A" limits={limits} />
        <Table at={dest} label="Table B" limits={limits} />
        <CubeMarker at={cube} limits={limits} />
        <DestMarker at={dest} limits={limits} />
        <RobotMarker at={pos} color={gantry} limits={limits} />
        <ZGauge z={pos.z} color={gantry} zLimit={limits.z} />
      </svg>
      <div className="legend">
        <span><i className="dot dot-cube" /> Cube (Table A)</span>
        <span><i className="dot dot-dest" /> Destination (Table B)</span>
        <span><i className="dot dot-gantry" /> Gantry Robot</span>
      </div>
    </>
  );
}
