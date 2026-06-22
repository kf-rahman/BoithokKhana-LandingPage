/** Shared types for the admin dashboard, mirroring the backend schemas. */

export type Confidence = "high" | "medium" | "low";
export type OrderStatus = "pending_parse" | "parsed" | "needs_review";

export type StructuredItem = {
  name: string;
  quantity: number;
  modifiers: string[];
  notes: string | null;
  matched: boolean;
  unit_price_cents: number | null;
};

export type Order = {
  id: string;
  raw_text: string;
  customer_name: string;
  customer_phone: string;
  customer_email: string | null;
  structured_items: StructuredItem[] | null;
  delivery_date: string | null;
  delivery_notes: string | null;
  item_confidence: Confidence | null;
  delivery_confidence: Confidence | null;
  status: OrderStatus;
  unmatched_text: string | null;
  menu_week_id: string | null;
  confirmation_email_sent: boolean;
  delivered: boolean;
  created_at: string;
  corrected_at: string | null;
  correction_note: string | null;
  total_cents: number;
};

export type MenuItem = { name: string; price_cents: number };

export type MenuWeek = {
  id: string;
  week_start_date: string;
  published: boolean;
  items: MenuItem[];
  created_at: string;
};

export const money = (cents: number): string => `$${(cents / 100).toFixed(2)}`;
