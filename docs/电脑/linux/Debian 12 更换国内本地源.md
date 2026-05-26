## 修改源


```
nano /etc/apt/sources.list
```


## 阿里云源

```
deb https://mirrors.aliyun.com/debian/ bookworm main non-free non-free-firmware contrib

deb-src https://mirrors.aliyun.com/debian/ bookworm main non-free non-free-firmware contrib

deb https://mirrors.aliyun.com/debian-security/ bookworm-security main

deb-src https://mirrors.aliyun.com/debian-security/ bookworm-security main

deb https://mirrors.aliyun.com/debian/ bookworm-updates main non-free non-free-firmware contrib

deb-src https://mirrors.aliyun.com/debian/ bookworm-updates main non-free non-free-firmware contrib

deb https://mirrors.aliyun.com/debian/ bookworm-backports main non-free non-free-firmware contrib

deb-src https://mirrors.aliyun.com/debian/ bookworm-backports main non-free non-free-firmware contrib
```

## 清华大学源(写该文章时有问题)

```shell
# 默认注释了源码镜像以提高 apt update 速度，如有需要可自行取消注释
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free non-free-firmware
# deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free non-free-firmware

deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware
# deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware

deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware
# deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware

# 以下安全更新软件源包含了官方源与镜像站配置，如有需要可自行修改注释切换
deb https://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
# deb-src https://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
```

## 中科大源

```shell
deb https://mirrors.ustc.edu.cn/debian/ bookworm main non-free non-free-firmware contrib

deb-src https://mirrors.ustc.edu.cn/debian/ bookworm main non-free non-free-firmware contrib

deb https://mirrors.ustc.edu.cn/debian-security/ bookworm-security main

deb-src https://mirrors.ustc.edu.cn/debian-security/ bookworm-security main

deb https://mirrors.ustc.edu.cn/debian/ bookworm-updates main non-free non-free-firmware contrib

deb-src https://mirrors.ustc.edu.cn/debian/ bookworm-updates main non-free non-free-firmware contrib

deb https://mirrors.ustc.edu.cn/debian/ bookworm-backports main non-free non-free-firmware contrib

deb-src https://mirrors.ustc.edu.cn/debian/ bookworm-backports main non-free non-free-firmware contrib
```

## 网易源

```shell
deb https://mirrors.163.com/debian/ bookworm main non-free non-free-firmware contrib

deb-src https://mirrors.163.com/debian/ bookworm main non-free non-free-firmware contrib

deb https://mirrors.163.com/debian-security/ bookworm-security main

deb-src https://mirrors.163.com/debian-security/ bookworm-security main

deb https://mirrors.163.com/debian/ bookworm-updates main non-free non-free-firmware contrib

deb-src https://mirrors.163.com/debian/ bookworm-updates main non-free non-free-firmware contrib

deb https://mirrors.163.com/debian/ bookworm-backports main non-free non-free-firmware contrib

deb-src https://mirrors.163.com/debian/ bookworm-backports main non-free non-free-firmware contrib
```

## 腾讯云源

```shell
deb https://mirrors.cloud.tencent.com/debian/ bookworm main non-free non-free-firmware contrib

deb-src https://mirrors.cloud.tencent.com/debian/ bookworm main non-free non-free-firmware contrib

deb https://mirrors.cloud.tencent.com/debian-security/ bookworm-security main

deb-src https://mirrors.cloud.tencent.com/debian-security/ bookworm-security main

deb https://mirrors.cloud.tencent.com/debian/ bookworm-updates main non-free non-free-firmware contrib

deb-src https://mirrors.cloud.tencent.com/debian/ bookworm-updates main non-free non-free-firmware contrib

deb https://mirrors.cloud.tencent.com/debian/ bookworm-backports main non-free non-free-firmware contrib

deb-src https://mirrors.cloud.tencent.com/debian/ bookworm-backports main non-free non-free-firmware contrib
```

## 把本地光盘当做源来使用

```shell
rambo@test1:~$ sudo vim /etc/apt/sources.list

# 在第一行插入下行内容

deb [trusted=yes] file:///mnt/usb1  bookworm   main  non-free-firmware

 

# 挂载光盘

rambo@test1:~$ mkdir /mnt/usb1

rambo@test1:~$ mount /dev/sr0   /mnt/usb1
```

## 更新源

```shell
sudo apt update
```
