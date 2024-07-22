import os
from math import sqrt
from typing import Optional, Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, FFMpegWriter
from numba import jit, njit
from tqdm import tqdm

from app_utils import (
    Parameters,
    BallonetParameters,
    BallonetCoordinates,
    Point
)
from plot_balloons import (
    get_ballonet_coordinates,
    get_polygon_from_ballonet,
    Polygon
)


@jit(nopython=True, fastmath=True)
def F_x_jit(A, B, x):
    up = (B[1] - A[1]) * (x ** 2 / 2 - A[0] * x)
    down = B[0] - A[0]
    return up / down + A[1] * x


@jit(nopython=True, fastmath=True)
def get_S_gap_jit(UP, h):
    return max(0, UP[1] - h)


@jit(fastmath=True)
def get_Q_in_jit(a, b, c, p):
    D = b ** 2 - 4 * a * (c - p)
    root1 = (-b - sqrt(D)) / (2 * a)
    root2 = (-b + sqrt(D)) / (2 * a)
    return max(root1, root2)


@jit(fastmath=True)
def get_Q_out_jit(xi, p, rho, S_gap):
    return xi * np.sqrt(2 * p / rho) * S_gap


@jit(fastmath=True)
def get_cylinder_volume_jit(up_y, V_c, S, h):
    if up_y <= 0:
        return V_c

    if up_y >= h:
        return 0

    V_upper_part = S * (h - up_y)
    return V_c - V_upper_part


@jit(fastmath=True)
def get_d2y_dt2_jit(Fp, Fa, Fm, m):
    return (Fp + Fa - Fm) / m


