# 下载安装
https://zh-wireguard.com/install/#windows-7-81-10-11-2008r2-2012r2-2016-2019-2022


# docker安装
```
docker run -d \
  --name=wg-easy \
  -e WG_HOST=123.123.123.123 (🚨这里输入服务器的公网IP) \
  -e PASSWORD=passwd123 (🚨这里输入你的密码) \
  -e WG_DEFAULT_ADDRESS=10.0.8.x （🚨默认IP地址）\
  -e WG_DEFAULT_DNS=114.114.114.114 （🚨默认DNS）\
  -e WG_ALLOWED_IPS=10.0.8.0/24 （🚨允许连接的IP段）\
  -e WG_PERSISTENT_KEEPALIVE=25 （🚨重连间隔）\
  -v ~/.wg-easy:/etc/wireguard \
  -p 51820:51820/udp \
  -p 51821:51821/tcp \
  --cap-add=NET_ADMIN \
  --cap-add=SYS_MODULE \
  --sysctl="net.ipv4.conf.all.src_valid_mark=1" \
  --sysctl="net.ipv4.ip_forward=1" \
  --restart unless-stopped \
  weejewel/wg-easy
```

```shell
docker run -d \
  --net wg \
  -e INSECURE=true \
  --name wg-easy \
  --ip6 fdcc:ad94:bacf:61a3::2a \
  --ip 10.42.42.42 \
  -v ~/.wg-easy:/etc/wireguard \
  -v /lib/modules:/lib/modules:ro \
  -p 51820:51820/udp \
  -p 51821:51821/tcp \
  --cap-add NET_ADMIN \
  --cap-add SYS_MODULE \
  --sysctl net.ipv4.ip_forward=1 \
  --sysctl net.ipv4.conf.all.src_valid_mark=1 \
  --sysctl net.ipv6.conf.all.disable_ipv6=0 \
  --sysctl net.ipv6.conf.all.forwarding=1 \
  --sysctl net.ipv6.conf.default.forwarding=1 \
  --restart unless-stopped \
  ghcr.io/wg-easy/wg-easy:15
```

不会用啊
