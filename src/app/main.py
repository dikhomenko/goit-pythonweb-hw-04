import asyncio
import time
from pathlib import Path
from aiopath import AsyncPath
from aioshutil import copyfile
from logging_config import logger
from typing import Union


async def read_folder(source: AsyncPath, target: AsyncPath, file_count: list) -> None:
    tasks = []
    async for item in source.iterdir():
        if await item.is_dir():
            tasks.append(read_folder(item, target, file_count))
        else:
            tasks.append(copy_file(item, target, file_count))
    await asyncio.gather(*tasks)


async def copy_file(file: AsyncPath, target: AsyncPath, file_count: list) -> None:
    ext = file.suffix[1:]  # Get file extension without the dot
    target_folder = target / ext
    await target_folder.mkdir(exist_ok=True, parents=True)
    target_file = target_folder / file.name

    # Check if the target file already exists and append a number if it does
    counter = 1
    while await target_file.exists():
        target_file = target_folder / f"{file.stem}_{counter}{file.suffix}"
        counter += 1

    try:
        await copyfile(file, target_file)
        logger.info(f"Copied {file} to {target_file}")
        file_count[0] += 1
    except Exception as ex:
        logger.error(f"Failed to copy {file} to {target_file}: {ex}")


async def main(source_folder: str, target_folder: str) -> None:
    start_time = time.time()
    file_count = [0]
    source = AsyncPath(source_folder)
    target = AsyncPath(target_folder)

    await read_folder(source, target, file_count)
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Copied {file_count[0]} files in {elapsed_time:.2f} seconds")
    print(f"Copied {file_count[0]} files in {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    print("Asynchronous file sorter")
    source_folder = input("Enter the source folder to read files from: ")
    target_folder = input("Enter the target folder to copy files to: ")

    # Synchronous validation of input paths
    valid = True
    if not Path(source_folder).exists():
        logger.error(f"Source folder '{source_folder}' does not exist.")
        print(f"Error: Source folder '{source_folder}' does not exist.")
        valid = False
    if not Path(target_folder).exists():
        logger.error(f"Target folder '{target_folder}' does not exist.")
        print(f"Error: Target folder '{target_folder}' does not exist.")
        valid = False

    if valid:
        asyncio.run(main(source_folder, target_folder))
