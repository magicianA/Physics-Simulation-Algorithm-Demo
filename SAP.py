import taichi as ti

ti.init(arch=ti.cpu)

max_cube_num = 200
delta_t = 0.02
cur_cube_num = 100
res = 1000
world_boundary = (1000, 1000)

cube_pos = ti.Vector.field(2, dtype=ti.i32, shape=max_cube_num)
cube_size = ti.Vector.field(2, dtype=ti.i32, shape=max_cube_num)
cube_v = ti.Vector.field(2, dtype=ti.i32, shape=max_cube_num)

intersect = ti.field(dtype=ti.i8, shape=(max_cube_num, max_cube_num))
collision = ti.field(dtype=ti.i8, shape=(max_cube_num))

index_points_x = ti.Vector.field(2, dtype=ti.i32, shape=2 * max_cube_num)
index_points_y = ti.Vector.field(2, dtype=ti.i32, shape=2 * max_cube_num)
end_points_x = ti.Vector.field(3, dtype=ti.i32, shape=2 * max_cube_num)
end_points_y = ti.Vector.field(3, dtype=ti.i32, shape=2 * max_cube_num)

enable_physics = 0
gravity = -19.8
cube_f = ti.Vector.field(2, dtype=ti.f32, shape=max_cube_num)


@ti.kernel
def init():
    for i in range(cur_cube_num):
        # cube_pos[i] = ti.Vector([40.0, 40.0 + 70.0 * i])
        # cube_v[i] = ti.Vector([20.0, 20.0 + 10.0 * i])
        # cube_size[i] = ti.Vector([20.0, 20.0])
        cube_pos[i] = ti.Vector([ti.random() * world_boundary[0], ti.random() * world_boundary[1]])
        cube_v[i] = ti.Vector([ti.random() * 100 + 100, ti.random() * 100 + 100])
        cube_size[i] = ti.Vector([30, 30])

        tr = cube_pos[i] + cube_size[i] / 2
        bl = cube_pos[i] - cube_size[i] / 2
        end_points_x[2 * i] = ti.Vector([bl[0], 0, i])
        end_points_x[2 * i + 1] = ti.Vector([tr[0], 1, i])
        end_points_y[2 * i] = ti.Vector([bl[1], 0, i])
        end_points_y[2 * i + 1] = ti.Vector([tr[1], 1, i])
        index_points_x[i] = ti.Vector([2 * i, 2 * i + 1])
        index_points_y[i] = ti.Vector([2 * i, 2 * i + 1])


@ti.func
def aabb_test(i, j):
    tr1 = cube_pos[i] + 0.5 * cube_size[i]
    bl1 = cube_pos[i] - 0.5 * cube_size[i]
    tr2 = cube_pos[j] + 0.5 * cube_size[j]
    bl2 = cube_pos[j] - 0.5 * cube_size[j]
    rv = 0
    if bl1[0] < tr2[0] and tr1[0] > bl2[0] and bl1[1] < tr2[1] and tr1[1] > bl2[1]:
        rv = 1
    return rv


@ti.kernel
def brute_force():
    for i in range(cur_cube_num):
        for j in range(i + 1, cur_cube_num):
            intersect[j, i] = aabb_test(i, j)
            intersect[i, j] = intersect[j, i]
    for i in range(cur_cube_num):
        collision[i] = 0
        for j in range(cur_cube_num):
            if intersect[i, j] == 1:
                collision[i] = 1


@ti.kernel
def add_cube(x: ti.f32, y: ti.f32):
    global cur_cube_num
    if cur_cube_num < max_cube_num:
        cur_cube_num += 1
        cube_pos[cur_cube_num - 1] = ti.Vector([x, y])
        cube_v[cur_cube_num - 1] = ti.Vector([ti.random() * 100, ti.random() * 100])
        cube_size[cur_cube_num - 1] = ti.Vector([30, 30])


