# 速度很慢
```bash
echo "Server = https://mirrors.tuna.tsinghua.edu.cn/archlinux/\$repo/os/\$arch" > /etc/pacman.d/mirrorlist

echo "Server = https://mirrors.aliyun.com/archlinux/\$repo/os/\$arch" >> /etc/pacman.d/mirrorlist

echo -e "[options]\nParallelDownloads = 30" >> /etc/pacman.conf

```


中文化
#### 设置locale

##### 生成中文locale

在 `/etc/locale.gen` 中删除的`zh_CN.UTF-8 UTF-8` 前方的 `#` 之后使用以下指令生成 Locale：

```bash
 locale-gen
```


# 磁盘分区
## 分区策略
在Arch Linux中，通常推荐以下分区布局：
1. `/boot`：用于存放引导加载器文件，如GRUB。
2. `/`：根分区，存放系统的核心文件和目录。
3. `/home`：用户家目录，存放个人文件和设置。
4. `/swap`：交换分区，用于虚拟内存。


而官方安装脚本默认使用 zram 作为 swap，因为 zram 是将一部分内存空间压缩当作 swap 空间，而内存断电丢失数据的特性决定了它不可以用于系统休眠，想要配置硬盘上的 swap 需要手动分区，而安装脚本的手动分区功能我研究了半天也没搞明白怎么用，所以我最终决定抛弃安装脚本，手动安装。

SSD 需开启优化（如 discard /TRIM、space_cache=v2），否则影响寿命和性能。

/          （根目录子卷，默认只读快照）
/home      （用户数据子卷，独立快照，避免系统回滚影响个人数据）
/var       （日志/缓存子卷，禁用快照，避免占用空间）
/var/lib/docker （容器数据子卷，禁用 CoW，优化性能）

```bash
lsblk # 显示当前分区情况
```


# sway
