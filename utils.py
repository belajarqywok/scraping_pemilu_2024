import os
import csv
import aiohttp
import aiofiles

async def download_image(path, url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                filename = os.path.join(path, os.path.basename(url))
                async with aiofiles.open(filename, "wb") as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        await file.write(chunk)

async def save_image(path, url):
    try:
        await download_image(path, url)
    except Exception as e:
        print(e)

def write_csv(path: str = 'data.csv', data: dict = {}, fields: list = []) -> None:
    if not os.path.exists(path):
        with open(path, mode='w+', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerow(data)
    else:
        with open(path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writerow(data)

def directory(path: str = './datasets') -> None:
  if not (os.path.exists(path) and os.path.isdir(path)): os.makedirs(path)
