# Python APK Template

将 Python 代码打包成 Android APK 的通用模板项目。只需修改一个文件，即可将你的 Python 脚本变成 Android 应用。

## 特性

- 开箱即用的项目结构
- 简洁的 GUI 界面，支持输入参数和显示输出
- GitHub Actions 云端构建 (推荐，无需本地环境)
- 支持中文显示
- 详细的配置说明

## 环境要求

| 环境 | 要求 |
|------|------|
| 操作系统 | Linux / macOS / Windows (WSL2) |
| Python | 3.8+ |
| 磁盘空间 | 首次构建需要 5-10 GB (下载 Android SDK/NDK) |
| 内存 | 建议 4GB+ |

---

## 快速开始

### 第一步：克隆项目

```bash
git clone https://github.com/Jaychouhh/python-apk-template.git
cd python-apk-template
```

### 第二步：编写你的代码

打开 `app/your_code.py`，修改 `run()` 函数：

```python
def run(args: list = None):
    """
    主函数 - 在这里写你的代码

    参数:
        args: 用户在输入框中输入的参数列表
              例如用户输入 "hello world" -> args = ["hello", "world"]

    返回:
        任意值，会显示在输出区域
    """

    # 示例：简单的计算器
    print("欢迎使用我的应用!")

    if args and len(args) >= 2:
        a, b = float(args[0]), float(args[1])
        print(f"{a} + {b} = {a + b}")
    else:
        print("请输入两个数字，用空格分隔")

    return "执行完成"
```

**重要说明：**
- 所有 `print()` 输出都会显示在 APP 界面上
- `args` 是用户在输入框中输入的内容（按空格分割成列表）
- 返回值也会显示在界面上

### 第三步：修改应用配置

编辑 `buildozer.spec` 文件，修改以下配置：

```ini
# 应用名称 (显示在手机上的名字)
title = My Calculator

# 包名 (唯一标识，格式: com.你的名字.应用名)
package.name = mycalculator
package.domain = com.example

# 版本号
version = 1.0.0

# 如果需要第三方库，在这里添加
requirements = python3,kivy,requests
```

### 第四步：构建 APK

```bash
# 1. 安装系统依赖 (首次运行)
./build.sh deps

# 2. 构建 Debug 版本
./build.sh debug
```

首次构建会下载 Android SDK 和 NDK，需要较长时间，请耐心等待。

### 第五步：获取 APK

构建成功后，APK 文件位于：

```
bin/mycalculator-1.0.0-debug.apk
```

将此文件传到手机上安装即可。

---

## 项目结构详解

```
python-apk-template/
│
├── main.py              # [无需修改] 主入口，提供 GUI 界面
│
├── app/
│   ├── __init__.py
│   └── your_code.py     # [修改这里] 你的 Python 代码
│
├── buildozer.spec       # [按需修改] 打包配置文件
├── requirements.txt     # Python 依赖 (开发时用)
├── build.sh             # 构建脚本
├── .gitignore
└── README.md
```

### 文件说明

| 文件 | 作用 | 是否需要修改 |
|------|------|-------------|
| `app/your_code.py` | 你的业务逻辑代码 | **必须修改** |
| `buildozer.spec` | APK 打包配置 | 需要修改应用名和包名 |
| `main.py` | GUI 界面代码 | 一般不需要修改 |
| `build.sh` | 构建脚本 | 不需要修改 |

---

## Windows 用户指南

Windows 不能直接运行 Buildozer，有以下几种方案：

### 方案一：GitHub Actions (推荐)

**无需配置任何本地环境**，直接在云端构建。

1. Fork 或 clone 本项目到你的 GitHub
2. 修改代码后 push 到 GitHub
3. 进入 GitHub 仓库页面 -> `Actions` -> `Build APK`
4. 点击 `Run workflow`，选择 debug 或 release
5. 等待构建完成，下载 APK

![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-自动构建-2088FF?logo=github-actions)

### 方案二：Docker

