import { useEffect, useState } from "react";
import {
  createLocalControlCenter,
  type ControlCenter,
} from "./controlCenter";

type GridMarker = {
  readonly label: string;
  readonly className: string;
  readonly column: number;
  readonly row: number;
};

const obstacles: readonly GridMarker[] = [
  { label: "Static Obstacle", className: "obstacle", column: 3, row: 2 },
  { label: "Static Obstacle", className: "obstacle", column: 3, row: 3 },
  { label: "Static Obstacle", className: "obstacle", column: 5, row: 4 },
  { label: "Static Obstacle", className: "obstacle", column: 6, row: 4 },
  { label: "Static Obstacle", className: "obstacle", column: 7, row: 5 },
];

const wasteItems: readonly GridMarker[] = [
  { label: "Plastic Waste Item", className: "waste plastic", column: 2, row: 2 },
  { label: "Paper Waste Item", className: "waste paper", column: 7, row: 2 },
  { label: "Metal Waste Item", className: "waste metal", column: 2, row: 6 },
  { label: "Organic Waste Item", className: "waste organic", column: 8, row: 6 },
];

const robot: GridMarker = {
  className: "robot",
  label: "Robot",
  column: 0,
  row: 0,
};

const collectionPoint: GridMarker = {
  label: "Compatible Collection Point",
  className: "collection-point",
  column: 8,
  row: 3,
};

function GridMarker({ marker }: { readonly marker: GridMarker }) {
  return (
    <span
      aria-label={marker.label}
      className={`grid-marker ${marker.className}`}
      role="img"
      style={{ gridColumn: marker.column, gridRow: marker.row }}
    />
  );
}

function StatusValue({ value }: { readonly value: string }) {
  return <strong className="status-value">{value}</strong>;
}

