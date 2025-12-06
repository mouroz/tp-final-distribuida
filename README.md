# Comunication Module

Handles the backbone of communication between the cliente and server, as well as the queue and active replication mechanisms. [See more](src/comm/README.md)


# Developer Information

The structure of this project is highly sensitive to changes in the directory structure (a file belonging to src/comm cannot be moved elsewhere).

Other than that, python files (atleast for comm/ and test/comm_test.py) currently can be executed from anywhere and imported from other scripts without breaking, if the proper sys.path location is provided

## Recompile proto:
**Changing names on proto is extremely prone to breaking! Only do this as developer**
```
sudo chmod +x src/comm/grpc_messager/compile_proto.sh
src/comm/grpc_messager/compile_proto.sh
```

## Start server: 
```
python src/comm/server.py --ip=[::] --port=50051
```

## Start client test:
```
python src/test/comm_test.py
```