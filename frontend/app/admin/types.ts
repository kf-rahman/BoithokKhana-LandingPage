/** Shared admin types, mirroring the backend schemas. */

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

export type StructuredOrder = {
  items: StructuredItem[];
  delivery_notes: string | null;
  unmatched_text: string | null;
};

export type Order = {
  id: string;
  raw_text: string;
  customer_name: string;
  customer_contact: string;
  structured_items: StructuredOrder | null;
  delivery_date: string | null;
  item_confidence: Confidence | null;
  delivery_confidence: Confidence | null;
  status: OrderStatus;
  created_at: string;
  corrected_at: string | null;
  correction_note: string | null;
  confirmation_email_sent: boolean;
  delivered: boolean;
  total_cents: number;
};

export type MenuItem = { name: string; price_cents: number };

export type MenuWeek = {
  id: string;
  week_start_date: string;
  items: MenuItem[];
};

export const money = (cents: number): string => `$${(cents / 100).toFixed(2)}`;
