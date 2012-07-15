
import coordinate_system

class Cube:
    #FLAG_NO_COLLISION_DETECTION = 1
    def __init__(self, wx=1., wy=1., wz=1., color=0xaabbccdd):
        """ wx, wy, wz : half widths """
        self.ocs = coordinate_system.CoordinateSystem()
        self.wx = wx
        self.wy = wy
        self.wz = wz
        #self.flags = 0
        self.color = color

    def set_color_8(self, r, g, b, a=255):
        """ ABGR """
        self.color = (int(a)<<24) | (int(b)<<16) | (int(g)<<8) | int(r)

    def set_color_f(self, r, g, b, a=1.):
        self.set_color_8( min(r,1.)*255.+0.5, min(g,1.)*255.+0.5, min(b,1.)*255.+0.5, min(a,1.)*255.+0.5 )
