import pytest
from docker.errors import APIError

from gefyra.configuration import default_configuration
from gefyra.local.networking import create_gefyra_network


def test_cycle_gefyra_network():
    config = default_configuration
    gefyra_network = create_gefyra_network(config)
    gefyra_network.remove()


def test_gefyra_network_create_failed(monkeypatch):
    def _raise_apierror_for_docker_network_create(*args, **kwargs):
        raise APIError("Something with pool overlap")

    monkeypatch.setattr(
        "docker.api.network.NetworkApiMixin.create_network",
        _raise_apierror_for_docker_network_create,
    )
    config = default_configuration
    with pytest.raises(APIError):
        create_gefyra_network(config)
