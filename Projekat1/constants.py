import struct
ATTRIBUTES = ["evidencioni broj", "registarska oznaka", "datum i vreme", "oznaka parking mesta", "duzina boravka", "status"] #definicija sloga
FORMAT = "i11s18s8s8si" #formatni string za pakovanje slogova
CODING = "ascii"
F = 5 #zadato u zadatku
HEADERFORMAT = "ii"

SERIALATTRIBUTES = ["evidencioni broj"]
SERIALFORMAT = "i"


# with open("data_file.dat", "rb") as f:
#     header = f.read(8)
# f.close()
# header = list(struct.unpack("ii", header))
# header[0] = 2
# header[1] = 5
# br_slogova=[int(i) for i in header]
# r = struct.pack("ii", *br_slogova)
# with open("data_file.dat", "wb") as f:
#     f.seek(0)
#     f.write(r)
# with open("data_file.dat", "rb") as f:
#     header = f.read(8)
#     print(list(struct.unpack("ii", header)))
# f.close()