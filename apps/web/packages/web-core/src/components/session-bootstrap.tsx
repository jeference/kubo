"use client";

import { unwrap } from "@kubo/api-client";
import { useApiClient } from "@kubo/api-client/react";
import { useEffect } from "react";

import { refreshSession } from "../api";
import { useSession } from "../session";

/**
 * Ao carregar: garante o cookie de visitante e tenta restaurar a conta pelo cookie de refresh.
 * Não renderiza nada. Só decide se quem está aqui é conta ou visitante.
 */
export function SessionBootstrap() {
  const api = useApiClient();

  useEffect(() => {
    let active = true;

    void fetch("/bff/visitor", { method: "POST" })
      .catch(() => undefined)
      .finally(() => {
        if (active) useSession.getState().setVisitorReady();
      });

    void (async () => {
      const token = await refreshSession();
      if (!token) {
        if (active) useSession.getState().setAnonymous();
        return;
      }
      try {
        const me = unwrap(await api.GET("/api/me/"));
        if (active) useSession.getState().setSession(token, me);
      } catch {
        if (active) useSession.getState().setAnonymous();
      }
    })();

    return () => {
      active = false;
    };
  }, [api]);

  return null;
}
