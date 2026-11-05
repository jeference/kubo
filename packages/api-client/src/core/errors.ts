export type FieldErrors = Record<string, string[]>;

export interface ApiErrorData {
  status: number;
  /** Código do backend, ou derivado do status. */
  code: string;
  /** Mensagem do backend, ou genérica em português. */
  message: string;
  fieldErrors?: FieldErrors;
  raw: unknown;
}

const GENERIC_MESSAGE = "Não foi possível concluir a ação. Tente de novo.";

function codeForStatus(status: number): string {
  switch (status) {
    case 400:
      return "bad_request";
    case 401:
      return "unauthorized";
    case 403:
      return "forbidden";
    case 404:
      return "not_found";
    case 409:
      return "conflict";
    case 422:
      return "unprocessable";
    case 429:
      return "too_many_requests";
    case 0:
      return "network_error";
    default:
      return status >= 500 ? "server_error" : "error";
  }
}

/**
 * Único formato de erro do app. O backend fala dois dialetos, normalizados aqui:
 * erros de domínio `{ detail, code }` e validação do DRF `{ campo: [mensagens] }`.
 */
export class ApiError extends Error implements ApiErrorData {
  readonly status: number;
  readonly code: string;
  readonly fieldErrors?: FieldErrors;
  readonly raw: unknown;

  constructor(data: ApiErrorData) {
    super(data.message);
    this.name = "ApiError";
    this.status = data.status;
    this.code = data.code;
    this.fieldErrors = data.fieldErrors;
    this.raw = data.raw;
  }
}

export function normalizeError(status: number, body: unknown): ApiError {
  if (body === null || typeof body !== "object") {
    return new ApiError({
      status,
      code: codeForStatus(status),
      message: GENERIC_MESSAGE,
      raw: body,
    });
  }

  const record = body as Record<string, unknown>;
  if (typeof record.detail === "string") {
    return new ApiError({
      status,
      code: typeof record.code === "string" ? record.code : codeForStatus(status),
      message: record.detail,
      raw: body,
    });
  }

  const fieldErrors: FieldErrors = {};
  let message = "";
  for (const [key, value] of Object.entries(record)) {
    const messages = Array.isArray(value)
      ? value.filter((item): item is string => typeof item === "string")
      : typeof value === "string"
        ? [value]
        : [];
    if (messages.length === 0) continue;
    if (key === "non_field_errors" || key === "detail") {
      if (!message) message = messages[0];
    } else {
      fieldErrors[key] = messages;
    }
  }
  if (!message) message = Object.values(fieldErrors)[0]?.[0] ?? GENERIC_MESSAGE;

  return new ApiError({
    status,
    code: typeof record.code === "string" ? record.code : codeForStatus(status),
    message,
    fieldErrors: Object.keys(fieldErrors).length > 0 ? fieldErrors : undefined,
    raw: body,
  });
}
