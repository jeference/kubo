"use client";

import { useSession } from "@kubo/web-core/session";
import { ShoppingCart, User } from "lucide-react";
import Link from "next/link";

import { useCart } from "@/features/cart/hooks";

export function SiteHeader() {
  const status = useSession((state) => state.status);
  const { data: cart } = useCart();
  const count = cart?.item_count ?? 0;

  return (
    <header className="bg-accent shadow-card">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:h-20 lg:px-9">
        <Link
          href="/"
          aria-label="Kubo"
          className="flex items-baseline font-display text-xl font-semibold tracking-tight text-highlight lg:text-3xl"
        >
          {/* O cubo é o K da marca: medido em em, acompanha as letras e fica centrado na altura do b. */}
          <picture className="shrink-0">
            <source srcSet="/brand/kubo-cube-still.webp" media="(prefers-reduced-motion: reduce)" />
            <img
              src="/brand/kubo-cube.webp"
              alt=""
              width={72}
              height={72}
              className="size-[1em] translate-y-[0.15em]"
            />
          </picture>
          ubo
        </Link>
        <nav className="flex items-center gap-1 text-sm font-medium text-white sm:gap-2">
          <Link href="/criacoes" className="rounded-full px-3 py-2 hover:bg-white/15">
            <span className="hidden sm:inline">Minhas criações</span>
            <span className="sm:hidden">Criações</span>
          </Link>
          <Link href="/pedidos" className="hidden rounded-full px-3 py-2 hover:bg-white/15 sm:block">
            Pedidos
          </Link>
          <Link
            href="/carrinho"
            aria-label={`Carrinho, ${count} ${count === 1 ? "item" : "itens"}`}
            className="relative flex size-10 items-center justify-center rounded-full hover:bg-white/15"
          >
            <ShoppingCart className="size-5" aria-hidden />
            {count > 0 && (
              <span className="absolute -right-0.5 -top-0.5 flex size-5 items-center justify-center rounded-full bg-highlight text-[11px] font-semibold text-accent">
                {count}
              </span>
            )}
          </Link>
          <Link
            href={status === "authenticated" ? "/conta" : "/entrar"}
            aria-label={status === "authenticated" ? "Minha conta" : "Entrar"}
            className="flex size-10 items-center justify-center rounded-full hover:bg-white/15"
          >
            <User className="size-5" aria-hidden />
          </Link>
        </nav>
      </div>
    </header>
  );
}
