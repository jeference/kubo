"""E-mail no console, para desenvolvimento. Guarda uma caixa em memória para os testes."""

from __future__ import annotations

from integrations.ports import EmailPort

outbox: list[dict] = []


class ConsoleEmailAdapter(EmailPort):
    def send(self, *, to: str, subject: str, body: str, html_body: str | None = None) -> None:
        outbox.append({"to": to, "subject": subject, "body": body, "html": html_body})
        print(f"\n--- E-mail para {to}: {subject}\n{body}\n---\n", flush=True)
