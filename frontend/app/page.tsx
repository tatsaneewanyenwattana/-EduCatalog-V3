/** โฮมเพจจริงจะอยู่ กลุ่มงานถัดไป — เก็บ placeholder ให้ build และ navigation ครบจนเปิดฟีเจอร์ได้ */
export default function HomePage() {
  return (
    <section
      className="flex flex-col justify-center border border-border bg-surface shadow-sm"
      style={{
        padding: "var(--pad-card-lg)",
        gap: "var(--space-6)",
        minHeight: "50vh",
      }}
    >
      <p className="text-2xl font-bold tracking-tight text-primary">
        EduCatalog — ระบบ Data Catalog การศึกษาไทย
      </p>
      <p className="max-w-xl text-base text-foreground-secondary">
        หน้าแรกเต็มรูปแบบ (ค้นหา ภาพรวม) อยู่ในแผนกลุ่มถัดไป — โครงเลย์เอาต์และธีมใช้ Design System เดียวกับที่กำหนดใน globals.css และ Tailwind tokens
      </p>
    </section>
  );
}
