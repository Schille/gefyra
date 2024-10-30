import logging

import kopf


@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
    settings.peering.standalone = True
    settings.posting.level = logging.WARNING
    settings.posting.enabled = False
    settings.persistence.diffbase_storage = kopf.AnnotationsDiffBaseStorage(
        prefix="gefyra.dev",
        key="last-handled-configuration",
    )
    settings.persistence.finalizer = "operator.gefyra.dev/kopf-finalizer"
    settings.watching.server_timeout = 10 * 60
    settings.watching.client_timeout = 5 * 60
