import { PromptStep } from "@/features/creations/components/prompt-step";

const STEPS = [
  {
    title: "Descreva ou envie uma foto",
    text: "Conte o que você imagina, escolha um estilo, e a IA cria a imagem em segundos.",
  },
  {
    title: "Ajuste até ficar do seu jeito",
    text: "Peça mudanças conversando, até a imagem ficar do jeito que você quer.",
  },
  {
    title: "Receba em casa",
    text: "Escolha o tamanho, pague com PIX, e a gente imprime e envia a sua peça.",
  },
];

const QUESTIONS = [
  {
    question: "Preciso criar conta?",
    answer:
      "Não. Você cria e compra sem conta, e acompanha o pedido pelo link enviado ao seu e-mail. A conta serve para ver suas criações em outros dispositivos.",
  },
  {
    question: "A peça fica igual à imagem?",
    answer:
      "A imagem é uma prévia. A peça é impressa em filamento com até 4 cores, então forma, cores e detalhes podem variar.",
  },
  {
    question: "Quais são as formas de pagamento?",
    answer:
      "No momento, aceitamos PIX. O pedido é confirmado assim que o pagamento é identificado.",
  },
  {
    question: "Quanto tempo leva?",
    answer:
      "O prazo aparece antes de você pagar, somando o tempo de produção ao do frete para o seu CEP.",
  },
];

export default function HomePage() {
  return (
    <div className="space-y-20">
      <PromptStep />

      <section className="mx-auto max-w-5xl" aria-labelledby="como-funciona">
        <h2
          id="como-funciona"
          className="text-center font-display text-2xl font-semibold tracking-tight"
        >
          Como funciona
        </h2>
        <ol className="mt-8 grid gap-6 md:grid-cols-3">
          {STEPS.map((step, index) => (
            <li key={step.title} className="rounded-3xl bg-sunken p-6">
              <span className="flex size-10 items-center justify-center rounded-full bg-accent font-display font-semibold text-highlight">
                {index + 1}
              </span>
              <h3 className="mt-4 font-semibold">{step.title}</h3>
              <p className="mt-2 text-sm text-muted">{step.text}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="mx-auto max-w-3xl" aria-labelledby="perguntas">
        <h2
          id="perguntas"
          className="text-center font-display text-2xl font-semibold tracking-tight"
        >
          Perguntas frequentes
        </h2>
        <dl className="mt-8 space-y-3">
          {QUESTIONS.map((item) => (
            <div key={item.question} className="rounded-2xl bg-sunken p-5">
              <dt className="font-semibold">{item.question}</dt>
              <dd className="mt-1.5 text-sm text-muted">{item.answer}</dd>
            </div>
          ))}
        </dl>
      </section>
    </div>
  );
}
