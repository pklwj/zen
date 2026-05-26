https://v2raya.org/en/

https://hub.docker.com/r/mzz2017/v2raya

如不慎忘记密码，使用 v2raya --reset-password 重置
http://192.168.31.121:2017/


#### 环境变量
`V2RAYA_ADDRESS`: 监听地址 (默认 ":::2017")

`V2RAYA_CONFIG`: v2rayA 配置文件目录 (default "/etc/v2raya")

`V2RAYA_V2RAY_BIN`: v2ray 可执行文件路径. 留空将自动检测. 可修改为 v2ray 分支如 xray 等文件路径

`V2RAYA_V2RAY_CONFDIR`: 附加的 v2ray 配置文件目录, 该目录中的 v2ray 配置文件会与 v2rayA 生成的配置文件进行组合

`V2RAYA_WEBDIR`: v2rayA 前端 GUI 文件目录 (默认 "/etc/v2raya/web")

`V2RAYA_PLUGINLISTENPORT`: v2rayA 内部插件端口 (默认 32346)

`V2RAYA_PASSCHECKROOT`: 跳过 root 权限检测, 确认你有 root 权限而 v2rayA 判断出错时使用

`V2RAYA_VERBOSE`: 详细日志模式，混合打印 v2ray-core 和 v2rayA 的运行日志

`V2RAYA_RESET_PASSWORD`: 重设密码