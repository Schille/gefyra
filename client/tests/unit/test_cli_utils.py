import os
from unittest import TestCase
import pytest
from unittest.mock import patch

import yaml

from gefyra.local.utils import get_connection_from_kubeconfig, get_processed_paths
from gefyra.api.utils import generate_env_dict_from_strings, get_workload_type
from gefyra.cli.utils import parse_env, parse_ip_port_map, parse_workload


@patch("kubernetes.config.kube_config.KUBE_CONFIG_DEFAULT_LOCATION", "/tmp/kube.yaml")
def test_a_get_connection_from_kubeconfig_no_connection():
    endpoint = get_connection_from_kubeconfig()
    assert endpoint is None


@patch("kubernetes.config.kube_config.KUBE_CONFIG_DEFAULT_LOCATION", "/tmp/kube.yaml")
def test_b_get_connection_from_kubeconfig_connection():
    data = {
        "current-context": "fake",
        "contexts": [
            {
                "name": "fake",
                "gefyra": "127.0.0.1:8090",
            },
        ],
    }
    f = open("/tmp/kube.yaml", "w")
    yaml.dump(data, f)
    f.close()
    try:
        endpoint = get_connection_from_kubeconfig()
        assert endpoint == "127.0.0.1:8090"
    except AssertionError:
        os.remove(f.name)
        raise
    else:
        os.remove(f.name)


@patch("kubernetes.config.kube_config.KUBE_CONFIG_DEFAULT_LOCATION", "/tmp/kube1.yaml")
def test_get_connection_from_kubeconfig_no_file():
    endpoint = get_connection_from_kubeconfig()
    assert endpoint is None


def test_workload_type_util():
    assert get_workload_type("po") == "pod"
    assert get_workload_type("pod") == "pod"
    assert get_workload_type("pods") == "pod"

    assert get_workload_type("deploy") == "deployment"
    assert get_workload_type("deployment") == "deployment"
    assert get_workload_type("deployments") == "deployment"

    assert get_workload_type("sts") == "statefulset"
    assert get_workload_type("statefulset") == "statefulset"
    assert get_workload_type("statefulsets") == "statefulset"

    with pytest.raises(RuntimeError) as rte:
        get_workload_type("fake")

    assert "Unknown workload type fake" in str(rte.value)


def test_path_cleaning_for_window():
    # It's a bit weird since the test is executed on a Linux machine.
    # That's why we have to use the os.getcwd() function.
    volumes = [
        "C:\\Users\\user\\Documents\\gefyra\\:/app",
    ]
    res = get_processed_paths(os.getcwd(), volumes)
    assert res == [
        os.getcwd() + "/C:\\Users\\user\\Documents\\gefyra\\:/app",
    ]


def test_env_dict_creation():
    env_vars = [
        "APP=test-app",
        "TEST=tautology=tautology=tautology",
        "123NUM=blubb",
        "VERSION=1.2.3",
    ]

    res = generate_env_dict_from_strings(env_vars=env_vars)
    TestCase().assertDictEqual(
        {
            "APP": "test-app",
            "TEST": "tautology=tautology=tautology",
            "123NUM": "blubb",
            "VERSION": "1.2.3",
        },
        res,
    )


def test_env_parsing():
    try:
        parse_env(None, None, ("APP",))
    except Exception as e:
        assert "use 'ENV=value'" in str(e)

    res = parse_env(None, None, ("APP=test-app",))
    TestCase().assertListEqual(res, ["APP=test-app"])


def test_workload_parsing():
    res = parse_workload(None, None, "pod/test")
    assert res == "pod/test"

    try:
        res = parse_workload(None, None, "pod")
    except Exception as e:
        assert "Invalid workload format" in str(e)


def test_ip_port_map_parsing():
    # single
    res = parse_ip_port_map(None, None, ("1234:1234",))
    TestCase().assertDictEqual(res, {"1234": "1234"})

    # multiple
    res = parse_ip_port_map(None, None, ("1234:1234", "9000:9000"))
    TestCase().assertDictEqual(res, {"1234": "1234", "9000": "9000"})

    # incl. ip
    res = parse_ip_port_map(None, None, ("127.0.0.1:1234:1234",))
    TestCase().assertDictEqual(res, {"1234": ("127.0.0.1", "1234")})

    # string
    try:
        res = parse_ip_port_map(None, None, ("1234:blah",))
    except Exception as e:
        assert "use integer" in str(e)

    # invalid format
    try:
        res = parse_ip_port_map(None, None, ("1234:1234:1234:1234",))
    except Exception as e:
        assert "Invalid value" in str(e)
