import socket 
import struct
import base64
import json
import hashlib
import pdb
import xml.etree.ElementTree as ET

HOST = "ubuntu-2004-postgres-1012_irods-catalog-provider_1"
PORT = 1247
MAX_PASSWORD_LENGTH = 50

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    # StartupPack is sent by client to initiate connection
    # Notice how message, header, and prelude have to be 
    # constructed in reverse order
    msg = """ 
    <StartupPack_PI>
             <irodsProt>1</irodsProt>
             <reconnFlag>1</reconnFlag>
             <connectCnt>2</connectCnt>
             <proxyUser>rods</proxyUser>
             <proxyRcatZone>tempZone</proxyRcatZone>
             <clientUser>rods</clientUser>
             <clientRcatZone>tempZone</clientRcatZone>
             <relVersion>rods4.3.0</relVersion>
             <apiVersion>d</apiVersion>
             <option>nonse</option>
    </StartupPack_PI>
    """.replace(" ", "").replace("\n", "").encode("utf-8") 
    
    header = f""" 
    <MsgHeader_PI>
            <type>RODS_CONNECT</type>
            <msgLen>{len(msg)}</msgLen>
            <errorLen>0</errorLen>
            <bsLen>0</bsLen>
            <intInfo>0</intInfo>
    </MsgHeader_PI>
    """.replace(' ', '').replace('\n', '').encode("utf-8")

    # First part of an iRODS message is always 4 bytes indicating how large the header is 
    s.send(len(header).to_bytes(4, byteorder='big'))
    # Then send the header
    s.send(header)
    # Finally message
    s.send(msg)
    # If we had an error stack or a raw byte stream, we'd send them here
    # Notice that both errorLen and bsLen in the header are set to 0, so we don't do that

    ## Now we just do the reverse
    reply_len = int.from_bytes(s.recv(4), byteorder='big')
    reply_header = s.recv(reply_len).decode('utf-8')
    print(reply_header)
    reply_header = ET.fromstring(reply_header)

    ## In some newer versions of the auth framework, 
    # this is just sent as a raw JSON object with a prelude. 
    # Tip of main wraps it in a base64-encoded bytes buf, which means this message still 
    # complies with the "official" iRODS protocol
    reply_body = s.recv(int(reply_header.find('msgLen').text)).decode("utf-8")
    print(reply_body)

    auth_ctx = {"a_ttl":"0",
                "force_password_prompt":"true",
                "next_operation":"auth_agent_auth_request",
                "scheme":"native",
                "user_name":"rods",
                "zone_name":"tempZone"}
    auth_ctx = json.dumps(auth_ctx).encode("utf-8")
    auth_ctx = base64.b64encode(auth_ctx)

    msg = f""" 
    <BinBytesBuf_PI>
        <buflen>{len(auth_ctx)}</buflen>
        <buf>{auth_ctx.decode('utf-8')}</buf>
    </BinBytesBuf_PI>
    """.replace(" ", "").replace("\n", "").encode("utf-8") 
    
    header = f""" 
    <MsgHeader_PI>
            <type>RODS_API_REQ</type>
            <msgLen>{len(msg)}</msgLen>
            <errorLen>0</errorLen>
            <bsLen>0</bsLen>
            <intInfo>110000</intInfo>
    </MsgHeader_PI>
    """.replace(' ', '').replace('\n', '').encode("utf-8")

    s.send(len(header).to_bytes(4, byteorder='big'))
    s.send(header)
    s.send(msg)

    reply_len = int.from_bytes(s.recv(4), byteorder='big')
    reply_header = s.recv(reply_len).decode('utf-8')
    print("HEADER")
    print(reply_header)
    reply_header = ET.fromstring(reply_header)

    reply_body = s.recv(
                int(reply_header.find('msgLen').text)
            ).decode("utf-8")
    reply_body = ET.fromstring(reply_body)
    buf = reply_body.find("buf").text
    buf = base64.b64decode(buf).decode("utf-8")
    buf = json.loads(buf[:-1]) ## There's a weird null(?) byte at the end

    ## Guessing this behavior based on PRC
    m = hashlib.md5()
    m.update(buf["request_result"].encode("utf-8"))
    pw = struct.pack("%ds" % MAX_PASSWORD_LENGTH, "rods".encode("utf-8").strip())
    m.update(pw)
    digest = m.digest()
    buf["digest"] = base64.b64encode(digest).decode("utf-8")
    ## The context has moved on to the next stage in the handshake
    buf["next_operation"] = "auth_agent_auth_response"
    buf = json.dumps(buf).encode("utf-8")
    buf = base64.b64encode(buf)

    msg = f""" 
    <BinBytesBuf_PI>
        <buf>{buf.decode('utf-8')}</buf>
        <buflen>{len(buf)}</buflen>
    </BinBytesBuf_PI>
    """.replace(" ", "").replace("\n", "").encode("utf-8") 
    print(msg)

    header = f""" 
    <MsgHeader_PI>
            <type>RODS_API_REQ</type>
            <msgLen>{len(msg)}</msgLen>
            <errorLen>0</errorLen>
            <bsLen>0</bsLen>
            <intInfo>110000</intInfo>
    </MsgHeader_PI>
    """.replace(' ', '').replace('\n', '').encode("utf-8")

    s.send(len(header).to_bytes(4, byteorder='big'))
    s.send(header)
    s.send(msg)

    reply_len = int.from_bytes(s.recv(4), byteorder='big')
    reply_header = s.recv(reply_len).decode('utf-8')
    print("HEADER")
    print(reply_header)
