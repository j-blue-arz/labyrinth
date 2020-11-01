""" Tests the server root ( / ) """


def test_get_root(client):
    """ Tests GET for /
    expects the 'static' VueJS app to be served.
    More specifically, it checks an OK response and
    includes several checks
    * a status code of 200

    """
    response = client.get('/')
    assert response.status_code == 200
    assert b'<!DOCTYPE html>' in response.get_data()
    assert b'<title>Labyrinth</title>' in response.get_data()
