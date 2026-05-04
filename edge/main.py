"""Edge inference entry point."""
import asyncio

async def main():
    print("Edge inference engine starting...")
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
