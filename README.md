# Web2APK - 把网站封装成 Android APK

在线 Web 工具，输入网址，一键生成可安装的 Android APK（WebView 壳应用）。

**在线体验：** http://13.210.179.29:8001

## 功能

- 输入网站地址，打包为独立 APK
- 自定义应用名称、图标（PNG/JPEG）、包名
- 应用名称中文自动转拼音包名
- 支持深色适配、全屏浏览、外部链接跳转
- 本地构建+签名，无需上传网站数据到服务器
- 生成后可直接下载安装，支持分享

## 一键部署（AI 友好）

以下命令在空白 Debian/Ubuntu 服务器上完整部署：

```bash
# 安装依赖
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq && apt-get install -y -qq openjdk-21-jdk-headless git wget unzip python3 python3-pil zip

# 安装 Android SDK
mkdir -p /opt/android-sdk/cmdline-tools
wget -q -O /tmp/cmdline-tools.zip "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"
unzip -q /tmp/cmdline-tools.zip -d /opt/android-sdk/cmdline-tools/
mv /opt/android-sdk/cmdline-tools/cmdline-tools /opt/android-sdk/cmdline-tools/latest
rm /tmp/cmdline-tools.zip
yes | /opt/android-sdk/cmdline-tools/latest/bin/sdkmanager --sdk_root=/opt/android-sdk "build-tools;35.0.0" "platforms;android-35"

# 克隆项目
git clone https://github.com/HJGSfz68/web2apk.git /root/web2apk

# 启动服务（后台运行）
cd /root/web2apk && python3 server/server.py &
```

访问 `http://<服务器IP>:8001` 即可使用。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | 原生 HTML + CSS + Vanilla JS |
| 后端 | Python http.server |
| 构建 | Android SDK build-tools (aapt2, d8, zipalign, apksigner) |
| 最低 SDK | Android 7.0 (API 23) |
| 目标 SDK | Android 15 (API 35) |

## 快速启动

```bash
python3 server/server.py
```

打开 http://localhost:8001 即可使用。

## 项目结构

```
├── app/                 # 前端页面
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── pinyin-pro.iife.js
├── server/              # 后端
│   ├── server.py        # HTTP 服务（端口 8001）
│   ├── build_apk.sh     # APK 构建脚本
│   ├── template/        # APK 模板（AndroidManifest, MainActivity, 样式）
│   ├── output/          # 构建产物
│   └── .keystore        # 签名证书（自动生成）
└── README.md
```

## 构建流程

```
用户填表 → POST /api/generate-apk → build_apk.sh
  → 替换模板占位符 → aapt2 编译资源 → javac 编译 Java
  → d8 转 DEX → zip 打包 → zipalign 对齐 → apksigner 签名
  → 返回 APK 下载链接
```

## License

MIT