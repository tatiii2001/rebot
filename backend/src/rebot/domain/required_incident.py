from dataclasses import dataclass


@dataclass(frozen=True)
class RequiredIncident:
    @property
    def concern(self) -> str:
        return "insufficient battery"
