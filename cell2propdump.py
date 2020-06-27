from Prop import Prop
from Cell import Cell
from struct import *
import argparse

def ApplyCells(cellProps, databasePath, AWVer):
    nIdx = databasePath + '.idx'
    nDat = databasePath + '.dat'
    print(f'Opening {nDat} and {nIdx}')
    

    with open(nIdx, 'rb') as f:
        cIdx = f.read()

    with open(nDat, 'rb') as f:
        cFile = f.read()

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
    if AWVer == 5 or AWVer == 6:
        STRING_ENCODING = 'utf-16'
        OBJECT_ENCODING = '<IIIIIhihhhhHHHH'
        OBJECT_ENCODING_SIZE = 0x2A
    elif AWVer == 4:
        STRING_ENCODING = 'latin-1'
        OBJECT_ENCODING = '<IIIIIhihhhhBBBH'
        OBJECT_ENCODING_SIZE = 0x27


    for c in cells:
        props = []
        cellProps[(c.x, c.z)] = props
        sectionStart = c.address
        FAFA, sectionLength, sectionEntryLength = unpack('<HII', cFile[sectionStart:sectionStart+10])

        objectStart = sectionStart+0x0A
        
        #Find at least one object, and stop when it goes beyond the length of the section
        while True:
            (obtype, data1, data2, user, time, obj_x, obj_y, obj_z, 
                yaw, tilt, roll, name_len, desc_len, action_len, data_len) = unpack( OBJECT_ENCODING, cFile[ objectStart : objectStart+OBJECT_ENCODING_SIZE ] )

            if obtype not in range(0, 7):
                print("Junk object data found. Skipping %s" % hex(objectStart))
                break
            
            namestart = objectStart+OBJECT_ENCODING_SIZE
            #print(cFile[ namestart : namestart+name_len ])
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


            if not action.isascii() or not desc.isascii() or not name.isascii():
                print(f'skipping {name}; {desc}; {action}')
            else:
                props.append(p)

            #Set up to read a new object
            objectStart = datastart+data_len
            
            if objectStart >= sectionStart+sectionLength:
                #Exit if that was the last object
                break


parser = argparse.ArgumentParser(description='Converts elev databases to propdumps.')
parser.add_argument('databases', type=str, help='Paths to databases, separated by the | symbol')
parser.add_argument('output', type=str, help='File to write resulting propdump to')
parser.add_argument('version', type=int, help='AW version of the databases')
args = parser.parse_args()

databases = args.databases.split('|')
output = args.output
awtype = args.version

cellProps = dict()

for database in databases:
    ApplyCells(cellProps, database, awtype)


props = []
for proplist in cellProps.values():
    props.extend(proplist)

print("%s props in total." % len(props))

#Make propdump
from Propdump import Propdump
pd = Propdump()
pd.objects = props
pd.Output(output)
