
how to use protobuf:

command to install:
pip install protobuf
sudo apt-install protobuf-compiler

how to write protocol:
https://developers.google.com/protocol-buffers/docs/pythontutorial

command to generate Your Protocol Buffers:
protoc -I=$SRC_DIR --python_out=$DST_DIR $SRC_DIR/[name_of_the_proto_file].proto

how to test the socket communication:
python3 server.py
python3 client.py

Protocol Buffers - Google's data interchange format
Copyright 2008 Google Inc.
https://developers.google.com/protocol-buffers/

This package contains a precompiled binary version of the protocol buffer
compiler (protoc). This binary is intended for users who want to use Protocol
Buffers in languages other than C++ but do not want to compile protoc
themselves. To install, simply place this binary somewhere in your PATH.

If you intend to use the included well known types then don't forget to
copy the contents of the 'include' directory somewhere as well, for example
into '/usr/local/include/'.

Please refer to our official github site for more installation instructions:
  https://github.com/protocolbuffers/protobuf
