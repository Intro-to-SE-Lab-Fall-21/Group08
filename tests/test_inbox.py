
url_link = "/inbox/"

def test_inbox_no_user(client):
    response = client.get(url_link)
    assert response.status_code == 302
    assert response.location == "http://localhost/"


def test_inbox_mock_user(client):
    with client.session_transaction() as sess:
        sess["user"] = ["test", "test"]
    assert client.get(url_link).status_code == 200