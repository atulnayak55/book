import type { ReactNode } from "react";

type SelectFieldProps = {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  children: ReactNode;
};

export function SelectField({
  id,
  label,
  value,
  onChange,
  disabled,
  children,
}: SelectFieldProps) {
  return (
    <label className="select-wrap" htmlFor={id}>
      <span className="select-label">{label}</span>
      <select
        id={id}
        className="select-input"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
      >
        {children}
      </select>
    </label>
  );
}
