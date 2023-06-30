import socket 
import struct
import base64
import json
import hashlib
import pdb
import time
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
    s.sendall(len(header).to_bytes(4, byteorder='big'))
    # Then send the header
    s.sendall(header)
    # Finally message
    s.sendall(msg)
    # If we had an error stack or a raw byte stream, we'd send them here
    # Notice that both errorLen and bsLen in the header are set to 0, so we don't do that

    ## Now we just do the reverse
    reply_len = int.from_bytes(s.recv(4), byteorder='big')
    reply_header = s.recv(reply_len).decode('utf-8')
    reply_header = ET.fromstring(reply_header)

    ## In some newer versions of the auth framework, 
    # this is just sent as a raw JSON object with a prelude. 
    # Tip of main wraps it in a base64-encoded bytes buf, which means this message still 
    # complies with the "official" iRODS protocol
    reply_body = s.recv(int(reply_header.find('msgLen').text)).decode("utf-8")

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

    s.sendall(len(header).to_bytes(4, byteorder='big'))
    s.sendall(header)
    s.sendall(msg)

    reply_len = int.from_bytes(s.recv(4), byteorder='big')
    reply_header = s.recv(reply_len).decode('utf-8')
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
    ## You must pad bc the server has fixed length arrays
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
        <buflen>{len(buf)}</buflen>
        <buf>{buf.decode('utf-8')}</buf>
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

    s.sendall(len(header).to_bytes(4, byteorder='big'))
    s.sendall(header)
    s.sendall(msg)

    ## The fact that the server responds with a bytesbuf 
    ## instead of error code -816000 means that it was happy with us 
    reply_len = int.from_bytes(s.recv(4), byteorder='big')
    reply_header = s.recv(reply_len).decode('utf-8')
    print("REPLY_HEADER")
    print("---")
    print(reply_header)
    print("---")
    reply_header = ET.fromstring(reply_header)
    reply_body = s.recv(int(reply_header.find("msgLen").text))
    print("REPLY_BODY")
    print("---")
    print(reply_body)
    print("---")
    ## A real `ils` would stat the collection first to make sure it's actually there,
    ## but we know it's there because we're smart, so we're gonna skip that.

    msg = f"""
    <GenQueryInp_PI>
        <maxRows>256</maxRows>
        <continueInx>0</continueInx>
        <partialStartIndex>-1</partialStartIndex>
        <options>0</options>
        <KeyValPair_PI>
            <ssLen>1</ssLen>
            <keyWord>zone</keyWord>
            <svalue>tempZone</svalue>
        </KeyValPair_PI>
        <InxIvalPair_PI>
            <iiLen>1</iiLen>
            <inx>506</inx>
            <ivalue>1</ivalue>
        </InxIvalPair_PI>
        <InxValPair_PI>
            <isLen>1</isLen>
            <inx>501</inx>
            <svalue>= &apos;/tempZone/home/rods&apos;</svalue>
        </InxValPair_PI>
    </GenQueryInp_PI>
    """.replace(' ', '').replace('\n', '').encode("utf-8")


    header = f""" 
    <MsgHeader_PI>
            <type>RODS_API_REQ</type>
            <msgLen>{len(msg)}</msgLen>
            <errorLen>0</errorLen>
            <bsLen>0</bsLen>
            <intInfo>702</intInfo>
    </MsgHeader_PI>
    """.replace(' ', '').replace('\n', '').encode("utf-8")

    s.sendall(len(header).to_bytes(4, byteorder='big'))
    s.sendall(header)
    s.sendall(msg)

    reply_len = int.from_bytes(s.recv(4), byteorder="big")
    reply_header = s.recv(reply_len).decode('utf-8')
    print("REPLY_HEADER")
    print("---")
    print(reply_header)
    print("---")
    reply_header = ET.fromstring(reply_header)

    reply_body = s.recv(
                int(reply_header.find('msgLen').text)
            ).decode("utf-8")
    print("REPLY_BODY")
    print("---")
    print(reply_body)
    print("---")
    reply_body = ET.fromstring(reply_body)

