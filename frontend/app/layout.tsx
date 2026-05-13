import type { Metadata } from "next";
import { Kanit } from "next/font/google";
import { CookieBanner } from "@/components/layout/CookieBanner";
import { Footer } from "@/components/layout/Footer";
import { Navbar } from "@/components/layout/Navbar";
import "./globals.css";
import { Providers } from "./providers";

/** โหลดฟอนต์ผ่าน next/font เพื่อลด layout shift และไม่ฝัง URL Google ใน CSS เอง (กฎ G1/G5) */
const kanit = Kanit({
  subsets: ["latin", "thai"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-kanit",
  display: "swap",
});

export const metadata: Metadata = {
  title: "EduCatalog",
  description:
    "ระบบ Data Catalog การศึกษาไทย — ค้นหาและเข้าถึงเมตาดาต้าภาคการศึกษาของไทย",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="th" className={kanit.variable}>
      <body className="flex min-h-screen flex-col bg-page font-sans text-foreground antialiased">
        <Navbar />
        <Providers>
          <main className="mx-auto w-full max-w-7xl flex-1 px-4 pb-24 pt-16">
            {children}
          </main>
        </Providers>
        <Footer />
        <CookieBanner />
      </body>
    </html>
  );
}
