import { useEffect, useState } from "react";
import { client } from "./index";
import type { StatusResponse } from "./gen/app_pb";

export interface Telemetry {
  status: StatusResponse | null;
  connected: boolean;
}

/**
 * Subscribe to the backend `status_info` server-stream and expose the latest
 * status. Reconnects automatically if the stream drops.
 */
export function useTelemetry(): Telemetry {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const abort = new AbortController();
    let cancelled = false;

    (async () => {
      while (!cancelled) {
        try {
          for await (const msg of client.telemetry({}, { signal: abort.signal })) {
            setConnected(true);
            setStatus(msg);
          }
        } catch {
          if (cancelled) break;
        }
        setConnected(false);
        if (!cancelled) await new Promise((r) => setTimeout(r, 1000));
      }
    })();

    return () => {
      cancelled = true;
      abort.abort();
    };
  }, []);

  return { status, connected };
}
