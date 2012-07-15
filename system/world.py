import coordinate_system
import vector
import cubes_vbo
import cube
import random


class World:
    """trees, cubes, floor"""
    def __init__(self):

        random.seed(5)
        base_ocs = coordinate_system.CoordinateSystem()
        w = 1.
        wy = .7
        cubes = []
        base_ocs.pos[2] += 25.

        print "generating cubes"
        base_ocs.pos[0] -= 7.
        cubes.extend( self._generate_cube_tree(base_ocs, base_wx=w, base_wy=wy, base_wz=w, height_elements=20) )
        base_ocs.pos[0] += 7.
        cubes.extend( self._generate_cube_tree(base_ocs, base_wx=w, base_wy=wy, base_wz=w, height_elements=20) )
        base_ocs.pos[0] += 7.
        cubes.extend( self._generate_cube_tree(base_ocs, base_wx=w, base_wy=wy, base_wz=w, height_elements=20) )

        base_ocs.pos[2] += 20.
        cubes.extend( self._generate_cube_tree(base_ocs, base_wx=w, base_wy=wy, base_wz=w, height_elements=20) )
        base_ocs.pos[0] -= 7.
        cubes.extend( self._generate_cube_tree(base_ocs, base_wx=w, base_wy=wy, base_wz=w, height_elements=20) )
        base_ocs.pos[0] -= 7.
        cubes.extend( self._generate_cube_tree(base_ocs, base_wx=w, base_wy=wy, base_wz=w, height_elements=20) )

        cubes.extend( self._generate_cube_clump(30) )
        cubes.extend( self._generate_cube_floor(vector.Vector((0., 0., 40.)), xnum=14, znum=40, xsize=28, zsize=80) )

        print "generated %i cubes. converting to VBO.. (~4s on macbook pro 2010)" % len(cubes)
        self._cubes_vbo_obj = cubes_vbo.CubesVbo(len(cubes))
        self._fill_cubes_vbo_with_cubes(self._cubes_vbo_obj, cubes)
        print "done"

    def render(self):
        self._cubes_vbo_obj.render()

    def _fill_cubes_vbo_with_cubes(self, cubes_vbo_obj, cubes):
        """takes a list of Cube instances and copies the data to the vertex buffer object"""
        assert cubes_vbo_obj.num_cubes == len(cubes)
        for i in range(cubes_vbo_obj.num_cubes):
            cubes_vbo_obj.update_cube(i, cubes[i])

    def _generate_cube_tree(self, base_ocs, base_wx, base_wy, base_wz, height_elements, branch_color=(1.,1.,1.,1.), first=True):
        """generate a branch. by some random treshold, generate recursively a new branch. return the resulting tree of Cube objects."""
        cubes = []
        if height_elements <= 0:
            return []

        c = cube.Cube()
        c.wx, c.wy, c.wz = base_wx, base_wy, base_wz

        r, g, b, a = branch_color
        c.set_color_f(r, g, b, 1.)

        c.ocs.set(base_ocs)
        if first:
            xrot = 0.
            yrot = random.uniform(0., 360)
        else:
            xrot = 5.
            yrot = 30.
        c.ocs.a_frame.rotate(c.ocs.a_frame.y_axis, yrot)
        c.ocs.a_frame.rotate(c.ocs.a_frame.x_axis, xrot)

        ocs = coordinate_system.CoordinateSystem()
        ocs.set(c.ocs)
        ocs.pos += ocs.a_frame.y_axis * base_wy * 2.

        cubes.append(c)
        cubes += self._generate_cube_tree(ocs, base_wx*.85, base_wy*.95, base_wz*0.85, height_elements-1, branch_color, False)

        if random.random() < 0.30:
            # start a new branch
            ocs.a_frame.rotate(c.ocs.a_frame.y_axis, 30.)
            ocs.a_frame.rotate(c.ocs.a_frame.x_axis, 40.)
            ocs.pos += ocs.a_frame.y_axis * base_wy * 2.
            r, g, b, a = branch_color
            r *= 0.7; g *= 0.7; b *= 0.7
            branch_color = (r, g, b, a)
            cubes += self._generate_cube_tree(ocs, base_wx*.80, base_wy*.90, base_wz*0.80, height_elements-1, branch_color, False)
        return cubes

    def _generate_cube_clump(self, num_cubes):
        """generate and return a list of random and colorful cubes (cube.Cube() objects)"""
        w = 20.
        h = 20.
        d = 70.
        cubes = []
        for i in range(num_cubes):
            x = random.randint(-w / 2, w / 2)
            y = random.uniform(0, h / 20.)
            z = random.randint(5, d)
            c = cube.Cube()
            dd = 0.5
            c.wx = 1. * dd * random.randint(1,4)
            c.wy = 1. * dd * random.randint(1,4) * .5
            c.wz = 1. * dd * random.randint(1,4)
            c.ocs.pos.set((x, y, z))
            ad = 8.
            ax, ay, az = random.uniform(-ad, ad), random.uniform(-ad, ad), random.uniform(-ad, ad)
            c.ocs.a_frame.rotate(c.ocs.a_frame.x_axis, ax)
            c.ocs.a_frame.rotate(c.ocs.a_frame.y_axis, ay)
            c.ocs.a_frame.rotate(c.ocs.a_frame.z_axis, az)
            if 0 and random.random() < 0.8:
                rr = random.random()
                rf, gf, bf = rr, rr, rr
                rf = rf / 2. + 0.5
                gf = gf / 2. + 0.5
                bf = bf / 2. + 0.5
            else:
                rf, gf, bf, af = random.random() *.8, random.random() *.8, random.random(), 1.
            c.set_color_f(rf, gf, bf)
            cubes.append(c)

        return cubes

    def _generate_cube_floor(self, midpoint, xnum, znum, xsize, zsize):
        cubes = []
        cube_xw = xsize / xnum
        cube_zw = zsize / znum
        cube_yw = 0.2
        for z in range(znum):
            for x in range(xnum):
                c = cube.Cube()
                c.ocs.pos.set( vector.Vector((cube_xw*(x-(xnum-1)/2), 0., cube_zw*(z-(znum-1)/2))) )
                c.ocs.pos.add( midpoint )
                c.wx = cube_xw * .9 / 2.
                c.wy = cube_yw / 2.
                c.wz = cube_zw * .9 / 2.
                rr = random.random()
                rf, gf, bf = rr, rr, rr
                rf = rf / 2. + 0.5
                gf = gf / 2. + 0.5
                bf = bf / 2. + 0.5
                c.set_color_f(rf, gf, bf)
                cubes.append(c)
        return cubes
