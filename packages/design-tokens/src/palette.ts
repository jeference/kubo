/**
 * Identidade da Kubo: roxo, amarelo neon e branco. Mantida em sincronia com `styles/tokens.css`.
 * Amarelo neon é quase invisível sobre branco: use como preenchimento ou sobre roxo, nunca como
 * texto em fundo branco.
 */
export const palette = {
  background: "#FFFFFF",
  surface: "#FFFFFF",
  sunken: "#F4F4F4",
  ink: "#141414",
  muted: "#6B6B6B",
  line: "#E5E5E5",
  /** Contorno dos controles: botão secundário, chips, contador, campos. */
  stroke: "#D6D6D6",
  strokeHover: "#ABABAB",
  accent: "#7C3AED",
  accentSoft: "#F0E9FF",
  highlight: "#FAFF00",
  highlightHover: "#F0F500",
  danger: "#C82828",
  success: "#1F8A4C",
} as const;
