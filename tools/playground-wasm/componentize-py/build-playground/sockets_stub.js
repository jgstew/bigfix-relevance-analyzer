// wasi:sockets stub for the browser build.
//
// componentize-py's CPython links the `socket` module, so the component
// *imports* wasi:sockets even though the analyzer never opens a socket.
// preview2-shim's browser build still exposes the old flat-function shape for
// wasi:sockets/ip-name-lookup, so the transpiled glue fails at instantiation
// with "unexpectedly undefined local import 'ResolveAddressStream'". These
// resource classes are never constructed -- every entry point throws, which is
// the correct behaviour for a page that has no network access anyway.
const nope = (what) => { throw new Error(`wasi:sockets is not available in this page (${what})`); };

class Network { static _create() { nope("Network"); } }
class ResolveAddressStream { resolveNextAddress() { nope("resolveNextAddress"); } subscribe() { nope("subscribe"); } }
class TcpSocket {
  startBind() { nope("tcp.startBind"); } finishBind() { nope("tcp.finishBind"); }
  startConnect() { nope("tcp.startConnect"); } finishConnect() { nope("tcp.finishConnect"); }
  startListen() { nope("tcp.startListen"); } finishListen() { nope("tcp.finishListen"); }
  accept() { nope("tcp.accept"); } localAddress() { nope("tcp.localAddress"); }
  remoteAddress() { nope("tcp.remoteAddress"); } isListening() { nope("tcp.isListening"); }
  addressFamily() { nope("tcp.addressFamily"); } setListenBacklogSize() { nope("tcp.setListenBacklogSize"); }
  keepAliveEnabled() { nope("tcp"); } setKeepAliveEnabled() { nope("tcp"); }
  keepAliveIdleTime() { nope("tcp"); } setKeepAliveIdleTime() { nope("tcp"); }
  keepAliveInterval() { nope("tcp"); } setKeepAliveInterval() { nope("tcp"); }
  keepAliveCount() { nope("tcp"); } setKeepAliveCount() { nope("tcp"); }
  hopLimit() { nope("tcp"); } setHopLimit() { nope("tcp"); }
  receiveBufferSize() { nope("tcp"); } setReceiveBufferSize() { nope("tcp"); }
  sendBufferSize() { nope("tcp"); } setSendBufferSize() { nope("tcp"); }
  subscribe() { nope("tcp.subscribe"); } shutdown() { nope("tcp.shutdown"); }
}
class IncomingDatagramStream { receive() { nope("udp.receive"); } subscribe() { nope("udp"); } }
class OutgoingDatagramStream { checkSend() { nope("udp.checkSend"); } send() { nope("udp.send"); } subscribe() { nope("udp"); } }
class UdpSocket {
  startBind() { nope("udp.startBind"); } finishBind() { nope("udp.finishBind"); }
  stream() { nope("udp.stream"); } localAddress() { nope("udp"); } remoteAddress() { nope("udp"); }
  addressFamily() { nope("udp"); } unicastHopLimit() { nope("udp"); } setUnicastHopLimit() { nope("udp"); }
  receiveBufferSize() { nope("udp"); } setReceiveBufferSize() { nope("udp"); }
  sendBufferSize() { nope("udp"); } setSendBufferSize() { nope("udp"); } subscribe() { nope("udp"); }
}

export const network = { Network, ErrorCode: {}, IpAddressFamily: {} };
export const instanceNetwork = { instanceNetwork: () => nope("instanceNetwork") };
export const ipNameLookup = { ResolveAddressStream, resolveAddresses: () => nope("resolveAddresses") };
export const tcp = { TcpSocket };
export const tcpCreateSocket = { createTcpSocket: () => nope("createTcpSocket") };
export const udp = { UdpSocket, IncomingDatagramStream, OutgoingDatagramStream };
export const udpCreateSocket = { createUdpSocket: () => nope("createUdpSocket") };
