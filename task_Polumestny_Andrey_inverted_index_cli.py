"""
module provide utils for work with inverted index
"""
from __future__ import annotations

import argparse
import json
import re
from struct import pack, unpack, calcsize
import sys
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).parent.resolve()


class InvertedIndex:
    """class represented inverted index"""

    def __init__(self, inverted_index: Dict[str, list[str]]):
        self.index = inverted_index

    def __eq__(self, other: InvertedIndex):
        return self.index == other.index

    def __str__(self):
        return str(self.index)

    def query(self, words: List[str]) -> List[int]:
        """Return the list of relevant documents for the given query"""
        relevant_documents = []
        for word in words:
            documents = self.index.get(word, None)
            if not documents:
                return []
            tmp_relevant_documents = [int(document) for document in documents]
            if not relevant_documents:
                relevant_documents = tmp_relevant_documents[:]
            else:
                relevant_documents = list(
                    set(relevant_documents).intersection(
                        tmp_relevant_documents))
        return relevant_documents

    def dump(self, filepath: str, method='struct') -> None:
        """save inverted index in file"""
        file = Path(filepath)
        if not file.is_absolute():
            file = BASE_DIR.joinpath(file)
        if method == 'json':
            self.json_dump(file)
        else:
            self.struct_dump(file)

    def json_dump(self, file: str) -> None:
        """save inverted index in file with json algorithm"""
        with open(file, 'w') as f_out:
            json.dump(self.index, f_out)

    def struct_dump(self, file:str) -> None:
        """save inverted index if file with struct algorithm"""
        pairs = {}
        documents_id = []
        with open(file, 'wb') as f_out:
            for word, documents in self.index.items():
                pairs[word] = len(documents)
                for doc_id in documents:
                    documents_id.append(doc_id)
            header = json.dumps(pairs).encode('utf8')
            # header = json.dumps(pairs).encode('utf8')
            print(f'{header=}', file=sys.stderr)
            meta = len(header)
            print(f'{meta=}', file=sys.stderr)
            print(f'{type(meta)=}', file=sys.stderr)
            print(f'{documents_id=}', file=sys.stderr)
            f_out.write(pack('I', meta))
            f_out.write(pack(f'{meta}s', header))
            f_out.write(pack('H', ))
            # f_out.write(pack('H', bytes(str(documents_id), encoding='utf8')))
            # f_out.write(pack('IPs', meta, header, bytes(str(documents_id), encoding='utf8')))
            # f_out.write(pack('Iss', meta, header, str(documents_id)))

    @classmethod
    def load(cls, filepath: str, strategy='struct') -> InvertedIndex:
        """load inverted index from file"""
        file = Path(filepath)
        if not file.is_absolute():
            file = BASE_DIR.joinpath(file)
        if strategy == 'json':
            cls.load_from_json(file)
        else:
            cls.load_from_binary(file)

    @classmethod
    def load_from_json(cls, file):
        with open(file, 'r') as f_in:
            inverted_index = json.load(f_in)
            print(inverted_index, file=sys.stderr)
        inverted_index_instance = InvertedIndex(inverted_index)
        return inverted_index_instance

    @classmethod
    def load_from_binary(cls, file):
        with open(file, 'rb') as f_in:
            data = f_in.read()
            print(data)
            unsigned_index = calcsize('I')
            meta, = unpack('I', data[:4])
            print(meta)
            print(sys.getsizeof(data[4:4+meta]))
            header, = unpack(f'{meta}s', data[4:4+meta])
            print(header)
            # print(f'{meta=}', file=sys.stderr)
            # print(f'{header=}', file=sys.stderr)
            # print(f'{documents_id=}', file=sys.stderr)


def load_documents(filepath: str) -> Dict[int, str]:
    """read file and load it to memory"""
    file = Path(filepath)
    if not file.is_absolute():
        file = BASE_DIR.joinpath(file)

    if not file.exists():
        raise FileNotFoundError
    in_memory_doc = {}
    with open(file, 'r') as f_in:
        for line in f_in:
            doc_id, content = line.lower().split("\t", 1)
            doc_id = int(doc_id)
            in_memory_doc[doc_id] = content.strip()
    return in_memory_doc


def build_inverted_index(documents: Dict[int, str]) -> InvertedIndex:
    """build inverted index from a document"""
    inv_index = {}
    for key, value in documents.items():
        for word in re.split(r"\W+", value):
            if word not in inv_index:
                inv_index[word] = [key]
            elif word in inv_index and key not in inv_index[word]:
                inv_index[word].append(key)
    inv_index_instance = InvertedIndex(inv_index)
    return inv_index_instance


def cli():
    parser = argparse.ArgumentParser(
        description='Inverted Index CLI',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparser = parser.add_subparsers(help='list of allowed commands')

    build_parser = subparser.add_parser(
        'build',
        help='build inverted index',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    build_parser.add_argument(
        '--strategy', choices=('json', 'struct'),
        default='struct',
        help='strategy to store inverted index'
    )
    build_parser.add_argument(
        '--dataset',
        required=True,
        help='path to dataset'
    )
    build_parser.add_argument(
        '--output',
        required=True,
        help='path to inverted index dump'
    )
    build_parser.set_defaults(callback=build_callback)

    query_parser = subparser.add_parser(
        'query',
        help='retrieve documents from inverted index',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    query_file_group = query_parser.add_mutually_exclusive_group(required=True)
    query_file_group.add_argument('--query-file-utf8', dest='query_file', type=argparse.FileType('r', encoding='utf-8'))
    query_file_group.add_argument('--query-file-cp1251', dest='query_file', type=argparse.FileType('r', encoding='cp1251'))
    query_file_group.add_argument('--query', dest='query', nargs='*', action='append')
    query_parser.add_argument(
        '--json-index',
        dest='inverted_index_path',
        required=True,
    )
    query_parser.set_defaults(callback=query_callback)

    return parser.parse_args()


def build_callback(arguments):
    build(arguments.dataset, arguments.output)


def build(dataset_filepath, output_filepath):
    documents = load_documents(dataset_filepath)
    inverted_index_instance = build_inverted_index(documents)
    inverted_index_instance.dump(output_filepath)
    print(f'build completed in {output_filepath}', file=sys.stderr)


def query_callback(arguments):
    print(arguments, file=sys.stderr)
    if arguments.query_file:
        query_from_file(arguments.inverted_index_path, arguments.query_file)
    else:
        query_from_list(arguments.inverted_index_path, arguments.query)
    print('query completed successfully', file=sys.stderr)


def query_from_file(inverted_index_path, query_file):
    inverted_index = InvertedIndex.load(inverted_index_path)
    for words in query_file:
        print(words, file=sys.stderr)
        documents = inverted_index.query(words.split(' '))
        if documents:
            print(','.join([str(doc_id) for doc_id in documents]))
        else:
            print()


def query_from_list(inverted_index_path, query):
    inverted_index = InvertedIndex.load(inverted_index_path)
    for words in query:
        documents = inverted_index.query(words)
        if documents:
            print(','.join([str(doc_id) for doc_id in documents]))
        else:
            print()



def main(arg=None):
    args = cli()
    args.callback(args)


if __name__ == '__main__':
    main()
