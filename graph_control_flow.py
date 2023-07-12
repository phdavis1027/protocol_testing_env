## Std imports
import sys
import argparse
import re
import xml.etree.ElementTree as ET
import itertools
from os import path

## NetworkX imports
import networkx as nx

def parse_args():
    parser = argparse.ArgumentParser(
            description="iRODS protocol control flower parser",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
            )
    
    parser.add_argument('src',
                        help='Filepath of ngrep output',
                        metavar='FILE'
                        )

    return parser.parse_args()

def parse_file_into_ngrep_stream(filename):
    ngrep_delimiter_regex = r"#+\nT.*->.*\[AP\].*" 
    f = open(filename, 'r')
    content = ''.join(f.readlines()[2:])
    f.close()

    return re.split(ngrep_delimiter_regex, content)

def remove_preludes_and_clean_stream(ngrep_stream):
    def criterion(tok):
        prelude_regex = "\n\.{4}\n"
        return not re.match(prelude_regex, tok)

    def transform(tok):
        return tok.rstrip("#").rstrip()

    return list(map(transform, 
        filter(criterion, ngrep_stream)))

def parse_xml(irods_msg_stream):
    def transform(tok):
        try: 
            return ET.fromstring(tok)
        except:
            return None # For now we'll only examine XML elements, that is, we ignore preludes and byte/error streams
    return list(filter(lambda tok: tok is not None, list(map(transform, irods_msg_stream))[1:]))

def create_input_stream(args):
    ngrep_stream = parse_file_into_ngrep_stream(args.src) 
    irods_msg_stream = remove_preludes_and_clean_stream(ngrep_stream)
    xml_stream = parse_xml(irods_msg_stream)
    return xml_stream

## Stolen from itertools docs
def window(seq, n=2):
    it = iter(seq)
    result = tuple(itertools.islice(it, n))
    if len(result) == n:
        yield result    
    for elem in it:
        result = result[1:] + (elem,)
        yield result

# On the one hand, including headers makes the whole thing somewhat 
# confusing to look at since most things wind up alternating between different headers, 
# but on the other hand there are some cases where the choice to send a header is 
# especially significant, e.g., in the case of a successful file transfer vs.
# whatever error message the server might send back.
def construct_graph(stream, include_headers=True):
    g = nx.DiGraph()
    for src, dst in window(stream):
        print(src, "->", dst)
        src, dst = [src.tag, dst.tag]
        if not include_headers:
            pass ## Do something else here
        if not g.has_edge(src, dst):
            g.add_edge(src, dst, weight=1)
        else:
            g[src][dst]['weight'] += 1
    return g

def main():
    stream = create_input_stream(parse_args())
    g = construct_graph(stream)

    widths = [g[src][dst]['weight']*.1 for src, dst in g.edges()]
    pos = nx.spring_layout(g)

    nx.draw_networkx_edges(g, pos, alpha=.3, width=widths, edge_color='m')
    nx.draw_networkx_nodes(g, pos, alpha=.9)
    nx.draw_networkx_labels(g, pos, font_size=5)
    
    with open(path.abspath("./Phonetic-Cubes/public/json/graph.json"), "w+") as f:
        f.write(nx.jit_data(g))

if __name__ == "__main__":
    main()
