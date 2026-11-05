"use client";

import * as React from "react";
import {
  Controller,
  type FieldPath,
  type FieldValues,
  FormProvider,
  type UseControllerProps,
  useFormContext,
} from "react-hook-form";

import { cn } from "../lib/utils";
import { Input } from "./input";
import { Label } from "./label";

const Form = FormProvider;

/** Campo de texto com rótulo e erro, ligado ao formulário. `format` aplica uma máscara. */
function TextField<T extends FieldValues, N extends FieldPath<T> = FieldPath<T>>({
  label,
  hint,
  format,
  className,
  type,
  autoComplete,
  placeholder,
  inputMode,
  maxLength,
  autoFocus,
  disabled,
  ...controller
}: UseControllerProps<T, N> & {
  label: string;
  hint?: string;
  format?: (value: string) => string;
  className?: string;
} & Pick<
    React.ComponentProps<"input">,
    "type" | "autoComplete" | "placeholder" | "inputMode" | "maxLength" | "autoFocus"
  >) {
  const id = React.useId();
  useFormContext<T>();
  return (
    <Controller
      {...controller}
      disabled={disabled}
      render={({ field, fieldState }) => (
        <div className={cn("space-y-1.5", className)}>
          <Label htmlFor={id}>{label}</Label>
          <Input
            {...field}
            id={id}
            type={type}
            autoComplete={autoComplete}
            placeholder={placeholder}
            inputMode={inputMode}
            maxLength={maxLength}
            autoFocus={autoFocus}
            value={field.value ?? ""}
            aria-invalid={Boolean(fieldState.error)}
            aria-describedby={fieldState.error ? `${id}-error` : undefined}
            onChange={(event) =>
              field.onChange(format ? format(event.target.value) : event.target.value)
            }
          />
          {hint && !fieldState.error && <p className="text-xs text-muted">{hint}</p>}
          {fieldState.error && (
            <p id={`${id}-error`} className="text-xs font-medium text-danger">
              {fieldState.error.message}
            </p>
          )}
        </div>
      )}
    />
  );
}

export { Form, TextField };
