# Web2APK - 把网站封装成 Android APK

在线 Web 工具，输入网址，一键生成可安装的 Android APK（WebView 壳应用）。

## 功能

- 输入网站地址，打包为独立 APK
- 自定义应用名称、图标、包名
- 支持深色适配、全屏浏览、外部链接跳转
- 本地构建+签名，无需上传网站数据到服务器
- 生成后可直接下载安装

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | 原生 HTML + CSS + Vanilla JS |
| 后端 | Python http.server |
| 构建 | Android SDK build-tools (aapt2, d8, zipalign, apksigner) |
| 最低 SDK | Android 7.0 (API 23) |
| 目标 SDK | Android 14 (API 34) |

## 快速启动

```bash
python3 server/server.py
```

打开 http://localhost:8001 即可使用。

## 本地构建依赖

- Java 17+ JDK
- Android SDK build-tools 34 + platform 34

## 项目结构

```
├── app/              # 前端页面
│   ├── index.html
│   ├── style.css
│   └── app.js
├── server/           # 后端
│   ├── server.py     # HTTP 服务
│   ├── build_apk.sh  # APK 构建脚本
│   ├── template/     # APK 模板
│   └── .keystore     # 签名证书
└── README.md
```

## License

MIT