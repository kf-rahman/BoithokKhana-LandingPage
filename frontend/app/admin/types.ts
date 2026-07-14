// Shared types for the admin orders dashboard. These mirror the backend
// JSON shapes returned by the API — OrderRead / MenuRead in
// backend/app/schemas (order.py, menu.py). Co-located per CLAUDE.md.

export type OrderItem = {
  id: number;
  item_name: string;
  quantity: number;
  notes: string | null;
  menu_item_id: number | null;
  unit_price_cents: number | null;
};

export type Order = {
  id: number;
  customer_name: string;
  customer_email: string | null;
  customer_phone: string;
  raw_text: string;
  status: string;
  menu_id: number | null;
  items: OrderItem[];
  total_cents: number;
  delivery_date: string | null;
  delivery_notes: string | null;
  confidence: string | null;
  unmatched_text: string | null;
  confirmation_email_sent: boolean;
  delivered: boolean;
  created_at: string;
  updated_at: string;
};

export type MenuItem = { id: number; name: string; price_cents: number; active: boolean };

export type Menu = {
  id: number;
  week_of: string;
  status: string;
  published_at: string | null;
  items: MenuItem[];
};

export type Message = { kind: "error" | "success" | "info"; text: string };
export type EditRow = { item_name: string; quantity: string; notes: string };
export type DetailsForm = {
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  delivery_date: string;
  delivery_notes: string;
};
export type CreateForm = DetailsForm & { raw_text: string };
