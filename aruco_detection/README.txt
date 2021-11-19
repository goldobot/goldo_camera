~> pip install zmq protobuf
~> sudo apt-get install protobuf-compiler

brancher la camera: camera <=> /dev/videox

>> protoc -I=. --python_out=. ./eyeInTheSky.proto
>> python3 eyeInTheSky.py --video x
>> python3 robot.py 

