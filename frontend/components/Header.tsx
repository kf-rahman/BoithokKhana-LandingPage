"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

export default function Header() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const close = () => setOpen(false);

  return (
    <header
      style={{
        boxShadow: scrolled
          ? "0 4px 30px rgba(220, 38, 38, 0.4)"
          : "0 4px 20px rgba(220, 38, 38, 0.3)",
      }}
    >
      <nav>
        <Link href="/" className="logo" onClick={close}>
          <i className="fas fa-utensils" />
          Boithok Khana
        </Link>
        <ul className={`nav-links${open ? " active" : ""}`}>
          <li>
            <Link href="/" onClick={close}>
              Home
            </Link>
          </li>
          <li>
            <Link href="/order#menu" onClick={close}>
              Menu
            </Link>
          </li>
          <li>
            <Link href="/order" onClick={close}>
              Order
            </Link>
          </li>
        </ul>
        <div className="mobile-menu" onClick={() => setOpen((v) => !v)}>
          <i className="fas fa-bars" />
        </div>
      </nav>
    </header>
  );
}
