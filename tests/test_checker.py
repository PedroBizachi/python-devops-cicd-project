import pytest
import requests
from pytest_mock import MockFixture

from simple_http_checker.checker import check_urls


def test_check_urls_success(mocker: MockFixture):
    mock_requests_get = mocker.patch("simple_http_checker.checker.requests.get")

    mock_response = mocker.MagicMock(spec=requests.Response)
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.reason = "OK"
    mock_requests_get.return_value = mock_response

    urls = ["https://example.com"]
    results = check_urls(urls)

    mock_requests_get.assert_called_once_with(urls[0], timeout=5)
    assert results[urls[0]] == "200 OK"


def test_check_urls_client_error(mocker: MockFixture):
    mock_resquests_get = mocker.patch("simple_http_checker.checker.requests.get")

    mock_response = mocker.MagicMock(spec=requests.Response)
    mock_response.ok = False
    mock_response.status_code = 404
    mock_response.reason = "NOT FOUND"
    mock_resquests_get.return_value = mock_response

    urls = ["https://example.com/non-existent"]
    results = check_urls(urls)

    mock_resquests_get.assert_called_once_with(urls[0], timeout=5)
    assert results[urls[0]] == "404 NOT FOUND"


@pytest.mark.parametrize(
    "error_exception, expected_status",
    [
        (requests.exceptions.Timeout, "TIMEOUT"),
        (requests.exceptions.ConnectionError, "CONNECTION_ERROR"),
        (requests.exceptions.RequestException, "REQUEST_ERROR: RequestException"),
    ],
)
def test_check_urls_response_exceptions(
    mocker: MockFixture,
    error_exception: type[requests.exceptions.RequestException],
    expected_status: str,
):
    mock_resquests_get = mocker.patch("simple_http_checker.checker.requests.get")
    mock_resquests_get.side_effect = error_exception(f"Simulated {expected_status}")

    urls = ["https://problem.com"]
    results = check_urls(urls)

    mock_resquests_get.assert_called_once_with(urls[0], timeout=5)
    assert results[urls[0]] == expected_status


def test_check_urls_with_multiple_urls(mocker: MockFixture):
    mock_requests_get = mocker.patch("simple_http_checker.checker.requests.get")

    # First call: OK
    mock_response_ok = mocker.MagicMock(spec=requests.Response)
    mock_response_ok.ok = True
    mock_response_ok.status_code = 200
    mock_response_ok.reason = "OK"

    # Second call: Timeout
    timeout_exception = requests.exceptions.Timeout("Simulated TIMEOUT")

    # Third call: 500 Server Error
    mock_response_fail = mocker.MagicMock(spec=requests.Response)
    mock_response_fail.ok = False
    mock_response_fail.status_code = 500
    mock_response_fail.reason = "SERVER ERROR"

    mock_requests_get.side_effect = [
        mock_response_ok,
        timeout_exception,
        mock_response_fail,
    ]

    urls = ["https://success.com", "https://timeout.com", "https://servererror.com"]
    results = check_urls(urls)

    assert len(results) == 3
    assert mock_requests_get.call_count == 3
    assert results["https://success.com"] == "200 OK"
    assert results["https://timeout.com"] == "TIMEOUT"
    assert results["https://servererror.com"] == "500 SERVER ERROR"


def test_check_urls_empty_list():
    results = check_urls([])
    assert results == {}


def test_check_urls_custom_timeout(mocker: MockFixture):
    mock_resquests_get = mocker.patch("simple_http_checker.checker.requests.get")

    mock_response = mocker.MagicMock(spec=requests.Response)
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.reason = "OK"
    mock_resquests_get.return_value = mock_response

    urls = ["https://example.com"]
    custom_timeout = 10
    results = check_urls(urls, timeout=custom_timeout)

    mock_resquests_get.assert_called_once_with(urls[0], timeout=custom_timeout)

    assert results[urls[0]] == "200 OK"
