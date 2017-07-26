from Prop import Prop
from Cell import Cell
import datetime
import time
from struct import *

def readbytes(contents, address, bytenum):
    result = 0
    i = bytenum-1
    while i >= 0:
        result = result + int(contents[address+i])*256**i
        i -= 1
    return result

def signed_int(integer, bytenum):
    if integer > ((256**bytenum)-1)//2:
        integer = integer - (256**bytenum)
    return integer

nFile = input("Input cell file: ")
hFile = open(nFile, 'rb')
cFile = hFile.read()
fileLen = len(cFile)
fileLocation = 0x00
hFile.close()

idxName = nFile[:-3]+'idx'
hIdx = open(idxName, 'rb')
cIdx = hIdx.read()
hIdx.close()

cells = []
IDX_START = 0x200
BLOCK_OFFSET = 0x1C


cIdx = cIdx[IDX_START+BLOCK_OFFSET:]
loc = IDX_START+BLOCK_OFFSET
block = 0
#print(type(cIdx))
while len(cIdx) > 13 and int(cIdx[13]) < 0xFA: #Sanity check? What else can be done?
    address = readbytes(cIdx, 0, 4)
    #print(hex(address), hex(loc))

    print(hex(address), hex(loc))
    if address == 0 or address == IDX_START or cFile[address] != 0xFA:
        block += 1
        newloc = (block+1)*0x400 + BLOCK_OFFSET
        #print(newloc)
        dif = newloc-loc
        loc = newloc
        cIdx = cIdx[dif:]
        
        #print('hi')
        #cIdx = cIdx[0x22:]
        #loc+=0x22
        continue
    data1, x, z = unpack('Hhh', cIdx[4:10])

    

    try:
        length = unpack('I', cFile[address+2:address+6])[0] #4 Byte Unsigned Int
    except:
        pass
        #print(hex(address), hex(loc))
        #quit()
    #print(length)
    if length != 0x0E:
        cells.append( Cell(data1, x, z, address, loc, length) )
    else:
        if cFile[address+0xE] == 0xFA:
            length = length = unpack('I', cFile[address+0x0E+2:address+0x0E+6])[0]
            cells.append( Cell(data1, x, z, address+0x0E, loc, length) ) 
    cIdx = cIdx[10:]
    loc += 10
#print(hex(cIdx[13]))
#print(hex(loc))
for c in cells:
    if c.data1 > 1:
        c.Details()

for i in range(len(cells)-1, -1 ,-1):
    c = cells[i]
    #print(hex(c.location))
    try:
        if cFile[c.address+2] == 0x0E:
            rip = cells.pop(i)
            #print("ignoring %s" % hex(rip.location))
            #print("removed", cells.pop(i).address)
    except:
        cells.pop(i)


##for c in cells:
##    c.Details()
print()

props = []
for c in cells:
    sectionStart = c.address
    start = sectionStart
    sectionLength = readbytes(cFile, sectionStart+2, 4)
    
    #Run until it seems like that was the last object in the section
    while True:

        if start <= 0:
            break
        
        #obtype = readbytes(cFile, start+0x0A, 4)
        (obtype, data1, data2, user, time, obj_x, obj_y, data3, obj_z,
         yaw, tilt, roll, name_len, desc_len, action_len, data_len) = unpack( 'IIIIIhhhhhhhBBBH', cFile[ start+0x0A : start+0x32+2-2 ] )

        try:
            time_built = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
        except:
            print(hex(c.location))
        print(obtype, data1, data2, user, time, obj_x, obj_y, data3, obj_z,
         yaw, tilt, roll, name_len, desc_len, action_len, data_len)
        print(hex(c.address))
        namestart = start+0x31
        print(hex(namestart))
        name = cFile[namestart:
                     namestart+name_len
                     ].decode("utf-8")
        descstart = namestart + name_len
        desc = cFile[descstart:
                     descstart+desc_len
                     ].decode("utf-8")
        actionstart = descstart + desc_len
        action = cFile[actionstart:
                       actionstart+action_len
                       ].decode("utf-8")
        datastart = actionstart+action_len
        data = cFile[datastart:data_len]
        data = ''.join('%02x' % x for x in cFile[datastart:datastart+data_len])
        data = ''

        

        p = Prop(
            user = user,
            time = time,
            x = obj_x+c.x*1000,
            y = obj_y,
            z = obj_z+c.z*1000,
            yaw = yaw,
            tilt = tilt,
            roll = roll,
            proptype = obtype,
            data = (name, desc, action, data) #!!!
            )
        props.append(p)

        if datastart+data_len < sectionStart + sectionLength - 2:
            #Set it up to read a new object
            start = datastart+data_len-10
        else:
            #No more objects in this section
            break


for p in props:
    p.Details()

#Remove duplicate objects
uniqueprops = []
totallen = len(props)
completed = 0
print("Removing any duplicates in %s props" % totallen)
for i in range(len(props)-1, -1, -1):
    p1 = props[i]
    for p2 in props:
        if p2 == p1: continue
        identical = True
        for variable in ['user', 'time', 'name', 'description', 'action', 'x', 'y', 'z', 'yaw', 'tilt', 'roll', 'proptype', 'data']:
            if eval("p1.%s" % variable) != eval("p2.%s" % variable):
                identical = False
                break
        if not identical:
            uniqueprops.append(p1)
            props.pop(i)
            #print('deleted object')
            break
    
    completed += 1
    if completed % 100 == 0:
        percent = (completed/totallen)*100
        #print("%.1f percent complete" % percent)
            


#uniqueprops=uniqueprops[:1000]


#Make propdump
from Propdump import Propdump
##for i in range(len(props)-1, -1, -1):
##    if props[i].proptype != 0:
##        props.pop(i)
pd = Propdump()
pd.objects = uniqueprops
pd.Output('dump.txt')
