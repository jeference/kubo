import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { OrderTimeline } from "./order-timeline";

describe("OrderTimeline", () => {
  it("destaca o status atual", () => {
    const { container } = render(<OrderTimeline status="in_production" />);
    expect(container.querySelector('[aria-current="step"]')).toHaveTextContent("Em produção");
    expect(screen.getByText("Entregue")).toBeInTheDocument();
  });

  it("não aparece em pedido encerrado sem produção", () => {
    const { container } = render(<OrderTimeline status="refunded" />);
    expect(container).toBeEmptyDOMElement();
  });
});
