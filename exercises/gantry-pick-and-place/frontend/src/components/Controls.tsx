import { useEffect, useState } from "react";
import { client } from "../index";
import type { Position } from "../gen/app_pb";

// Position value input fields
function Axis({
  label,
  value,
  disabled,
  onChange,
}: {
  label: string;
  value: number;
  disabled: boolean;
  onChange: (value: number) => void;
}) {
  return (
    <label className="axis">
      {label}
      <input
        type="number"
        aria-label={label}
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(Number(e.target.value))}
      />
    </label>
  );
}

export function Controls({
  state,
  connected,
  cube,
  dest,
}: {
  state: string;
  connected: boolean;
  cube?: Position;
  dest?: Position;
}) {
  // Check for ready state
  const canControl = connected && state === "ready";

  const [cubeIn, setCubeIn] = useState({ x: cube?.x ?? 0, y: cube?.y ?? 0, z: cube?.z ?? 0 });
  const [destIn, setDestIn] = useState({ x: dest?.x ?? 0, y: dest?.y ?? 0, z: dest?.z ?? 0 });
  
  useEffect(() => {
    if (cube) setCubeIn({ x: cube.x, y: cube.y, z: cube.z });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cube?.x, cube?.y, cube?.z]);

  useEffect(() => {
    if (dest) setDestIn({ x: dest.x, y: dest.y, z: dest.z });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dest?.x, dest?.y, dest?.z]);

  // Fire a command and log any transport/RPC error to the console.
  const run = (fn: () => Promise<unknown>) => () => {
    fn().catch((err) => console.error(err));
  };

  const setCube = run(() => client.set_cube_position(cubeIn));
  const setDest = run(() => client.set_destination_position(destIn));

  return (
    <div className="commands">
      <fieldset disabled={!canControl}>
        <legend>Cube start (Table A)</legend>
        <div className="axes">
          <Axis label="X" value={cubeIn.x} disabled={!canControl} onChange={(x) => setCubeIn({ ...cubeIn, x })} />
          <Axis label="Y" value={cubeIn.y} disabled={!canControl} onChange={(y) => setCubeIn({ ...cubeIn, y })} />
          <Axis label="Z" value={cubeIn.z} disabled={!canControl} onChange={(z) => setCubeIn({ ...cubeIn, z })} />
          <button type="button" onClick={setCube}>Set cube</button>
        </div>
      </fieldset>

      <fieldset disabled={!canControl}>
        <legend>Destination (Table B)</legend>
        <div className="axes">
          <Axis label="X" value={destIn.x} disabled={!canControl} onChange={(x) => setDestIn({ ...destIn, x })} />
          <Axis label="Y" value={destIn.y} disabled={!canControl} onChange={(y) => setDestIn({ ...destIn, y })} />
          <Axis label="Z" value={destIn.z} disabled={!canControl} onChange={(z) => setDestIn({ ...destIn, z })} />
          <button type="button" onClick={setDest}>Set dest</button>
        </div>
      </fieldset>

      <div className="command-buttons">
        <button type="button" className="btn-start" disabled={!canControl} onClick={run(() => client.start_sequence({}))}>
          Start Pick and Place Sequence
        </button>
         <button type="button" className="btn-home" disabled={!canControl} onClick={run(() => client.home({}))}>
          Start Home Sequence
        </button>
      </div>
    </div>
  );
}
