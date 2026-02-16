from __future__ import annotations

from typing import Any

from nestipy.common.logger import logger
from nestipy.ioc import NestipyContainer


class LifecycleRunner:
    """Handle application startup/shutdown hooks and resource cleanup."""
    def __init__(self, background_tasks: Any, instance_loader: Any) -> None:
        self._background_tasks = background_tasks
        self._instance_loader = instance_loader

    async def startup(self) -> None:
        self._background_tasks.run()

    async def shutdown(self) -> None:
        await self._background_tasks.shutdown()
        try:
            from nestipy.microservice.client.base import ClientProxy

            container = NestipyContainer.get_instance()
            for instance in container.get_all_singleton_instance():
                if isinstance(instance, ClientProxy):
                    await instance.before_close()
                    await instance.close()
        except Exception as e:
            logger.error("Error while closing microservice clients: %s", e)
        await self._instance_loader.destroy()


__all__ = ["LifecycleRunner"]
