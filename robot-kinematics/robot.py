import numpy as np

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal
from numpy.typing import ArrayLike

class Robot:
    def __init__(self, *, home_tool_pose: ArrayLike, joint_screw_axes: ArrayLike) -> None:
        pose = np.array(home_tool_pose, dtype=float)

        if pose.shape != (4, 4) or not np.isfinite(pose).all():
            raise ValueError(f"home_tool_pose must be a finite 4x4 matrix, got shape {pose.shape}")

        axes = np.array(joint_screw_axes, dtype=float)

        if axes.ndim !=2 or axes.shape[0] != 6 or axes.shape[1] == 0 or not np.isfinite(axes).all():
            raise ValueError(f"joint_screw_axes must be a finite 6xN matrix, got shape with n >= 1 {axes.shape}")

        self._home_tool_pose = pose
        self._joint_screw_axes = axes

    def joint_count(self) -> int:
        return self._joint_screw_axes.shape[1]




