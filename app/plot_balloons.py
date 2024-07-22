import matplotlib.pyplot as plt
import numpy as np
from math import pi
from typing import List
from app_utils import BallonetParameters, BallonetCoordinates
from shapely.geometry import Polygon


def calculate_ballonet_parameters(phi, r, x, y,
                                  alpha, direction,
                                  grain=100, minor=False, name=None):
    t = np.linspace(alpha, alpha + direction * phi, grain)
    xs = x + r * np.cos(t)
    ys = y + r * np.sin(t)
    if minor:
        xs = -xs

    if name == 'DE':
        xs = xs[::-1]
        ys = ys[::-1]
    return xs, ys


def get_ballonet_coordinates(params: BallonetParameters,
                             minor: bool = False,
                             new_dx: float | int = 0,
                             new_dy: float | int = 0,
                             grain: int = 100) -> List[BallonetCoordinates]:
    return [BallonetCoordinates(
        name=name,
        x=calculate_ballonet_parameters(phi, r, x + new_dx, y + new_dy, alpha, direction,
                                        minor=minor, grain=grain, name=name)[0],
        y=calculate_ballonet_parameters(phi, r, x + new_dx, y + new_dy, alpha, direction,
                                        minor=minor, grain=grain, name=name)[1])
        for name, phi, r, x, y, alpha, direction in params.get_segments()
    ]


def plot_data(params: BallonetParameters,
              minor: bool = False,
              new_dx: float | int = 0,
              new_dy: float | int = 0,
              grain: int = 100,
              plot_borders=False) -> None:
    plt.axis('equal')
    for segment in get_ballonet_coordinates(params,
                                            minor=minor, grain=grain,
                                            new_dx=new_dx, new_dy=new_dy):
        if plot_borders:
            plt.scatter(segment.x[0], segment.y[0], color='red')
            plt.scatter(segment.x[-1], segment.y[-1], color='blue')
        plt.plot(segment.x, segment.y, color='black', linestyle='dotted', linewidth=4)


def get_polygon_from_ballonet(ballonet_segments: List[BallonetCoordinates]) -> Polygon:
    p_list = list()
    for s in ballonet_segments:
        p_list.extend([(x, y) for x, y in zip(s.x, s.y)])
    return Polygon(np.array(p_list))


if __name__ == '__main__':
    poly_1 = get_polygon_from_ballonet(
        get_ballonet_coordinates(BallonetParameters(),
                                 minor=True, grain=1000, new_dy=20)
    )

    # poly_2 = get_polygon_from_ballonet(
    #     get_ballonet_coordinates(BallonetParameters(),
    #                              minor=False, grain=300)
    # )

    plt.axis('equal')
    water_poly = Polygon([(-3, 0), (3, 0), (3, -3), (-3, -3)])
    intersect_poly = poly_1.intersection(water_poly)
    plt.plot(*water_poly.exterior.xy)
    intersect_area = intersect_poly.area
    plt.title(f"{intersect_area=}")
    plt.plot(*intersect_poly.exterior.xy)
    plt.plot(*poly_1.exterior.xy, linestyle='dotted', color='black', linewidth=2)
    # plt.plot(*poly_2.exterior.xy)

    # plot_data(BallonetParameters(), minor=True, grain=300)
    # plot_data(BallonetParameters(), minor=False, grain=300)
    plt.show()
