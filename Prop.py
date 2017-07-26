class Prop():
    def __init__(self, user, time, x, y, z, yaw, tilt, roll, proptype, data):
        self.user = user
        self.time = time
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.tilt = tilt
        self.roll = roll
        self.proptype = proptype
        self.data = data
        #print(self.data)
        self.name, self.description, self.action, self.data = tuple(self.data)
    def Details(s):
        import datetime
        objecttypes = ['Object', 'Camera', 'Zone', 'Particle Emitter', 'Mover', 'Camera']
        print('Object Type: %s\nName: %s\nDescription: %s\nAction: %s\nYaw: %s\nTilt: %s\nRoll: %s' %
              (objecttypes[s.proptype], s.name, s.description, s.action, s.yaw, s.tilt, s.roll))
        print("Time built: %s" % (datetime.datetime.fromtimestamp(s.time).strftime('%Y-%m-%d %H:%M:%S')))
        print('Coords: %s %s %s 0\n' % s.Coords())
    def Coords(s):
        coords = []
        for v in [s.x, s.y, s.z]:
            coords.append(v/1000)
        if coords[0] >= 0.0:
            XDir = 'W'
        else:
            XDir = 'E'

        if coords[2] >= 0.0:
            ZDir = 'N'
        else:
            ZDir = 'S'

        X = "%0.2f%s" % (abs(coords[0]), XDir)
        Z = "%0.2f%s" % (abs(coords[2]), ZDir)
        Y = "%0.2fa" % (coords[1])
        return (Z, X, Y)
        
        
        



