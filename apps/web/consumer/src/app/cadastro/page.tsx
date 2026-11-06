"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@kubo/ui/button";
import { Form, TextField } from "@kubo/ui/form";
import { useRegister } from "@kubo/web-core/auth-client";
import { handleFormError } from "@kubo/web-core/forms";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { useForm } from "react-hook-form";

import { type RegisterValues, registerSchema } from "@/features/account/schemas";
import { safeNext } from "@/lib/safe-next";

function RegisterForm() {
  const router = useRouter();
  const params = useSearchParams();
  const next = safeNext(params.get("next"));
  const register = useRegister();
  const form = useForm<RegisterValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { first_name: "", email: "", password: "" },
  });

  function onSubmit(values: RegisterValues) {
    register.mutate(values, {
      onSuccess: () =>
        router.push(
          `/verificar-email?email=${encodeURIComponent(values.email)}&next=${encodeURIComponent(next)}`,
        ),
      onError: (error) => handleFormError(error, form.setError),
    });
  }

  return (
    <div className="mx-auto max-w-md py-8">
      <h1 className="font-display text-3xl font-semibold tracking-tight">Criar conta</h1>
      <p className="mt-2 text-sm text-muted">
        O que você criou neste navegador passa para a sua conta.
      </p>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} noValidate className="mt-6 space-y-4">
          <TextField
            control={form.control}
            name="first_name"
            label="Nome"
            autoComplete="given-name"
          />
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
            autoComplete="new-password"
            hint="Use pelo menos 8 caracteres."
          />
          <Button type="submit" variant="primary" className="w-full" pending={register.isPending}>
            Criar conta
          </Button>
        </form>
      </Form>
      <p className="mt-5 text-sm">
        Já tem conta?{" "}
        <Link href={`/entrar?next=${encodeURIComponent(next)}`} className="text-accent underline">
          Entrar
        </Link>
      </p>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <Suspense>
      <RegisterForm />
    </Suspense>
  );
}
