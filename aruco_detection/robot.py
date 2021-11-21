# Import the opencv library.
import argparse
import sys
import cv2
import zmq
import cosmorak_pb2

def cmdLineArgs():
    # Create parser.
    parser = argparse.ArgumentParser(description='Publisher parser.')
    parser.add_argument('--host', type=str, default='127.0.0.1')
    parser.add_argument('--port', type=int, default=2000)
    args = parser.parse_args()

    return args

def main():
    # Get command line arguments.
    args = cmdLineArgs()

    # Bind ZMQ socket.
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect('tcp://%s:%s' % (args.host, args.port))

    # Subscribes to all topics
    socket.subscribe('')

    # Listening to published data.
    while True:
        raw = socket.recv()
        data = cosmorak_pb2.data()
        data.ParseFromString(raw)
        print('[INFO] detected ArUco marker: ID={}, c=({}, {}), u=({}, {}), v=({}, {})'.format(data.markerID, data.cX, data.cY, data.uX, data.uY, data.vX, data.vY))

# Main program.
if __name__ == '__main__':
    sys.exit(main())
