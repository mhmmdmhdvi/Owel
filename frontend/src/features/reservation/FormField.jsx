export default function FormField({ name, label, error, hint, ...props }) {
  const describedBy = [hint && `${name}-hint`, error && `${name}-error`].filter(Boolean).join(' ') || undefined;
  return (
    <div className="reservation-field">
      <label htmlFor={name}>{label}</label>
      <input id={name} name={name} required aria-invalid={Boolean(error)} aria-describedby={describedBy} {...props} />
      {hint && <p className="field-hint" id={`${name}-hint`}>{hint}</p>}
      {error && <p className="field-error" id={`${name}-error`}>{error}</p>}
    </div>
  );
}
