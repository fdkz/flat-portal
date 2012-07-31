# http://www.songho.ca/opengl/gl_vbo.html : OpenGL Vertex Buffer Object (VBO)
# http://www.slideshare.net/Mark_Kilgard/using-vertex-bufferobjectswell


#include "coordinate_system_t.h"
#include "cube_template.h"

from pyglet.gl import *
from ctypes import Structure, sizeof, pointer, c_uint32
import vector

import struct

class CubeVertex(Structure):
    # TODO: correct use of __pack__?
    _pack_ = 0
    _fields_ = [
        ("x", GLfloat),
        ("y", GLfloat),
        ("z", GLfloat),
        ("color", c_uint32),
        ("nx", GLfloat),
        ("ny", GLfloat),
        ("nz", GLfloat)]
        #float s0, t0 # Texcoord0
        #float s1, t1 # Texcoord1
        #float s2, t2 # Texcoord2
        #float padding[4]

#print "CubeVertex.x", CubeVertex.x
#print "sizeof(CubeVertex)", sizeof(CubeVertex)


class CubesVbo:
    VERTS_PER_CUBE = 6*6
    BYTES_PER_CUBE_VERT = 28
    def __init__(self, num_cubes, raw_vbo_bytes=None):
        self.num_cubes = num_cubes

        assert self.BYTES_PER_CUBE_VERT == sizeof(CubeVertex)

        self._vbo_vertices_num   = self.VERTS_PER_CUBE * num_cubes;
        self._vbo_vertices_bytes = self._vbo_vertices_num * self.BYTES_PER_CUBE_VERT
        if raw_vbo_bytes:
            assert len(raw_vbo_bytes) == self._vbo_vertices_num * sizeof(CubeVertex)
            self._vbo_python_buffer = bytearray(raw_vbo_bytes)
        else:
            self._vbo_python_buffer = bytearray(self._vbo_vertices_num * sizeof(CubeVertex))
        vbo_buf_type = CubeVertex * self._vbo_vertices_num
        #self._vbo_vertices = (CubeVertex * self._vbo_vertices_num)()
        self._vbo_vertices = vbo_buf_type.from_buffer(self._vbo_python_buffer)

        assert sizeof(self._vbo_vertices) == self._vbo_vertices_bytes

        self._vboid_vertices = GLuint()
        glGenBuffers(1, pointer(self._vboid_vertices))

        self._vbo_initialized = False

    def close(self):
        glDeleteBuffers(1, pointer(self._vboid_vertices));

    def _set_cube_vertex(self, vertex_index, v, n, color):
        """ convert the given coordinate data to the vb format
        vertex_index : index to the _vbo_vertices buf
        v : vertex
        n : vertex normal
        color : GLuint
        """
        # this struct version is very slightly faster. but a bit more cryptic.
        #struct.pack_into("fffIfff", self._vbo_python_buffer, 7*4*vertex_index, v[0], v[1], v[2], color, n[0], n[1], n[2])
        #return
        vv = self._vbo_vertices[vertex_index]
        vv.x = v[0]
        vv.y = v[1]
        vv.z = v[2]
        vv.nx = n[0]
        vv.ny = n[1]
        vv.nz = n[2]
        vv.color = color

    def update_cube(self, cube_index, cube):
        """ this only works before any rendering """
        i = cube_index * self.VERTS_PER_CUBE
        ocs = cube.ocs
        wx, wy, wz = cube.wx, cube.wy, cube.wz
        color = cube.color

        # front
        v1 = ocs.projv_out(vector.Vector((-wx,  wy, -wz)))
        v2 = ocs.projv_out(vector.Vector(( wx,  wy, -wz)))
        v3 = ocs.projv_out(vector.Vector(( wx, -wy, -wz)))
        v4 = ocs.projv_out(vector.Vector((-wx, -wy, -wz)))
        # back
        v5 = ocs.projv_out(vector.Vector((-wx,  wy,  wz)))
        v6 = ocs.projv_out(vector.Vector(( wx,  wy,  wz)))
        v7 = ocs.projv_out(vector.Vector(( wx, -wy,  wz)))
        v8 = ocs.projv_out(vector.Vector((-wx, -wy,  wz)))

        n1 = ocs.a_frame.projv_out(vector.Vector(( 0.,  0., -1.)))
        n2 = ocs.a_frame.projv_out(vector.Vector(( 0.,  0.,  1.)))
        n3 = ocs.a_frame.projv_out(vector.Vector((-1.,  0.,  0.)))
        n4 = ocs.a_frame.projv_out(vector.Vector(( 1.,  0.,  0.)))
        n5 = ocs.a_frame.projv_out(vector.Vector(( 0.,  1.,  0.)))
        n6 = ocs.a_frame.projv_out(vector.Vector(( 0., -1.,  0.)))

        s = self._set_cube_vertex

        # front
        s(i, v1, n1, color); i += 1
        s(i, v2, n1, color); i += 1
        s(i, v3, n1, color); i += 1
        s(i, v1, n1, color); i += 1
        s(i, v3, n1, color); i += 1
        s(i, v4, n1, color); i += 1
        # back
        s(i, v6, n2, color); i += 1
        s(i, v5, n2, color); i += 1
        s(i, v8, n2, color); i += 1
        s(i, v6, n2, color); i += 1
        s(i, v8, n2, color); i += 1
        s(i, v7, n2, color); i += 1
        # left
        s(i, v5, n3, color); i += 1
        s(i, v1, n3, color); i += 1
        s(i, v4, n3, color); i += 1
        s(i, v5, n3, color); i += 1
        s(i, v4, n3, color); i += 1
        s(i, v8, n3, color); i += 1
        # right
        s(i, v2, n4, color); i += 1
        s(i, v6, n4, color); i += 1
        s(i, v7, n4, color); i += 1
        s(i, v2, n4, color); i += 1
        s(i, v7, n4, color); i += 1
        s(i, v3, n4, color); i += 1
        # top
        s(i, v1, n5, color); i += 1
        s(i, v5, n5, color); i += 1
        s(i, v6, n5, color); i += 1
        s(i, v1, n5, color); i += 1
        s(i, v6, n5, color); i += 1
        s(i, v2, n5, color); i += 1
        # bottom
        s(i, v4, n6, color); i += 1
        s(i, v3, n6, color); i += 1
        s(i, v7, n6, color); i += 1
        s(i, v4, n6, color); i += 1
        s(i, v7, n6, color); i += 1
        s(i, v8, n6, color); i += 1

    def render(self):
        glBindBuffer(GL_ARRAY_BUFFER, self._vboid_vertices)
        if not self._vbo_initialized:
            # upload vbo contents to the graphics card
            self._vbo_initialized = True
            glBufferData(GL_ARRAY_BUFFER, sizeof(self._vbo_vertices), self._vbo_vertices, GL_STATIC_DRAW)
            #glBufferData(GL_ARRAY_BUFFER, sizeof(self._vbo_vertices), pointer(self._vbo_vertices), GL_STATIC_DRAW)
            #glBufferData(GL_ARRAY_BUFFER, sizeof(data), 0, GL_DYNAMIC_DRAW)
            #glBufferSubData(GL_ARRAY_BUFFER, 0, sizeof(data), data)

        glVertexPointer(3, GL_FLOAT, sizeof(CubeVertex), 0);
        glColorPointer(4, GL_UNSIGNED_BYTE, sizeof(CubeVertex), 12);
        glNormalPointer(GL_FLOAT, sizeof(CubeVertex), 16);
        glEnableClientState(GL_VERTEX_ARRAY);
        glEnableClientState(GL_COLOR_ARRAY);
        glEnableClientState(GL_NORMAL_ARRAY);
        glDrawArrays(GL_TRIANGLES, 0, self._vbo_vertices_num);
        glDisableClientState(GL_NORMAL_ARRAY);
        glDisableClientState(GL_COLOR_ARRAY);
        glDisableClientState(GL_VERTEX_ARRAY);
