"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { track } from "@kubo/analytics";
import { ApiError, type Schemas, unwrap } from "@kubo/api-client";
import { qk, useApiClient } from "@kubo/api-client/react";
import { Button } from "@kubo/ui/button";
import { Callout } from "@kubo/ui/callout";
import { Card } from "@kubo/ui/card";
import { Checkbox } from "@kubo/ui/checkbox";
import { EmptyState } from "@kubo/ui/empty-state";
import { Form, TextField } from "@kubo/ui/form";
import { formatBRL, formatCep, formatCpf, formatPhone } from "@kubo/ui/lib/format";
import { RadioCard } from "@kubo/ui/radio-card";
import { Skeleton } from "@kubo/ui/skeleton";
import { useSession } from "@kubo/web-core/session";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Lock } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

import { useCart } from "@/features/cart/hooks";
import { type CheckoutValues, checkoutSchema } from "@/features/checkout/schemas";
import { messageOf } from "@/lib/errors";

type Quote = Schemas["ShippingQuote"];

export function CheckoutForm() {
  const api = useApiClient();
  const router = useRouter();
  const queryClient = useQueryClient();
  const params = useSearchParams();
  const onlyItem = params.get("item");
  const user = useSession((state) => state.user);
  const { data: cart, isLoading } = useCart();

  const form = useForm<CheckoutValues>({
    resolver: zodResolver(checkoutSchema),
    defaultValues: {
      email: "",
      name: "",
      cpf: "",
      phone: "",
      postal_code: "",
      street: "",
      number: "",
      complement: "",
      neighborhood: "",
      city: "",
      state: "",
    },
  });

  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [quoteError, setQuoteError] = useState<string | null>(null);
  const [selectedQuoteId, setSelectedQuoteId] = useState<string | null>(null);
  const [shippingNotice, setShippingNotice] = useState<string | null>(null);
  const [acceptTerms, setAcceptTerms] = useState(false);
  // A mesma chave em toda tentativa: um clique duplo nunca cria dois pedidos.
  const idempotencyKey = useRef(crypto.randomUUID());

  const items = (cart?.items ?? []).filter(
    (item) => !item.unavailable_reason && (!onlyItem || item.id === onlyItem),
  );
  const itemIds = items.map((item) => item.id);
  const itemKey = itemIds.join(",");
  const subtotal = items.reduce((total, item) => total + item.line_total_cents, 0);
  const selectedQuote = quotes.find((quote) => quote.id === selectedQuoteId) ?? null;

  const { data: addresses } = useQuery({
    queryKey: qk.addresses(),
    enabled: Boolean(user),
    queryFn: async () => unwrap(await api.GET("/api/me/addresses/")),
  });

  // Conta: preenche o que já sabemos, sem apagar o que foi digitado.
  useEffect(() => {
    if (!user) return;
    const current = form.getValues();
    if (!current.email) form.setValue("email", user.email);
    if (!current.name && user.first_name) form.setValue("name", user.first_name);
    if (!current.phone && user.phone) form.setValue("phone", formatPhone(user.phone));
  }, [user, form]);

  useEffect(() => {
    const saved = addresses?.[0];
    if (!saved || form.getValues("postal_code")) return;
    form.reset({
      ...form.getValues(),
      postal_code: formatCep(saved.postal_code),
      street: saved.street,
      number: saved.number,
      complement: saved.complement,
      neighborhood: saved.neighborhood,
      city: saved.city,
      state: saved.state,
    });
  }, [addresses, form]);

  useEffect(() => {
    if (itemKey) track("checkout_started", { items: itemIds.length });
    // Só uma vez por conjunto de itens.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [itemKey]);

  const postalCode = form.watch("postal_code");
  const cepDigits = postalCode.replace(/\D/g, "");

  const quote = useMutation({
    mutationFn: async (variables: { postalCode: string; itemIds: string[] }) =>
      unwrap(
        await api.POST("/api/shipping/quotes/", {
          body: { postal_code: variables.postalCode, item_ids: variables.itemIds },
        }),
      ),
    onSuccess: (result) => {
      setQuotes(result);
      setSelectedQuoteId(result[0]?.id ?? null);
      setQuoteError(null);
      track("shipping_quoted", { options: result.length });
    },
    onError: (error) => {
      setQuotes([]);
      setSelectedQuoteId(null);
      setQuoteError(messageOf(error, "Não conseguimos calcular o frete. Tente de novo."));
    },
  });
  const quoteMutate = quote.mutate;

  // CEP completo: busca o endereço e cota o frete.
  useEffect(() => {
    setShippingNotice(null);
    if (cepDigits.length !== 8 || !itemKey) {
      setQuotes([]);
      setSelectedQuoteId(null);
      setQuoteError(null);
      return;
    }
    quoteMutate({ postalCode: cepDigits, itemIds: itemKey.split(",") });
    void (async () => {
      const { data } = await api.GET("/api/shipping/address/{postal_code}/", {
        params: { path: { postal_code: cepDigits } },
      });
      if (!data) return;
      const current = form.getValues();
      if (data.street && !current.street) form.setValue("street", data.street);
      if (data.neighborhood && !current.neighborhood) {
        form.setValue("neighborhood", data.neighborhood);
      }
      if (data.city && !current.city) form.setValue("city", data.city);
      if (data.state && !current.state) form.setValue("state", data.state);
    })();
  }, [cepDigits, itemKey, api, form, quoteMutate]);

  const placeOrder = useMutation({
    mutationFn: async (values: CheckoutValues) => {
      const order = unwrap(
        await api.POST("/api/orders/", {
          params: { header: { "Idempotency-Key": idempotencyKey.current } },
          body: {
            ...values,
            complement: values.complement ?? "",
            item_ids: itemIds,
            shipping_quote_id: selectedQuoteId ?? "",
            accept_terms: acceptTerms,
          },
        }),
      );
      // Se o PIX falhar aqui, a página do pedido tenta de novo.
      await api.POST("/api/orders/{order_id}/pay/", {
        params: { path: { order_id: order.id } },
      });
      return order;
    },
    onSuccess: (order) => {
      void queryClient.invalidateQueries({ queryKey: qk.orders() });
      track("pix_generated");
      router.replace(`/pedidos/${order.id}`);
    },
    onError: (error) => {
      if (error instanceof ApiError && error.code === "shipping_changed") {
        const raw = error.raw as {
          new_quote_id?: string;
          new_price_cents?: number;
          new_delivery_days?: number;
        };
        if (raw.new_quote_id && raw.new_price_cents !== undefined) {
          const previous = selectedQuote;
          const updated: Quote = {
            ...(previous as Quote),
            id: raw.new_quote_id,
            price_cents: raw.new_price_cents,
            delivery_days: raw.new_delivery_days ?? previous?.delivery_days ?? 0,
          };
          setQuotes([updated]);
          setSelectedQuoteId(updated.id);
          setShippingNotice(
            `O frete mudou para ${formatBRL(raw.new_price_cents)}. Confira o total e confirme.`,
          );
          return;
        }
        quoteMutate({ postalCode: cepDigits, itemIds });
        setShippingNotice(error.message);
        return;
      }
      if (error instanceof ApiError && error.fieldErrors) {
        for (const [field, messages] of Object.entries(error.fieldErrors)) {
          form.setError(field as keyof CheckoutValues, { message: messages[0] });
        }
      }
      toast.error(messageOf(error));
    },
  });

  if (isLoading || !cart) {
    return (
      <div className="mx-auto max-w-5xl space-y-3">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }
  if (items.length === 0) {
    return (
      <div className="mx-auto max-w-xl py-8">
        <EmptyState
          title="Nada para finalizar"
          description="Seu carrinho está vazio, ou os itens não estão mais disponíveis."
          action={
            <Button asChild variant="primary">
              <Link href="/carrinho">Ver carrinho</Link>
            </Button>
          }
        />
      </div>
    );
  }

  const canSubmit = Boolean(selectedQuote) && acceptTerms && !quote.isPending;

  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="font-display text-3xl font-semibold tracking-tight">Finalizar compra</h1>
      {!user && (
        <p className="mt-2 text-sm text-muted">
          Não precisa de conta: enviamos o acompanhamento para o seu e-mail.{" "}
          <Link href="/entrar?next=/checkout" className="text-accent underline">
            Já tenho conta
          </Link>
        </p>
      )}

      <Form {...form}>
        <form
          noValidate
          onSubmit={form.handleSubmit((values) => placeOrder.mutate(values))}
          className="mt-6 grid gap-8 lg:grid-cols-[minmax(0,1fr)_380px]"
        >
          <div className="space-y-8">
            <fieldset className="space-y-4">
              <legend className="font-display text-lg font-semibold">Seus dados</legend>
              <TextField
                control={form.control}
                name="email"
                label="E-mail"
                type="email"
                autoComplete="email"
                hint="O link de acompanhamento vai para este e-mail."
              />
              <TextField
                control={form.control}
                name="name"
                label="Nome completo"
                autoComplete="name"
              />
              <div className="grid gap-4 sm:grid-cols-2">
                <TextField
                  control={form.control}
                  name="cpf"
                  label="CPF"
                  inputMode="numeric"
                  format={formatCpf}
                  hint="Necessário para a nota fiscal e o envio."
                />
                <TextField
                  control={form.control}
                  name="phone"
                  label="Telefone"
                  type="tel"
                  autoComplete="tel"
                  format={formatPhone}
                />
              </div>
            </fieldset>

            <fieldset className="space-y-4">
              <legend className="font-display text-lg font-semibold">Entrega</legend>
              <TextField
                control={form.control}
                name="postal_code"
                label="CEP"
                inputMode="numeric"
                autoComplete="postal-code"
                format={formatCep}
                className="sm:max-w-48"
              />
              <TextField
                control={form.control}
                name="street"
                label="Rua"
                autoComplete="address-line1"
              />
              <div className="grid gap-4 sm:grid-cols-[140px_minmax(0,1fr)]">
                <TextField control={form.control} name="number" label="Número" />
                <TextField
                  control={form.control}
                  name="complement"
                  label="Complemento (opcional)"
                />
              </div>
              <TextField control={form.control} name="neighborhood" label="Bairro" />
              <div className="grid gap-4 sm:grid-cols-[minmax(0,1fr)_100px]">
                <TextField control={form.control} name="city" label="Cidade" />
                <TextField control={form.control} name="state" label="UF" maxLength={2} />
              </div>
            </fieldset>

            <fieldset className="space-y-3">
              <legend className="font-display text-lg font-semibold">Frete</legend>
              {cepDigits.length !== 8 && (
                <p className="text-sm text-muted">Informe o CEP para ver as opções.</p>
              )}
              {quote.isPending && <Skeleton className="h-16 w-full" />}
              {quoteError && (
                <div className="flex flex-wrap items-center gap-3 text-sm text-danger" role="alert">
                  {quoteError}
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={() => quoteMutate({ postalCode: cepDigits, itemIds })}
                  >
                    Tentar de novo
                  </Button>
                </div>
              )}
              {shippingNotice && (
                <Callout tone="accent" role="alert">
                  {shippingNotice}
                </Callout>
              )}
              {!quote.isPending &&
                quotes.map((option) => (
                  <RadioCard
                    key={option.id}
                    name="shipping"
                    checked={option.id === selectedQuoteId}
                    onSelect={() => setSelectedQuoteId(option.id)}
                    aside={formatBRL(option.price_cents)}
                  >
                    <span className="block text-sm font-semibold">
                      {option.company} {option.service_name}
                    </span>
                    <span className="block text-xs text-muted">
                      Até {option.delivery_days} dias úteis, com a produção
                    </span>
                  </RadioCard>
                ))}
            </fieldset>
          </div>

          <Card asChild className="h-fit space-y-4 p-5 lg:sticky lg:top-6">
            <aside>
              <h2 className="font-display text-lg font-semibold">Resumo</h2>
              <ul className="space-y-3">
                {items.map((item) => (
                  <li key={item.id} className="flex items-center gap-3">
                    {/* eslint-disable-next-line @next/next/no-img-element -- imagem dinâmica */}
                    <img
                      src={item.image_url}
                      alt=""
                      className="size-14 rounded-xl bg-sunken object-contain"
                    />
                    <span className="min-w-0 flex-1 text-sm">
                      {item.size_label}
                      <span className="block text-muted">Quantidade: {item.quantity}</span>
                    </span>
                    <span className="text-sm tabular-nums">{formatBRL(item.line_total_cents)}</span>
                  </li>
                ))}
              </ul>
              <dl className="space-y-1.5 border-t border-line pt-3 text-sm">
                <div className="flex justify-between">
                  <dt className="text-muted">Subtotal</dt>
                  <dd className="tabular-nums">{formatBRL(subtotal)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-muted">Frete</dt>
                  <dd className="tabular-nums">
                    {selectedQuote ? formatBRL(selectedQuote.price_cents) : "—"}
                  </dd>
                </div>
                <div className="flex justify-between pt-1.5 text-lg font-semibold">
                  <dt>Total</dt>
                  <dd className="tabular-nums" data-testid="total">
                    {formatBRL(subtotal + (selectedQuote?.price_cents ?? 0))}
                  </dd>
                </div>
              </dl>
              <Checkbox
                checked={acceptTerms}
                onChange={(event) => setAcceptTerms(event.target.checked)}
              >
                Li e aceito os{" "}
                <Link href="/termos" target="_blank" className="underline">
                  Termos de Uso
                </Link>{" "}
                e a{" "}
                <Link href="/trocas" target="_blank" className="underline">
                  Política de Trocas
                </Link>
                . Sei que a peça impressa pode ter diferenças de cor e detalhe em relação à prévia.
              </Checkbox>
              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full"
                disabled={!canSubmit}
                pending={placeOrder.isPending}
              >
                <Lock aria-hidden />
                Pagar com PIX
              </Button>
            </aside>
          </Card>
        </form>
      </Form>
    </div>
  );
}
