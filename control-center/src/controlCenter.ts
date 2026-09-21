export type MissionState = "pending" | "running";
export type RobotOperationalState = "available" | "executing mission";
export type RoutePreviewState = "unavailable" | "ready" | "playing" | "complete";
export type WasteLifecycle = "detected" | "classified" | "targeted" | "collected" | "deposited";
export type RoutePurpose = "to-waste" | "to-collection-point";

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
  readonly routePurpose?: RoutePurpose;
}

export interface ControlCenter {
  getSnapshot(): ControlCenterSnapshot;
  startMission(): ControlCenterSnapshot;
  targetPlasticWaste(): ControlCenterSnapshot;
  playRoutePreview(prefersReducedMotion: boolean): ControlCenterSnapshot;
  advanceRoutePreview(): ControlCenterSnapshot;
  collectPlasticWaste(): ControlCenterSnapshot;
  playDepositRoute(prefersReducedMotion: boolean): ControlCenterSnapshot;
  depositPlasticWaste(): ControlCenterSnapshot;
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

// Fixed route from the collected Waste at (2,2) to the existing Collection Point at (8,3).
// Each frame after the origin consumes one Battery percentage point: 77% through 68%.
const collectionPointRouteFrames: readonly GridPosition[] = [
  { column: 2, row: 2 },
  { column: 2, row: 3 },
  { column: 2, row: 4 },
  { column: 3, row: 4 },
  { column: 4, row: 4 },
  { column: 4, row: 3 },
  { column: 5, row: 3 },
  { column: 6, row: 3 },
  { column: 7, row: 3 },
  { column: 8, row: 3 },
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
                currentTask: "Reached targeted plastic waste; ready to collect",
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
        const isComplete = nextFrameIndex === snapshot.routeFrames.length - 1;
        const isCollectionPointRoute = snapshot.routePurpose === "to-collection-point";
        snapshot = {
          ...snapshot,
          currentTask: isComplete
            ? isCollectionPointRoute
              ? "Ready to deposit plastic waste"
              : "Reached targeted plastic waste; ready to collect"
            : isCollectionPointRoute
              ? `Moving collected plastic to collection point · step ${nextFrameIndex + 1} of ${snapshot.routeFrames.length}`
              : `Following route to plastic waste: ${nextFrameIndex + 1} of ${snapshot.routeFrames.length} positions`,
          robotPosition: snapshot.routeFrames[nextFrameIndex],
          batteryLevel: snapshot.batteryLevel - 1,
          routeFrameIndex: nextFrameIndex,
          routePreviewState: isComplete ? "complete" : "playing",
        };
      }

      return snapshot;
    },
    collectPlasticWaste: () => {
      const robotAtPlasticWaste = snapshot.robotPosition.column === plasticTarget.position.column
        && snapshot.robotPosition.row === plasticTarget.position.row;
      if (snapshot.wasteHandling?.lifecycle === "targeted" && snapshot.routePreviewState === "complete" && robotAtPlasticWaste) {
        snapshot = {
          ...snapshot,
          wasteCollected: 1,
          wasteHandling: { ...snapshot.wasteHandling, lifecycle: "collected" },
          selectedTarget: undefined,
          routeFrames: collectionPointRouteFrames,
          routeFrameIndex: 0,
          routePreviewState: "ready",
          routePurpose: "to-collection-point",
          currentTask: "Validated route available to collection point",
        };
      }

      return snapshot;
    },
    playDepositRoute: (prefersReducedMotion) => {
      if (snapshot.wasteHandling?.lifecycle === "collected" && snapshot.routePurpose === "to-collection-point" && snapshot.routePreviewState === "ready") {
        const finalFrameIndex = collectionPointRouteFrames.length - 1;
        snapshot = prefersReducedMotion
          ? {
              ...snapshot,
              currentTask: "Ready to deposit plastic waste",
              robotPosition: collectionPointRouteFrames[finalFrameIndex],
              batteryLevel: snapshot.batteryLevel - finalFrameIndex,
              routeFrameIndex: finalFrameIndex,
              routePreviewState: "complete",
            }
          : {
              ...snapshot,
              currentTask: `Moving collected plastic to collection point · step 1 of ${collectionPointRouteFrames.length}`,
              routePreviewState: "playing",
            };
      }

      return snapshot;
    },
    depositPlasticWaste: () => {
      const atCollectionPoint = snapshot.robotPosition.column === 8 && snapshot.robotPosition.row === 3;
      if (snapshot.wasteHandling?.lifecycle === "collected" && snapshot.routePurpose === "to-collection-point" && snapshot.routePreviewState === "complete" && atCollectionPoint) {
        snapshot = {
          ...snapshot,
          currentTask: "Plastic waste deposited",
          wasteHandling: { ...snapshot.wasteHandling, lifecycle: "deposited" },
        };
      }

      return snapshot;
    },
  };
}
