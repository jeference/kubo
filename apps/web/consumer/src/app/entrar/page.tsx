"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { ApiError } from "@kubo/api-client";
import { Button } from "@kubo/ui/button";
import { Form, TextField } from "@kubo/ui/form";
import { useLogin } from "@kubo/web-core/auth-client";
import { handleFormError } from "@kubo/web-core/forms";
import { useSession } from "@kubo/web-core/session";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

import { type LoginValues, loginSchema } from "@/features/account/schemas";
import { safeNext } from "@/lib/safe-next";

function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const next = safeNext(params.get("next"));
  const status = useSession((state) => state.status);
  const login = useLogin();
  const form = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  useEffect(() => {
    if (status === "authenticated") router.replace(next);
  }, [status, next, router]);

  function onSubmit(values: LoginValues) {
    login.mutate(values, {
      onError: (error) => {
        if (error instanceof ApiError && error.code === "email_not_verified") {
          toast.info("Enviamos um código de verificação para o seu e-mail.");
          router.push(
            `/verificar-email?email=${encodeURIComponent(values.email)}&next=${encodeURIComponent(next)}`,
          );
          return;
        }
        handleFormError(error, form.setError);
      },
    });
  }

  return (
    <div className="mx-auto max-w-md py-8">
      <h1 className="font-display text-3xl font-semibold tracking-tight">Entrar</h1>
      <p className="mt-2 text-sm text-muted">
        A conta é opcional. Ela guarda suas criações e seus pedidos em todos os dispositivos.
      </p>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} noValidate className="mt-6 space-y-4">
          <TextField
            control={form.control}
            name="email"
            label="E-mail"
            type="email"
            autoComplete="email"
          />
          <TextField
            control={form.control}
            name="password"
            label="Senha"
            type="password"
            autoComplete="current-password"
          />
          <Button type="submit" variant="accent" className="w-full" pending={login.isPending}>
            Entrar
          </Button>
        </form>
      </Form>
      <div className="mt-5 flex justify-between text-sm">
        <Link href={`/cadastro?next=${encodeURIComponent(next)}`} className="text-accent underline">
          Criar conta
        </Link>
        <Link href="/recuperar-senha" className="text-muted underline">
          Esqueci a senha
        </Link>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginForm />
    </Suspense>
  );
}
