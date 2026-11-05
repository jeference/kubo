import { z } from "zod";

const digits = (value: string) => value.replace(/\D/g, "");

export function isValidCpf(value: string): boolean {
  const cpf = digits(value);
  if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false;
  for (const length of [9, 10]) {
    let total = 0;
    for (let i = 0; i < length; i += 1) total += Number(cpf[i]) * (length + 1 - i);
    const digit = ((total * 10) % 11) % 10;
    if (digit !== Number(cpf[length])) return false;
  }
  return true;
}

/** Validação para a experiência. A autoridade continua sendo o backend. */
export const checkoutSchema = z.object({
  email: z.string().email("Informe um e-mail válido."),
  name: z.string().trim().min(3, "Informe seu nome completo."),
  cpf: z.string().refine(isValidCpf, "Informe um CPF válido."),
  phone: z.string().refine((v) => [10, 11].includes(digits(v).length), "Informe o telefone com DDD."),
  postal_code: z.string().refine((v) => digits(v).length === 8, "Informe um CEP válido."),
  street: z.string().trim().min(2, "Informe a rua."),
  number: z.string().trim().min(1, "Informe o número."),
  complement: z.string().optional(),
  neighborhood: z.string().trim().min(2, "Informe o bairro."),
  city: z.string().trim().min(2, "Informe a cidade."),
  state: z
    .string()
    .trim()
    .regex(/^[A-Za-z]{2}$/, "Use a sigla, como SP."),
});

export type CheckoutValues = z.infer<typeof checkoutSchema>;
