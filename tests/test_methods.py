from flaskr.bullymail import *
import pytest
import os



# USER *

# Testing valid password with bad user
@pytest.mark.parametrize("sender", ["400testss@gmail.com", "childer", None, 1])
def test_validate_badusername(sender):
    PASS_KEY = os.environ['PASS_KEY']

    # Pass in a valid password but bad username
    userObj = User(sender, PASS_KEY)
    result = userObj.validate()

    assert result is None

# Testing valid user with invalid passwords
@pytest.mark.parametrize("password", ["12345", "qwerty", None])
def test_validate_badpassword(password):
    USER_KEY = os.environ['USER_KEY']

    # Pass in a valid username but bad password
    userObj = User(USER_KEY, password)
    result = userObj.validate()

    assert result is None

# Test the validate function
def test_validate():
    USER_KEY = os.environ['USER_KEY']
    PASS_KEY = os.environ['PASS_KEY']

    # Pass in a valid login
    userObj = User(USER_KEY, PASS_KEY)
    result = userObj.validate()

    assert result is None

def test_search_no_user(client):
    process_search_url_link = "/process/inbox/search"
    response = client.post(process_search_url_link, data=dict(search=""))

    assert response.status_code == 302
    assert response.location == "http://localhost/"


# TODO: Write tests for searching with invalid user credientials
# May have to fix the code for tests to work


def test_forward_no_user(client):
    response = client.get("/forward/0")
    assert response.status_code == 302
    assert response.location == "http://localhost/"

# TODO: Write tests for forwarding with invalid user credientials
# May have to fix the code for tests to work
