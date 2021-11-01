from flaskr import bullymail
from flaskr.bullymail import BullyMail

url_link = "/compose/"

def test_compose_no_user(client):
    response = client.get(url_link)
    assert response.status_code == 302
    assert response.location == "http://localhost/"


def test_compose_mock_user(client):
    with client.session_transaction() as sess:
        sess["user"] = ["test", "test"]
    assert client.get(url_link).status_code == 200


def test_compose_invalid_user():
    bullymail = BullyMail("test", "test", "test", None)
    assert bullymail.send_message("test", "test", "test", "test", "test", None, None) == False