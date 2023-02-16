# pyli5 module
Proof of concept for LI infrastructure in 5G SA Core. pyli5 is part of the [P3LI5](https://github.com/intx4/P3LI5) and provides the components to simulate a new protocol allowing privacy-preserving LI on 5G. pyli5 only supports modified message protocols to perform private LI. However it provides modules for parsing
X1 and H1 messages as per ETSI and 3GPP specifications (TS 133 127, TS 133 128, 103 221, 103 120) and can support ```LI_HI1, LI_HIQR. LI_XQR, LI_XEM and LI_XER``` interfaces.
There is no current support for TLS.
**Components are meant to be deployed using Docker following [P3LI5](https://github.com/intx4/P3LI5).**

## RUN
We provide scripts in the form of ```start_*.py``` for bootstrapping the various components.

## GRPC
We already provide the Python bindings for GRPC.
This is how they were generated (for reference):
### Python
-   Install grpc:
```
pip install grpcio
pip install grpcio-tools
```
- Run protoc inside ```src/pyli5/lea```:
```
python3 -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. client.proto
```

- Fix imports:
  - in client_pb2_grpc.py:
  ```
  import pyli5.lea.client_pb2 as client__pb2
  ```
- Same applies for ```icf```.