from dataclasses import dataclass
from math import hypot, isfinite
from typing import Literal, get_args

JOINT_TYPES = Literal["revolute", "prismatic", "fixed", "continuous"]

@dataclass(frozen=True)
class Joint:
    """Definition of a joint, with its motion axis in the local joint frame.

    Rotating joints use radians and N·m. Sliding joints use metres and N.
    Velocity, acceleration, deceleration, and jerk are nonnegative magnitudes.
    Damping is a viscous coefficient. Friction is a Coulomb effort magnitude.
    None means the model does not specify that parameter.
    """

    name: str
    type: JOINT_TYPES
    axis: tuple[float, float, float] | None = None
    position_limits: tuple[float, float] | None = None
    max_velocity: float | None = None
    max_acceleration: float | None = None
    max_deceleration: float | None = None
    max_jerk: float | None = None
    damping: float | None = None
    friction: float | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Joint name must not be empty or whitespace.")

        if self.type not in get_args(JOINT_TYPES):
            raise ValueError(f"Unknown joint type: {self.type!r}")

        magnitudes = {
            "max_velocity": self.max_velocity,
            "max_acceleration": self.max_acceleration,
            "max_deceleration": self.max_deceleration,
            "max_jerk": self.max_jerk,
            "damping": self.damping,
            "friction": self.friction
        }

        if not self.is_movable:
            if (self.axis is not None or self.position_limits is not None
                    or any(value is not None for value in magnitudes.values())):
                raise ValueError("A fixed joint cannot have motion parameters.")

            return

        if self.axis is None or len(self.axis) != 3:
            raise ValueError("A movable joint must have a defined three-component axis.")

        length = hypot(*self.axis)

        if not isfinite(length) or length == 0:
            raise ValueError("Joint axis must be a finite non-zero vector.")

        object.__setattr__(self, "axis", tuple(component / length for component in self.axis))

        if self.position_limits is not None:
            if self.type == "continuous":
                raise ValueError("Continuous joints cannot have position bounds.")

            lower, upper = self.position_limits

            if not (isfinite(lower) and isfinite(upper) and lower < upper):
                raise ValueError("Position limits must be finite and ordered.")
            object.__setattr__(self, "position_limits", (lower, upper))

        for name, value in magnitudes.items():
            if value is not None and (not isfinite(value) or value < 0):
                raise ValueError(f"{name} must be finite and nonnegative.")


    @property
    def is_movable(self) -> bool:
        """Return True if the joint is movable (not fixed)."""
        return self.type != "fixed"

    