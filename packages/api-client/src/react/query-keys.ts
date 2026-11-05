/** Chaves do React Query em um só lugar, para a invalidação ser previsível. */
export const qk = {
  me: () => ["me"] as const,
  addresses: () => ["me", "addresses"] as const,
  quota: () => ["quota"] as const,
  styles: () => ["catalog", "styles"] as const,
  sizes: () => ["catalog", "sizes"] as const,
  creations: () => ["creations"] as const,
  creation: (id: string) => ["creations", id] as const,
  cart: () => ["cart"] as const,
  orders: () => ["orders"] as const,
  order: (id: string) => ["orders", id] as const,
  tracking: (token: string) => ["tracking", token] as const,
};
