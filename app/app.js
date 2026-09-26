const $ = id => document.getElementById(id);

const state = {
  dark: false,
  fullscreen: false,
  externalLinks: false,
  iconDataUrl: null,
};

const toggles = [
  ['swDark', 'dark'],
  ['swFull', 'fullscreen'],
  ['swExt', 'externalLinks'],
];
toggles.forEach(([id, key]) => {
  $(id).addEventListener('click', () => {
    state[key] = !state[key];
    $(id).classList.toggle('on', state[key]);
    $(id).setAttribute('aria-checked', String(state[key]));
  });
});

$('pickIcon').addEventListener('click', () => $('iconInput').click());
$('iconInput').addEventListener('change', e => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    state.iconDataUrl = reader.result;
    $('iconPreview').innerHTML = `<img src="${state.iconDataUrl}" alt="icon">`;
  };
  reader.readAsDataURL(file);
});

function validUrl(u) {
  try {
    const url = new URL(u);
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch { return false; }
}

function slugPkg(pkg) {
  return pkg.trim().toLowerCase().replace(/[^a-z0-9.]/g, '').replace(/\.{2,}/g, '.').replace(/^\.|\.$/g, '');
}

function buildConfig() {
  return {
    appName: $('appName').value.trim() || 'My App',
    siteUrl: $('siteUrl').value.trim(),
    packageName: slugPkg($('pkg').value) || 'app.lumen.webapp',
    versionName: $('verName').value.trim() || '1.0.0',
    versionCode: parseInt($('verCode').value, 10) || 1,
    ...state,
    createdAt: new Date().toISOString(),
  };
}

let lastDownloadUrl = null;
let lastPkgName = null;

$('generate').addEventListener('click', async () => {
  const cfg = buildConfig();
  if (!validUrl(cfg.siteUrl)) {
    $('result').hidden = false;
    $('resultText').textContent = '请输入有效的网站地址（以 http/https 开头）';
    $('resultText').style.color = '#f87171';
    return;
  }
  const btn = $('generate');
  btn.disabled = true;
  btn.textContent = '正在生成…';

  try {
    const payload = {
      appName: cfg.appName,
      siteUrl: cfg.siteUrl,
      packageName: cfg.packageName,
      versionName: cfg.versionName,
      versionCode: cfg.versionCode,
      dark: state.dark,
      fullscreen: state.fullscreen,
      externalLinks: state.externalLinks,
      iconData: state.iconDataUrl || null,
    };
    const resp = await fetch('/api/generate-apk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok || !data.ok) {
      throw new Error(data.detail || data.error || '构建失败');
    }
    lastDownloadUrl = data.downloadUrl;
    lastPkgName = cfg;

    $('result').hidden = false;
    $('resultText').style.color = '';
    $('resultText').textContent = `生成成功 · ${data.packageName} · ${data.sizeKb} KB`;
  } catch (e) {
    $('result').hidden = false;
    $('resultText').style.color = '#f87171';
    $('resultText').textContent = `生成失败：${e.message}`;
  } finally {
    btn.disabled = false;
    btn.textContent = '生成可安装 APK';
  }
});

$('install').addEventListener('click', () => {
  if (!lastDownloadUrl) return;
  const a = document.createElement('a');
  a.href = lastDownloadUrl;
  a.download = `${lastPkgName.packageName}.apk`;
  a.click();
});

$('share').addEventListener('click', async () => {
  if (!lastDownloadUrl) return;
  const cfg = lastPkgName;
  const shareData = {
    title: cfg.appName,
    text: `${cfg.appName} APK 下载地址：${location.origin}${lastDownloadUrl}`,
  };
  if (navigator.share) {
    try { await navigator.share(shareData); return; } catch {}
  }
  try {
    await navigator.clipboard.writeText(shareData.text);
    $('resultText').textContent = 'APK 下载链接已复制到剪贴板';
  } catch {
    $('resultText').textContent = shareData.text;
  }
});
