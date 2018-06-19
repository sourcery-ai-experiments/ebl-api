import json
import pytest
from bson.objectid import ObjectId

import falcon
from falcon import testing
from falcon_auth import NoneAuthBackend

import mongomock

import dictionary.app
from dictionary.dictionary import MongoDictionary


@pytest.fixture
def mongo_dictionary():
    mongo_dictionary = MongoDictionary(mongomock.MongoClient().dictionary)
    return mongo_dictionary

@pytest.fixture
def client(mongo_dictionary):
    user_loader = lambda: {}
    auth_backend = NoneAuthBackend(user_loader)

    api = dictionary.app.create_app(mongo_dictionary, auth_backend)
    return testing.TestClient(api)

@pytest.fixture
def word(mongo_dictionary):
    word = {
        'lemma': ['part1', 'part2'],
        'homonym':  'I'
    }
    mongo_dictionary.create(word)
    return word

@pytest.fixture
def expected_word(word):
    return {
        '_id': str(word['_id']),
        'lemma': word['lemma'],
        'homonym':  word['homonym']
    }

def test_get_word(client, word, expected_word):
    object_id = str(word['_id'])
    result = client.simulate_get(f'/words/{object_id}')

    assert json.loads(result.content) == expected_word
    assert result.status == falcon.HTTP_OK
    assert result.headers['Access-Control-Allow-Origin'] == '*'

def test_word_not_found(client):
    object_id = str(ObjectId())
    result = client.simulate_get(f'/words/{object_id}')

    assert result.status == falcon.HTTP_NOT_FOUND

def test_word_invalid_id(client):
    object_id = 'invalid object id'
    result = client.simulate_get(f'/words/{object_id}')

    assert result.status == falcon.HTTP_NOT_FOUND

def test_search_word(client, word, expected_word):
    lemma = ' '.join(word['lemma'])
    result = client.simulate_get(f'/words/search/{lemma}')

    assert json.loads(result.content) == [expected_word]
    assert result.status == falcon.HTTP_OK
    assert result.headers['Access-Control-Allow-Origin'] == '*'

def test_cors(client):
    object_id = str(ObjectId())
    headers = {'Access-Control-Request-Method': 'GET'}
    result = client.simulate_options(f'/words/{object_id}', headers=headers)

    assert result.headers['Access-Control-Allow-Methods'] == 'GET'
    assert result.headers['Access-Control-Allow-Origin'] == '*'
    assert result.headers['Access-Control-Max-Age'] == '86400'
