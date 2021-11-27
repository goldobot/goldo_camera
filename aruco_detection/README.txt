Installation:
-------------

~> pip install opencv-contrib-python zmq protobuf
~> sudo apt-get install protobuf-compiler

Utilisation:
------------

brancher la camera: camera <=> /dev/videoX

Pour protobuf:
>> protoc -I=. --python_out=. ./cosmorak.proto

Dans un terminal, lancer le publisher zmq:
>> python3 cosmorak.py --video X

Dans un autre terminal, lancer le subscriber zmq:
>> python3 robot.py 

