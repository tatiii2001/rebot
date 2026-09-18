import { act, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { App } from "./App";

describe("Control Center start mission", () => {
  it("shows the local visual mission transition after the Operator starts it", async () => {
    const user = userEvent.setup();
    render(<App />);

    expect(screen.getByText("pending")).toBeInTheDocument();
    expect(screen.getByText("available")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Start Mission" }));

    expect(screen.getByText("running")).toBeInTheDocument();
    expect(screen.getByText("executing mission")).toBeInTheDocument();
    expect(screen.getByText("Target selected: plastic waste")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Mission running" })).toBeDisabled();
  });
});

describe("Control Center route preview", () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("plays the predefined plastic Waste Item route after the Mission starts", () => {
    vi.useFakeTimers();
    render(<App />);

    expect(screen.getByRole("button", { name: "Play route preview" })).toBeDisabled();
    expect(screen.queryByText("Predefined local route")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Start Mission" }));

    expect(screen.getByText("Target selected: plastic waste")).toBeInTheDocument();
    expect(screen.getByLabelText("Selected target: Plastic Waste Item at grid position 2, 2")).toBeInTheDocument();
    expect(screen.getByText("Predefined local route")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Play route preview" })).toBeEnabled();

    fireEvent.click(screen.getByRole("button", { name: "Play route preview" }));

    expect(screen.getByText("Following route to plastic waste")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Play route preview" })).toBeDisabled();

    act(() => {
      vi.advanceTimersByTime(550);
    });

    expect(screen.getByLabelText("Robot at grid position 4, 6")).toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(4_000);
    });

    expect(screen.getByText("Ready to collect plastic waste")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Route preview complete" })).toBeDisabled();
    expect(screen.getByLabelText("Robot at grid position 2, 3")).toBeInTheDocument();
    expect(screen.getByText("84%")).toBeInTheDocument();
    expect(screen.getByText("0%")).toBeInTheDocument();
    expect(screen.getByText("Waste collected").nextElementSibling).toHaveTextContent("0");
  });

  it("completes the same route immediately when reduced motion is preferred", () => {
    vi.useFakeTimers();
    vi.stubGlobal("matchMedia", vi.fn().mockReturnValue({ matches: true }));
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Start Mission" }));
    fireEvent.click(screen.getByRole("button", { name: "Play route preview" }));

    expect(screen.getByText("Ready to collect plastic waste")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Route preview complete" })).toBeDisabled();
    expect(screen.getByLabelText("Robot at grid position 2, 3")).toBeInTheDocument();
  });
});
