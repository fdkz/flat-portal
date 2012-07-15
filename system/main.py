import pyglet
from pyglet.window import key
from pyglet.gl import *

import world

import vector
import coordinate_system
import camera


WINDOW_SIZE = (1100, 600)
# side-by-side stereo rendering
USE_SBS_STEREO_RENDERING = True
SWAP_LEFT_RIGHT_EYE = False
EYE_DIST = 1.


class App(pyglet.window.Window):
    def __init__(self, *args, **kwds):
        pyglet.window.Window.__init__(self, *args, **kwds)
        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)
        #self.exclusive_mouse = False
        #self.invalid = False

        # camera position and direction in world-space
        self.camera_ocs  = coordinate_system.CoordinateSystem()
        self.camera      = camera.Camera(pixel_aspect_w_h=.5)
        self.camera.mode = self.camera.PERSPECTIVE
        self.sun_pos  = vector.Vector((0., 20., 0.)) # 20m above the floor
        self.sun2_pos = vector.Vector((0., 20., 80.)) # 20m above the floor, 80m away

        self.world = world.World()

        # position camera
        self.camera_ocs.pos.set([1.5658892333227183, 1.8, 76.2182825865293])
        self.camera_ocs.a_frame.x_axis.set([-0.9999976846266786, 0.0, -0.0021519157237374215])
        self.camera_ocs.a_frame.y_axis.set([0.0, 1.0, 0.0])
        self.camera_ocs.a_frame.z_axis.set([0.0021519157237374215, 0.0, -0.9999976846266786])

        glClearColor(0., 0., 0., 1.0)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glDisable(GL_LINE_STIPPLE)
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);

        glEnable(GL_FOG)

        glFogi(GL_FOG_MODE, GL_EXP2) # GL_EXP, GL_EXP2, GL_LINEAR
        glFogfv(GL_FOG_COLOR, (GLfloat*4)(.1, .1, .1, 1.))
        #glFogf(GL_FOG_DENSITY, .00008)
        glFogf(GL_FOG_DENSITY, .000009)
        glHint(GL_FOG_HINT, GL_DONT_CARE)
        #glEnable(GL_RESCALE_NORMAL)

    def tick(self, dt):
        #print "dt %.4f" % dt
        self.handle_controls(dt)
        #self.fps_counter.tick(real_dt)

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # glViewport(0, 0, self.width, self.height)
        # # reset some opengl settings
        # glEnable(GL_DEPTH_TEST)
        # glDisable(GL_TEXTURE_2D)
        # glDisable(GL_LIGHTING)
        #
        # # setup screen projection for 2d objects (text, hud)
        # glMatrixMode(GL_PROJECTION)
        # glLoadIdentity()
        # z_near = -100.; z_far = 100.
        # glOrtho(0., self.width, self.height, 0., z_near, z_far)

        # glMatrixMode(GL_MODELVIEW)
        # glLoadIdentity()
        # glScalef(1.,1.,-1.)

        # # "If exact two-dimensional rasterization is desired, you must
        # #  carefully specify both the orthographic projection and the
        # #  vertices of primitives that are to be rasterized. The
        # #  orthographic projection should be specified with integer
        # #  coordinates, as shown in the following example: ...."
        # #  (what follows is important)
        # #
        # # -- OpenGL Programming Guide (the redbook)
        # #    http://www.glprogramming.com/red/appendixg.html
        # #
        # glTranslatef(.375, .375, 0.)

        if USE_SBS_STEREO_RENDERING:
            eyedist = -EYE_DIST if SWAP_LEFT_RIGHT_EYE else EYE_DIST
            w, h = int(self.width/2), self.height
            camera_ocs = coordinate_system.CoordinateSystem()
            camera_ocs.set(self.camera_ocs)

            # render images with pixel_aspect_w_h = 2

            # render left view. view for the left eye if not SWAP_LEFT_RIGHT_EYE
            glViewport(0, 0, w, h)
            camera_ocs.pos -= camera_ocs.a_frame.x_axis * eyedist / 2.
            self._render_window(w, h, camera_ocs, self.camera, 2.)

            # render right view
            glViewport(w, 0, w, h)
            camera_ocs.pos += camera_ocs.a_frame.x_axis * eyedist
            self._render_window(w, h, camera_ocs, self.camera, 2.)
        else:
            glViewport(0, 0, self.width, self.height)
            self._render_window(self.width, self.height, self.camera_ocs, self.camera, 1.)

    def _render_window(self, w, h, camera_ocs, camera, pixel_aspect_w_h=1.):
        camera.pixel_aspect_w_h = pixel_aspect_w_h

        #camera.set_fovy(60)
        #camera.update_fovx(float(w) / h)
        camera.set_fovx(98)
        camera.update_fovy(float(w) / h)
        #print "foo", camera.fovy, camera.pixel_aspect_w_h

        camera.set_opengl_projection(camera.PERSPECTIVE, w, h, .5, 50000.)

        # render world

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glScalef(1.,1.,-1.)

        p = camera_ocs.pos
        glMultMatrixf((GLfloat*16)(*camera_ocs.a_frame.get_opengl_matrix()))
        glTranslatef(-p[0], -p[1], -p[2])

        glDisable(GL_TEXTURE_2D)
        glEnable(GL_FOG)
        glDepthFunc(GL_LESS)
        glFrontFace(GL_CW)
        glDepthMask(GL_TRUE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glEnable(GL_LIGHTING)

        # set up lighting and materials

        glLightfv(GL_LIGHT0, GL_POSITION, (GLfloat*4)(self.sun_pos[0], self.sun_pos[1], self.sun_pos[2], 1.))
        glLightfv(GL_LIGHT0, GL_AMBIENT,  (GLfloat*4)(0., 0., 0., 1.))
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  (GLfloat*4)(.8, .8, .8, 1.))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (GLfloat*4)(1., 1., 1., 1.))
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT1, GL_POSITION, (GLfloat*4)(self.sun2_pos[0], self.sun2_pos[1], self.sun2_pos[2], 1.))
        glLightfv(GL_LIGHT1, GL_AMBIENT,  (GLfloat*4)(0., 0., 0., 1.))
        glLightfv(GL_LIGHT1, GL_DIFFUSE,  (GLfloat*4)(.4, .4, .4, 1.))
        glLightfv(GL_LIGHT1, GL_SPECULAR, (GLfloat*4)(1., 1., 1., 1.))
        glEnable(GL_LIGHT1)

        # if glColorMaterial is set to GL_AMBIENT_AND_DIFFUSE, then these GL_AMBIENT and GL_DIFFUSE here have no
        # effect, because the ambient and diffuse values are being taken from vertices themselves.
        #glMaterialfv(GL_FRONT, GL_AMBIENT,   (GLfloat*4)(.0, .0, .0, 1.))
        #glMaterialfv(GL_FRONT, GL_DIFFUSE,   (GLfloat*4)(1., .1, 1., 1.)) # has no effect if using GL_COLOR_MATERIAL
        glMaterialfv(GL_FRONT, GL_EMISSION,  (GLfloat*4)(0.0, 0.0, 0.0, 1.))
        glMaterialfv(GL_FRONT, GL_SPECULAR,  (GLfloat*4)( .2,  .2,  .2, 1.))
        glMaterialfv(GL_FRONT, GL_SHININESS, (GLfloat)(30.))

        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (GLfloat*4)(.2, .2, .2, 1.))

        glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, 1)

        glEnable(GL_COLOR_MATERIAL)
        # what the color value in vertex should be
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        #glColorMaterial(GL_FRONT, GL_DIFFUSE)
        #glColorMaterial(GL_FRONT, GL_AMBIENT)
        #glColorMaterial(GL_FRONT, GL_SPECULAR)
        #glColorMaterial(GL_FRONT, GL_EMISSION)

        self.world.render()

    def handle_controls(self, dt):
        keys = self.keys
        ocs = self.camera_ocs
        camera_speed = 6. # m/s
        camera_turn_speed = 90. # degrees per second

        if keys[key.LSHIFT] or keys[key.RSHIFT]:
            camera_speed *= 2.

        if keys[key.LEFT]:  ocs.a_frame.rotate(ocs.a_frame.y_axis,  camera_turn_speed * dt)
        if keys[key.RIGHT]: ocs.a_frame.rotate(ocs.a_frame.y_axis, -camera_turn_speed * dt)
        if keys[key.W]: ocs.pos += ocs.a_frame.z_axis * camera_speed * dt
        if keys[key.S]: ocs.pos -= ocs.a_frame.z_axis * camera_speed * dt
        if keys[key.A]: ocs.pos -= ocs.a_frame.x_axis * camera_speed * dt
        if keys[key.D]: ocs.pos += ocs.a_frame.x_axis * camera_speed * dt

        if keys[key.UP]:   ocs.a_frame.rotate(ocs.a_frame.x_axis, -camera_turn_speed * dt)
        if keys[key.DOWN]: ocs.a_frame.rotate(ocs.a_frame.x_axis,  camera_turn_speed * dt)
        if keys[key.Q]:    ocs.a_frame.rotate(ocs.a_frame.z_axis, -camera_turn_speed * dt * 1.5)
        if keys[key.E]:    ocs.a_frame.rotate(ocs.a_frame.z_axis,  camera_turn_speed * dt * 1.5)

    def on_resize(self, width, height): pass

    def on_key_press(self, symbol, modifiers):
        #if symbol == key.P and modifiers & key.MOD_SHIFT:
        if symbol == key.ESCAPE:
            self.close()
        if symbol == key.C:
            print "camera ocs:"
            print "pos   :", self.camera_ocs.pos
            print self.camera_ocs.a_frame

def main():
    app = App(width=WINDOW_SIZE[0], height=WINDOW_SIZE[1])
    pyglet.clock.schedule(app.tick)
    pyglet.app.run()

if __name__ == "__main__":
    main()
