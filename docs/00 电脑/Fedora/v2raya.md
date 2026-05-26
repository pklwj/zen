# 添加 copr 源
```bash
sudo dnf copr enable zhullyb/v2rayA
```
# 安装 V2Ray 内核
```bash
sudo dnf install v2ray v2raya
```
# 启动 v2rayA
```bash
sudo systemctl start v2raya.service 
```
# 设置开机自动启动
```bash
sudo systemctl enable v2raya.service
```
   