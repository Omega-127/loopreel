import asyncio
import random



async def worker(name: str, log: list[str]) -> None:
    await asyncio.sleep(random.random() * 0.01)
    log.append(name)
    await asyncio.sleep(random.random() * 0.01)
    log.append(name + "'")

async def main() -> list[str]:
    log: list[str] = []
    await asyncio.gather(*(worker(f"t{i}", log)for i in range(4)))
    return log

if __name__ == "__main__":
    print(asyncio.run(main()))
