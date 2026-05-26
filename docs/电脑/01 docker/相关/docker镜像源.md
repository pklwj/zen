#docker 
https://cloud.tencent.com/developer/article/2485043

```shell
nano /etc/docker/daemon.json
```
```shell
sudo systemctl daemon-reload
sudo systemctl restart docker
```


```shell
sudo tee /etc/docker/daemon.json <<EOF
{
    "registry-mirrors": ["https://hub.1panel.dev"]
}
EOF
```