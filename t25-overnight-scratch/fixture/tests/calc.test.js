import { describe, it, expect } from "vitest";
import { evaluate } from "../src/calc.js";

describe("evaluate", () => {
  it("adds", () => expect(evaluate("1+2")).toBe(3));
  it("respects precedence", () => expect(evaluate("2+3*4")).toBe(14));
  it("parens override precedence", () => expect(evaluate("(2+3)*4")).toBe(20));
  it("subtracts left-associative", () => expect(evaluate("10-2-3")).toBe(5));
  it("divides left-associative", () => expect(evaluate("12/4/3")).toBe(1));
  it("unary minus at start", () => expect(evaluate("-5+2")).toBe(-3));
  it("unary minus after operator", () => expect(evaluate("3*-2")).toBe(-6));
  it("nested parens", () => expect(evaluate("((1+2)*(3+4))")).toBe(21));
  it("decimals", () => expect(evaluate("0.5*4")).toBe(2));
  it("ignores whitespace", () => expect(evaluate(" 2  +  2 ")).toBe(4));
  it("throws on divide by zero", () =>
    expect(() => evaluate("1/0")).toThrow("division by zero"));
  it("deep nested precedence", () => expect(evaluate("2*(3+4*(5-1))")).toBe(38));
});
