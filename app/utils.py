from dataclasses import dataclass, field


@dataclass
class Parameters:
    m: float = field(default=None)
    rho: float = field(default=None)
    S: float = field(default=None)
    g: float = field(default=None)
    n: float = field(default=None)
    p_a: float = field(default=None)
    I: float = field(default=None)
    l: float = field(default=None)
    xi: float = field(default=None)
    a: float = field(default=None)
    b: float = field(default=None)
    c: float = field(default=None)
