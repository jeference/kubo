import { describe, expect, it } from "vitest";

import { normalizeError } from "./errors";

describe("normalizeError", () => {
  it("lê erro de domínio", () => {
    const error = normalizeError(429, {
      detail: "Limite do dia atingido.",
      code: "quota_exceeded",
      quota_kind: "image",
    });
    expect(error.code).toBe("quota_exceeded");
    expect(error.message).toBe("Limite do dia atingido.");
    expect((error.raw as { quota_kind: string }).quota_kind).toBe("image");
  });

  it("lê validação do DRF e usa a primeira mensagem", () => {
    const error = normalizeError(400, { email: ["E-mail inválido."] });
    expect(error.fieldErrors).toEqual({ email: ["E-mail inválido."] });
    expect(error.message).toBe("E-mail inválido.");
    expect(error.code).toBe("bad_request");
  });

  it("usa mensagem genérica sem corpo", () => {
    const error = normalizeError(500, null);
    expect(error.code).toBe("server_error");
    expect(error.message).toContain("Tente de novo");
  });
});
