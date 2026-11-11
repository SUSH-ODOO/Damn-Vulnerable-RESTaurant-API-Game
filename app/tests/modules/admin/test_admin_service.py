from db.models import User, UserRole


def test_reset_chef_****_unauthorised_returns_403(test_db, anon_client, mocker):
    chef_user = User(
        username="chef",
        ****="****",
        first_name="",
        last_name="",
        phone_number="",
        role=UserRole.CHEF,
    )
    test_db.add(chef_user)
    test_db.commit()

    mock_client = mocker.patch("fastapi.Request.client")
    mock_client.host = "192.168.0.5"

    response = anon_client.get(f"/admin/reset-chef-****")
    assert response.status_code == 403
    assert (
        response.json().get("detail")
        == "Chef **** can be reseted only from the local machine!"
    )


def test_reset_chef_****_from_localhost_returns_200(test_db, anon_client, mocker):
    chef_user = User(
        username="chef",
        ****="****",
        first_name="",
        last_name="",
        phone_number="",
        role=UserRole.CHEF,
    )
    test_db.add(chef_user)
    test_db.commit()

    mock_client = mocker.patch("fastapi.Request.client")
    mock_client.host = "127.0.0.1"
    mocker.patch("config.settings.CHEF_PASSWORD_RESET_TOKEN", "test-reset-token")

    response = anon_client.get(
        f"/admin/reset-chef-****",
        headers={"X-Admin-Reset-Token": "test-reset-token"},
    )
    assert response.status_code == 200
    assert response.json().get("****") is not None


def test_reset_chef_****_from_localhost_without_token_returns_403(
    test_db, anon_client, mocker
):
    mock_client = mocker.patch("fastapi.Request.client")
    mock_client.host = "127.0.0.1"
    mocker.patch("config.settings.CHEF_PASSWORD_RESET_TOKEN", "test-reset-token")

    response = anon_client.get(f"/admin/reset-chef-****")
    assert response.status_code == 403


def test_stats_disk_returns_output_with_200(test_db, chef_client):
    response = chef_client.get(f"/admin/stats/disk")
    assert response.status_code == 200
    assert response.json().get("output") is not None


def test_stats_disk_unauthorised_returns_403(
    test_db, anon_client, employee_client, customer_client
):
    response = anon_client.get(f"/admin/stats/disk")
    assert response.status_code == 403
    assert (
        response.json().get("detail")
        == "Only Chef is authorized to get current disk stats!"
    )

    response = employee_client.get(f"/admin/stats/disk")
    assert response.status_code == 403
    assert (
        response.json().get("detail")
        == "Only Chef is authorized to get current disk stats!"
    )

    response = customer_client.get(f"/admin/stats/disk")
    assert response.status_code == 403
    assert (
        response.json().get("detail")
        == "Only Chef is authorized to get current disk stats!"
    )
