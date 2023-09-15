from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class AbstractGefyraConnectionProvider(ABC):
    provider_type = ""

    @abstractmethod
    def installed(self, config: Optional[Dict[Any, Any]] = None) -> bool:
        """
        Check if this Gefyra connection provider is properly installed to the cluster
        """
        raise NotImplementedError

    @abstractmethod
    def install(self, config: Optional[Dict[Any, Any]] = None):
        """
        Install this Gefyra connection provider to the cluster
        """
        raise NotImplementedError

    @abstractmethod
    def uninstall(self, config: Optional[Dict[Any, Any]] = None):
        """
        Uninstall this Gefyra connection provider from the cluster
        """
        raise NotImplementedError

    @abstractmethod
    def ready(self) -> bool:
        """
        Returns True if the connection provider is ready to accept peer connections
        """
        raise NotImplementedError

    @abstractmethod
    def add_peer(self, peer_id: str, parameters: Optional[Dict[Any, Any]] = None):
        """
        Add a new peer to the connection provider
        """
        raise NotImplementedError

    @abstractmethod
    def remove_peer(self, peer_id: str):
        """
        Remove a peer from the connection provider
        """
        raise NotImplementedError

    @abstractmethod
    def get_peer_config(self, peer_id: str) -> Dict[str, str]:
        """
        Returns a dict of configuration values for the peer to be stored in the Peer CRD
        """
        raise NotImplementedError

    @abstractmethod
    def peer_exists(self, peer_id: str) -> bool:
        """
        Returns True if the peer exists, otherwise False
        """
        raise NotImplementedError

    @abstractmethod
    def add_destination(
        self,
        peer_id: str,
        destination_ip: str,
        destination_port: int,
        parameters: Optional[Dict[Any, Any]] = None,
    ) -> str:
        """
        Add a destintation route to this connection provider proxy, returns
        the service URL
        """
        raise NotImplementedError

    @abstractmethod
    def remove_destination(
        self, peer_id: str, destination_ip: str, destination_port: int
    ):
        """
        Remove a destintation route from this connection provider proxy
        """
        raise NotImplementedError

    @abstractmethod
    def destination_exists(
        self, peer_id: str, destination_ip: str, destination_port: int
    ) -> bool:
        """
        Returns True if the destination exists, otherwise False
        """
        raise NotImplementedError

    @abstractmethod
    def get_destination(
        self, peer_id: str, destination_ip: str, destination_port: int
    ) -> str:
        """
        Returns the service URL for the destination
        """
        raise NotImplementedError

    @abstractmethod
    def validate(self, gclient: dict, hints: Dict[Any, Any]):
        """
        Validate the Gefyra client object with this connection provider
        Raises a kopf.AdmissionError if validation fails
        """
        raise NotImplementedError
