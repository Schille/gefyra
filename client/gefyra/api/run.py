import logging
import os

from gefyra.configuration import default_configuration, ClientConfiguration
from .utils import stopwatch
from ..cluster.resources import (
    get_pods_and_containers_for_workload,
    get_pods_and_containers_for_pod_name,
)
from ..local.cargo import probe_wireguard_connection

logger = logging.getLogger(__name__)


def retrieve_pod_and_container(
    env_from: str, namespace: str, config: ClientConfiguration
) -> (str, str):
    container_name = ""
    workload_type, workload_name = env_from.split("/")

    if workload_type not in ["pod", "deployment", "statefulset"]:
        raise RuntimeError(f"Unknown workload type {workload_type}")

    if "/" in workload_name:
        workload_name, container_name = workload_name.split("/")

    if workload_type != "pod":
        pods = get_pods_and_containers_for_workload(
            config, name=workload_name, namespace=namespace, workload_type=workload_type
        )
    else:
        pods = get_pods_and_containers_for_pod_name(
            config=config, name=workload_name, namespace=namespace
        )
    pod_name, containers = pods.popitem()

    if container_name and container_name not in containers:
        raise RuntimeError(
            f"{container_name} was not found for {workload_type}/{workload_name}"
        )

    return pod_name, container_name or containers[0]


@stopwatch
def run(
    image: str,
    name: str = None,
    command: str = None,
    volumes: dict = None,
    ports: dict = None,
    detach: bool = True,
    auto_remove: bool = True,
    namespace: str = "default",
    env: list = None,
    env_from: str = None,
    config=default_configuration,
) -> bool:
    from kubernetes.client import ApiException
    from gefyra.cluster.utils import get_env_from_pod_container
    from gefyra.local.bridge import deploy_app_container
    from ..local.utils import get_processed_paths
    from docker.errors import NotFound, APIError

    dns_search = f"{namespace}.svc.cluster.local"
    try:
        item = "network"
        config.DOCKER.networks.get(config.NETWORK_NAME)
        item = "Cargo"
        config.DOCKER.containers.get(config.CARGO_CONTAINER_NAME)
    except NotFound:
        logger.error(f"Gefyra {item} not found. Please run 'gefyra up' first.")
        return False

    #
    # Confirm the wireguard connection working
    #
    try:
        probe_wireguard_connection(config)
    except Exception as e:
        logger.error(e)
        return False

    volumes = get_processed_paths(os.getcwd(), volumes)
    #
    # 1. get the ENV together a) from a K8s container b) from override
    #
    env_dict = {}
    try:
        if env_from:

            env_from_pod, env_from_container = retrieve_pod_and_container(
                env_from, namespace=namespace, config=config
            )

            raw_env = get_env_from_pod_container(
                config, env_from_pod, namespace, env_from_container
            )
            logger.debug("ENV from pod/container is:\n" + raw_env)
            env_dict = {
                k[0]: k[1]
                for k in [arg.split("=") for arg in raw_env.split("\n")]
                if len(k) > 1
            }
    except ApiException as e:
        logger.error(f"Cannot copy environment from Pod: {e.reason}")
        return False
    if env:
        env_overrides = {
            k[0]: k[1] for k in [arg.split("=") for arg in env] if len(k) > 1
        }
        env_dict.update(env_overrides)

    #
    # 2. deploy the requested container to Gefyra
    #
    try:
        container = deploy_app_container(
            config,
            image,
            name,
            command,
            volumes,
            ports,
            env_dict,
            auto_remove,
            dns_search,
        )
    except APIError as e:
        if e.status_code == 409:
            logger.warning("This container is already deployed and running")
            return True
        else:
            logger.error(e)
            return False

    logger.info(
        f"Container image '{', '.join(container.image.tags)}' started with name '{container.name}' in "
        f"Kubernetes namespace '{namespace}'"
    )
    if detach:
        return True
    else:
        #
        # 3. print out logs if not detached
        #
        logger.debug("Now printing out logs")
        for logline in container.logs(stream=True):
            print(logline)
