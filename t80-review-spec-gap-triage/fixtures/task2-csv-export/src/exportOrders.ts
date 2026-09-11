import { writeFileSync } from "node:fs";

export type OrderStatus = "pending" | "paid" | "shipped" | "cancelled";

export interface Order {
  id: string;
  phone: string;
  amountCents: number;
  status: OrderStatus;
  createdAt: Date;
}

const HEADER = ["订单号", "用户手机号", "金额", "状态", "创建时间"];

function maskPhone(phone: string): string {
  if (phone.length !== 11) return phone;
  return phone.slice(0, 3) + "****" + phone.slice(7);
}

function formatAmount(cents: number): string {
  return (cents / 100).toFixed(1);
}

function csvCell(v: string): string {
  if (/[",\n]/.test(v)) return '"' + v.replace(/"/g, '""') + '"';
  return v;
}

function inRange(order: Order, start: Date, end: Date): boolean {
  return order.createdAt >= start && order.createdAt < end;
}

export function buildCsv(orders: Order[], start: Date, end: Date): string {
  const rows = orders
    .filter((o) => o.status !== "pending")
    .filter((o) => inRange(o, start, end))
    .map((o) => [
      o.id,
      maskPhone(o.phone),
      formatAmount(o.amountCents),
      o.status,
      o.createdAt.toISOString(),
    ]);
  return [HEADER, ...rows].map((r) => r.map(csvCell).join(",")).join("\n");
}

function ymd(d: Date): string {
  return d.toISOString().slice(0, 10);
}

/** start / end 为运营在页面上选的日期（YYYY-MM-DD） */
export function exportOrders(orders: Order[], startYmd: string, endYmd: string, dir = "."): string {
  const start = new Date(startYmd);
  const end = new Date(endYmd);
  const csv = buildCsv(orders, start, end);
  const file = `${dir}/orders_${ymd(start)}_${ymd(end)}.csv`;
  writeFileSync(file, csv, { encoding: "utf8" });
  return file;
}
