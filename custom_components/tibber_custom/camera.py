import asyncio

from homeassistant.components.local_file.camera import LocalFile


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None, retry=3
):
    dev = []
    try:
        for home in hass.data["tibber"].get_homes(only_active=True):
            name = home.info["viewer"]["home"]["appNickname"]
            if name is None:
                name = home.info["viewer"]["home"]["address"].get("address1", "")
            path = hass.config.path(f"www/prices_{name}.png")
            dev.append(LocalFile(name, path))
    except KeyError:
        await asyncio.sleep(10)
        if retry > 0:
            return await async_setup_platform(
                hass, config, async_add_entities, discovery_info=None, retry=retry - 1
            )

    async_add_entities(dev)
