"use client";

import { unwrap } from "@kubo/api-client";
import { useApiClient } from "@kubo/api-client/react";
import { Button } from "@kubo/ui/button";
import { Input } from "@kubo/ui/input";
import { Label } from "@kubo/ui/label";
import { formatPhone } from "@kubo/ui/lib/format";
import { signOutAndRedirect, useLogout } from "@kubo/web-core/auth-client";
import { AuthGuard } from "@kubo/web-core/components/auth-guard";
import { handleFormError } from "@kubo/web-core/forms";
import { type SessionUser, useSession } from "@kubo/web-core/session";
import { useMutation } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
import { toast } from "sonner";

export default function AccountPage() {
  return (
    <AuthGuard loginPath="/entrar?next=/conta">
      <Account />
    </AuthGuard>
  );
}

function Account() {
  const user = useSession((state) => state.user) as SessionUser;
  const logout = useLogout();

  return (
    <div className="mx-auto max-w-xl space-y-8">
      <div className="flex items-center justify-between gap-3">
        <h1 className="font-display text-3xl font-semibold tracking-tight">Minha conta</h1>
        <Button
          variant="outline"
          pending={logout.isPending}
          onClick={() => logout.mutate("/")}
        >
          Sair
        </Button>
      </div>
      <ProfileForm user={user} />
      <PasswordForm />
      <DeleteAccount />
    </div>
  );
}

function ProfileForm({ user }: { user: SessionUser }) {
  const api = useApiClient();
  const [firstName, setFirstName] = useState(user.first_name);
  const [phone, setPhone] = useState(formatPhone(user.phone));
  const save = useMutation({
    mutationFn: async () =>
      unwrap(
        await api.PATCH("/api/me/", {
          body: { first_name: firstName, phone: phone.replace(/\D/g, "") },
        }),
      ),
    onSuccess: (updated) => {
      useSession.getState().setUser(updated);
      toast.success("Dados salvos.");
    },
    onError: (error) => handleFormError(error),
  });

  return (
    <form
      className="space-y-4 rounded-2xl border border-line p-5"
      onSubmit={(event: FormEvent) => {
        event.preventDefault();
        save.mutate();
      }}
    >
      <h2 className="font-display text-lg font-semibold">Seus dados</h2>
      <p className="text-sm text-muted">{user.email}</p>
      <div className="space-y-1.5">
        <Label htmlFor="first-name">Nome</Label>
        <Input
          id="first-name"
          value={firstName}
          onChange={(event) => setFirstName(event.target.value)}
        />
      </div>
      <div className="space-y-1.5">
        <Label htmlFor="phone">Telefone</Label>
        <Input
          id="phone"
          type="tel"
          value={phone}
          onChange={(event) => setPhone(formatPhone(event.target.value))}
        />
      </div>
      <Button type="submit" pending={save.isPending}>
        Salvar
      </Button>
    </form>
  );
}

function PasswordForm() {
  const api = useApiClient();
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const change = useMutation({
    mutationFn: async () =>
      unwrap(
        await api.POST("/api/auth/password/change/", {
          body: { old_password: current, new_password: next },
        }),
      ),
    onSuccess: () => {
      toast.success("Senha alterada.");
      setCurrent("");
      setNext("");
    },
    onError: (error) => handleFormError(error),
  });

  return (
    <form
      className="space-y-4 rounded-2xl border border-line p-5"
      onSubmit={(event: FormEvent) => {
        event.preventDefault();
        change.mutate();
      }}
    >
      <h2 className="font-display text-lg font-semibold">Alterar senha</h2>
      <div className="space-y-1.5">
        <Label htmlFor="current-password">Senha atual</Label>
        <Input
          id="current-password"
          type="password"
          required
          autoComplete="current-password"
          value={current}
          onChange={(event) => setCurrent(event.target.value)}
        />
      </div>
      <div className="space-y-1.5">
        <Label htmlFor="new-password">Nova senha</Label>
        <Input
          id="new-password"
          type="password"
          required
          minLength={8}
          autoComplete="new-password"
          value={next}
          onChange={(event) => setNext(event.target.value)}
        />
      </div>
      <Button type="submit" pending={change.isPending}>
        Alterar senha
      </Button>
    </form>
  );
}

function DeleteAccount() {
  const api = useApiClient();
  const [password, setPassword] = useState("");
  const remove = useMutation({
    mutationFn: async () => {
      const result = await api.POST("/api/me/delete/", { body: { password } });
      if (!result.response.ok) unwrap(result);
    },
    onSuccess: () => signOutAndRedirect("/"),
    onError: (error) => handleFormError(error),
  });

  return (
    <form
      className="space-y-4 rounded-2xl border border-danger/30 p-5"
      onSubmit={(event: FormEvent) => {
        event.preventDefault();
        if (window.confirm("Excluir sua conta? Esta ação não pode ser desfeita.")) remove.mutate();
      }}
    >
      <h2 className="font-display text-lg font-semibold">Excluir conta</h2>
      <p className="text-sm text-muted">
        Apagamos seus dados e suas criações sem pedido. Dados de pedidos ficam guardados pelo prazo
        exigido por lei.
      </p>
      <div className="space-y-1.5">
        <Label htmlFor="delete-password">Confirme sua senha</Label>
        <Input
          id="delete-password"
          type="password"
          required
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
      </div>
      <Button type="submit" variant="danger" pending={remove.isPending}>
        Excluir conta
      </Button>
    </form>
  );
}
