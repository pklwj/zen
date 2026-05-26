# 查看目录总大小​
```shell
du -sh /path/to/directory
# -s：汇总显示总大小
# -h：以人类可读格式（如 K/M/G）显示
```

# 查看cpu当前运行频率
```shell
cat /proc/cpuinfo | grep "cpu MHz"
```

# 解压rar

# 使用 lsmod 检查驱动模块
```shell
# 查看 NVIDIA 驱动
lsmod | grep nvidia

# 查看 Intel 驱动
lsmod | grep i915

# 查看 AMD 驱动
lsmod | grep amdgpu
```

# 查看 AMD GPU 使用情况
- **安装 AMD 监控工具**：
```shell
sudo apt install radeontop
```
- **查看 GPU 使用情况**：
```shell
radeontop
```

# 查看CPU使用情况
```shell
watch -n 1 "top -b -n 1 | grep 'Cpu(s)'"
```

# 在提示符中显示高亮用户名
```shell
nano ~/.bashrc
```

```
PS1='${debian_chroot:+($debian_chroot)}\[\033[01;35m\]\u\[\033[00m\]@\[\033[01;34m\]\h\[\033[00m\]:\[\033[01;32m\]\w\[\033[00m\]\$ '
```

```
PS1='\[\033[01;34m\]\u@\h\[\033[00m\]:\[\033[01;32m\]\w\[\033[00m\]\$ '
```

```
source ~/.bashrc
```
---
# 修改hosts
#### 添加hosts

访问 [https://hosts.gitcdn.top/hosts.txt](https://hosts.gitcdn.top/hosts.txt) ， 将其全部内容粘贴到你的hosts文件中，即可。

- <font color="#f79646">Linux / MacOS</font> hosts路径：<font color="#f79646">/etc/hosts</font>
- <font color="#f79646">Windows</font> hosts路径：<font color="#f79646">C:\Windows\System32\drivers\etc\hosts</font>
#### 刷新生效

- Linux: /etc/init.d/network restart
- Windows: ipconfig /flushdns
- Macos: sudo killall -HUP mDNSResponder

#### Unix/Linux 一键使用

```shell
sed -i "/# fetch-github-hosts begin/Q" /etc/hosts && curl https://hosts.gitcdn.top/hosts.txt >> /etc/hosts
```
---
# SFTP在当前目录打开
```shell
export PS1="$PS1\[\e]1337;CurrentDir="'$(pwd)\a\]'
```
---

# 查看docker占用多少内存的方法：
```shell
docker stats
```
