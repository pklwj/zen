# 字体
```bash
sudo pacman -S adobe-source-han-sans-cn-fonts ttf-jetbrains-mono-nerd
```
- **思源黑体**：负责系统 UI 和网页阅读。
- **Nerd Font**：负责 niri/Waybar 上的各种小图标。
- **更纱黑体 (Sarasa)**：负责终端和代码，中文不位移。
```bash
gsettings set org.gnome.desktop.interface font-name 'Source Han Sans CN 11'
gsettings set org.gnome.desktop.interface document-font-name 'Source Han Sans CN 11'
gsettings set org.gnome.desktop.interface monospace-font-name 'Sarasa Mono SC 10'
```


```bash
sudo pacman -S noto-fonts-emoji otf-font-awesome  
  
# 搜索可用的 CaskaydiaCove 相关包，这是waybar配置文件中的首选字体  
yay -Ss caskaydia  
yay -Ss cascadia  
  
# 安装找到的包  
yay -S ttf-cascadia-code-nerd
```

