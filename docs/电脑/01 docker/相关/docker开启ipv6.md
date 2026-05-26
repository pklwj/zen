```shell
nano /etc/docker/daemon.json
```

```json
{
  "ipv6": true,
  "fixed-cidr-v6": "2001:db8:1::/64",
  "experimental": true,
  "ip6tables": true
}
```

```bash
sudo systemctl restart docker
```
