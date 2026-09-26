## Web2APK - 网站一键打包成 Android APK

输入网址，自动生成可安装的独立 APK，无需上传网站数据到服务器。

### 功能

- 自定义名称、图标、包名，中文名自动转拼音
- 支持深色适配、全屏浏览、外部链接跳转
- 本地构建 + 签名，所有操作在服务端完成
- 生成后直接下载安装

### 一键部署

空白 Debian/Ubuntu 服务器上执行：

```bash
apt-get update -qq && apt-get install -y -qq openjdk-21-jdk-headless git wget unzip python3 python3-pil zip
mkdir -p /opt/android-sdk/cmdline-tools
wget -q -O /tmp/cmdline-tools.zip https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip -q /tmp/cmdline-tools.zip -d /opt/android-sdk/cmdline-tools/
mv /opt/android-sdk/cmdline-tools/cmdline-tools /opt/android-sdk/cmdline-tools/latest
rm /tmp/cmdline-tools.zip
yes | /opt/android-sdk/cmdline-tools/latest/bin/sdkmanager --sdk_root=/opt/android-sdk "build-tools;35.0.0" "platforms;android-35"
git clone https://github.com/HJGSfz68/web2apk.git /root/web2apk
cd /root/web2apk && python3 server/server.py &
```

访问 `http://服务器IP:8001` 即可使用。

### 技术栈

前端原生 HTML/CSS/JS，后端 Python，构建使用 Android SDK 35，最低支持 Android 7.0。

### 开源地址

https://github.com/HJGSfz68/web2apk