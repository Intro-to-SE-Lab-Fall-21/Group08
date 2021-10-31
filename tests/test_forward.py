
def test_forward_no_user(client):
    response = client.get("/forward/0")
    assert response.status_code == 302
    assert response.location == "http://localhost/"

# TODO: Write tests for forwarding with invalid user credientials
# May have to fix the code for tests to work