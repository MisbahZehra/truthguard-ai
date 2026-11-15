import { STATUS } from "../utils";
import type { Status } from "../types";
export default function StatusBadge({ status }: { status: Status }) {
  const m = STATUS[status];
  return <span title={m.hint} className={`inline-block rounded-full border px-2.5 py-0.5 text-xs font-medium ${m.cls}`}>{m.label}</span>;
}
