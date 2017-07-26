class Cell():
    def __init__(s, data1, x, z, address, loc, length):
        s.data1 = data1 # 2 bytes
        s.x = x # 2 bytes int
        s.z = z # 2 bytes int
        s.address = address # 4 bytes int
        s.location = loc
        s.length = length
    def Details(s):
        print("Address: %s\nX, Z: %s, %s\ndata1: %s\nLocation: %s\n" % (hex(s.address),s.x,s.z,s.data1,hex(s.location)))
