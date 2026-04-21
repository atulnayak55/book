type StatusMessageProps = {
  title: string;
  subtitle?: string;
};

export function StatusMessage({ title, subtitle }: StatusMessageProps) {
  return (
    <div className="status-message" role="status" aria-live="polite">
      <p className="status-title">{title}</p>
      {subtitle ? <p className="status-subtitle">{subtitle}</p> : null}
    </div>
  );
}
