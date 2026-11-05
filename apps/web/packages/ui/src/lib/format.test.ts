import { describe, expect, it } from "vitest";

import { formatBRL, formatCep, formatCpf, formatPhone } from "./format";

describe("formatação", () => {
  it("converte centavos em reais", () => {
    expect(formatBRL(12990).replace(/\s/g, " ")).toBe("R$ 129,90");
  });

  it("aplica máscaras durante a digitação", () => {
    expect(formatCep("01310100")).toBe("01310-100");
    expect(formatCep("0131")).toBe("0131");
    expect(formatCpf("52998224725")).toBe("529.982.247-25");
    expect(formatCpf("5299")).toBe("529.9");
    expect(formatPhone("11999998888")).toBe("(11) 99999-8888");
    expect(formatPhone("1133334444")).toBe("(11) 3333-4444");
  });
});
