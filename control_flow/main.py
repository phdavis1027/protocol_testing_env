import graphviz

dot = graphviz.Digraph('irods-prot-control-flow', comment="iRODS Protocol Control Flow")

dot.edge("Handshake", "Authentication")
dot.edge("Authentication", "API Request-Response Loop")

dot.render()
