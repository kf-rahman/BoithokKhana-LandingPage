import type { CSSProperties } from "react";
import type { Message } from "../types";
import { messageBg } from "./lib";

/** Coloured status banner (error / success / info). Renders nothing when
 * there's no message. */
export default function MessageBanner({
  message,
  extra,
}: {
  message: Message | null;
  extra?: CSSProperties;
}) {
  if (!message) return null;
  return (
    <div
      style={{
        marginBottom: "1.5rem",
        padding: "0.85rem 1rem",
        borderRadius: "10px",
        fontWeight: 600,
        color: "white",
        background: messageBg(message.kind),
        ...extra,
      }}
    >
      {message.kind === "info" && <i className="fas fa-spinner fa-spin" />} {message.text}
    </div>
  );
}
