
## 1. Goals of this Document 
^^^^^^^
||||||| This section is a direct ripoff of the [AMQP spec's](https://www.rabbitmq.com/resources/specs/amqp0-9-1.pdf) identically-titled section.

This document defines the protocol used by clients and servers running iRODS, which is open-source data management software. 
This protocol is application-specific and tightly coupled with the APIs provided by particular clients/servers.
As such, some familiarity with iRODS, as well as basic technical experience, is assumed. Additionally, the description of the 
iRODS protocol provided in this document is not sufficient for a skilled engineer to implement an iRODS server or client 
from scratch. However, this document should allow a skilled engineer to send and interpret messages in the iRODS protocol comfortably
enough to reverse engineer such an implementation, e.g., by observing network traffic in the course of a target iRODS workflow.

## 2. iRODS 

iRODS stands for Integrated, Rule-Oriented Data System. It provides a platform for automated, large-scale, policy-based management of 
data with a focus on data integrity, secure collaboration, workflow automation, metadata-driven data discovery, and virtualization of 
key services. A single iRODS deployment is called a "zone." A single installation of iRODS running on a particular machine is called 
a "node." Note that the term "node" in this usage refers to either a producer or a consumer. See the 
[iRODS documentation](https://docs.irods.org) for more information. 
Although iRODS is a large and complex system, its protocol is minimalistic in the sense that common workloads can be 
achieved using a handful of basic patterns. 

## 3. The iRODS Protocol

Nodes in an iRODS zone communicate using a message-oriented, wire-level protocol. Before describing the capabilities of this protocol,
we will describe the structure of iRODS protocol messages. 


### a. Primitive Types 

The most basic elements in the iRODS protocol are primitive types. The following table describes all primitive types.

| Type   | Description                                                                                                                          |
|--------|--------------------------------------------------------------------------------------------------------------------------------------|
| char   | 8-bit unsigned integer.                                                                                                              |
| bin    | 8-bit binary data. In XML protocol items of type `bin` MUST be base64-encoded.                                                       |
| str    | A null-terminated string of valid UTF-8 chars.                                                                                       |
| piStr  | Syntactically the same as `str` but value must be the name of a valid iRODS protocol type.                                           |
| int    | 32-bit integer or floating point value.                                                                                              |
| double | 64-bit integer or floating point value.                                                                                              |
| struct | A nested packing instruction (see Section b).                                                                                        |
| ?      | Signals a dependent type. Following string must correspond to the name of a `piStr` in the same packing instruction (see Section b). |


### b. Packing Instructions

IRODS protocol messages cannot be composed solely of primitive types. Rather, instances of primitive types must be transmitted
in structured formats called packing instructions. Packing instructions are described using a special syntax described in section (???). 
Each packing instruction maps in a one-to-one fashion to a C struct in the source code of the iRODS server. For example, the following
packing instruction string

```
"KeyValPair_PI kvp; str s; int i;"
```

corresponds to the struct 

```
struct S
{
    keyValPair_t kvp;
    char* s;
    int i;
};
```
 
### c. Native vs. XML encoding

Any packing instruction can be represented in either of two encodings: native and XML. The environment variable `irodsProt` is used by 
iCommands to determine which encoding should be used, with 0 meaning native and 1 meaning XML.

#### i. Native encoding  

This is the original encoding 
