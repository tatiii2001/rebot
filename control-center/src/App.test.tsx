import { act, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { App } from "./App";

describe("Control Center start mission", () => {
  it("does not present a target or route playback before the Mission starts", () => {
    render(<App />);

    expect(screen.getByText("pending")).toBeInTheDocument();
    expect(screen.getByText("available")).toBeInTheDocument();
    expect(screen.getByText("84%")).toBeInTheDocument();
    expect(screen.queryByLabelText("Selected target: Plastic Waste Item at grid position 2, 2")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Play route preview" })).not.toBeInTheDocument();
  });

  it("shows classified processable plastic and a targeting action after the Operator starts it", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: "Start Mission" }));

    expect(screen.getByText("running")).toBeInTheDocument();
    expect(screen.getByText("executing mission")).toBeInTheDocument();
    expect(screen.getByText("Plastic")).toBeInTheDocument();
    expect(screen.getByText("Processable")).toBeInTheDocument();
    expect(screen.getByText("Classified")).toBeInTheDocument();
    expect(screen.getByText("Classified Waste")).toBeInTheDocument();
    expect(screen.queryByText("Classification candidate")).not.toBeInTheDocument();
    expect(screen.getByText("Validated route available for plastic waste")).toBeInTheDocument();
    expect(screen.queryByLabelText("Selected target: Plastic Waste Item at grid position 2, 2")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Target plastic waste" })).toBeEnabled();
    expect(screen.queryByRole("button", { name: "Play route preview" })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Mission running" })).toBeDisabled();
    expect(screen.getByText("84%")).toBeInTheDocument();
    expect(screen.getByText("0%")).toBeInTheDocument();
    expect(screen.getByText("Waste detected").nextElementSibling).toHaveTextContent("4");
    expect(screen.getByText("Waste collected").nextElementSibling).toHaveTextContent("0");
    expect(screen.getByText("Incidents").nextElementSibling).toHaveTextContent("0");
  });

  it("targets classified plastic once before exposing route playback", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: "Start Mission" }));
    await user.click(screen.getByRole("button", { name: "Target plastic waste" }));

    expect(screen.getByText("Targeted")).toBeInTheDocument();
    expect(screen.getByText("Targeted Waste")).toBeInTheDocument();
    expect(screen.getByText("Plastic")).toBeInTheDocument();
    expect(screen.getByText("Target selected: plastic waste")).toBeInTheDocument();
    expect(screen.getByLabelText("Selected target: Plastic Waste Item at grid position 2, 2")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Plastic waste targeted" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Play route preview" })).toBeEnabled();
    expect(screen.getByText("84%")).toBeInTheDocument();
  });
});

describe("Control Center route preview", () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("cannot expose route playback before plastic Waste is targeted", () => {
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Start Mission" }));

    expect(screen.queryByRole("button", { name: "Play route preview" })).not.toBeInTheDocument();
  });

  it("moves the Robot and Battery Level together through the targeted plastic Waste route", () => {
    vi.useFakeTimers();
    render(<App />);

    expect(screen.queryByRole("button", { name: "Play route preview" })).not.toBeInTheDocument();
    expect(screen.queryByText("Validated local route")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Start Mission" }));
    fireEvent.click(screen.getByRole("button", { name: "Target plastic waste" }));

    expect(screen.getByText("Target selected: plastic waste")).toBeInTheDocument();
    expect(screen.getByLabelText("Selected target: Plastic Waste Item at grid position 2, 2")).toBeInTheDocument();
    expect(screen.getByText("Validated local route")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Play route preview" })).toBeEnabled();

    fireEvent.click(screen.getByRole("button", { name: "Play route preview" }));

    expect(screen.getByText("Following route to plastic waste: 1 of 8 positions")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Play route preview" })).toBeDisabled();

    act(() => {
      vi.advanceTimersByTime(550);
    });

    expect(screen.getByLabelText("Robot at grid position 4, 6")).toBeInTheDocument();
    expect(screen.getByText("83%")).toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(1_100);
    });

    expect(screen.getByLabelText("Robot at grid position 3, 5")).toBeInTheDocument();
    expect(screen.getByText("81%")).toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(4_000);
    });

    expect(screen.getByText("Reached targeted plastic waste; ready for a future collection action")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Route preview complete" })).toBeDisabled();
    expect(screen.getByLabelText("Robot at grid position 2, 2")).toBeInTheDocument();
    expect(screen.getByLabelText(/Robot and selected target occupy grid position 2, 2/)).toBeInTheDocument();
    expect(screen.getByText("77%")).toBeInTheDocument();
    expect(screen.getByText("0%")).toBeInTheDocument();
    expect(screen.getByText("running")).toBeInTheDocument();
    expect(screen.getByText("executing mission")).toBeInTheDocument();
    expect(screen.getByText("Waste detected").nextElementSibling).toHaveTextContent("4");
    expect(screen.getByText("Waste collected").nextElementSibling).toHaveTextContent("0");
    expect(screen.getByText("Incidents").nextElementSibling).toHaveTextContent("0");
    expect(screen.getByText("Targeted")).toBeInTheDocument();
    expect(screen.queryByText("Collected")).not.toBeInTheDocument();
  });

  it("completes the same route immediately when reduced motion is preferred", () => {
    vi.useFakeTimers();
    vi.stubGlobal("matchMedia", vi.fn().mockReturnValue({ matches: true }));
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Start Mission" }));
    fireEvent.click(screen.getByRole("button", { name: "Target plastic waste" }));
    fireEvent.click(screen.getByRole("button", { name: "Play route preview" }));

    expect(screen.getByText("Targeted")).toBeInTheDocument();
    expect(screen.getByText("Reached targeted plastic waste; ready for a future collection action")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Route preview complete" })).toBeDisabled();
    expect(screen.getByLabelText("Robot at grid position 2, 2")).toBeInTheDocument();
    expect(screen.getByLabelText(/Robot and selected target occupy grid position 2, 2/)).toBeInTheDocument();
    expect(screen.getByText("77%")).toBeInTheDocument();
    expect(screen.getByText("Targeted")).toBeInTheDocument();
    expect(screen.queryByText("Collected")).not.toBeInTheDocument();
  });
});
