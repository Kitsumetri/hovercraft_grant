from dataclasses import dataclass, field
import numpy as np


@dataclass
class Parameters:
    m: float | int = field(default=16_000)  # Масса судна
    rho: float | int = field(default=1_000)  # Плотность воды
    S: float | int = field(default=60)  # Площадь воздушной подушки
    g: float | int = field(default=9.8)  # Ускорение свободного падения
    n: float | int = field(default=1.4)  # Показатель политропы для адиабатического процесса
    p_a: float | int = field(default=101_300)  # Давление воздуха
    I: float | int = field(default=250_000)  # Момент инерции Y
    l: float | int = field(default=3)  # Длина плеча
    xi: float | int = field(default=1)  # Коэффициент расхода
    a: float | int = field(default=-2.756287)  # 1-й параметр параболы P(Q)
    b: float | int = field(default=48.461925)  # 2-й параметр параболы P(Q)
    c: float | int = field(default=2770.846481)  # 3-й параметр параболы P(Q)
    k: float | int = field(default=0.7)  # Клиренс судна
    h: float | int = field(default=2)  # Высота цилиндра баллонета


@dataclass
class BalloonParameters:
    phi: float | int
    r: float | int
    x: float | int
    y: float | int
    _a: float | int
    alpha: float | int = field(init=False)

    def __post_init__(self):
        self.alpha = np.pi - self._a


@dataclass
class BallonetParameters:
    AD: BalloonParameters = field(
        default=BalloonParameters(
            phi=3.129,
            r=0.5,
            x=0.761343,
            y=0.98531,
            _a=0.977996
        )
    )

    CB: BalloonParameters = field(
        default=BalloonParameters(
            phi=0.740152,
            r=0.5,
            x=0.761343,
            y=0.98531,
            _a=5.269
        )
    )

    DC: BalloonParameters = field(
        default=BalloonParameters(
            phi=1.162,
            r=0.5,
            x=0.761343,
            y=0.98531,
            _a=4.107
        )
    )

    ED: BalloonParameters = field(
        default=BalloonParameters(
            phi=2.26476,
            r=0.35,
            x=0.776836,
            y=0.350314,
            _a=-np.pi / 2
        )
    )

    EC: BalloonParameters = field(
        default=BalloonParameters(
            phi=2.21598,
            r=0.35,
            x=0.776836,
            y=0.350314,
            _a=-np.pi / 2
        )
    )

    def get_segments(self):
        return [
            ('AD', self.AD.phi, self.AD.r, self.AD.x, self.AD.y, self.AD.alpha, -1),
            ('DE', self.ED.phi, self.ED.r, self.ED.x, self.ED.y, self.ED.alpha, 1),
            # ('DC', self.DC.phi, self.DC.r, self.DC.x, self.DC.y, self.DC.alpha, -1),
            ('EC', self.EC.phi, self.EC.r, self.EC.x, self.EC.y, self.EC.alpha, -1),
            ('CB', self.CB.phi, self.CB.r, self.CB.x, self.CB.y, self.CB.alpha, -1),
        ]


@dataclass
class BallonetCoordinates:
    name: str
    x: np.array
    y: np.array


@dataclass
class Point:
    x: int | float
    y: int | float

    def to_array(self) -> np.array:
        return np.array([self.x, self.y], dtype=np.float32)
