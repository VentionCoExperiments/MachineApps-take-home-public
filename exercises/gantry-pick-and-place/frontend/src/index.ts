import { createClient } from "@connectrpc/connect";
import { createConnectTransport } from "@connectrpc/connect-web";
import { GantryPickAndPlaceService } from "./gen/app_pb.ts";

// Connect-Web transport (JSON mode). The relative baseUrl keeps calls
// same-origin. Vite proxies /rpc to the backend (see vite.config.ts).
const transport = createConnectTransport({
  baseUrl: "/rpc",
  useBinaryFormat: false,
});

export const client = createClient(GantryPickAndPlaceService, transport);
