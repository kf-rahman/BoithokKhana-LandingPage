import { useState } from "react";
import { API_BASE_URL } from "@/lib/api";
import type { CreateForm, DetailsForm, EditRow, Menu, Message, Order } from "../types";
import { buildCsv, detailsPayload, EMPTY_CREATE } from "./lib";

const EMPTY_DETAILS: DetailsForm = {
  customer_name: "",
  customer_email: "",
  customer_phone: "",
  delivery_date: "",
  delivery_notes: "",
};

/** All state + server interactions for the orders dashboard, kept out of the
 * page so the page stays a thin composition of components. Every admin call
 * carries the shared PIN in the X-Admin-Pin header; the raw order text is
 * never mutated here. */
export function useOrdersAdmin() {
  const [pin, setPin] = useState("");
  const [orders, setOrders] = useState<Order[]>([]);
  const [menu, setMenu] = useState<Menu | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [message, setMessage] = useState<Message | null>(null);
  const [busy, setBusy] = useState(false);
  const [parsingId, setParsingId] = useState<number | null>(null);
  const [parsingAll, setParsingAll] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [createForm, setCreateForm] = useState<CreateForm>(EMPTY_CREATE);
  const [editing, setEditing] = useState<number | null>(null);
  const [editRows, setEditRows] = useState<EditRow[]>([]);
  const [editDetails, setEditDetails] = useState<DetailsForm>(EMPTY_DETAILS);

  function adminFetch(path: string, init?: RequestInit): Promise<Response> {
    return fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        "X-Admin-Pin": pin,
        ...(init?.headers ?? {}),
      },
    });
  }

  function applyUpdated(updated: Order) {
    setOrders((prev) => prev.map((o) => (o.id === updated.id ? updated : o)));
  }

  async function loadAll() {
    if (!pin) {
      setMessage({ kind: "error", text: "Enter the admin PIN first." });
      return;
    }
    setBusy(true);
    setMessage(null);
    try {
      const res = await adminFetch("/api/admin/orders");
      if (res.status === 401) {
        setMessage({ kind: "error", text: "Wrong admin PIN." });
        return;
      }
      if (!res.ok) {
        setMessage({ kind: "error", text: "Couldn't load orders." });
        return;
      }
      setOrders((await res.json()) as Order[]);
      const menuRes = await fetch(`${API_BASE_URL}/api/menus/current`, { cache: "no-store" });
      setMenu(menuRes.ok ? ((await menuRes.json()) as Menu) : null);
      setLoaded(true);
    } catch {
      setMessage({ kind: "error", text: "Couldn't reach the server." });
    } finally {
      setBusy(false);
    }
  }

  async function createOrder() {
    if (!pin.trim()) {
      setMessage({ kind: "error", text: "Enter the admin PIN at the top first, then save." });
      return;
    }
    if (
      !createForm.customer_name.trim() ||
      !createForm.customer_phone.trim() ||
      !createForm.raw_text.trim()
    ) {
      setMessage({ kind: "error", text: "Name, phone, and the order text are required." });
      return;
    }
    setBusy(true);
    setMessage(null);
    try {
      const res = await adminFetch("/api/admin/orders", {
        method: "POST",
        body: JSON.stringify({ ...detailsPayload(createForm), raw_text: createForm.raw_text }),
      });
      if (res.status === 201) {
        const created = (await res.json()) as Order;
        setOrders((prev) => [created, ...prev]);
        setLoaded(true);
        setShowCreate(false);
        setCreateForm(EMPTY_CREATE);
        setMessage({ kind: "success", text: `Added order #${created.id}.` });
      } else if (res.status === 401) {
        setMessage({ kind: "error", text: "Wrong admin PIN." });
      } else {
        setMessage({ kind: "error", text: "Couldn't create the order." });
      }
    } catch {
      setMessage({ kind: "error", text: "Couldn't reach the server." });
    } finally {
      setBusy(false);
    }
  }

  async function deleteOrder(order: Order) {
    if (
      !window.confirm(
        `Delete order #${order.id} from ${order.customer_name}? This can't be undone.`,
      )
    ) {
      return;
    }
    setBusy(true);
    try {
      const res = await adminFetch(`/api/admin/orders/${order.id}`, { method: "DELETE" });
      if (res.status === 204) {
        setOrders((prev) => prev.filter((o) => o.id !== order.id));
        setMessage({ kind: "success", text: `Deleted order #${order.id}.` });
      } else if (res.status === 401) {
        setMessage({ kind: "error", text: "Wrong admin PIN." });
      } else {
        setMessage({ kind: "error", text: "Couldn't delete that order." });
      }
    } catch {
      setMessage({ kind: "error", text: "Couldn't reach the server." });
    } finally {
      setBusy(false);
    }
  }

  async function parseAllPending() {
    setBusy(true);
    setParsingAll(true);
    setMessage({ kind: "info", text: "Parsing pending orders — this can take a few seconds…" });
    try {
      const res = await adminFetch("/api/admin/orders/parse-pending", { method: "POST" });
      if (res.ok) {
        const parsed = (await res.json()) as Order[];
        setMessage({ kind: "success", text: `Parsed ${parsed.length} pending order(s).` });
        await loadAll();
      } else if (res.status === 503) {
        setMessage({
          kind: "error",
          text: "Parser not configured — set ANTHROPIC_API_KEY on the backend.",
        });
      } else {
        setMessage({ kind: "error", text: "Couldn't parse pending orders." });
      }
    } catch {
      setMessage({ kind: "error", text: "Couldn't reach the server." });
    } finally {
      setBusy(false);
      setParsingAll(false);
    }
  }

  async function toggleFlag(order: Order, field: "confirmation_email_sent" | "delivered") {
    setBusy(true);
    try {
      const res = await adminFetch(`/api/admin/orders/${order.id}`, {
        method: "PATCH",
        body: JSON.stringify({ [field]: !order[field] }),
      });
      if (res.ok) applyUpdated((await res.json()) as Order);
      else setMessage({ kind: "error", text: "Couldn't update the order." });
    } catch {
      setMessage({ kind: "error", text: "Couldn't reach the server." });
    } finally {
      setBusy(false);
    }
  }

  async function parseOrder(order: Order) {
    setBusy(true);
    setParsingId(order.id);
    setMessage({ kind: "info", text: `Parsing order #${order.id} — this takes a few seconds…` });
    try {
      const res = await adminFetch(`/api/admin/orders/${order.id}/parse`, { method: "POST" });
      if (res.ok) {
        applyUpdated((await res.json()) as Order);
        setMessage({ kind: "success", text: `Parsed order #${order.id}.` });
      } else if (res.status === 503) {
        setMessage({
          kind: "error",
          text: "Parser not configured — set ANTHROPIC_API_KEY on the backend.",
        });
      } else {
        setMessage({ kind: "error", text: "Couldn't parse that order." });
      }
    } catch {
      setMessage({ kind: "error", text: "Couldn't reach the server." });
    } finally {
      setBusy(false);
      setParsingId(null);
    }
  }

  function startEdit(order: Order) {
    setEditing(order.id);
    setEditRows(
      order.items.length > 0
        ? order.items.map((it) => ({
            item_name: it.item_name,
            quantity: String(it.quantity),
            notes: it.notes ?? "",
          }))
        : [{ item_name: "", quantity: "1", notes: "" }],
    );
    setEditDetails({
      customer_name: order.customer_name,
      customer_email: order.customer_email ?? "",
      customer_phone: order.customer_phone,
      delivery_date: order.delivery_date ?? "",
      delivery_notes: order.delivery_notes ?? "",
    });
  }

  function cancelEdit() {
    setEditing(null);
  }

  function updateEditRow(index: number, field: keyof EditRow, value: string) {
    setEditRows((prev) => prev.map((r, i) => (i === index ? { ...r, [field]: value } : r)));
  }

  function addEditRow() {
    setEditRows((prev) => [...prev, { item_name: "", quantity: "1", notes: "" }]);
  }

  function removeEditRow(index: number) {
    setEditRows((prev) => (prev.length === 1 ? prev : prev.filter((_, i) => i !== index)));
  }

  async function saveEdit(order: Order) {
    const items = editRows
      .map((r) => ({
        item_name: r.item_name.trim(),
        quantity: parseInt(r.quantity, 10),
        notes: r.notes.trim() || null,
      }))
      .filter((r) => r.item_name !== "" && Number.isFinite(r.quantity) && r.quantity >= 1);
    if (!editDetails.customer_name.trim() || !editDetails.customer_phone.trim()) {
      setMessage({ kind: "error", text: "Name and phone are required." });
      return;
    }
    setBusy(true);
    try {
      const detailsRes = await adminFetch(`/api/admin/orders/${order.id}`, {
        method: "PATCH",
        body: JSON.stringify(detailsPayload(editDetails)),
      });
      if (!detailsRes.ok) {
        setMessage({ kind: "error", text: "Couldn't save the order details." });
        return;
      }
      const itemsRes = await adminFetch(`/api/admin/orders/${order.id}/items`, {
        method: "PATCH",
        body: JSON.stringify({ items }),
      });
      if (itemsRes.ok) {
        applyUpdated((await itemsRes.json()) as Order);
        setEditing(null);
        setMessage({ kind: "success", text: `Order #${order.id} updated.` });
      } else {
        setMessage({ kind: "error", text: "Saved details, but couldn't save the items." });
      }
    } catch {
      setMessage({ kind: "error", text: "Couldn't reach the server." });
    } finally {
      setBusy(false);
    }
  }

  const columns = menu ? menu.items.filter((i) => i.active).map((i) => i.name) : [];
  const revenueCents = orders.reduce((s, o) => s + o.total_cents, 0);
  const pendingCount = orders.filter((o) => o.status === "pending_parse").length;

  function exportCsv() {
    const csv = buildCsv(orders, columns);
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `orders-week-${menu?.week_of ?? "current"}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return {
    // state
    pin,
    setPin,
    orders,
    menu,
    loaded,
    message,
    busy,
    parsingId,
    parsingAll,
    showCreate,
    setShowCreate,
    createForm,
    setCreateForm,
    editing,
    editRows,
    editDetails,
    setEditDetails,
    // actions
    loadAll,
    createOrder,
    deleteOrder,
    parseAllPending,
    toggleFlag,
    parseOrder,
    startEdit,
    cancelEdit,
    updateEditRow,
    addEditRow,
    removeEditRow,
    saveEdit,
    exportCsv,
    // derived
    columns,
    revenueCents,
    pendingCount,
  };
}
