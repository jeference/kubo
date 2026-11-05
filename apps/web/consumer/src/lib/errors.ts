import { ApiError } from "@kubo/api-client";

export function messageOf(error: unknown, fallback = "Não deu certo. Tente de novo."): string {
  return error instanceof ApiError ? error.message : fallback;
}