@ti.kernel
def sap():
    for i in range(cur_cube_num):
        tr = cube_pos[i] + cube_size[i] / 2
        bl = cube_pos[i] - cube_size[i] / 2
        end_points_x[index_points_x[i][0]][0] = bl[0]
        end_points_x[index_points_x[i][1]][0] = tr[0]
        end_points_y[index_points_y[i][0]][0] = bl[1]
        end_points_y[index_points_y[i][1]][0] = tr[1]
    for sap_index in range(0,1): # to ensure the following for loop is not parallel
        for i in range(2 * cur_cube_num):
            for k in range(0, i):
                j = i - 1 - k
                if end_points_x[j][0] > end_points_x[j + 1][0]:
                    t = end_points_x[j]
                    end_points_x[j] = end_points_x[j + 1]
                    end_points_x[j + 1] = t

                    id_j = end_points_x[j][2]
                    id_j1 = end_points_x[j+1][2]

                    if end_points_x[j][1] == 1:  # ti.vector : col 0 must be constant
                        index_points_x[end_points_x[j][2]][1] = j + 1
                    else:
                        index_points_x[end_points_x[j][2]][0] = j + 1
                    if end_points_x[j + 1][1] == 1:
                        index_points_x[end_points_x[j + 1][2]][1] = j
                    else:
                        index_points_x[end_points_x[j + 1][2]][0] = j


                    if end_points_x[j][1] == 0 and end_points_x[j + 1][1] == 1:
                        intersect[id_j1, id_j] = 0
                        intersect[id_j, id_j1] = intersect[id_j1, id_j]
                    elif end_points_x[j][1] == 1 and end_points_x[j + 1][1] == 0:
                        intersect[id_j1, id_j] = aabb_test(id_j1,id_j)
                        intersect[id_j, id_j1] = intersect[id_j1,id_j]

                else:
                    break
        for i in range(2 * cur_cube_num):
            for k in range(0, i):
                j = i - k - 1
                if end_points_y[j][0] > end_points_y[j + 1][0]:
                    t = end_points_y[j]
                    end_points_y[j] = end_points_y[j + 1]
                    end_points_y[j + 1] = t

                    if end_points_y[j][1] == 1:
                        index_points_y[end_points_y[j][2]][1] = j + 1
                    else:
                        index_points_y[end_points_y[j][2]][0] = j + 1
                    if end_points_y[j + 1][1] == 1:
                        index_points_y[end_points_y[j + 1][2]][1] = j
                    else:
                        index_points_y[end_points_y[j + 1][2]][0] = j

                    id_j = end_points_y[j][2]
                    id_j1 = end_points_y[j+1][2]

                    if end_points_y[j][1] == 0 and end_points_y[j + 1][1] == 1:
                        intersect[id_j, id_j1] = 0
                        intersect[id_j1, id_j] = intersect[id_j, id_j1]
                    elif end_points_y[j][1] == 1 and end_points_y[j + 1][1] == 0:
                        intersect[id_j, id_j1] = aabb_test(id_j1, id_j)
                        intersect[id_j1, id_j] = intersect[id_j, id_j1]


                else:
                    break

    for i in range(cur_cube_num):
        collision[i] = 0
    for i in range(cur_cube_num):
        for j in range(cur_cube_num):
            if i != j and intersect[i, j] == 1:
                collision[i] = 1


@ti.kernel
def update_velocity():
    # explicit forward Euler
    for i in range(cur_cube_num):
        cube_f[i] = ti.Vector([0, gravity])
    for i in range(cur_cube_num):
        cube_v[i] += cube_f[i] * delta_t


@ti.kernel
def update_position():
    # explicit forward Euler
    for i in range(cur_cube_num):
        cube_pos[i] += delta_t * cube_v[i]
        if cube_pos[i][0] < 0 or cube_pos[i][0] > world_boundary[0]:
            cube_v[i][0] *= -1
        if cube_pos[i][1] < 0 or cube_pos[i][1] > world_boundary[1]:
            cube_v[i][1] *= -1


def main():
    gui = ti.GUI('test', res=(res, res), background_color=0xDDDDDD)
    init()
    while gui.running:
        if enable_physics == 1:
            update_velocity()
        update_position()

        sap()
        # print(collision.to_numpy()[0:cur_cube_num].tostring())
        #brute_force()
        # print(collision.to_numpy()[0:cur_cube_num].tostring())

        if gui.get_event() and gui.is_pressed(gui.SPACE):
            exit()
        for i in range(cur_cube_num):
            if collision[i] == 1:
                c = 0xff0000
            else:
                c = 0x222222
            gui.rect(((cube_pos[i][0] - cube_size[i][0] * 0.5) / res, (cube_pos[i][1] - cube_size[i][1] * 0.5) / res), (
                (cube_pos[i][0] + cube_size[i][0] * 0.5) / res, (cube_pos[i][1] + cube_size[i][1] * 0.5) / res),
                     radius=2,
                     color=c)
        gui.show()


if __name__ == '__main__':
    main()