class SystemOfEquations:
    def __init__(self,
                 params: Parameters,
                 ballonet_params: BallonetParameters,
                 t_end: int | float = 1_000,
                 eps: float = 0.01) -> None:

        self.params: Parameters = params
        self.ballonet_params: BallonetParameters = ballonet_params
        self.eps: float = eps
        self.current_iteration: int = 0

        self.p = (params.m * params.g) / params.S
        self.gamma = 0
        self.y = params.k
        self.W = params.S * params.k
        self.S_gap = 0

        self.dW_dt = 0

        self.t_array = np.arange(0, t_end, eps)

        self.y_array = np.zeros_like(self.t_array)
        self.y_array[0] = self.y

        self.p_array = np.zeros_like(self.t_array)
        self.p_array[0] = self.p

        self.w_array = np.zeros_like(self.t_array)
        self.w_array[0] = self.W

        self.gamma_array = np.zeros_like(self.t_array)
        self.gamma_array[0] = self.gamma

        self.A = Point(x=-self.params.l, y=self.y)
        self.B = Point(x=self.params.l, y=self.y)

        # self.circle_S = np.pi * (self.params.r ** 2)
        # self.V_cylinder = self.circle_S * self.params.h

        self.A_positions = [self.A.to_array().copy()]
        self.B_positions = [self.B.to_array().copy()]

        self.grain = 100

        self.A_coords: list[BallonetCoordinates] = get_ballonet_coordinates(self.ballonet_params,
                                                                            minor=True,
                                                                            new_dx=2.5,
                                                                            new_dy=self.A.y - 1.2,
                                                                            grain=self.grain)
        self.B_coords: list[BallonetCoordinates] = get_ballonet_coordinates(self.ballonet_params,
                                                                            minor=False,
                                                                            new_dx=2.5,
                                                                            new_dy=self.B.y - 1.2,
                                                                            grain=self.grain)

        self.water_poly = Polygon(Polygon([(-4, 0), (4, 0), (4, -4), (-4, -4)]))

        self.A_poly = get_polygon_from_ballonet(self.A_coords)
        self.B_poly = get_polygon_from_ballonet(self.B_coords)

    def update_ballonet_polygons(self) -> None:
        self.A_coords: list[BallonetCoordinates] = get_ballonet_coordinates(self.ballonet_params,
                                                                            minor=True,
                                                                            new_dx=self.A.x,
                                                                            new_dy=self.A.y - self.params.h,
                                                                            grain=self.grain)
        self.B_coords: list[BallonetCoordinates] = get_ballonet_coordinates(self.ballonet_params,
                                                                            minor=False,
                                                                            new_dx=self.B.x,
                                                                            new_dy=self.B.y - self.params.h,
                                                                            grain=self.grain)
        self.A_poly = get_polygon_from_ballonet(self.A_coords)
        self.B_poly = get_polygon_from_ballonet(self.B_coords)

    @staticmethod
    def F_x(A: Point, B: Point, x: int | float) -> int | float:
        return F_x_jit(A.to_array(), B.to_array(), x)

    def get_W(self, A: Point, B: Point, down: int | float, up: int | float) -> int | float:
        return self.F_x(A, B, up) - self.F_x(A, B, down)

    def get_cylinder_volume(self) -> int | float:
        return self.A_poly.intersection(self.water_poly).area + self.B_poly.intersection(self.water_poly).area
        # return get_cylinder_volume_jit(upper_point.y, self.V_cylinder, self.circle_S, self.params.h)

    def get_S_gap(self, upper_point: Point) -> int | float:
        return get_S_gap_jit(upper_point.to_array(), self.params.h)

    def solve(self):
        self.current_iteration = self.t_array.shape[0]
        for idx in tqdm(range(1, self.current_iteration)):
            ###################
            dp_dt = self.get_dp_dt(W=self.W,
                                   Q_in=self.get_Q_in(),
                                   Q_out=self.get_Q_out(),
                                   dW_dt=self.dW_dt) * self.eps

            self.p = self.clamp(value=self.p + dp_dt,
                                min_value=600,
                                max_value=2964)

            # FIXME Changed: A.x + self.params.r | B.x - self.params.r
            self.W = self.get_W(A=self.A,
                                B=self.B,
                                down=self.A.x + self.ballonet_params.AD.r,
                                up=self.B.x - self.ballonet_params.AD.r)

            self.dW_dt = self.W - self.w_array[idx - 1]
            self.S_gap = (get_S_gap_jit(self.A.to_array(), self.params.h) +
                          get_S_gap_jit(self.B.to_array(), self.params.h))

            self.w_array[idx] = self.W
            self.p_array[idx] = self.p
            ###################

            # FIXME Changed:
            # V = self.get_cylinder_volume(self.A) + self.get_cylinder_volume(self.B)

            V = self.get_cylinder_volume()
            d2y_dt2 = self.get_d2y_dt2(Fp=self.get_F_p(),
                                       Fm=self.params.m * self.params.g,
                                       Fa=self.get_F_a(V)) * self.eps
            self.y += d2y_dt2
            self.y_array[idx] = self.y
            ###################

            d2gamma_dt2 = self.get_d2gamma_d2t(Fa=self.get_F_a(V),
                                               cos_a=self.get_cos_alpha(self.A.to_array())) * self.eps

            # FIXME: нужно крутить точки
            # if self.gamma > 0:
            #     self.B.y += d2y_dt2
            #     self.A.y -= d2y_dt2
            # else:
            #     self.A.y += d2y_dt2
            #     self.B.y -= d2y_dt2

            self.A.y += d2y_dt2
            self.B.y += d2y_dt2

            self.A_positions.append(self.A.to_array().copy())
            self.B_positions.append(self.B.to_array().copy())
            self.update_ballonet_polygons()
            # #########

            self.gamma += d2gamma_dt2
            self.gamma_array[idx] = self.gamma

    def get_d2y_dt2(self,
                    Fp: int | float,
                    Fm: int | float,
                    Fa: int | float) -> float:
        return get_d2y_dt2_jit(Fp, Fa, Fm, self.params.m)

    def get_dp_dt(self,
                  W: int | float,
                  Q_in: int | float,
                  Q_out: float,
                  dW_dt: int | float | Any) -> float:
        first_half = (self.params.n * self.params.p_a) / W
        second_half = Q_in - Q_out - dW_dt
        return first_half * second_half

    def get_d2gamma_d2t(self,
                        Fa: int | float,
                        cos_a: float) -> float:
        return (Fa * self.params.l * cos_a) / self.params.I

    def get_F_p(self) -> int | float:
        return self.params.S * self.p

    def get_F_a(self, V: int | float) -> int | float:
        return self.params.rho * self.params.g * V

    def get_Q_in(self) -> int | float:
        return get_Q_in_jit(self.params.a, self.params.b, self.params.c, self.p)

    @staticmethod
    @njit(fastmath=True)
    def get_cos_alpha(v1: np.array,
                      v2: Optional[np.array] = None) -> float:
        v2 = np.array([0, 1], dtype=np.float32) if v2 is None else v2
        dot_prod = np.dot(v1, v2)
        magnitude1, magnitude2 = np.linalg.norm(v1), np.linalg.norm(v2)

        return dot_prod / (magnitude1 * magnitude2)

    def get_Q_out(self) -> float:
        return get_Q_out_jit(self.params.xi, self.p, self.params.rho, self.S_gap)

    @staticmethod
    @jit(fastmath=True)
    def clamp(value: int | float,
              min_value: int | float,
              max_value: int | float) -> int | float:
        return min(max(value, min_value), max_value)

    def __repr__(self) -> str:
        separator = "\n" + "+" + ("-" * 50) + "\n"
        repr_str = (
            f"{separator}"
            f"| System of Equations"
            f"{separator}"
            f"| Params: {self.params}"
            f"{separator}"
            f"| Solution (Iteration: {self.current_iteration}):"
            f"{separator}"
            f"| p = {self.p}\n"
            f"| y = {self.y}\n"
            f"| γ = {self.gamma}\n"
            f"| W = {self.W}\n"
            f"| A: {self.A}\n"
            f"| B: {self.B}\n"
            f"| S_gap: {self.S_gap}"
            f"{separator}"
        )
        return repr_str

    def plot(self, max_elem: Optional[int] = None) -> None:

        if self.current_iteration == 0:
            raise RuntimeError("Use .solve() method first")

        if max_elem is None:
            max_elem = self.t_array.shape[0]

        y = self.y_array[:max_elem]
        p = self.p_array[:max_elem]
        gamma = self.gamma_array[:max_elem]
        W = self.w_array[:max_elem]
        t = self.t_array[:max_elem]

        plt.figure(figsize=(18, 8))
        plt.subplot(2, 2, 1)
        plt.grid()
        plt.plot(t, y)
        plt.title('Y')
        plt.xlabel('Time (s)')
        plt.ylabel('Y')

        plt.subplot(2, 2, 2)
        plt.plot(t, gamma)
        plt.grid()
        plt.title('Gamma')
        plt.xlabel('Time (s)')
        plt.ylabel('Gamma')

        plt.subplot(2, 2, 3)
        plt.plot(t, p)
        plt.grid()
        plt.title('P')
        plt.xlabel('Time (s)')
        plt.ylabel('P')

        plt.subplot(2, 2, 4)
        plt.plot(t, W)
        plt.grid()
        plt.title('W')
        plt.xlabel('Time (s)')
        plt.ylabel('W')

        plt.tight_layout()
        plt.show()

    def animate_model(self,
                      save: bool = True,
                      interval: int | float = 10,
                      filename: str = "animation.mp4") -> None:
        fig, ax = plt.subplots()
        step = int(1 / (self.eps * 100))
        ax.grid(True)
        ax.axis('equal')
        ax.set_title('Model Animation')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_xlim(-self.params.l - 1, self.params.l + 1)
        ax.set_ylim(min(self.y_array) - 5, max(self.y_array) + 5)
        line, = ax.plot([], [], 'k-')
        ballonet_poly, = ax.plot([], [], 'k-')
        ballonet_poly_reverse, = ax.plot([], [], 'k-')

        scatter_A = ax.scatter([], [], s=100, color='orange')
        scatter_B = ax.scatter([], [], s=100, color='orange')
        scatter_O = ax.scatter([], [], s=100, color='red')

        water_surface = ax.fill_between([ax.get_xlim()[0], ax.get_xlim()[1]],
                                        [0, 0],
                                        ax.get_ylim()[0],
                                        color='blue',
                                        alpha=0.3)

        def init() -> tuple:
            line.set_data([], [])
            ballonet_poly.set_data([], [])
            ballonet_poly_reverse.set_data([], [])
            scatter_A.set_offsets(np.empty((0, 2)))
            scatter_B.set_offsets(np.empty((0, 2)))
            scatter_O.set_offsets(np.empty((0, 2)))
            return (line,
                    ballonet_poly, ballonet_poly_reverse,
                    scatter_A, scatter_B, scatter_O,
                    water_surface)

        def update(frame):
            A_pos = [self.A_positions[frame][0], self.A_positions[frame][1]]
            B_pos = [self.B_positions[frame][0], self.B_positions[frame][1]]
            O_pos = [0, self.y_array[frame]]
            scatter_A.set_offsets(np.array(A_pos).reshape(1, 2))
            scatter_B.set_offsets(np.array(B_pos).reshape(1, 2))
            scatter_O.set_offsets(np.array(O_pos).reshape(1, 2))
            line.set_data([A_pos[0], B_pos[0]], [A_pos[1], B_pos[1]])

            coords: list[BallonetCoordinates] = get_ballonet_coordinates(self.ballonet_params,
                                                                         minor=True,
                                                                         new_dx=2.5,
                                                                         new_dy=A_pos[1] - 1.2)
            coords_reverse: list[BallonetCoordinates] = get_ballonet_coordinates(self.ballonet_params,
                                                                                 minor=False,
                                                                                 new_dx=2.5,
                                                                                 new_dy=B_pos[1] - 1.2)
            ballonet_poly.set_data(
                *get_polygon_from_ballonet(coords).exterior.xy
            )
            ballonet_poly_reverse.set_data(
                *get_polygon_from_ballonet(coords_reverse).exterior.xy)

            return (line,
                    ballonet_poly, ballonet_poly_reverse,
                    scatter_A, scatter_B, scatter_O,
                    water_surface)

        ani = FuncAnimation(fig, update,
                            frames=tuple(range(0, len(self.A_positions), step)),
                            init_func=init,
                            blit=True, interval=interval)

        if save:
            os.makedirs("animations", exist_ok=True)
            writer = FFMpegWriter(fps=1000 // interval, metadata=dict(artist='User'), bitrate=1800)
            ani.save(os.path.join("animations", filename), writer=writer)
            print(f"Animation saved as animations/{filename}")

        plt.show()


def main() -> None:
    equations = SystemOfEquations(Parameters(h=1, m=16_000),
                                  BallonetParameters(),
                                  t_end=30,
                                  eps=1e-3)
    print(equations)
    equations.solve()
    print(equations)
    equations.plot()
    equations.animate_model(save=False)


if __name__ == '__main__':
    main()
