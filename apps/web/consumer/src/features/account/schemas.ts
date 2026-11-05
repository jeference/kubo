import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Informe um e-mail válido."),
  password: z.string().min(1, "Informe a senha."),
});
export type LoginValues = z.infer<typeof loginSchema>;

export const registerSchema = z.object({
  first_name: z.string().trim().min(2, "Informe seu nome."),
  email: z.string().email("Informe um e-mail válido."),
  password: z.string().min(8, "Use pelo menos 8 caracteres."),
});
export type RegisterValues = z.infer<typeof registerSchema>;

export const codeSchema = z.object({
  code: z.string().regex(/^\d{6}$/, "O código tem 6 números."),
});
export type CodeValues = z.infer<typeof codeSchema>;
