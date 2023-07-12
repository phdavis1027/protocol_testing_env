
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
we will describe the 
