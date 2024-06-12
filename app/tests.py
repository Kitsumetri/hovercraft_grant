from solve_eq import *


def test_clamp():
    assert clamp(100, (-100, 101)) == 100
    assert clamp(-100, (-100, 101)) == -100
    assert clamp(0, (-1, 1)) == 0


def test_get_single_balloon_V():
    assert round(get_single_balloon_V(10, 10, -10, 0.7), 4) == 3141.5927
    assert get_single_balloon_V(10, 10, 100, 0.7) == 0
    assert get_single_balloon_V(10, 10, 10, 0.7) == 0
    assert get_single_balloon_V(10, 10, 9.99, 0.7) != 0
    assert get_single_balloon_V(10, 10, 10, 10) == 0


def test_Q_in():
    assert round(Q_in(10_000, Parameters(a=1, b=-10, c=1)), 2) == 105.12
    assert round(Q_in(0, Parameters(a=-3.8, b=19, c=1)), 3) == 5.052


def test_get_F_m():
    assert get_F_m(Parameters(m=8_000, g=9.81)) == 78_480
    assert get_F_m(Parameters(m=0, g=9.81)) == 0


def test_get_cos_alpha():
    assert (round(get_cos_alpha(np.array([1, 1]), np.array([0, 1])), 6) == round(np.cos(np.pi / 4), 6))
    assert np.isnan(get_cos_alpha(np.array([0, 0]), np.array([0, 0])))
    assert (get_cos_alpha(np.array([0, 100]), np.array([100, 0])) == round(np.cos(np.pi / 2), 6))
    assert get_cos_alpha(np.array([-10, 0]), np.array([10, 0])) == np.cos(np.pi)
