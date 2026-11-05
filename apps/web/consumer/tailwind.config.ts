import { tailwindPreset } from "@kubo/design-tokens";
import type { Config } from "tailwindcss";

const config: Config = {
  presets: [tailwindPreset as Config],
  content: [
    "./src/**/*.{ts,tsx}",
    "../packages/ui/src/**/*.{ts,tsx}",
    "../packages/web-core/src/**/*.{ts,tsx}",
  ],
};

export default config;
