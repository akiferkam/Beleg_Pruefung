import { mockApi } from "./mock";
import { createRestApi } from "./rest";
import type { BelegApi } from "./types";

/** Set VITE_BELEG_API_URL (e.g. http://127.0.0.1:5050) to talk to the Python backend. */
const base = import.meta.env.VITE_BELEG_API_URL as string | undefined;

export const api: BelegApi = base ? createRestApi(base) : mockApi;
export * from "./types";
