import struct
from Obj import Obj
from collections import namedtuple

V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])

def char(c):
    return struct.pack('=c', c.encode('ascii'))

def word(c):
    return struct.pack('=h', c)

def dword(c):
    return struct.pack('=l', c)

def color(red, green, blue):
     return bytes([round(blue * 255), round(green * 255), round(red * 255)])

def color2(r, g, b):
    return bytes([b, g, r])

#Funciones vistas con Dennis
def dot(v0, v1):
  return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

def length(v0):
  return (v0.x**2 + v0.y**2 + v0.z**2)**0.5

def mul(v0, k):
  return V3(v0.x * k, v0.y * k, v0.z *k)

def cross(v1, v2):
  return V3(
    v1.y * v2.z - v1.z * v2.y,
    v1.z * v2.x - v1.x * v2.z,
    v1.x * v2.y - v1.y * v2.x,
  )

def sum(v0, v1):
  return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)

def sub(v0, v1):
  return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)

def bbox(*vertices):

  xs = [ vertices.x for vertices in vertices ]
  ys = [ vertices.y for vertices in vertices ]

  return (max(xs), max(ys), min(xs), min(ys))

def barycentric(A, B, C, P):
  cx, cy, cz = cross(
    V3(B.x - A.x, C.x - A.x, A.x - P.x), 
    V3(B.y - A.y, C.y - A.y, A.y - P.y)
  )

  if abs(cz) < 1:
    return -1, -1, -1   


  u = cx/cz
  v = cy/cz
  w = 1 - (u + v)

  return w, v, u

def norm(v0):
  v0length = length(v0)

  if not v0length:
    return V3(0, 0, 0)

  return V3(v0.x/v0length, v0.y/v0length, v0.z/v0length)

class Render(object):

    def __init__(self):
        self.width = 0
        self.height = 0
        self.xVP = 0
        self.yVP = 0
        self.hVP = 0
        self.wVP = 0
        self.clear_color = color(0,0,0)
        self.framebuffer = []
        self.glClear()

    def glClear(self):
        self.framebuffer = [[self.clear_color for x in range(self.width)] for y in range(self.height)]
        self.zbuffer = [[-float('inf') for x in range(self.width)] for y in range(self.height)]

    def glpoint(self, x, y):
        self.framebuffer[y][x] = self.clear_color

    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height

    def triangle(self, A, B, C):
        xmax, ymax, xmin, ymin = bbox(A, B, C)
        
        for x in range(xmin, xmax + 1):
            for y in range(ymin, ymax + 1):
                P = V2(x, y)
                w, v, u = barycentric(A, B, C, P)
                if w < 0 or v < 0 or u < 0:
                    continue
                z = A.z * w + B.z * u + C.z * v
                try:
                    if z > self.zbuffer[x][y]:
                        self.glpoint(x,y)
                        self.zbuffer[x][y] = z
                except:
                    pass

    def load(self, filename, translate=(0, 0, 0), scale=(1, 1, 1)):
        model = Obj(filename)

        light = V3(0, 0, 1)
    
        for face in model.faces:
            vcount = len(face)
            
            if vcount == 3:
                face1 = face[0][0] - 1
                face2 = face[1][0] - 1
                face3 = face[2][0] - 1

                v1 = V3(model.vertices[face1][0], model.vertices[face1][1], model.vertices[face1][2])
                v2 = V3(model.vertices[face2][0], model.vertices[face2][1], model.vertices[face2][2])
                v3 = V3(model.vertices[face3][0], model.vertices[face3][1], model.vertices[face3][2])

                x1 = round((v1.x * scale[0]) + translate[0])
                y1 = round((v1.y * scale[1]) + translate[1])
                z1 = round((v1.z * scale[2]) + translate[2])

                x2 = round((v2.x * scale[0]) + translate[0])
                y2 = round((v2.y * scale[1]) + translate[1])
                z2 = round((v2.z * scale[2]) + translate[2])

                x3 = round((v3.x * scale[0]) + translate[0])
                y3 = round((v3.y * scale[1]) + translate[1])
                z3 = round((v3.z * scale[2]) + translate[2])

                A = V3(x1, y1, z1)
                B = V3(x2, y2, z2)
                C = V3(x3, y3, z3)

                xs = min([x1, x2, x3])
                ys = min([y1, y2, y3])
                colorShader = self.neptuno(xs, ys)

                normal = norm(cross(sub(B, A), sub(C, A)))
                intensity = dot(normal, norm(light))
                colors = []
                for i in colorShader:
                    if i * intensity > 0:
                        colors.append(round(i * intensity))
                    else:
                        colors.append(10)
                colors.reverse()

                self.clear_color = color2(colors[0], colors[1], colors[2])
                self.triangle(A, B, C)

            else:
                face1 = face[0][0] - 1
                face2 = face[1][0] - 1
                face3 = face[2][0] - 1
                face4 = face[3][0] - 1   

                v1 = V3(model.vertices[face1][0], model.vertices[face1][1], model.vertices[face1][2])
                v2 = V3(model.vertices[face2][0], model.vertices[face2][1], model.vertices[face2][2])
                v3 = V3(model.vertices[face3][0], model.vertices[face3][1], model.vertices[face3][2])
                v4 = V3(model.vertices[face4][0], model.vertices[face4][1], model.vertices[face4][2])

                x1 = round((v1.x * scale[0]) + translate[0])
                y1 = round((v1.y * scale[1]) + translate[1])
                z1 = round((v1.z * scale[2]) + translate[2])

                x2 = round((v2.x * scale[0]) + translate[0])
                y2 = round((v2.y * scale[1]) + translate[1])
                z2 = round((v2.z * scale[2]) + translate[2])

                x3 = round((v3.x * scale[0]) + translate[0])
                y3 = round((v3.y * scale[1]) + translate[1])
                z3 = round((v3.z * scale[2]) + translate[2])

                x4 = round((v4.x * scale[0]) + translate[0])
                y4 = round((v4.y * scale[1]) + translate[1])
                z4 = round((v4.z * scale[2]) + translate[2])

                A = V3(x1, y1, z1)
                B = V3(x2, y2, z2)
                C = V3(x3, y3, z3)
                D = V3(x4, y4, z4)
                
                normal = norm(cross(sub(B, A), sub(C, A)))
                intensity = dot(normal, norm(light))
                colors = []
                for i in colorShader:
                    if i * intensity > 0:
                        colors.append(round(i * intensity))
                    else:
                        colors.append(10)
                self.clear_color = color(colors[0], colors[1], colors[2])
                colors.reverse()

                self.triangle(A, B, C)
                self.triangle(A, C, D)
                
    def neptuno(self, x, y):
        if (x > 350 and y > 325):
            return color2(67,145,223)

        elif (y>320):
            return color2(58,125,191)

        elif (x > 230 and x < 295 and y > 200):
            return color2(48,104,159)

        elif (y<150 and x>200):
            return color2(58,125,191)

        else:
            return color2(67,145,223)

    def glFinish(self, filename):
        f = open(filename, 'bw')

        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14 + 40 + self.width + self.height * 3))
        f.write(dword(0))
        f.write(dword(14 + 40))

        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))


        for x in range(self.height):
            for y in range(self.width):
                f.write(self.framebuffer[x][y])
        f.close()

bitmap = Render()
bitmap.glCreateWindow(1920, 1080)
bitmap.glClear()
bitmap.load('./sphere.obj', (450, 350, 0), (350, 350, 350))
bitmap.glFinish('Neptunooo.bmp')
