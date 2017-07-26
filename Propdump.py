class Propdump():
    def __init__(self):
        self.objects = []
    def AddObject(self, prop):
        self.objects.append(prop)
    def Output(self, nFile):
        hFile = open(nFile, 'wb')
        hFile.write(b'propdump version 5\r\n')
        for ob in self.objects:

            datalen = len(ob.data)//2
            namelen = len(ob.name)
            desclen = len(ob.description)
            actionlen = len(ob.action)
            d = ''.join(ob.data)
            description = bytes(ob.description.encode('UTF-8'))
            if b'\xE2\x82\xAC\x7F' in description:
                pass#print(description)
            

            line = '%s %s %s %s %s %s %s %s %s %s %s %s %s %s%s%s%s'% (
                ob.user, ob.time, ob.x, ob.y, ob.z,
                ob.yaw, ob.tilt, ob.roll, ob.proptype,
                namelen, desclen, actionlen, datalen,
                ob.name, ob.description, ob.action,
                d
                )
            line = bytes(line.encode("UTF-8"))
            line = line.replace(bytes([0xE2, 0x82, 0xAC, 0x7F]), bytes([0x80, 0x7F]))
            line = line.replace(bytes([0x0D, 0x0A]), bytes([0x80, 0x7F]))
            line = line.replace(bytes([0x0D]), bytes([0x80, 0x7F]))
            line = line.replace(bytes([0x0A]), bytes([0x80, 0x7F]))
            line = line + bytes([0x0D, 0x0A])



            hFile.write(line)
            
            
