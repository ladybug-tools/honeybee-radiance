from honeybee_radiance.view import View


def test_from_grid_vtv():
    v = View('test_vtv')
    v.position = (0, 0, 0)
    v.direction = (0, 1, 0)
    v.up_vector = (0, 0, 1)
    v.type = 'v'
    v.h_size = 60
    v.v_size = 60

    grid = v.grid(x_div_count=2, y_div_count=5)
    from_grid = View.from_grid(grid)

    assert v.to_radiance() == from_grid.to_radiance()


def test_from_grid_vtl():
    v = View('test_vtl')
    v.position = (0, 0, 0)
    v.direction = (0, 1, 0)
    v.up_vector = (0, 0, 1)
    v.type = 'l'
    v.h_size = 60
    v.v_size = 60

    grid = v.grid(x_div_count=2, y_div_count=5)
    from_grid = View.from_grid(grid)

    assert v.to_radiance() == from_grid.to_radiance()


def test_from_grid_vta():
    v = View('test_vta')
    v.position = (0, 0, 0)
    v.direction = (0, 1, 0)
    v.up_vector = (0, 0, 1)
    v.type = 'a'
    v.h_size = 180
    v.v_size = 180

    grid = v.grid(x_div_count=2, y_div_count=5)
    from_grid = View.from_grid(grid)

    assert v.to_radiance() == from_grid.to_radiance()


def test_from_grid_vth():
    v = View('test_vth')
    v.position = (0, 0, 0)
    v.direction = (0, 1, 0)
    v.up_vector = (0, 0, 1)
    v.type = 'h'
    v.h_size = 180
    v.v_size = 180

    grid = v.grid(x_div_count=2, y_div_count=5)
    from_grid = View.from_grid(grid)

    assert v.to_radiance() == from_grid.to_radiance()


def test_grid_dimension():
    v = View('test_vtv')
    v.position = (0, 0, 0)
    v.direction = (0, 1, 0)
    v.up_vector = (0, 0, 1)
    v.type = 'v'
    v.h_size = 60
    v.v_size = 60

    grid = v.grid(x_div_count=1, y_div_count=1)
    from_grid = View.from_grid(grid)
    assert v.to_radiance() == from_grid.to_radiance()

    grid = v.grid(x_div_count=2, y_div_count=4)
    from_grid = View.from_grid(grid)
    assert v.to_radiance() == from_grid.to_radiance()

    grid = v.grid(x_div_count=1, y_div_count=10)
    from_grid = View.from_grid(grid)
    assert v.to_radiance() == from_grid.to_radiance()

    grid = v.grid(x_div_count=10, y_div_count=100)
    from_grid = View.from_grid(grid)
    assert v.to_radiance() == from_grid.to_radiance()


def test_from_grid_unf():
    v = View('test_vta')
    v.position = (3, 7, 1.8)
    v.direction = (0, 1, 0)
    v.up_vector = (0, 0, 1)
    v.type = 'a'
    v.h_size = 360
    v.v_size = 360

    grid = [
        './tests/assets/view/view_0000.unf',
        './tests/assets/view/view_0001.unf',
        './tests/assets/view/view_0002.unf',
        './tests/assets/view/view_0003.unf',
        './tests/assets/view/view_0004.unf'
        ]

    from_grid = View.from_grid(grid)
    assert v.to_radiance() == from_grid.to_radiance()
