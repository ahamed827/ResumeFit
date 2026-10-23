import asyncio

from app.core.logging import logger


class BackgroundTaskWorker:
    """
    Asynchronous task worker for handling background resume parsing,
    job requirement analysis, and match generations.
    """

    def __init__(self):
        self.is_running = False

    async def start(self):
        self.is_running = True
        logger.info("ResumeFit Background Worker started and listening for jobs...")
        while self.is_running:
            try:
                # Heartbeat and processing loop
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker iteration error: {e}")
                await asyncio.sleep(5)

    def stop(self):
        self.is_running = False
        logger.info("Background Worker stopped.")


if __name__ == "__main__":
    worker = BackgroundTaskWorker()
    try:
        asyncio.run(worker.start())
    except KeyboardInterrupt:
        worker.stop()
