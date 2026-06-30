# rclone玩法
## 1. 添加文件夹右键上传网盘


```ini
# 可单选，可多选
[Nemo Action]
Active=true
Name=使用 rclone 上传
Comment=在终端中查看 rclone 上传进度
Exec=gnome-terminal -- bash -c 'for file in %F; do echo "正在上传: $file"; rclone copy -P "$file" "OneDrive:"; echo "--------------------------------"; done; echo "文件上传完毕！"; read -p "按回车键关闭窗口..." -n 1'
Icon-Name=utilities-terminal
Selection=any
Extensions=any;
Quote=double
```
