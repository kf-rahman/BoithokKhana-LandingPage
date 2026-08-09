import type { Menu, Order } from "../types";
import { gridTd, gridTh, money, qtyFor } from "./lib";

/** Birds-eye "quantities" grid: one row per order, one column per active
 * menu item, with a totals row and the week's revenue. This is the view Dad
 * uses to plan prep and shopping (and what Export CSV mirrors). */
export default function WeeklyGrid({
  menu,
  orders,
  columns,
  revenueCents,
}: {
  menu: Menu;
  orders: Order[];
  columns: string[];
  revenueCents: number;
}) {
  return (
    <div className="contact-info-box" style={{ marginBottom: "2rem" }}>
      {/* Flex + wrap rather than a float: on a phone the floated revenue
          overlapped the heading text instead of dropping below it. */}
      <h3
        style={{
          color: "var(--deep-red)",
          marginBottom: "1rem",
          display: "flex",
          flexWrap: "wrap",
          gap: "0.5rem",
          justifyContent: "space-between",
          alignItems: "baseline",
        }}
      >
        <span>
          <i className="fas fa-table" /> Week of {menu.week_of} — quantities
        </span>
        <span style={{ color: "var(--deep-green)" }}>
          Revenue: {money(revenueCents)}
        </span>
      </h3>
      {/* The scroller must wrap the table itself. With `width: 100%` the table
          shrank to the screen and squeezed columns into unreadable slivers
          instead of scrolling; minWidth forces it to overflow and scroll. */}
      <div style={{ overflowX: "auto", WebkitOverflowScrolling: "touch" }}>
        <p
          className="grid-scroll-hint"
          style={{ fontSize: "0.8rem", color: "#777", margin: "0 0 0.5rem" }}
        >
          Scroll sideways to see every dish.
        </p>
        <table
          style={{
            width: "100%",
            minWidth: `${180 + columns.length * 90}px`,
            borderCollapse: "collapse",
            fontSize: "0.9rem",
          }}
        >
        <thead>
          <tr>
            <th style={gridTh}>Customer</th>
            {columns.map((c) => (
              <th key={c} style={gridTh}>
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {orders.map((o) => (
            <tr key={o.id}>
              <td style={gridTd}>{o.customer_name}</td>
              {columns.map((c) => (
                <td key={c} style={{ ...gridTd, textAlign: "center" }}>
                  {qtyFor(o, c) || ""}
                </td>
              ))}
            </tr>
          ))}
          <tr>
            <td style={{ ...gridTd, fontWeight: 800 }}>TOTAL</td>
            {columns.map((c) => (
              <td key={c} style={{ ...gridTd, textAlign: "center", fontWeight: 800 }}>
                {orders.reduce((s, o) => s + qtyFor(o, c), 0) || ""}
              </td>
            ))}
          </tr>
        </tbody>
        </table>
      </div>
    </div>
  );
}
