Linux預設在~/.config/mpv/

Flatpak版預設在~/.var/app/io.mpv.Mpv/config/mpv/

**mpv.conf** 是關於影片播放器本身的設定，例如解碼器、GPU加速、字幕設定
**input.conf** 代表綁定的快捷鍵。
**scripts 目錄**：MPV支援插件系統，使用Lua語言撰寫，放在底下的.lua檔案MPV一開啟就會自動執行。
**scripts-opts** 為個別插件的設定檔。

```
vo=gpu-next
hwdec=auto                              # 优先使用硬解（原生模式）
hwdec-codecs=all                        # 所有格式优先硬解
#log-file="~~desktop/mpv.log"            # 输出log日志在桌面
keep-open=yes                           # 播放列表中的最后一个条目播放完毕后暂停
save-position-on-quit=yes               # 退出时保存当前的播放状态 
watch-later-options=start,vid,aid,sid   # 指定保存播放状态的属性列表（示例表示：播放位置、视频 音频 字幕轨号）
audio-file-auto=fuzzy                   # 自动加载近似名的外置音轨
sub-auto=fuzzy                          # 自动加载近似名的外置字幕
#profile=high-quality                    # 使用一个内置的画质方案预设

#截图
screenshot-template="%F-%tY-%tm-%td_%tH-%tM-%tS"
screenshot-directory="/home/user/Pictures/"
screenshot-format=png

#缓存
#cache = yes            # <yes|no|默认auto> 是否启用网络缓存（进内存）
#demuxer-max-bytes=300MiB # 增大解码缓存（默认150MiB→300MiB），减少大码率视频卡顿
#demuxer-max-back-bytes=200MiB  # 缓存向后预读时长（配合max-bytes，可选）


#uosc
# 禁用原生 OSD 进度条（使用 uosc 的闪光时间轴/音量提示）
osd-bar=no
# 禁用原生窗口边框（uosc 会绘制自定义边框/控件）
border=no
# （可选）解决 UI 卡顿问题
video-sync=display-resample




```

# uosc
scripts-opts/uosc.conf
修改 `language` 选项为中文：

```
languages=slang,zh-hans
```