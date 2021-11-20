# This method tests the majority of our URLs while there is not a user in the session.
def test_URLs_outsession(client):

    response = client.get("/auth/login/")
    result = response.status_code
    assert result == 200

    response = client.get("/auth/logout/")
    result = response.status_code
    assert result == 302

    response = client.get("/inbox/")
    result = response.status_code
    assert result == 302

    response = client.get("/drafts/")
    result = response.status_code
    assert result == 302

    response = client.get("/process/inbox/fetch")
    result = response.status_code
    assert result == 405

    response = client.get("/process/drafts/fetch")
    result = response.status_code
    assert result == 405

    response = client.get("/process/inbox/search")
    result = response.status_code
    assert result == 405

    response = client.get("/process/drafts/search")
    result = response.status_code
    assert result == 405

    response = client.get("/process/inbox/message")
    result = response.status_code
    assert result == 405

    response = client.get("/process/draft/message")
    result = response.status_code
    assert result == 405

    response = client.get("/compose/")
    result = response.status_code
    assert result == 302

    response = client.get("/drafts/save")
    result = response.status_code
    assert result == 302

    response = client.get("/compose/draft")
    result = response.status_code
    assert result == 302


# This method tests the majority of our URLs while there is a user in the session.
def test_URLs_insession(client):

    with client.session_transaction() as sess:
        sess["user"] = ["test", "test"]

    response = client.get("/auth/login/")
    result = response.status_code
    assert result == 302

    with client.session_transaction() as sess:
        sess["user"] = ["test", "test"]

    response = client.get("/auth/logout/")
    result = response.status_code
    assert result == 302

    with client.session_transaction() as sess:
        sess["user"] = ["test", "test"]

    response = client.get("/inbox/")
    result = response.status_code
    assert result == 200

    with client.session_transaction() as sess:
        sess["user"] = ["test", "test"]

    response = client.get("/drafts/")
    result = response.status_code
    assert result == 200

    with client.session_transaction() as sess:
        sess["user"] = ["test", "test"]

    response = client.get("/process/inbox/fetch")
    result = response.status_code
    assert result == 405

    with client.session_transaction() as sess:
        sess["user"] = ["test", "test"]

    response = client.get("/process/drafts/fetch")
    result = response.status_code
    assert result == 405

    with client.session_transaction() as sess:
        sess["user"] = ["test", "test"]

    response = client.get("/process/inbox/search")
    result = response.status_code
    assert result == 405

    with client.session_transaction() as sess:
        sess["user"] = ["test", "test"]

    response = client.get("/process/drafts/search")
    result = response.status_code
    assert result == 405

    with client.session_transaction() as sess:
        sess["user"] = ["test", "test"]

    response = client.get("/process/inbox/message")
    result = response.status_code
    assert result == 405

    with client.session_transaction() as sess:
        sess["user"] = ["test", "test"]

    response = client.get("/process/draft/message")
    result = response.status_code
    assert result == 405

    with client.session_transaction() as sess:
        sess["user"] = ["test", "test"]

    response = client.get("/compose/")
    result = response.status_code
    assert result == 200

    with client.session_transaction() as sess:
        sess["user"] = ["test", "test"]

    response = client.get("/drafts/save")
    result = response.status_code
    assert result == 200

    with client.session_transaction() as sess:
        sess["user"] = ["test", "test"]

    response = client.get("/compose/draft")
    result = response.status_code
    assert result == 200
