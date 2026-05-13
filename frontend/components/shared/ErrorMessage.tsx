/**
 * โชว์ error ใกล้ฟอร์ม/ส่วนที่ fail แทนให้ error หายเงียบ (กฎ F5)
 */

export interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorMessage({ message, onRetry }: ErrorMessageProps) {
  return (
    <div
      className="flex flex-col border border-error bg-page"
      role="alert"
      style={{ gap: "var(--space-2)", padding: "var(--pad-card)" }}
    >
      <p className="text-sm font-medium text-error">{message}</p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="self-start border border-error text-sm font-semibold text-error hover:bg-primary-light"
          style={{ padding: "var(--pad-btn-sm)" }}
        >
          ลองใหม่
        </button>
      ) : null}
    </div>
  );
}
