from dataclasses import dataclass, field


@dataclass
class Parameters:
    m: float | int = field(default=16_000)  # Масса судна
    rho: float | int = field(default=1_000)  # Плотность воды
    S: float | int = field(default=60)  # Площадь воздушной подушки
    g: float | int = field(default=9.8)  # Ускорение свободного падения
    n: float | int = field(default=1.4)  # Показатель политропы
    p_a: float | int = field(default=101_300)  # Давление воздуха
    I: float | int = field(default=250_000)  # Момент инерции Y
    l: float | int = field(default=3)  # Длина плеча
    xi: float | int = field(default=1)  # Коэффициент расхода
    a: float | int = field(default=2.756287)  # 1-й параметр параболы P(Q)
    b: float | int = field(default=48.461925)  # 2-й параметр параболы P(Q)
    c: float | int = field(default=2770.846481)  # 3-й параметр параболы P(Q)
    k: float | int = field(default=0.7)  # Клиренс судна
    h: float | int = field(default=2)  # Высота цилиндра баллонета
    r: float | int = field(default=1)  # Радиус цилиндра баллонета
