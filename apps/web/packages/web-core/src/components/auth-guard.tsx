"use client";

import { Skeleton } from "@kubo/ui/skeleton";
import { useRouter } from "next/navigation";
import { type ReactNode, useEffect } from "react";

import { useSession } from "../session";

/** O middleware já confere o cookie; aqui, espera a sessão resolver e redireciona visitantes. */
export function AuthGuard({ children, loginPath }: { children: ReactNode; loginPath: string }) {
  const router = useRouter();
  const status = useSession((state) => state.status);

  useEffect(() => {
    if (status === "anonymous") router.replace(loginPath);
  }, [status, router, loginPath]);

  if (status !== "authenticated") {
    return (
      <div className="mx-auto w-full max-w-3xl space-y-3 px-4 py-12">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }
  return <>{children}</>;
}
