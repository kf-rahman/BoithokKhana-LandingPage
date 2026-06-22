"use client";

import Link from "next/link";
import { useState } from "react";

export default function Header() {
  const [open, setOpen] = useState(false);
  const close = () => setOpen(false);

  return (
    <header>
      <nav>
        <Link href="/" className="logo" onClick={close}>
          <i className="fas fa-utensils" /> Boithok Khana
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
