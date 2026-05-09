# Desktop Clock 桌面时钟

一个基于 PyQt5 的桌面时钟挂件，支持模拟钟表与数字时钟切换、多时区显示。

## 功能特性

- **模拟钟表** — 精致表盘，带时针、分针、秒针平滑动画
- **数字时钟** — LED 风格大字体数字显示
- **一键切换** — 模拟 / 数字样式随时切换
- **多时区** — 添加不同时区时钟，并排显示
- **预设时区** — 内置 16 个常用时区，也支持自定义 UTC 偏移
- **桌面置顶** — 无边框窗口，始终保持在最上层
- **拖拽移动** — 未锁定时可拖拽到桌面任意位置
- **配置记忆** — 时区列表和窗口位置自动保存，下次启动恢复
- **右键菜单** — 快捷操作入口

## 截图

启动后默认显示本地时间的模拟钟表，点击「＋ 添加时区」可添加全球各地时钟。

## 安装与运行

### 环境要求

- Python 3.8+
- PyQt5

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/your-username/desktop-clock.git
cd desktop-clock

# 安装依赖
pip install -r requirements.txt

# 运行
python clock.py
```

### 国内镜像加速

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 使用说明

| 操作 | 方式 |
|------|------|
| 切换样式 | 点击「全部切换」或单个时钟上的「数字/钟表」按钮 |
| 添加时区 | 点击「＋ 添加时区」或右键菜单 |
| 删除时区 | 点击时钟卡片上的「删除」按钮（至少保留一个） |
| 移动窗口 | 未锁定时拖拽工具栏空白处 |
| 锁定位置 | 点击 🔓 切换为 🔒 |
| 退出程序 | 点击 ✕ 或右键菜单「退出」 |

## 项目结构

```
desktop-clock/
├── clock.py           # 主程序（单文件）
├── requirements.txt   # Python 依赖
├── README.md          # 项目说明
├── LICENSE            # MIT 许可证
└── .gitignore
```

## 技术栈

- **Python 3.12**
- **PyQt5** — GUI 框架
- **QPainter** — 模拟钟表绘制
- **QSettings / JSON** — 配置持久化

## 开发计划

- [ ] 系统托盘常驻
- [ ] 半透明/毛玻璃背景
- [ ] 自定义主题配色
- [ ] 闹钟 / 整点报时
- [ ] 秒表 / 倒计时

## License

MIT License
