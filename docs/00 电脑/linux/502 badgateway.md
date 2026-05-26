# ​​一、核心问题定位​​
​​路径权限冲突​​
/run/php/php8.2-fpm-openmediavault-webgui.sock 路径可能被其他进程占用或权限不足。
OpenMediaVault 的 WebGUI 进程可能已创建同名 Socket，导致冲突。
​​配置文件残留​​
配置文件中存在旧版路径定义（如 openmediavault-webgui 后缀），需彻底清理。
​​服务依赖异常​​
OpenMediaVault 的 PHP-FPM 插件可能与系统默认配置冲突。
# ​​二、分步解决方案​​
## ​​1. 彻底清理残留配置​​
### 删除所有 PHP-FPM 残留进程
sudo pkill -9 php-fpm

### 清理所有 Socket 和 PID 文件
sudo rm -rf /run/php/php8.2-fpm*.sock
sudo rm -f /var/run/php/php8.2-fpm.pid

### 检查并删除 OpenMediaVault 相关配置
sudo sed -i '/openmediavault-webgui/d' /etc/php/8.2/fpm/pool.d/www.conf
## ​​2. 修复 Socket 路径权限​​
### 创建专用目录并设置权限
sudo mkdir -p /run/php/php8.2-fpm.sock
sudo chown www-data:www-data /run/php/php8.2-fpm.sock
sudo chmod 755 /run/php/php8.2-fpm.sock

### 确保 Systemd 服务文件路径一致
sudo sed -i 's|/run/php/php8.2-fpm-openmediavault-webgui.sock|/run/php/php8.2-fpm.sock|g' /lib/systemd/system/php8.2-fpm.service
## ​​3. 重置 PHP-FPM 配置​​
### 备份并重置默认配置
sudo mv /etc/php/8.2/fpm/pool.d/www.conf /etc/php/8.2/fpm/pool.d/www.conf.bak
sudo cp /usr/share/doc/php8.2-fpm/examples/www.conf /etc/php/8.2/fpm/pool.d/

### 修改关键参数
sudo sed -i 's/^;listen.owner = www-data/listen.owner = www-data/' /etc/php/8.2/fpm/pool.d/www.conf
sudo sed -i 's/^;listen.group = www-data/listen.group = www-data/' /etc/php/8.2/fpm/pool.d/www.conf
## ​​4. 重启服务并验证​​
```shell
systemctl daemon-reload
systemctl restart php8.2-fpm
systemctl status php8.2-fpm --no-pager
```


### 检查 Socket 文件是否生成
ls -l /run/php/php8.2-fpm.sock