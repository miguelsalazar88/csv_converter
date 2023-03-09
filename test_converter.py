from converter import convert


def test_converter1():
    response1 = convert()
    assert response1['statusCode'] == 200


def test_converter2():
    response2 = convert()
    assert response2['statusCode'] == 200


def tect_converter3():
    response3 = convert()
    assert response3['statusCode'] == 200
