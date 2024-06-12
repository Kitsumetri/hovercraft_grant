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

