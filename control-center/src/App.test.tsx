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
    expect(screen.queryByRole("button", { name: "Collect plastic waste" })).not.toBeInTheDocument();
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
    expect(screen.queryByRole("button", { name: "Collect plastic waste" })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Mission running" })).toBeDisabled();
    expect(screen.getByText("84%")).toBeInTheDocument();
    expect(screen.getByText("Mission Progress").nextElementSibling).toHaveTextContent("0%");
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
    expect(screen.queryByRole("button", { name: "Collect plastic waste" })).not.toBeInTheDocument();
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

    expect(screen.getAllByText("Following route to plastic waste: 1 of 8 positions")[0]).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Play route preview" })).toBeDisabled();
    expect(screen.queryByRole("button", { name: "Collect plastic waste" })).not.toBeInTheDocument();

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

    expect(screen.getByText("Reached targeted plastic waste; ready to collect")).toBeInTheDocument();
    expect(screen.queryByText("Deposit route")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Play route to collection point" })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Collect plastic waste" })).toBeEnabled();
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
    expect(screen.getByText("Waste collected").nextElementSibling).toHaveTextContent("0");
  });

  it("collects plastic Waste only after route completion", () => {
    vi.useFakeTimers();
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Start Mission" }));
    fireEvent.click(screen.getByRole("button", { name: "Target plastic waste" }));
    fireEvent.click(screen.getByRole("button", { name: "Play route preview" }));

    act(() => {
      vi.advanceTimersByTime(4_000);
    });

    const collectButton = screen.getByRole("button", { name: "Collect plastic waste" });
    expect(collectButton).toHaveFocus();
    fireEvent.click(collectButton);

    expect(screen.getByText("Collected Waste")).toBeInTheDocument();
    expect(screen.getByText("Collected")).toBeInTheDocument();
    expect(screen.getByText("Carrying").nextElementSibling).toHaveTextContent("Robot");
    expect(screen.getByText("Battery cost").nextElementSibling).toHaveTextContent("0%");
    expect(screen.getByText("Validated route available to collection point")).toBeInTheDocument();
    expect(screen.getByLabelText("Robot carrying one plastic Waste Item at grid position 2, 2")).toBeInTheDocument();
    expect(screen.queryByLabelText("Selected target: Plastic Waste Item at grid position 2, 2")).not.toBeInTheDocument();
    expect(screen.getByLabelText("Environment grid with one Robot, three ground Waste Items, five Static Obstacles, and one Compatible Collection Point. Robot carries one plastic Waste Item at grid position 2, 2")).toBeInTheDocument();
    expect(screen.getByText("77%")).toBeInTheDocument();
    expect(screen.getByLabelText("Robot at grid position 2, 2 carrying plastic Waste")).toBeInTheDocument();
    expect(screen.getByText("running")).toBeInTheDocument();
    expect(screen.getByText("executing mission")).toBeInTheDocument();
    expect(screen.getByText("Mission Progress").nextElementSibling).toHaveTextContent("0%");
    expect(screen.getByText("Waste detected").nextElementSibling).toHaveTextContent("4");
    expect(screen.getByText("Waste collected").nextElementSibling).toHaveTextContent("1");
    expect(screen.getByText("Incidents").nextElementSibling).toHaveTextContent("0");
    expect(screen.getByRole("button", { name: "Play route to collection point" })).toBeEnabled();
    expect(screen.getByText("Plastic waste collected")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Collect plastic waste" })).not.toBeInTheDocument();
  });

  it("completes the same route immediately when reduced motion is preferred without collecting", () => {
    vi.useFakeTimers();
    vi.stubGlobal("matchMedia", vi.fn().mockReturnValue({ matches: true }));
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Start Mission" }));
    fireEvent.click(screen.getByRole("button", { name: "Target plastic waste" }));
    fireEvent.click(screen.getByRole("button", { name: "Play route preview" }));

    expect(screen.getByText("Targeted")).toBeInTheDocument();
    expect(screen.getByText("Reached targeted plastic waste; ready to collect")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Route preview complete" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Collect plastic waste" })).toBeEnabled();
    expect(screen.getByLabelText("Robot at grid position 2, 2")).toBeInTheDocument();
    expect(screen.getByLabelText(/Robot and selected target occupy grid position 2, 2/)).toBeInTheDocument();
    expect(screen.getByText("77%")).toBeInTheDocument();
    expect(screen.getByText("Targeted")).toBeInTheDocument();
    expect(screen.queryByText("Collected")).not.toBeInTheDocument();
    expect(screen.getByText("Waste collected").nextElementSibling).toHaveTextContent("0");
  });

  it("collects the same final snapshot when reduced motion is preferred", () => {
    vi.useFakeTimers();
    vi.stubGlobal("matchMedia", vi.fn().mockReturnValue({ matches: true }));
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Start Mission" }));
    fireEvent.click(screen.getByRole("button", { name: "Target plastic waste" }));
    fireEvent.click(screen.getByRole("button", { name: "Play route preview" }));
    fireEvent.click(screen.getByRole("button", { name: "Collect plastic waste" }));

    expect(screen.getByText("Collected")).toBeInTheDocument();
    expect(screen.getByText("Validated route available to collection point")).toBeInTheDocument();
    expect(screen.getByText("77%")).toBeInTheDocument();
    expect(screen.getByLabelText("Robot at grid position 2, 2 carrying plastic Waste")).toBeInTheDocument();
    expect(screen.getByText("Waste collected").nextElementSibling).toHaveTextContent("1");
    expect(screen.getByText("Plastic waste collected")).toBeInTheDocument();
  });
});

