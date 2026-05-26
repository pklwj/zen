# 系统换源
```shell
omv-env set OMV_APT_REPOSITORY_URL "https://mirrors.tuna.tsinghua.edu.cn/OpenMediaVault/public"    
omv-env set OMV_APT_ALT_REPOSITORY_URL "https://mirrors.tuna.tsinghua.edu.cn/OpenMediaVault/packages"    
omv-env set OMV_APT_KERNEL_BACKPORTS_REPOSITORY_URL "https://mirrors.tuna.tsinghua.edu.cn/debian"    
omv-env set OMV_APT_SECURITY_REPOSITORY_URL "https://mirrors.tuna.tsinghua.edu.cn/debian-security" 
```








插件
1. `openmediavault-flashmemory：加载临时文件到内存，保护硬盘`
2. `openmediavault-fail2ban ：扫描日志文件并禁止显示恶意迹象的IP-太多的密码错误，寻找漏洞等`
3. `openmediavault-cputemp：显示CPU温度`
4. `openmediavault-diskstats：监控收集硬盘的性能统计数据`
5. `openmediavault-filebrowser：简单文件浏览器`
6. `openmediavault-resetperms：重置共享文件夹权限`
7. `openmediavault-locate：全系统文件名搜索，类似everything`
8. `OpenMediaVault WebDAV plugin：webdav共享插件`
9. `openmediavault-backup：OMV系统备份`
10. `openmediavault-usbbackup：自动将共享文件夹同步到USB/eSATA/SD设备，插入设备时也可同步。设备在同步后进入睡眠模式，以发出信号，表示可以安全地移除`
11. `openmediavault-remotemount：装载远程共享`
12. `openmediavault-hosts：管理系统etc/hosts文件`
13. `openmediavault-compose：docker管理软件`
14. `openmediavault-kvm：虚拟机软件`

