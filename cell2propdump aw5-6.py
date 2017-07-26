from Prop import Prop
from Cell import Cell
from struct import *


#read dat file
nFile = input("Input cell.dat file: ")
hFile = open(nFile, 'rb')
cFile = hFile.read()
hFile.close()

#read idx file
idxName = nFile[:-3]+'idx'
hIdx = open(idxName, 'rb')
cIdx = hIdx.read()
hIdx.close()

#Parse IDX header
(IDXLength, #0
 IDXunk1, #4
 IDXEnd, #8
 IDXunk2, #C
 IDXunk3, #10
 IDXunk4, #14
 IDXunk5, #18
 IDXunk6, #1C
 IDXunk7, #20
 IDXunk8, #24
 IDXunk9, #28
 IDXunk10, #2C
 IDXunk11, #30
 IDXunk12, #34
 IDXunk13, #38
 IDXunk14, #3C  
 IDXunk15, #40
 IDXunk16, #44
 IDXStart, #48
 IDXunk18, #4C
 IDXunk19, #50
 IDXunk20, #54
 IDXunk21, #58
 IDXunk22, #5C
 IDXunk23, #60
 IDXunk24, #64
 IDXunk25, #68
 IDXunk26, #6C
 IDXunk27, #70
 IDXunk28, #74
 IDXunk29, #78
 IDXunk30 #7C
) = unpack('IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII', cIdx[0:0x80])



cells = []

DAT_START = 0x200
IDX_START = IDXStart

#Section header length
IDX_OFFSET = 0x12


BlockStart = IDXStart

#Loop at least once, and stop when next block is at 0 (end of index)
while True:
    forward, backward, entries, entrieslength = unpack('<IIHH', cIdx[BlockStart:BlockStart+12])
    loc = BlockStart + IDX_OFFSET
    print("Reading %s index entries from index block %s" % (entries, hex(BlockStart)))

    #Get entries until entry limit
    for entrycount in range(0, entries):
        address, data1, x, z = unpack("IHhh", cIdx[loc:loc+10])
        length = unpack('I', cFile[address+2:address+6])[0]

        #Entries whose data length are 0x0E contain no data
        if length != 0x0E:
            cells.append( Cell(data1, x, z, address, loc, length) )

        #Each index entry is 10 bytes long
        loc += 10

    if forward == 0x00000000:
        break
    
    BlockStart = forward


##for c in cells:
##    c.Details()

#AW4 and before use utf-8
STRING_ENCODING = 'utf-16'

props = []
for c in cells:
    sectionStart = c.address
    FAFA, sectionLength, sectionEntryLength = unpack('<HII', cFile[sectionStart:sectionStart+10])

    objectStart = sectionStart+0x0A
    
    #Find at least one object, and stop when it goes beyond the length of the section
    while True:
    
        (obtype, data1, data2, user, time, obj_x, obj_y, data3, obj_z,
         yaw, tilt, roll, name_len, desc_len, action_len, data_len) = unpack( '<IIIIIhhhhhhhHHHH', cFile[ objectStart : objectStart+0x2A ] )
        
        namestart = objectStart+0x2A
        name = cFile[ namestart : namestart+name_len ].decode(STRING_ENCODING)
        
        descstart = namestart + name_len
        desc = cFile[ descstart : descstart+desc_len ].decode(STRING_ENCODING)
        
        actionstart = descstart + desc_len
        action = cFile[ actionstart : actionstart+action_len ].decode(STRING_ENCODING)
        
        datastart = actionstart+action_len
        data = cFile[datastart:data_len]
        #Convert data binary data to a string of hex. That's how propdumps work.
        data = ''.join('%02x' % x for x in cFile[datastart:datastart+data_len])
        
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
            data = (name, desc, action, data) 
            )
        props.append(p)

        #Set up to read a new object
        objectStart = datastart+data_len
        
        if objectStart >= sectionStart+sectionLength:
            #Exit if that was the last object
            break

##
##for p in props:
##    p.Details()


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
    if completed % 1000 == 0:
        percent = (completed/totallen)*100
        print("%.1f percent complete" % percent)
print("%s props in total." % len(uniqueprops))
#Uniques have been stored un uniqueprops
#Removed props are in props



#Make propdump
from Propdump import Propdump
pd = Propdump()
pd.objects = uniqueprops
pd.Output('dump.txt')
