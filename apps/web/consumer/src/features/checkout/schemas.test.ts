import { describe, expect, it } from "vitest";

import { checkoutSchema, isValidCpf } from "./schemas";

const VALID = {
  email: "ana@exemplo.com",
  name: "Ana Souza",
  cpf: "529.982.247-25",
  phone: "(11) 99999-8888",
  postal_code: "01310-100",
  street: "Av. Paulista",
  number: "1000",
  complement: "",
  neighborhood: "Bela Vista",
  city: "São Paulo",
  state: "SP",
};

describe("checkout", () => {
  it("valida o dígito do CPF", () => {
    expect(isValidCpf("52998224725")).toBe(true);
    expect(isValidCpf("52998224724")).toBe(false);
    expect(isValidCpf("11111111111")).toBe(false);
    expect(isValidCpf("123")).toBe(false);
  });

  it("aceita dados válidos e recusa os inválidos", () => {
    expect(checkoutSchema.safeParse(VALID).success).toBe(true);
    expect(checkoutSchema.safeParse({ ...VALID, phone: "123" }).success).toBe(false);
    expect(checkoutSchema.safeParse({ ...VALID, state: "São Paulo" }).success).toBe(false);
    expect(checkoutSchema.safeParse({ ...VALID, postal_code: "123" }).success).toBe(false);
  });
});
