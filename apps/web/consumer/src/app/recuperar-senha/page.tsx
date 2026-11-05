"use client";

import { unwrap } from "@kubo/api-client";
import { useApiClient } from "@kubo/api-client/react";
import { Button } from "@kubo/ui/button";
import { Input } from "@kubo/ui/input";
import { Label } from "@kubo/ui/label";
import { handleFormError } from "@kubo/web-core/forms";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { type FormEvent, useState } from "react";
import { toast } from "sonner";

export default function PasswordResetPage() {
  const api = useApiClient();
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [step, setStep] = useState<"email" | "code" | "done">("email");

  const request = useMutation({
    mutationFn: async () => unwrap(await api.POST("/api/auth/password/reset/", { body: { email } })),
    onSuccess: (data) => {
      toast.info(data.detail);
      setStep("code");
    },
    onError: (error) => handleFormError(error),
  });
  const confirm = useMutation({
    mutationFn: async () =>
      unwrap(
        await api.POST("/api/auth/password/reset/confirm/", {
          body: { email, code, new_password: password },
        }),
      ),
    onSuccess: () => setStep("done"),
    onError: (error) => handleFormError(error),
  });

  function submit(event: FormEvent) {
    event.preventDefault();
    if (step === "email") request.mutate();
    else confirm.mutate();
  }

  return (
    <div className="mx-auto max-w-md py-8">
      <h1 className="font-display text-3xl font-semibold tracking-tight">Recuperar senha</h1>
      {step === "done" ? (
        <div className="mt-6 space-y-4">
          <p className="rounded-2xl bg-accent-soft p-4 text-sm" role="status">
            Senha redefinida. Por segurança, encerramos as sessões abertas.
          </p>
          <Button asChild variant="accent">
            <Link href="/entrar">Entrar</Link>
          </Button>
        </div>
      ) : (
        <form onSubmit={submit} className="mt-6 space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="email">E-mail</Label>
            <Input
              id="email"
              type="email"
              required
              autoComplete="email"
              disabled={step === "code"}
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </div>
          {step === "code" && (
            <>
              <div className="space-y-1.5">
                <Label htmlFor="code">Código enviado por e-mail</Label>
                <Input
                  id="code"
                  required
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  maxLength={6}
                  value={code}
                  onChange={(event) => setCode(event.target.value)}
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="password">Nova senha</Label>
                <Input
                  id="password"
                  type="password"
                  required
                  minLength={8}
                  autoComplete="new-password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                />
              </div>
            </>
          )}
          <Button
            type="submit"
            variant="accent"
            className="w-full"
            pending={request.isPending || confirm.isPending}
          >
            {step === "email" ? "Enviar código" : "Redefinir senha"}
          </Button>
        </form>
      )}
    </div>
  );
}
