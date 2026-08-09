import asyncio


async def download_file():
    print("Downloading...")
    await asyncio.sleep(3)
    print("Download Complete")


async def send_email():
    print("Sending Email...")
    await asyncio.sleep(1)
    print("Email Sent")


async def main():
    await asyncio.gather(
        download_file(),
        send_email()
    )


asyncio.run(main())