import pytest

from gefyra.__main__ import run_parser, bridge_parser


def test_ip_port_mapper(caplog):
    caplog.set_level("DEBUG")
    args = run_parser.parse_args(
        [
            "--expose=localhost:8080:8080",
            "--expose=127.0.0.1:9090:1234",
            "--expose=7071:7070",
            "-i=1",
            "-N=test",
        ]
    )
    assert "1234" in args.expose
    assert "8080" in args.expose
    assert "7070" in args.expose
    assert args.expose["1234"] == ("127.0.0.1", "9090")
    assert args.expose["8080"] == ("localhost", "8080")
    assert args.expose["7070"] == "7071"

    with pytest.raises(SystemExit):
        run_parser.parse_args(
            [
                "--expose=localhost:abc:8080",
            ]
        )
    assert "Invalid port" in caplog.text
    caplog.clear()

    with pytest.raises(SystemExit):
        run_parser.parse_args(
            [
                "--expose=localhost:8080:8080:too-many",
            ]
        )
    assert "Invalid port" in caplog.text


def test_port_mapper(caplog):
    caplog.set_level("DEBUG")
    args = bridge_parser.parse_args(
        ["--port=8081:8080", "--port=9091:9090", "-N=random"]
    )
    assert "9090" in args.port
    assert "8080" in args.port
    assert args.port["9090"] == "9091"
    assert args.port["8080"] == "8081"

    with pytest.raises(SystemExit):
        bridge_parser.parse_args(["--port=8081", "--port=9091:9090", "-N=random"])
    assert "Invalid port" in caplog.text