```bash
# 安装 Docker Desktop for Windows

# 使用官方镜像构建 (Linux/macOS)
docker run --rm \
  --entrypoint="" \
  -v "$(pwd)":/home/user/hostcwd \
  -w /home/user/hostcwd \
  kivy/buildozer:latest \
  buildozer android debug

# Windows CMD
docker run --rm --entrypoint="" -v "%cd%":/home/user/hostcwd -w /home/user/hostcwd kivy/buildozer:latest buildozer android debug

# Windows PowerShell
docker run --rm --entrypoint="" -v "${PWD}:/home/user/hostcwd" -w /home/user/hostcwd kivy/buildozer:latest buildozer android debug
```

### 方案三：Google Colab (免费云端)

1. 打开 [Google Colab](https://colab.research.google.com/)
2. 上传项目文件或从 GitHub 克隆
3. 运行以下代码：

```python
# 安装依赖
!pip install buildozer cython
!sudo apt-get install -y openjdk-17-jdk

# 克隆你的项目
!git clone https://github.com/你的用户名/python-apk-template.git
%cd python-apk-template

# 构建
!buildozer android debug

# 下载 APK
from google.colab import files
files.download('bin/你的应用名-1.0.0-debug.apk')
```

### 方案四：WSL2

```powershell
# 1. 以管理员身份打开 PowerShell，运行：
wsl --install -d Ubuntu

# 2. 重启电脑

# 3. 打开 Ubuntu，设置用户名和密码
```

在 WSL 中构建：

```bash
# 1. 进入 WSL
wsl

# 2. 进入项目目录 (Windows 路径映射到 /mnt/)
# 例如 D:\projects\python-apk-template 对应：
cd /mnt/d/projects/python-apk-template

# 3. 安装依赖
./build.sh deps

# 4. 构建
./build.sh debug
```

### Windows 路径映射规则 (WSL)

| Windows 路径 | WSL 路径 |
|-------------|----------|
| `C:\Users\xxx` | `/mnt/c/Users/xxx` |
| `D:\projects` | `/mnt/d/projects` |
| `E:\code` | `/mnt/e/code` |

---

## 添加第三方库

### 支持的库

大多数**纯 Python** 库都可以使用，例如：
- `requests` - HTTP 请求
- `beautifulsoup4` - HTML 解析
- `pillow` - 图片处理
- `numpy` - 数值计算 (需要额外配置)

### 如何添加

编辑 `buildozer.spec`，找到 `requirements` 行：

```ini
# 添加你需要的库，用逗号分隔
requirements = python3,kivy,requests,beautifulsoup4,pillow
```

### 不支持的库

以下类型的库**无法**在 Android 上使用：
- 依赖系统 GUI 的库 (如 `tkinter`, `PyQt`)
- 依赖特定操作系统的库
- 需要编译的 C 扩展 (除非有 Android 版本)

---

## 自定义应用图标

### 1. 准备图标

- 格式：PNG
- 尺寸：512 x 512 像素
- 命名：`icon.png`

### 2. 放置图标

将 `icon.png` 放在项目根目录：

```
python-apk-template/
├── icon.png          # <-- 放在这里
├── main.py
└── ...
```

### 3. 修改配置

编辑 `buildozer.spec`，取消注释：

```ini
# 取消这行的注释
icon.filename = icon.png
```

### 4. 添加启动画面 (可选)

同样的方式添加启动画面：

```ini
presplash.filename = presplash.png
```

---

## 构建命令参考

```bash
# 安装系统依赖 (Ubuntu/Debian)
./build.sh deps

# 构建 Debug 版本 (用于测试)
./build.sh debug

# 构建 Release 版本 (用于发布)
./build.sh release

# 清理构建缓存
./build.sh clean
```

---

## 构建 Release 版本 (签名 APK)

Release 版本需要签名才能安装到手机上，适合正式发布。

### 1. 创建签名密钥 (只需一次)

```bash
keytool -genkey -v -keystore ~/my-release-key.keystore -alias myapp -keyalg RSA -keysize 2048 -validity 10000
```

按提示输入密码和信息。**请妥善保管此文件和密码，丢失后无法更新应用。**

### 2. 配置签名信息

编辑 `buildozer.spec`，取消注释并填写：

```ini
android.keystore = ~/my-release-key.keystore
android.keyalias = myapp
android.keystore_password = 你设置的密码
android.keyalias_password = 你设置的密码
```

### 3. 构建 Release APK

```bash
./build.sh release
```

生成的 APK 位于 `bin/` 目录，可以上传到应用商店或直接分发。

### Debug vs Release 区别

| 特性 | Debug | Release |
|------|-------|---------|
| 签名 | 自动生成调试签名 | 需要正式签名 |
| 体积 | 较大 | 较小 (优化过) |
| 性能 | 包含调试信息 | 优化后更快 |
| 用途 | 开发测试 | 正式发布 |

---

## 常见问题

### Q: 构建失败，提示找不到 SDK/NDK

**A:** 首次构建会自动下载，确保网络通畅。如果下载失败，可以手动设置：

```bash
export ANDROIDSDK=~/android-sdk
export ANDROIDNDK=~/android-ndk
```

### Q: 构建时内存不足

**A:** 尝试以下方法：
1. 关闭其他程序
2. 增加 swap 空间
3. 在 `buildozer.spec` 中只保留一个架构：
   ```ini
   android.archs = arm64-v8a
   ```

### Q: APK 安装失败

**A:** 检查以下几点：
1. 手机允许安装未知来源应用
2. 如果是更新，先卸载旧版本
3. 检查 Android 版本是否符合 `android.minapi` 要求

### Q: 应用闪退

**A:** 查看日志：
```bash
# 手机连接电脑，开启 USB 调试
adb logcat | grep python
```

常见原因：
- 缺少依赖库
- 代码有语法错误
- 使用了不支持的库

### Q: 如何减小 APK 体积

**A:**
1. 只包含需要的架构：
   ```ini
   android.archs = arm64-v8a
   ```
2. 移除不需要的依赖
3. 使用 Release 版本

---

## 代码示例

### 示例 1：简单计算器

```python
def run(args):
    if not args or len(args) < 3:
        print("用法: 数字1 运算符 数字2")
        print("例如: 10 + 5")
        return

    a, op, b = float(args[0]), args[1], float(args[2])

    if op == '+':
        result = a + b
    elif op == '-':
        result = a - b
    elif op == '*':
        result = a * b
    elif op == '/':
        result = a / b if b != 0 else "错误: 除数不能为0"
    else:
        result = "不支持的运算符"

    print(f"{a} {op} {b} = {result}")
    return result
```

### 示例 2：网络请求

```python
import requests

def run(args):
    url = args[0] if args else "https://httpbin.org/get"

    print(f"正在请求: {url}")

    try:
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应内容:\n{response.text[:500]}")
    except Exception as e:
        print(f"请求失败: {e}")
```

### 示例 3：文件处理

```python
import os

def run(args):
    # 获取应用私有目录
    app_dir = os.path.dirname(os.path.abspath(__file__))

    # 创建数据文件
    data_file = os.path.join(app_dir, "data.txt")

    if args and args[0] == "save":
        content = " ".join(args[1:])
        with open(data_file, "w") as f:
            f.write(content)
        print(f"已保存: {content}")

    elif args and args[0] == "read":
        if os.path.exists(data_file):
            with open(data_file, "r") as f:
                print(f"内容: {f.read()}")
        else:
            print("文件不存在")

    else:
        print("用法:")
        print("  save 内容 - 保存内容")
        print("  read - 读取内容")
```

---

## 进阶配置

### 修改 Android 权限

编辑 `buildozer.spec`：

```ini
# 常用权限
android.permissions = INTERNET,CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_FINE_LOCATION
```

常用权限说明：

| 权限 | 用途 |
|------|------|
| `INTERNET` | 网络访问 |
| `CAMERA` | 相机 |
| `WRITE_EXTERNAL_STORAGE` | 写入存储 |
| `READ_EXTERNAL_STORAGE` | 读取存储 |
| `ACCESS_FINE_LOCATION` | GPS 定位 |

### 修改屏幕方向

```ini
# portrait = 竖屏
# landscape = 横屏
# all = 自动旋转
orientation = portrait
```

### 修改目标 Android 版本

```ini
android.api = 33        # 目标 API (Android 13)
android.minapi = 21     # 最低 API (Android 5.0)
```

---

## License

MIT License
