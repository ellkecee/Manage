from io import BytesIO

from aiohttp import ClientSession


def get_readable_time2(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["detik", "menit", "jam", "hari", "bulan", "tahun", "y"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for i in range(len(time_list)):
        time_list[i] = str(time_list[i]) + time_suffix_list[i]
    if len(time_list) == 4:
        ping_time += f"{time_list.pop()}, "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time

async def make_carbon(code):
    url = "https://carbonara.solopov.dev/api/cook"
    async with ClientSession().post(url, json={"code": code}) as resp:
        image = BytesIO(await resp.read())
    image.name = "carbon.png"
    return image
