import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { Loader2 } from "lucide-react";
import * as React from "react";

import { cn } from "../lib/utils";

const buttonVariants = cva(
  "relative inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-full font-semibold transition-[background-color,border-color,color,transform] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent active:scale-[0.97] disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-[1.15em] [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        /** Ação principal: uma por tela. */
        primary: "bg-highlight text-ink hover:bg-highlight-hover",
        /** Ações de apoio, ao lado da principal ou sozinhas. */
        secondary: "border-2 border-stroke bg-surface text-ink hover:border-stroke-hover",
        ghost: "text-muted hover:bg-sunken hover:text-ink",
        /** Sobre imagens: branco com sombra, para descolar do fundo. */
        floating: "bg-surface text-ink shadow-float hover:bg-sunken",
        danger: "bg-danger/10 text-danger hover:bg-danger/15",
      },
      size: {
        default: "h-11 px-5 text-sm",
        sm: "h-9 px-4 text-[13px]",
        lg: "h-12 px-7 text-[15px]",
        icon: "size-10",
        "icon-sm": "size-8",
      },
    },
    defaultVariants: { variant: "secondary", size: "default" },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  /** Ação em andamento: bloqueia cliques e mostra o spinner sem mudar o tamanho. */
  pending?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    { className, variant, size, asChild = false, pending = false, disabled, children, ...props },
    ref,
  ) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        ref={ref}
        className={cn(buttonVariants({ variant, size, className }))}
        disabled={asChild ? disabled : disabled || pending}
        aria-busy={pending || undefined}
        {...props}
      >
        {asChild ? (
          children
        ) : (
          <>
            {pending && <Loader2 className="absolute animate-spin" aria-hidden />}
            <span className={cn("inline-flex items-center gap-2", pending && "invisible")}>
              {children}
            </span>
          </>
        )}
      </Comp>
    );
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };
