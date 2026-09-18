export type MissionState = "pending" | "running";
export type RobotOperationalState = "available" | "executing mission";

export interface ControlCenterSnapshot {
  readonly missionState: MissionState;
  readonly robotOperationalState: RobotOperationalState;
  readonly batteryLevel: number;
  readonly missionProgress: number;
  readonly currentTask: string;
  readonly wasteDetected: number;
  readonly wasteCollected: number;
  readonly incidents: number;
}

export interface ControlCenter {
  getSnapshot(): ControlCenterSnapshot;
  startMission(): ControlCenterSnapshot;
}

const initialSnapshot: ControlCenterSnapshot = {
  missionState: "pending",
  robotOperationalState: "available",
  batteryLevel: 84,
  missionProgress: 0,
  currentTask: "Awaiting mission",
  wasteDetected: 4,
  wasteCollected: 0,
  incidents: 0,
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
          currentTask: "Scanning environment",
        };
      }

      return snapshot;
    },
  };
}