describe("Control Center deposit route and deposit", () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  function collectPlasticWaste() {
    fireEvent.click(screen.getByRole("button", { name: "Start Mission" }));
    fireEvent.click(screen.getByRole("button", { name: "Target plastic waste" }));
    fireEvent.click(screen.getByRole("button", { name: "Play route preview" }));
    act(() => {
      vi.advanceTimersByTime(4_000);
    });
    fireEvent.click(screen.getByRole("button", { name: "Collect plastic waste" }));
  }

  it("exposes a validated deposit route only after collection and never exposes deposit early", () => {
    vi.useFakeTimers();
    render(<App />);

    expect(screen.queryByRole("button", { name: "Deposit plastic waste" })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Start Mission" }));
    expect(screen.queryByRole("button", { name: "Deposit plastic waste" })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Target plastic waste" }));
    fireEvent.click(screen.getByRole("button", { name: "Play route preview" }));
    expect(screen.queryByRole("button", { name: "Deposit plastic waste" })).not.toBeInTheDocument();
    act(() => {
      vi.advanceTimersByTime(4_000);
    });
    fireEvent.click(screen.getByRole("button", { name: "Collect plastic waste" }));

    expect(screen.getByText("Deposit route").nextElementSibling).toHaveTextContent("Validated");
    expect(screen.getByRole("button", { name: "Play route to collection point" })).toBeEnabled();
    expect(screen.getByText("Validated route available to collection point")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Deposit plastic waste" })).not.toBeInTheDocument();
  });

  it("moves collected waste with the Robot at one percent per deposit-route frame before explicit deposit", () => {
    vi.useFakeTimers();
    render(<App />);
    collectPlasticWaste();

    fireEvent.click(screen.getByRole("button", { name: "Play route to collection point" }));
    expect(screen.getAllByText("Moving collected plastic to collection point · step 1 of 10")[0]).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("Moving collected plastic to collection point · step 1 of 10");
    expect(screen.queryByRole("button", { name: "Deposit plastic waste" })).not.toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(550);
    });

    expect(screen.getByLabelText("Robot at grid position 2, 3 carrying plastic Waste")).toBeInTheDocument();
    expect(screen.getByLabelText("Robot carrying one plastic Waste Item at grid position 2, 3")).toBeInTheDocument();
    expect(screen.getByText("76%")).toBeInTheDocument();
    expect(screen.getByText("Moving collected plastic to collection point · step 2 of 10")).toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(5_000);
    });

    expect(screen.getByLabelText("Robot at Compatible Collection Point at grid position 8, 3 carrying plastic Waste")).toBeInTheDocument();
    expect(screen.getByText("68%")).toBeInTheDocument();
    expect(screen.getAllByText("Ready to deposit plastic waste")[0]).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("Ready to deposit plastic waste");
    expect(screen.getByText("Collected")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Deposit plastic waste" })).toHaveFocus();
    expect(screen.getByRole("button", { name: "Deposit plastic waste" })).toBeEnabled();
    expect(screen.queryByRole("button", { name: "Play route to collection point" })).not.toBeInTheDocument();
    expect(screen.getByText("Waste collected").nextElementSibling).toHaveTextContent("1");
  });

  it("reaches the same pre-deposit arrival snapshot with reduced motion", () => {
    vi.useFakeTimers();
    vi.stubGlobal("matchMedia", vi.fn().mockReturnValue({ matches: true }));
    render(<App />);
    collectPlasticWaste();

    fireEvent.click(screen.getByRole("button", { name: "Play route to collection point" }));

    expect(screen.getByLabelText("Robot at Compatible Collection Point at grid position 8, 3 carrying plastic Waste")).toBeInTheDocument();
    expect(screen.getByText("68%")).toBeInTheDocument();
    expect(screen.getAllByText("Ready to deposit plastic waste")[0]).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Deposit plastic waste" })).toBeEnabled();
    expect(screen.getByText("Collected")).toBeInTheDocument();
  });

  it("deposits only after the explicit action without changing mission metrics or arrival battery", () => {
    vi.useFakeTimers();
    render(<App />);
    collectPlasticWaste();
    fireEvent.click(screen.getByRole("button", { name: "Play route to collection point" }));
    act(() => {
      vi.advanceTimersByTime(5_000);
    });

    fireEvent.click(screen.getByRole("button", { name: "Deposit plastic waste" }));

    expect(screen.getByText("Deposited Waste")).toBeInTheDocument();
    expect(screen.getByText("Deposited")).toBeInTheDocument();
    expect(screen.getByText("Location").nextElementSibling).toHaveTextContent("Collection point");
    expect(screen.getByText("Current task").parentElement).toHaveTextContent("Plastic waste deposited");
    expect(screen.getByRole("status")).toHaveTextContent("Plastic waste deposited");
    expect(screen.getByLabelText("Deposited plastic Waste at Compatible Collection Point at grid position 8, 3")).toBeInTheDocument();
    expect(screen.queryByLabelText(/Robot carrying one plastic Waste Item/)).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Deposit plastic waste" })).not.toBeInTheDocument();
    expect(screen.getByText("68%")).toBeInTheDocument();
    expect(screen.getByText("running")).toBeInTheDocument();
    expect(screen.getByText("executing mission")).toBeInTheDocument();
    expect(screen.getByText("Mission Progress").nextElementSibling).toHaveTextContent("0%");
    expect(screen.getByText("Waste detected").nextElementSibling).toHaveTextContent("4");
    expect(screen.getByText("Waste collected").nextElementSibling).toHaveTextContent("1");
    expect(screen.getByText("Incidents").nextElementSibling).toHaveTextContent("0");
  });
});
