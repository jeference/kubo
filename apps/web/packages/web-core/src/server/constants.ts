/** Cookie httpOnly com o refresh token, gravado pelo BFF. */
export const REFRESH_COOKIE = "kubo_refresh";
/** Igual ao REFRESH_TOKEN_LIFETIME do backend (7 dias). */
export const REFRESH_MAX_AGE_SECONDS = 60 * 60 * 24 * 7;
/** Cookie httpOnly com o token do visitante. */
export const VISITOR_COOKIE = "kubo_visitor";
export const VISITOR_MAX_AGE_SECONDS = 60 * 60 * 24 * 365;
