import pytest
import requests
from iss_tracker import epochs, specific_epoch, instantaneous_speed, nearest_epoch, comment, header, metadata, location, calculate_location 

def test_epochs():
    response = requests.get('http://127.114.37.110:5000/epochs')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_specific_epoch():
    response = requests.get('http://127.114.37.110:5000/epochs')
    a_representative_epoch = response.json()[0]
    response = requests.get(f'http://127.114.37.110:5000/epochs/{a_representative_epoch}')
    assert response.status_code == 200

def test_instantaneous_speed():
    response = requests.get('http://127.114.37.110:5000/epochs')
    a_representative_epoch = response.json()[0]
    response = requests.get(f'http://127.114.37.110:5000/epochs/{a_representative_epoch}/speed')
    assert response.status_code == 200
    assert isinstance(response.text, str)

def test_nearest_epoch():
    response = requests.get('http://127.114.37.110:5000/now')
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_comment():
    response = requests.get('http://127.114.37.110:5000/comment')
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert 'comments' in response.json()

def test_header():
    response = requests.get('http://127.114.37.110:5000/header')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_metadata():
    response = requests.get('http://127.114.37.110:5000/metadata')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_location():
    response = requests.get('http://127.114.37.110:5000/epochs')
    a_representative_epoch = response.json()[0]
    response = requests.get(f'http://127.114.37.110:5000/epochs/{a_representative_epoch}/location')
    assert response.status_code == 200

def test_calculate_location():
    epoch = '2024-03-08T12:00:00.000Z'
    x = 1000.0
    y = 2000.0
    z = 3000.0

    result = calculate_location(epoch, x, y, z)

    assert isinstance(result, dict)
    assert 'latitude' in result
    assert 'longitude' in result
    assert 'altitude' in result
    assert 'geoposition' in result

    assert isinstance(result['latitude'], float)
    assert isinstance(result['longitude'], float)
    assert isinstance(result['altitude'], float)
    assert isinstance(result['geoposition'], dict) or result['geoposition'] is None
