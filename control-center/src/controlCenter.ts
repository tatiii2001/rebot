export type MissionState = "pending" | "running";
export type RobotOperationalState = "available" | "executing mission";
export type RoutePreviewState = "unavailable" | "ready" | "playing" | "complete";
export type WasteLifecycle = "detected" | "classified" | "targeted";

export interface GridPosition {
  readonly column: number;
  readonly row: number;
}

export interface SelectedTarget {
  readonly label: string;
  readonly category: "plastic";
  readonly position: GridPosition;
}

export interface WasteHandlingStatus {
  readonly category: "plastic";
  readonly processability: "processable";
  readonly lifecycle: WasteLifecycle;
  readonly position: GridPosition;
  readonly validatedRouteAvailable: boolean;
}

export interface ControlCenterSnapshot {
  readonly missionState: MissionState;
  readonly robotOperationalState: RobotOperationalState;
  readonly batteryLevel: number;
  readonly missionProgress: number;
  readonly currentTask: string;
  readonly wasteDetected: number;
  readonly wasteCollected: number;
  readonly incidents: number;
  readonly robotPosition: GridPosition;
  readonly wasteHandling?: WasteHandlingStatus;
  readonly selectedTarget?: SelectedTarget;
  readonly routeFrames: readonly GridPosition[];
  readonly routeFrameIndex: number;
  readonly routePreviewState: RoutePreviewState;
}

export interface ControlCenter {
  getSnapshot(): ControlCenterSnapshot;
  startMission(): ControlCenterSnapshot;
  targetPlasticWaste(): ControlCenterSnapshot;
  playRoutePreview(prefersReducedMotion: boolean): ControlCenterSnapshot;
  advanceRoutePreview(): ControlCenterSnapshot;
}

const plasticTarget: SelectedTarget = {
  label: "Plastic Waste Item",
  category: "plastic",
  position: { column: 2, row: 2 },
};

const classifiedPlasticWaste: WasteHandlingStatus = {
  category: "plastic",
  processability: "processable",
  lifecycle: "classified",
  position: plasticTarget.position,
  validatedRouteAvailable: true,
};

// Fixed display snapshots for this visual adapter; no navigation is calculated here.
const routeFrames: readonly GridPosition[] = [
  { column: 5, row: 6 },
  { column: 4, row: 6 },
  { column: 3, row: 6 },
  { column: 3, row: 5 },
  { column: 2, row: 5 },
  { column: 2, row: 4 },
  { column: 2, row: 3 },
  { column: 2, row: 2 },
];

const initialSnapshot: ControlCenterSnapshot = {
  missionState: "pending",
  robotOperationalState: "available",
  batteryLevel: 84,
  missionProgress: 0,
  currentTask: "Awaiting mission",
  wasteDetected: 4,
  wasteCollected: 0,
  incidents: 0,
  robotPosition: routeFrames[0],
  routeFrames: [],
  routeFrameIndex: 0,
  routePreviewState: "unavailable",
};

// This fixed visual adapter is replaceable when the backend boundary exists.
export function createLocalControlCenter(): ControlCenter {
  let snapshot = initialSnapshot;

  return {
    getSnapshot: () => snapshot,
    startMission: () => {
      if (snapshot.missionState === "pending") {
        snapshot = {
          ...snapshot,
          missionState: "running",
          robotOperationalState: "executing mission",
          currentTask: "Validated route available for plastic waste",
          wasteHandling: classifiedPlasticWaste,
          routeFrames,
        };
      }

      return snapshot;
    },
    targetPlasticWaste: () => {
      if (snapshot.wasteHandling?.lifecycle === "classified") {
        snapshot = {
          ...snapshot,
          currentTask: "Target selected: plastic waste",
          wasteHandling: { ...snapshot.wasteHandling, lifecycle: "targeted" },
          selectedTarget: plasticTarget,
          routePreviewState: "ready",
        };
      }

      return snapshot;
    },
    playRoutePreview: (prefersReducedMotion) => {
      if (snapshot.routePreviewState === "ready") {
        const finalFrameIndex = routeFrames.length - 1;
        snapshot = prefersReducedMotion
            ? {
                ...snapshot,
                currentTask: "Reached targeted plastic waste; ready for a future collection action",
                robotPosition: routeFrames[finalFrameIndex],
                batteryLevel: initialSnapshot.batteryLevel - finalFrameIndex,
                routeFrameIndex: finalFrameIndex,
                routePreviewState: "complete",
              }
            : {
                ...snapshot,
                currentTask: `Following route to plastic waste: 1 of ${routeFrames.length} positions`,
                routePreviewState: "playing",
              };
      }

      return snapshot;
    },
    advanceRoutePreview: () => {
      if (snapshot.routePreviewState === "playing") {
        const nextFrameIndex = snapshot.routeFrameIndex + 1;
        const isComplete = nextFrameIndex === routeFrames.length - 1;
        snapshot = {
          ...snapshot,
          currentTask: isComplete
            ? "Reached targeted plastic waste; ready for a future collection action"
            : `Following route to plastic waste: ${nextFrameIndex + 1} of ${routeFrames.length} positions`,
          robotPosition: routeFrames[nextFrameIndex],
          batteryLevel: snapshot.batteryLevel - 1,
          routeFrameIndex: nextFrameIndex,
          routePreviewState: isComplete ? "complete" : "playing",
        };
      }

      return snapshot;
    },
  };
}
