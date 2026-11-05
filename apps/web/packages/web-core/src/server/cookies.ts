import { cookies } from "next/headers";

import {
  REFRESH_COOKIE,
  REFRESH_MAX_AGE_SECONDS,
  VISITOR_COOKIE,
  VISITOR_MAX_AGE_SECONDS,
} from "./constants";

const BASE = {
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",
  sameSite: "lax",
  path: "/",
} as const;

export async function setRefreshCookie(token: string): Promise<void> {
  const store = await cookies();
  store.set(REFRESH_COOKIE, token, { ...BASE, maxAge: REFRESH_MAX_AGE_SECONDS });
}

export async function clearRefreshCookie(): Promise<void> {
  const store = await cookies();
  store.set(REFRESH_COOKIE, "", { ...BASE, maxAge: 0 });
}

export async function getRefreshCookie(): Promise<string | undefined> {
  const store = await cookies();
  return store.get(REFRESH_COOKIE)?.value;
}

export async function setVisitorCookie(token: string): Promise<void> {
  const store = await cookies();
  store.set(VISITOR_COOKIE, token, { ...BASE, maxAge: VISITOR_MAX_AGE_SECONDS });
}

export async function getVisitorCookie(): Promise<string | undefined> {
  const store = await cookies();
  return store.get(VISITOR_COOKIE)?.value;
}
