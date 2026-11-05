"use client";

import { track } from "@kubo/analytics";
import type { Schemas } from "@kubo/api-client";
import { Button } from "@kubo/ui/button";
import { Check, Copy } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

function useCountdown(expiresAt: string): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);
  return Math.max(0, Math.floor((new Date(expiresAt).getTime() - now) / 1000));
}

export function PixPayment({ charge }: { charge: Schemas["Charge"] }) {
  const remaining = useCountdown(charge.expires_at);
  const [copied, setCopied] = useState(false);
  const minutes = String(Math.floor(remaining / 60)).padStart(2, "0");
  const seconds = String(remaining % 60).padStart(2, "0");

  async function copy() {
    try {
      await navigator.clipboard.writeText(charge.pix_br_code);
      setCopied(true);
      track("pix_copied");
      setTimeout(() => setCopied(false), 2500);
    } catch {
      toast.error("Não foi possível copiar. Selecione o código abaixo.");
    }
  }

  return (
    <div className="space-y-4 rounded-2xl border border-line p-5 text-center">
      <h2 className="font-display text-xl font-semibold">Pague com PIX</h2>
      {charge.pix_qr_base64 && (
        // eslint-disable-next-line @next/next/no-img-element -- QR Code gerado pelo gateway
        <img
          src={charge.pix_qr_base64}
          alt="QR Code do PIX"
          className="mx-auto size-56 rounded-xl border border-line"
        />
      )}
      <p className="text-sm text-muted">
        {remaining > 0 ? (
          <>
            Este código vale por{" "}
            <span className="font-mono font-medium text-ink" data-testid="pix-countdown">
              {minutes}:{seconds}
            </span>
          </>
        ) : (
          "Este código venceu. Estamos conferindo o pagamento."
        )}
      </p>
      <Button variant="accent" size="lg" className="w-full sm:w-auto" onClick={copy}>
        {copied ? <Check /> : <Copy />}
        {copied ? "Código copiado" : "Copiar código PIX"}
      </Button>
      <p className="break-all rounded-xl bg-sunken p-3 text-left font-mono text-xs text-muted">
        {charge.pix_br_code}
      </p>
      <p className="text-sm text-muted">
        Assim que o pagamento for identificado, esta página atualiza sozinha.
      </p>
    </div>
  );
}
