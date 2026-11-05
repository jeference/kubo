import { ApiError } from "@kubo/api-client";
import type { FieldValues, Path, UseFormSetError } from "react-hook-form";
import { toast } from "sonner";

/** Leva os erros do servidor aos campos e mostra a mensagem. O backend é a autoridade. */
export function handleFormError<T extends FieldValues>(
  error: unknown,
  setError?: UseFormSetError<T>,
): void {
  if (error instanceof ApiError) {
    if (setError && error.fieldErrors) {
      for (const [field, messages] of Object.entries(error.fieldErrors)) {
        if (messages.length > 0) {
          setError(field as Path<T>, { type: "server", message: messages[0] });
        }
      }
    }
    toast.error(error.message);
    return;
  }
  toast.error("Erro inesperado. Tente de novo.");
}
