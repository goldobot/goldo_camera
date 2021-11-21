Install:
--------

~> pip install opencv-contrib-python zmq protobuf
~> sudo apt-get install protobuf-compiler

Use:
----

brancher la camera: camera <=> /dev/videox

Pour protobuf:
>> protoc -I=. --python_out=. ./cosmorak.proto

Dans un terminal, lancer le publisher zmq:
>> python3 cosmorak.py --video x

Dans un autre terminal, lancer le subscriber zmq:
>> python3 robot.py 

