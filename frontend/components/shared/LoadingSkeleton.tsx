/**
 * ใช้ pulse แทน spinner ตลอดเพราะ skeleton บอกตำแหน่ง layout ชัดกว่าเมื่อรอ async (กฎ F4)
 */

type SkeletonVariant = "card" | "text" | "table";

export function LoadingSkeleton({ variant }: { variant: SkeletonVariant }) {
  const bar = "h-4 w-full animate-pulse bg-border opacity-70";

  if (variant === "card") {
    return (
      <div
        className="border border-border bg-surface shadow-sm"
        style={{ padding: "var(--pad-card-lg)" }}
      >
        <div className="mb-4 h-6 w-1/3 animate-pulse bg-border opacity-70" />
        <div className={bar} />
        <div style={{ height: "var(--space-2)" }} />
        <div className={bar} />
        <div style={{ height: "var(--space-2)" }} />
        <div className={bar} />
      </div>
    );
  }

  if (variant === "text") {
    return (
      <div className="flex flex-col" style={{ gap: "var(--space-2)" }}>
        <div className={bar} />
        <div className={bar} />
        <div className="h-4 w-2/3 animate-pulse bg-border opacity-70" />
      </div>
    );
  }

  return (
    <div className="border border-border bg-surface">
      <div className="grid grid-cols-4 gap-2 border-b border-border p-3">
        {["h1", "h2", "h3", "h4"].map((h) => (
          <div key={h} className="h-4 animate-pulse bg-border opacity-70" />
        ))}
      </div>
      {[0, 1, 2, 3, 4].map((i) => (
        <div key={i} className="grid grid-cols-4 gap-2 border-b border-border p-3">
          {[0, 1, 2, 3].map((j) => (
            <div key={j} className="h-4 animate-pulse bg-border opacity-50" />
          ))}
        </div>
      ))}
    </div>
  );
}
