import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
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
    expect(screen.getByText("Scanning environment")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Mission running" })).toBeDisabled();
  });
});
