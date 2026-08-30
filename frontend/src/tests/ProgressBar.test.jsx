import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import ProgressBar from "../components/ProgressBar";

describe("ProgressBar", () => {
  it("renders the given percentage", () => {
    render(<ProgressBar value={42} />);
    expect(screen.getByText("42% complete")).toBeInTheDocument();
  });

  it("clamps values above 100", () => {
    render(<ProgressBar value={150} />);
    expect(screen.getByText("100% complete")).toBeInTheDocument();
  });

  it("clamps negative values to 0", () => {
    render(<ProgressBar value={-10} />);
    expect(screen.getByText("0% complete")).toBeInTheDocument();
  });

  it("hides the label when showLabel is false", () => {
    render(<ProgressBar value={50} showLabel={false} />);
    expect(screen.queryByText("50% complete")).not.toBeInTheDocument();
  });
});
