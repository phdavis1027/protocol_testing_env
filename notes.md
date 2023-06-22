# Towards An iRODS Protocol Spec

This document assumes XML encoding at all times

## The absolute basics 

All iRODS Messages have three parts, which are each transmitted as separated TCP packets. In order, these are the prelude, the header, and the body.

The prelude is a sequence of four hexadecimal bytes indicating how many bytes long the header will be. 

The header is always an XML object of type MsgHeader_PI. We outline the fields of MsgHeader_PI here:

- type: Indicates the type of message. One questions work asking is why this is necessary when the message body appears to be self-describing.
- msgLen: Indicates how many bytes long the message body will be.

## The handshake

## Key Abbreviations

PI - Packing Instruction
