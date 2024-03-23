import glob
import os

dir = '/opt/MagAOX/telem'
from binascii import hexlify
for file in glob.glob(os.path.join(dir, '*')):
    if os.path.isfile(file):
        print(file)
        with open(file, 'rb') as line:
            line = line.read(50)
            line = line.decode('utf8')
            print(type(line))
            print(hexlify(line))
            break
   