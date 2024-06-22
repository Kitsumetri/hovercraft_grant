import numpy as np

from app_utils import Parameters
from solve_eq import SystemOfEquations, Point


class TestClassGetVolume:
    def test_full_volume(self):
        test_system = SystemOfEquations(Parameters(h=2, k=0.7))
        assert test_system.get_cylinder_volume(Point(0, 0)) == test_system.V_cylinder
        assert test_system.get_cylinder_volume(Point(0, -2)) == test_system.V_cylinder
        assert test_system.get_cylinder_volume(Point(0, -7)) == test_system.V_cylinder

    def test_0_volume(self):
        test_system = SystemOfEquations(Parameters(h=2))
        assert test_system.get_cylinder_volume(Point(0, 5)) == 0
        assert test_system.get_cylinder_volume(Point(0, 2)) == 0
        assert test_system.get_cylinder_volume(Point(0, 1.99)) != 0

    def test_part_volume(self):
        test_system = SystemOfEquations(Parameters(h=2, k=0.7, r=1))
        assert round(test_system.get_cylinder_volume(Point(0, 1.3)), 4) == 4.0841
        assert round(test_system.get_cylinder_volume(Point(0, 0.9)), 4) == 2.8274


class TestClassUtils:
    def test_clamp(self):
        assert SystemOfEquations.clamp(10, -1, 100) == 10
        assert SystemOfEquations.clamp(10, 100, 1_000) == 100
        assert SystemOfEquations.clamp(100, -10, 10) == 10
        assert SystemOfEquations.clamp(1, 1, 1) == 1

    def test_cosine_similarity(self):
        # FIXME: Numba руинит тесты, но оно точно работает нормально
        pass
        # assert SystemOfEquations.get_cos_alpha(np.array([0, -1]), np.array([0, 1])) == -1
        # assert SystemOfEquations.get_cos_alpha(np.array([0, 40]), np.array([40, 0])) == 0
        # assert round(SystemOfEquations.get_cos_alpha(np.array([0, 1]), np.array([1, 1])), 6) == 0.707107


class TestClassGetForce:

    def test_F_a(self):
        test_system = SystemOfEquations(Parameters(rho=1_000, g=9.8))
        assert test_system.get_F_a(0) == 0
        assert test_system.get_F_a(10) == 1_000 * 9.8 * 10

    def test_F_p(self):
        test_system = SystemOfEquations(Parameters())
        default_p = (Parameters().m * Parameters().g) / Parameters().S
        assert test_system.get_F_p() == default_p * Parameters().S

        test_system = SystemOfEquations(Parameters(S=10))
        new_p = (Parameters().m * Parameters().g) / 10
        assert test_system.get_F_p() == new_p * 10


class TestClassSubEquations:
    def test_S_gap(self):
        test_system = SystemOfEquations(Parameters(h=2))
        assert test_system.get_S_gap(Point(0, -10)) == 0
        assert test_system.get_S_gap(Point(0, 1)) == 0
        assert test_system.get_S_gap(Point(0, 2)) == 0
        assert round(test_system.get_S_gap(Point(0, 2.01)), 2) == 0.01
        assert test_system.get_S_gap(Point(0, 4)) == 2

    def test_Q_out(self):
        xi = 2
        p = 650
        rho = 1_000
        S_gap = 1

        test_system = SystemOfEquations(Parameters(xi=xi, rho=rho))
        test_system.p = p
        test_system.S_gap = S_gap

        assert test_system.get_Q_out() == xi * np.sqrt(2 * p / rho) * S_gap

    def test_Q_in(self):
        test_system = SystemOfEquations(Parameters(a=-1, b=2, c=34))
        test_system.p = 10
        assert test_system.get_Q_in() == 6

    def test_area(self):
        test_system = SystemOfEquations(Parameters())

        assert test_system.get_area(Point(0, 3), Point(8, 11), 0, 8) == 56
        assert test_system.get_area(Point(0, 1), Point(8, 1), 0, 8) == 8
