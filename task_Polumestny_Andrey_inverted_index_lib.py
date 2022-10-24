"""
module provide utils for work with inverted index
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).parent


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
                relevant_documents = list(set(relevant_documents).intersection(tmp_relevant_documents))
        return relevant_documents

    def dump(self, filepath: str) -> None:
        """save inverted index in file"""
        file = Path(filepath)
        if not file.is_absolute():
            file = BASE_DIR.joinpath(file)
        with open(file, 'w') as f_out:
            json.dump(self.index, f_out)

    @classmethod
    def load(cls, filepath: str) -> InvertedIndex:
        """load inverted index from file"""
        file = Path(filepath)
        if not file.is_absolute():
            file = BASE_DIR.joinpath(file)
        with open(file, 'r') as f_in:
            inverted_index = json.load(f_in)
        inverted_index_instance = InvertedIndex(inverted_index)
        return inverted_index_instance


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
            in_memory_doc[doc_id] = content
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
