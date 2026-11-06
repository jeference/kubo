"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { unwrap } from "@kubo/api-client";
import { useApiClient } from "@kubo/api-client/react";
import { Button } from "@kubo/ui/button";
import { Form, TextField } from "@kubo/ui/form";
import { useVerifyEmail } from "@kubo/web-core/auth-client";
import { handleFormError } from "@kubo/web-core/forms";
import { useMutation } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

import { type CodeValues, codeSchema } from "@/features/account/schemas";
import { safeNext } from "@/lib/safe-next";

function VerifyForm() {
  const api = useApiClient();
  const router = useRouter();
  const params = useSearchParams();
  const email = params.get("email") ?? "";
  const next = safeNext(params.get("next"));
  const verify = useVerifyEmail();
  const form = useForm<CodeValues>({
    resolver: zodResolver(codeSchema),
    defaultValues: { code: "" },
  });
  const resend = useMutation({
    mutationFn: async () =>
      unwrap(await api.POST("/api/auth/verify-email/resend/", { body: { email } })),
    onSuccess: (data) => toast.success(data.detail),
    onError: (error) => handleFormError(error),
  });

  function onSubmit(values: CodeValues) {
    verify.mutate(
      { email, code: values.code },
      {
        onSuccess: () => router.replace(next),
        onError: (error) => handleFormError(error, form.setError),
      },
    );
  }

  return (
    <div className="mx-auto max-w-md py-8">
      <h1 className="font-display text-3xl font-semibold tracking-tight">Confirme seu e-mail</h1>
      <p className="mt-2 text-sm text-muted">
        Enviamos um código de 6 números para <strong>{email}</strong>.
      </p>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} noValidate className="mt-6 space-y-4">
          <TextField
            control={form.control}
            name="code"
            label="Código"
            inputMode="numeric"
            autoComplete="one-time-code"
            maxLength={6}
            autoFocus
          />
          <Button type="submit" variant="primary" className="w-full" pending={verify.isPending}>
            Confirmar
          </Button>
        </form>
      </Form>
      <Button
        variant="ghost"
        size="sm"
        className="mt-3"
        pending={resend.isPending}
        onClick={() => resend.mutate()}
      >
        Reenviar código
      </Button>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense>
      <VerifyForm />
    </Suspense>
  );
}
