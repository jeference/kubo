import Link from "next/link";

const LINKS = [
  { href: "/ajuda", label: "Ajuda" },
  { href: "/acompanhar", label: "Acompanhar pedido" },
  { href: "/trocas", label: "Trocas e devoluções" },
  { href: "/termos", label: "Termos de Uso" },
  { href: "/privacidade", label: "Privacidade" },
];

export function SiteFooter() {
  return (
    <footer className="border-t border-line pb-24 lg:pb-0">
      <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-2 px-4 py-6 text-sm text-muted sm:px-6 lg:px-9">
        <span>© {new Date().getFullYear()} Kubo</span>
        <nav className="flex flex-wrap gap-x-5 gap-y-1">
          {LINKS.map((link) => (
            <Link key={link.href} href={link.href} className="hover:text-ink">
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </footer>
  );
}
