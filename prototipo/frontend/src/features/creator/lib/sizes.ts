/** Example prices for the visual-only purchase panel: there is no real pricing yet. */
export const SIZES = [
  { id: "6cm", label: "6 cm Ideal", price: 129.9 },
  { id: "4cm", label: "4 cm Mini", price: 59.9 },
  { id: "5cm", label: "5 cm Pequeno", price: 89.9 },
  { id: "7cm", label: "7 cm Médio", price: 179.9 },
  { id: "8cm", label: "8 cm Grande", price: 229.9 },
  { id: "10cm", label: "10 cm Destaque", price: 299.9 },
  { id: "12cm", label: "12 cm Exposição", price: 599.9 },
  { id: "15cm", label: "15 cm Peça central", price: 799.9 },
] as const;

export const DEFAULT_SIZE = SIZES[0];

export const LOWEST_PRICE = Math.min(...SIZES.map((size) => size.price));

const brl = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

export function formatPrice(value: number): string {
  return brl.format(value);
}
