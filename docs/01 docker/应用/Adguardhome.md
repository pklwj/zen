[adguard/adguardhome](https://hub.docker.com/r/adguard/adguardhome)
```yaml
services:
  adguardhome:
    container_name: adguardhome
    restart: unless-stopped
    volumes:
      - /my/own/workdir:/opt/adguardhome/work
      - /my/own/confdir:/opt/adguardhome/conf
    ports:
      - 53:53/tcp
      - 53:53/udp
      - 67:67/udp
      - 68:68/udp
      - 80:80/tcp
      - 443:443/tcp
      - 443:443/udp
      - 3000:3000/tcp
      - 853:853/tcp
      - 784:784/udp
      - 853:853/udp
      - 8853:8853/udp
      - 5443:5443/tcp
      - 5443:5443/udp
    image: adguard/adguardhome
networks: {}
```

| 端口        | 作用                                                                                         |
| --------- | ------------------------------------------------------------------------------------------ |
| **53**    | DNS 端口。即其他设备访问 AdGuard Home 进行 DNS 解析的默认端口。因为部分系统不支持自定义 DNS 端口，所以不建议自定义。部署前务必要查看是否有其它程序占用。 |
| **67/68** | DHCP 端口。除非想代替你路由上的 DHCP 服务器，否则用不到。                                                         |
| **80**    | 管理页面默认 HTTP 端口。可忽略，在初始化页面设置管理端口为 3000 端口即可。                                                |
| **443**   | HTTPS 和 DoH 端口。本地内网环境不需要。                                                                  |
| **853**   | DoT 端口。不使用相关功能可忽略。                                                                         |
| **3000**  | 初始化设置端口。除非通过配置文件去设置，否则必须开启。                                                                |

# 配置