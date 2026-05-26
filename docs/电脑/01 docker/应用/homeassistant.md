https://www.home-assistant.io/installation/linux
```yaml
services:
  homeassistant:
    container_name: homeassistant
    image: "ghcr.io/home-assistant/home-assistant:stable"
    volumes:
      - /PATH_TO_YOUR_CONFIG:/config
      - /etc/localtime:/etc/localtime:ro
      - /run/dbus:/run/dbus:ro
    restart: unless-stopped
    privileged: true
    network_mode: host
```

> [!NOTE] http://host:8123

# 蓝牙
```shell
apt-get install bluez
```

# HACS
```shell
wget -O - https://get.hacs.xyz | bash -
```







https://sts.api.io.mi.com/sts?d=wb_0b93fe6c-600c-4246-8898-2c1d14d6227c&ticket=0&pwd=1&p_ts=1748840991877&fid=0&p_lm=1&auth=sBLeofcze40blVg0BDYk4tlR%2BIJ3vUL877Ze7jsxPJK9TBBiTxZ8x1nPl8JkLGRH%2Bg3xJcAg%2B5lC0RNEBBhhy%2FOpj03Bm1dx4YxbvQu5MQis8Ih51qEX8bARgOBmLkTEVkmwwgls2hUr5wY0xqAethZNh7WFxn3or2xZhr6Vl2E%3D&m=5&_group=DEFAULT&tsl=1&p_ca=0&p_ur=CN&p_idc=China&nonce=IltkUceN%2BgwBvMDV&_ssign=DcWKGJj8XI9ZWXlzEPN9rdxjXKY%3D
