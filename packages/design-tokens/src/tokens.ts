/** Raios generosos em tudo: a identidade da Kubo é arredondada, nunca quadrada. */
export const borderRadius = { lg: "12px", xl: "16px", "2xl": "24px", "3xl": "32px" };

export const boxShadow = {
  card: "0 1px 2px rgb(20 20 20 / 0.04), 0 8px 24px -12px rgb(20 20 20 / 0.12)",
  /** Botões que flutuam sobre imagens. */
  float: "0 2px 10px -2px rgb(20 20 20 / 0.18)",
};

/** Tom visual de um status: cada status mapeia para um deles em `ui/lib/status`. */
export type StatusTone = "neutral" | "progress" | "success" | "danger";
