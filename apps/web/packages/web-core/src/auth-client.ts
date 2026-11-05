"use client";

import { ApiError, normalizeError, unwrap } from "@kubo/api-client";
import { useApiClient } from "@kubo/api-client/react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { getApiClient } from "./api";
import { useSession } from "./session";

async function postBff<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = (await response.json().catch(() => null)) as unknown;
  if (!response.ok) throw normalizeError(response.status, data);
  return data as T;
}

/** Depois de entrar: carrega o usuário e traz para a conta o que foi feito como visitante. */
async function completeSignIn(access: string) {
  useSession.getState().setAccessToken(access);
  const api = getApiClient();
  unwrap(await api.POST("/api/me/claim/"));
  const user = unwrap(await api.GET("/api/me/"));
  useSession.getState().setSession(access, user);
}

export function useLogin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (values: { email: string; password: string }) => {
      const { access } = await postBff<{ access: string }>("/bff/auth/login", values);
      await completeSignIn(access);
    },
    onSuccess: () => queryClient.invalidateQueries(),
  });
}

export function useVerifyEmail() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (values: { email: string; code: string }) => {
      const { access } = await postBff<{ access: string }>("/bff/auth/verify-email", values);
      await completeSignIn(access);
    },
    onSuccess: () => queryClient.invalidateQueries(),
  });
}

export function useRegister() {
  const api = useApiClient();
  return useMutation({
    mutationFn: async (values: {
      email: string;
      password: string;
      first_name?: string;
    }) => unwrap(await api.POST("/api/auth/register/", { body: values })),
  });
}

/**
 * Encerra a sessão e recarrega o app. Sem limpar o estado antes de navegar: os guards veriam
 * "visitante" e mandariam para o login, em vez do destino pedido.
 */
export async function signOutAndRedirect(destination = "/"): Promise<void> {
  await fetch("/bff/auth/logout", { method: "POST" }).catch(() => undefined);
  window.location.assign(destination);
}

export function useLogout() {
  return useMutation({ mutationFn: (destination?: string) => signOutAndRedirect(destination) });
}

export { ApiError };
