import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

export const metadata: Metadata = {
  title: "Boithok Khana | Order System",
  description:
    "Order authentic Bangladeshi weekly meals and catering from Boithok Khana.",
  // Same knife-and-fork icon the marketing page uses, so /order and /admin
  // don't fall back to the browser's default globe.
  icons: {
    icon: "/favicon.svg",
    apple: "/favicon.svg",
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Header />
        {children}
        <Footer />
      </body>
    </html>
  );
}
