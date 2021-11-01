
process_search_url_link = "/process/inbox/search"

def test_search_no_user(client):
    response = client.post(process_search_url_link, data=dict(search=""))
    assert response.status_code == 302
    assert response.location == "http://localhost/"


# TODO: Write tests for searching with invalid user credientials
# May have to fix the code for tests to work