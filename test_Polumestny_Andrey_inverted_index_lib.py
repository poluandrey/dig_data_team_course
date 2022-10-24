"""
test for inverted_index module
"""
from textwrap import dedent

import pytest

import task_Polumestny_Andrey_inverted_index_lib as inverted_index


@pytest.fixture(ids='small_dataset')
def small_doc(tmpdir):
    """
    fixture load in memory small document
    """
    data = dedent("""\
    12	Anarchism         Anarchism is often defined as topic test
    25	Test             Another topic 
    """)
    small_dataset = tmpdir.join('small_dataset')
    small_dataset.write(data)
    documents = inverted_index.load_documents(small_dataset)
    return documents


@pytest.fixture(ids='small_inverted_index')
def small_inverted_index(small_doc):
    """
    build inverted index base on small_doc fixture
    """
    small_inverted_index = inverted_index.build_inverted_index(small_doc)
    return small_inverted_index


def test_load_non_existing_documents():
    """
    test raising exception when load not existing document
    """
    with pytest.raises(FileNotFoundError):
        inverted_index.load_documents('datasets/some_file.txt')


def test_load_doc():
    """
    test load_document function
    """
    file_dump = inverted_index.load_documents('datasets/small_dataset')
    err_msg = (f'loaded file should be a dict instance'
               f' instead of {type(file_dump)}')
    assert isinstance(file_dump, dict), err_msg


def test_build_inverted_index_return(small_doc):
    inv_index = inverted_index.build_inverted_index(small_doc)
    err_msg = (f'build_inverted_index should return InvertedIndex,'
               f' instead of {type(inv_index)}')
    assert isinstance(inv_index, inverted_index.InvertedIndex), err_msg


def test_build_inverted_index_for_same_doc_equal(small_doc):
    """
    test __eq__ method of InvertedIndex
    """
    inv_index_1 = inverted_index.build_inverted_index(small_doc)
    inv_index_2 = inverted_index.build_inverted_index(small_doc)
    err_msg = 'same documents return different inverted index'
    assert inv_index_1 == inv_index_2, err_msg


def test_load_doc_count_of_topic():
    """
    test cont of topic in inmemory doc
    """
    expected_count = 2
    file_dump = inverted_index.load_documents('datasets/small_dataset')
    topic_count = len(file_dump)
    err_msg = f'topic count is {topic_count} instead of {expected_count}'
    assert expected_count == topic_count, err_msg


@pytest.mark.parametrize(
    'words, answer',
    [
        pytest.param(['anarchism'], [12], id='one_document_matching'),
        pytest.param(['topic'], [12, 25], id='two_document_matching'),
        pytest.param(['topic', 'test'], [25, 12], id='list_of_words_in_two_document_matching'),
        pytest.param(['topic', 'something'], [], id='list_of_words_in_two_document_not_found'),
        pytest.param(['None'], [], id='not_found_document'),
    ]
)
def test_query_inverted_index(small_inverted_index, words, answer):
    """
    test InvertedIndex query method
    """
    documents = small_inverted_index.query(words)
    err_msg = f'wrong documents found, expected {answer}, got {documents}'
    assert documents == answer, err_msg


def test_dump_inverted_index(small_inverted_index, tmpdir):
    """
    test InvertedIndex dump method
    """
    file = tmpdir.join('inverted_index_dump.json')
    small_inverted_index.dump(file)

    assert file.exists(), 'file did not create'
    assert file.size() > 0, 'empty file created'


def test_inverted_index_load(small_inverted_index):
    """
    test InvertedIndex load method
    """
    document = inverted_index.load_documents('datasets/small_dataset')
    inv_index = inverted_index.build_inverted_index(document)
    inv_index.dump('datasets/small_dataset.json')
    loaded_inv_index = inv_index.load('datasets/small_dataset.json')

    err_msg = 'loaded inverted index not equal with expected'
    assert inv_index == loaded_inv_index, err_msg
