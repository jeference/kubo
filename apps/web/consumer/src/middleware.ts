import { type NextRequest, NextResponse } from "next/server";

import { REFRESH_COOKIE } from "@kubo/web-core/auth-constants";

/** Primeira barreira da área da conta. A autorização de verdade é sempre do backend. */
export function middleware(request: NextRequest): NextResponse {
  if (request.cookies.has(REFRESH_COOKIE)) return NextResponse.next();
  const url = request.nextUrl.clone();
  url.pathname = "/entrar";
  url.search = `next=${encodeURIComponent(request.nextUrl.pathname)}`;
  return NextResponse.redirect(url);
}

export const config = { matcher: ["/conta/:path*"] };
