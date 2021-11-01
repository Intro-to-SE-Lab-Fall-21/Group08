
def test_login(client):
    assert client.get("/auth/login/").status_code == 200


def test_logout(client):
    assert client.get("/auth/logout/", follow_redirects=True).status_code == 200