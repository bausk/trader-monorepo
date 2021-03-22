import asyncio


class MeteredQueue:
    def __init__(self):
        self.metered_queues = []
        self.logger = print
        self.report_every = 5

    def __call__(self, q):
        self.metered_queues.append(q)
        return q

    def report(self):
        self.logger("--- QUEUE REPORT ---")
        for i, q in enumerate(self.metered_queues):
            try:
                size = q.qsize()
                self.logger(
                    f"Queue #{i}: {size} items, empty: {q.empty()}, full: {q.full()}"
                )
            except Exception:
                try:
                    size1 = q.sync_q.qsize()
                    size2 = q.async_q.qsize()
                    self.logger(
                        f"Queue #{i}: {size1}({size2}) items, empty: {q.sync_q.empty()}, full: {q.sync_q.full()}"
                    )
                except Exception:
                    self.logger(f"Queue #{i}: Unknown queue type")

    async def work(self):
        try:
            while True:
                await asyncio.sleep(self.report_every)
                self.report()
        except asyncio.CancelledError:
            pass

    def start(self):
        return asyncio.create_task(self.work())