function ControlCenterScreen({ controlCenter }: { readonly controlCenter: ControlCenter }) {
  const [snapshot, setSnapshot] = useState(() => controlCenter.getSnapshot());
  const isRunning = snapshot.missionState === "running";
  const isClassified = snapshot.wasteHandling?.lifecycle === "classified";
  const isTargeted = snapshot.wasteHandling?.lifecycle === "targeted";
  const isRouteAvailable = snapshot.routePreviewState === "ready";
  const isRouteComplete = snapshot.routePreviewState === "complete";
  const robotHasReachedTarget = isTargeted
    && snapshot.robotPosition.column === snapshot.selectedTarget?.position.column
    && snapshot.robotPosition.row === snapshot.selectedTarget?.position.row;

  useEffect(() => {
    if (snapshot.routePreviewState !== "playing") {
      return;
    }

    const playback = window.setInterval(() => {
      setSnapshot(controlCenter.advanceRoutePreview());
    }, 550);

    return () => window.clearInterval(playback);
  }, [controlCenter, snapshot.routePreviewState]);

  function startMission() {
    setSnapshot(controlCenter.startMission());
  }

  function playRoutePreview() {
    const prefersReducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;
    setSnapshot(controlCenter.playRoutePreview(prefersReducedMotion));
  }

  function targetPlasticWaste() {
    setSnapshot(controlCenter.targetPlasticWaste());
  }

  return (
    <main className="control-center-shell">
      <header className="site-header">
        <div className="brand-lockup">
          <span aria-hidden="true" className="brand-mark">R</span>
          <div>
            <p className="eyebrow">Control Center</p>
            <h1>ReBot</h1>
          </div>
        </div>
        <p className="product-name">Autonomous Waste Collection</p>
        <p className="local-status"><span aria-hidden="true" />Local simulation</p>
      </header>

      <section aria-label="Mission overview" className="dashboard-layout">
        <section aria-labelledby="environment-heading" className="environment-panel panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Simulated Environment</p>
              <h2 id="environment-heading">Collection sector A-04</h2>
            </div>
            <div className="environment-signals">
              {snapshot.wasteHandling?.validatedRouteAvailable && <span className="route-label">Validated local route</span>}
              <span className="grid-status">Grid online</span>
            </div>
          </div>
          <div aria-label={`Environment grid with one Robot, four Waste Items, five Static Obstacles, and one Compatible Collection Point${robotHasReachedTarget ? ". Robot and selected target occupy grid position 2, 2; the Waste Item remains targeted and uncollected" : ""}`} className="environment-grid">
            {isTargeted && snapshot.routeFrames.map((position, index) => {
              const progress = index < snapshot.routeFrameIndex
                ? "completed"
                : index === snapshot.routeFrameIndex ? "current" : "remaining";
              return <span aria-hidden="true" className={`route-frame route-${progress}`} key={`${position.column}-${position.row}`} style={{ gridColumn: position.column, gridRow: position.row }} />;
            })}
            {obstacles.map((marker, index) => <GridMarker key={`obstacle-${index}`} marker={marker} />)}
            {wasteItems.map((marker) => {
              const isSelectedTarget = marker.column === snapshot.selectedTarget?.position.column && marker.row === snapshot.selectedTarget.position.row;
              const targetMarker = isSelectedTarget
                ? { ...marker, className: `${marker.className} targeted-waste`, label: `Selected target: ${marker.label} at grid position ${marker.column}, ${marker.row}` }
                : marker;
              return <GridMarker key={marker.label} marker={targetMarker} />;
            })}
            <GridMarker marker={collectionPoint} />
            <GridMarker marker={{ ...robot, column: snapshot.robotPosition.column, row: snapshot.robotPosition.row, label: `Robot at grid position ${snapshot.robotPosition.column}, ${snapshot.robotPosition.row}` }} />
          </div>
          <div aria-label="Environment legend" className="environment-legend">
            <span><i className="legend-icon robot-icon" aria-hidden="true" />Robot</span>
            <span><i className="legend-icon waste-icon" aria-hidden="true" />Waste Item</span>
            <span><i className="legend-icon obstacle-icon" aria-hidden="true" />Static Obstacle</span>
            <span><i className="legend-icon collection-icon" aria-hidden="true" />Compatible Collection Point</span>
          </div>
        </section>

        <aside aria-label="Mission and Robot status" className="status-stack">
          <section aria-labelledby="mission-heading" className="panel mission-panel">
            <p className="eyebrow">Cleaning Mission</p>
            <h2 id="mission-heading">Mission status</h2>
            <dl className="status-list">
              <div>
                <dt>Mission State</dt>
                <dd><StatusValue value={snapshot.missionState} /></dd>
              </div>
              <div>
                <dt>Mission Progress</dt>
                <dd><StatusValue value={`${snapshot.missionProgress}%`} /></dd>
              </div>
            </dl>
            <button className="start-button" disabled={isRunning} onClick={startMission} type="button">
              {isRunning ? "Mission running" : "Start Mission"}
            </button>
            {snapshot.wasteHandling && (
              <section aria-label="Waste handling status" className="waste-handling-status">
                <p className="eyebrow">{isTargeted ? "Targeted Waste" : "Classified Waste"}</p>
                <dl className="handling-list">
                  <div><dt>Category</dt><dd>Plastic</dd></div>
                  <div><dt>Processability</dt><dd>Processable</dd></div>
                  <div><dt>Lifecycle</dt><dd className={isTargeted ? "targeted-state" : "classified-state"}>{isTargeted ? "Targeted" : "Classified"}</dd></div>
                  <div><dt>Route</dt><dd>{isTargeted ? "Preview ready" : "Validated"}</dd></div>
                </dl>
              </section>
            )}
            {isClassified && <button className="target-button" onClick={targetPlasticWaste} type="button">Target plastic waste</button>}
            {isTargeted && <button className="target-button" disabled type="button">Plastic waste targeted</button>}
            {isTargeted && <button className="route-preview-button" disabled={!isRouteAvailable} onClick={playRoutePreview} type="button">
              {isRouteComplete ? "Route preview complete" : "Play route preview"}
            </button>}
          </section>

          <section aria-labelledby="robot-heading" className="panel robot-panel">
            <p className="eyebrow">Assigned Robot</p>
            <h2 id="robot-heading">Robot status</h2>
            <dl className="status-list">
              <div>
                <dt>Robot Operational State</dt>
                <dd><StatusValue value={snapshot.robotOperationalState} /></dd>
              </div>
              <div>
                <dt>Battery Level</dt>
                <dd className="battery-reading">{snapshot.batteryLevel}%</dd>
              </div>
            </dl>
            <div aria-label={`Battery Level ${snapshot.batteryLevel}%`} aria-valuemax={100} aria-valuemin={0} aria-valuenow={snapshot.batteryLevel} className="battery-meter" role="meter">
              <span style={{ width: `${snapshot.batteryLevel}%` }} />
            </div>
            <p aria-live="polite" className="current-task"><span>Current task</span>{snapshot.currentTask}</p>
          </section>
        </aside>
      </section>

      <section aria-label="Mission summary" className="summary-metrics">
        <article><span>Waste detected</span><strong>{snapshot.wasteDetected}</strong></article>
        <article><span>Waste collected</span><strong>{snapshot.wasteCollected}</strong></article>
        <article><span>Incidents</span><strong>{snapshot.incidents}</strong></article>
      </section>

      <p className="backend-note"><span aria-hidden="true">i</span> Backend connection is not active yet. This is a deterministic local simulation for visual validation.</p>
    </main>
  );
}

export function App() {
  const [controlCenter] = useState(createLocalControlCenter);

  return <ControlCenterScreen controlCenter={controlCenter} />;
}
