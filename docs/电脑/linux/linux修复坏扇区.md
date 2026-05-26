
# 首先检测下坏掉

```shell
badblocks -s -v -o /root/bb.log /dev/sda
```

​
将结果保存到bb.log

[[696b2bc1b8fb0f072493213681d64bec_MD5.webp|Open: image-e3718ccc.webp]]
![[696b2bc1b8fb0f072493213681d64bec_MD5.webp]]

smartctl -a /dev/sda3 (快速检测硬盘坏道,看read，write 后面有没有errors)

# 逻辑坏道修复方法
①、badblocks -s -w /dev/sda END START (END代表需要修复的扇区末端，START代表需要修复的扇区起始端)
②、fsck -a /dev/sda
修复后再用badblocks -s -v -o /root/bb.log /dev/sda监测看是否还有坏道存在，如果坏道还是存在的话说明坏道属于硬盘坏道。硬盘坏道要用隔离方法，首先记录监测出的硬盘坏道然后分区的时候把硬盘坏道所在的扇区分在一个分区（大小一般大于坏扇区大小），划分出的坏道分区不使用即可达到隔离的目的

# 0磁道坏道和硬盘坏道（准备换硬盘）
0磁道坏道的修复方法是隔离0磁道，使用fdsk划分区的时候从1磁道开始划分区。

如果是硬盘坏道的话，只能隔离不能修复