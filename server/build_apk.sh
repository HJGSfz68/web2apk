#!/bin/bash
# Build a WebView-shell APK. Usage: build_apk.sh <config.json> <out.apk>
set -e
CFG="$1"
BUILD=/tmp/apkbuild
TOOLS=/opt/android-sdk/build-tools/34.0.0
PLATFORM=/opt/android-sdk/platforms/android-34/android.jar

eval "$(python3 - "$CFG" <<'PYEOF'
import json, sys
from urllib.parse import urlparse
c = json.load(open(sys.argv[1]))
print(f"PACKAGE={c['packageName']!r}")
print(f"APP_NAME={c['appName']!r}")
print(f"SITE_URL={c['siteUrl']!r}")
print(f"VERSION_NAME={c['versionName']!r}")
print(f"VERSION_CODE={int(c.get('versionCode') or 1)}")
print(f"FORCE_DARK={'true' if c.get('dark') else 'false'}")
print(f"FULLSCREEN={'true' if c.get('fullscreen') else 'false'}")
print(f"EXTERNAL={'true' if c.get('externalLinks') else 'false'}")
print(f"ICON={c.get('iconPath') or ''!r}")
print(f"HOST={urlparse(c['siteUrl']).netloc!r}")
PYEOF
)"

rm -rf $BUILD && mkdir -p $BUILD/gen $BUILD/obj $BUILD/out

sed -e "s|__PACKAGE__|com.lumen.web|g" \
    -e "s|__VERSION_CODE__|$VERSION_CODE|g" \
    -e "s|__VERSION_NAME__|$VERSION_NAME|g" \
    -e "s|__APP_NAME__|$APP_NAME|g" \
    /workspace/server/template/AndroidManifest.xml > $BUILD/AndroidManifest.xml

ICON_OK=0
mkdir -p $BUILD/res
cp -r /workspace/server/template/res/* $BUILD/res/
if [ -n "$ICON" ] && [ -f "$ICON" ] && head -c 8 "$ICON" | grep -q $'\x89PNG'; then
  mkdir -p $BUILD/res/drawable && cp "$ICON" $BUILD/res/drawable/icon.png && ICON_OK=1
fi
if [ $ICON_OK -eq 0 ]; then
  mkdir -p $BUILD/res/drawable
  python3 -c "
import struct, zlib, math
w = h = 192
px = b''
for y in range(h):
    for x in range(w):
        r = int(45+14*math.sin(y/24)); g = int(200+20*math.sin(x/30)); b = 191
        px += bytes((r, g, b, 255))
raw = b''.join(b'\x00' + px[y*w*4:(y+1)*w*4] for y in range(h))
def chunk(t, d):
    c = t + d
    return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
png = b'\x89PNG\r\n\x1a\n'
png += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
png += chunk(b'IDAT', zlib.compress(raw))
png += chunk(b'IEND', b'')
open('$BUILD/res/drawable/icon.png', 'wb').write(png)
"
fi

$TOOLS/aapt2 compile --dir $BUILD/res -o $BUILD/res.zip
$TOOLS/aapt2 link -o $BUILD/out/base.apk \
    -I $PLATFORM \
    --manifest $BUILD/AndroidManifest.xml \
    --rename-manifest-package "$PACKAGE" \
    --java $BUILD/gen \
    $BUILD/res.zip

cat > $BUILD/MainActivity.java <<EOF
$(sed -e "s|__FORCE_DARK__|$FORCE_DARK|g" \
     -e "s|__FULLSCREEN__|$FULLSCREEN|g" \
     -e "s|__EXTERNAL_LINKS__|$EXTERNAL|g" \
     -e "s|__HOST__|$HOST|g" \
     -e "s|__SITE_URL__|$SITE_URL|g" \
     /workspace/server/template/java/com/lumen/web/MainActivity.java)
EOF

javac -source 8 -target 8 -bootclasspath $PLATFORM \
    -classpath $BUILD/out/base.apk \
    -d $BUILD/obj $BUILD/MainActivity.java $BUILD/gen/com/lumen/web/R.java

$TOOLS/d8 --release --min-api 23 --lib $PLATFORM \
    --output $BUILD/out $(find $BUILD/obj -name '*.class')

cd $BUILD/out && zip -q base.apk classes.dex && cd /

KS=/workspace/server/.keystore
if [ ! -f "$KS" ]; then
  keytool -genkeypair -keystore $KS -alias lumen -keyalg RSA -keysize 2048 \
    -validity 10000 -storepass lumen123456 -keypass lumen123456 \
    -dname "CN=Lumen, O=Lumen, C=CN" >/dev/null 2>&1
fi

$TOOLS/zipalign -f 4 $BUILD/out/base.apk $BUILD/out/aligned.apk
$TOOLS/apksigner sign --ks $KS --ks-pass pass:lumen123456 \
    --key-pass pass:lumen123456 --out "$2" $BUILD/out/aligned.apk
echo "BUILD_OK $2"
