"use client";

import { unwrap } from "@kubo/api-client";
import { useApiClient } from "@kubo/api-client/react";
import { Callout } from "@kubo/ui/callout";
import { Button } from "@kubo/ui/button";
import { Input } from "@kubo/ui/input";
import { Label } from "@kubo/ui/label";
import { useMutation } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
import { toast } from "sonner";

import { messageOf } from "@/lib/errors";

export default function TrackLookupPage() {
  const api = useApiClient();
  const [email, setEmail] = useState("");
  const resend = useMutation({
    mutationFn: async () =>
      unwrap(await api.POST("/api/orders/track/resend/", { body: { email } })),
  });

  function submit(event: FormEvent) {
    event.preventDefault();
    resend.mutate(undefined, { onError: (error) => toast.error(messageOf(error)) });
  }

  return (
    <div className="mx-auto max-w-md py-8">
      <h1 className="font-display text-3xl font-semibold tracking-tight">Acompanhar pedido</h1>
      <p className="mt-2 text-sm text-muted">
        Informe o e-mail usado na compra. Enviaremos o link de cada pedido.
      </p>
      {resend.isSuccess ? (
        <Callout tone="accent" role="status" className="mt-6 p-4">
          {resend.data.detail}
        </Callout>
      ) : (
        <form onSubmit={submit} className="mt-6 space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="email">E-mail</Label>
            <Input
              id="email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </div>
          <Button type="submit" variant="primary" className="w-full" pending={resend.isPending}>
            Enviar link
          </Button>
        </form>
      )}
    </div>
  );
}
