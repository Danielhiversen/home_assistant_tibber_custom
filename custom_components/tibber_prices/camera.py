from homeassistant.components.local_file.camera import LocalFile


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    dev = []
    print("aaaaa")
    for home in hass.data["tibber"].get_homes(only_active=True):
        name = home.info["viewer"]["home"]["appNickname"]
        if name is None:
            name = home.info["viewer"]["home"]["address"].get("address1", "")
        path = hass.config.path(f"www/prices_{name}.png")
        print(name)
        dev.append(LocalFile(name, path))

    async_add_entities(dev)
