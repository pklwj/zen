```bash
sudo flatpak remote-modify flathub --url=https://mirror.sjtu.edu.cn/flathub
```

如果出现错误可尝试：
```bash
wget https://mirror.sjtu.edu.cn/flathub/flathub.gpg 
sudo flatpak remote-modify --gpg-import=flathub.gpg flathub
```
 
 flatpak repair