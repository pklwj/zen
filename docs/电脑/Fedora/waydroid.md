一次性隐藏所有已安装的 Android 应用图标
for file in $HOME/.local/share/applications/waydroid.*.desktop; do desktop-file-edit --set-key=NoDisplay --set-value=true $file; done
