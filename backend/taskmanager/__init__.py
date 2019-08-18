import asyncio


class DataManager:
    def __init__(self):
        self.tasks = []
        self._data = {
            'kunaio': None,
        }

    async def start_background_tasks(self, app):
        pass

    async def cleanup_background_tasks(self, app):
        pass

    def setup_tasks(self, app):
        app.on_startup.append(self.start_background_tasks)
        app.on_cleanup.append(self.cleanup_background_tasks)
