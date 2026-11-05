import type { Schemas } from "@kubo/api-client";
import { create } from "zustand";

export type SessionUser = Schemas["User"];
export type SessionStatus = "loading" | "authenticated" | "anonymous";

interface SessionState {
  status: SessionStatus;
  /** Token de acesso só em memória. O refresh fica em cookie httpOnly. */
  accessToken: string | null;
  user: SessionUser | null;
  /** O cookie de visitante já existe: quem não tem conta pode chamar a API. */
  visitorReady: boolean;
  setSession: (accessToken: string, user: SessionUser) => void;
  setAccessToken: (accessToken: string) => void;
  setUser: (user: SessionUser) => void;
  setAnonymous: () => void;
  setVisitorReady: () => void;
  clear: () => void;
}

export const useSession = create<SessionState>((set) => ({
  status: "loading",
  accessToken: null,
  user: null,
  visitorReady: false,
  setSession: (accessToken, user) => set({ accessToken, user, status: "authenticated" }),
  setAccessToken: (accessToken) => set({ accessToken }),
  setUser: (user) => set({ user, status: "authenticated" }),
  setAnonymous: () => set({ status: "anonymous", accessToken: null, user: null }),
  setVisitorReady: () => set({ visitorReady: true }),
  clear: () => set({ status: "anonymous", accessToken: null, user: null }),
}));

/** A identidade já está resolvida: conta autenticada, ou visitante com cookie. */
export function useActorReady(): boolean {
  return useSession(
    (state) =>
      state.status === "authenticated" || (state.status === "anonymous" && state.visitorReady),
  );
}
