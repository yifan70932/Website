# 把 Watchlist 项目融入现有的 yifanova.com (Website repo)

这个 bundle 是为你**现有的 `yifan70932/Website` repo 量身定制的**——不是要你创建新 repo，而是把新文件加到现有结构里。

## 集成后的最终效果

```
yifan70932/Website/
├── assets/                    ← 你现有的，不动
├── chess/                     ← 你现有的，不动 (yifanova.com/chess/)
├── religion/                  ← 你现有的，不动 (yifanova.com/religion/)
├── CNAME                      ← 你现有的，不动 (= yifanova.com)
├── LICENSE                    ← 你现有的，不动
│
├── watchlist/                 ← 新增！(yifanova.com/watchlist/)
│   ├── index.html               入口页面 (英文,套用站点主题)
│   ├── zh.html                  入口页面 (中文,套用站点主题)
│   └── report.html              workflow 自动生成、自动更新
│
├── _analyzer/                 ← 新增！分析器代码（不会被 GitHub Pages 服务）
│   └── quant_watchlist/         Python 包
│       ├── __main__.py
│       ├── core.py
│       └── ...
│
├── .github/                   ← 新增！自动化工作流
│   └── workflows/
│       └── build-report.yml
│
├── _config.yml                ← 新增！Jekyll 配置 (告诉 Jekyll 哪些文件不要发布)
└── requirements.txt           ← 新增！Python 依赖列表
```

访问路径：`yifanova.com/watchlist/` 进入入口页，点击按钮跳转到 `yifanova.com/watchlist/report.html` 看完整报告。

**`/chess/` 和 `/religion/` 完全不受影响，正常工作。**

## 几个重要前提确认

1. **关于 Jekyll**: GitHub Pages 默认会用 Jekyll 处理你的 repo,即使你没有显式配置 Jekyll。这个 bundle 已经做了相应处理:
   - `watchlist/index.html` 和 `watchlist/zh.html` 顶部有 `---\nlayout: null\n---` 的 Jekyll front matter,告诉 Jekyll "原样输出,不要套模板"
   - `watchlist/report.html` 没有 front matter,Jekyll 会**直接复制不处理**(这正是我们想要的——4MB 的 Plotly 报告不需要 Jekyll 处理)
   - 新增的 `_config.yml` 告诉 Jekyll 排除 `requirements.txt`、`INTEGRATION.md` 等不应发布的文件
   - **如果你 repo 里已经有 `_config.yml`**(目前看起来没有),不要直接覆盖!应该把我们 `_config.yml` 里的 `exclude:` 列表合并到你现有的配置里

2. **关于 Actions**: 这个方案需要 Actions 启用。如果你看到 "Actions is currently unavailable for your repository" 这种错误,说明 Actions 被禁用了。启用方式:
   - Settings → Actions → General
   - 顶部 "Actions permissions" 选 "Allow all actions and reusable workflows" → Save
   - 同一页面底部 "Workflow permissions" 选 "Read and write permissions" → Save

3. **GitHub Pages 部署源**: 你的 repo 当前应该是从 `main` 分支根目录部署的(因为 `chess/` 和 `religion/` 是直接放在根目录的)。我们的方案沿用同样的部署源,把 `watchlist/` 也放在根目录。如果你不确定,可以去 Settings → Pages 检查一下:"Build and deployment" 下的 Source 应该是 "Deploy from a branch",Branch 是 `main`,Folder 是 `/ (root)`。

4. **`_analyzer/` 的下划线前缀**: 以下划线开头的目录是 Jekyll 的"忽略"约定。Jekyll 不会把 `_analyzer/` 当作网页内容来处理,所以那里的 Python 代码不会出现在 yifanova.com 的任何 URL 下。

5. **`.github/` 不是网页内容**: 这是 GitHub 的元数据目录,Jekyll 自动忽略,workflow 文件不会出现在你的网站上。

6. **关于视觉风格**:
   - **入口页面 (`watchlist/index.html` 和 `watchlist/zh.html`)** 完全套用了你站点的主题——引用 `../assets/tokens.css` 和 `../assets/base.css`,使用 `.colophon`、`<article>`、`.term`、`.page-footer` 等你已有的语义类。视觉上和 `chess/`、`religion/` 完全一致
   - **报告页面 (`watchlist/report.html`)** 保留了它原本的深色仪表盘风格——这是有意为之的:30 个 Plotly 互动图表加 1600px 宽布局,和 36rem 的散文版心人体工学需求不同。报告顶部加了一行 `yifanova.com / Watchlist / Report` 的面包屑导航,确保从任何路径进入报告都能一键返回主站。入口页面里也明确说明了这种风格对比是有意的设计选择

## 集成步骤

### 步骤 1：把文件加到本地仓库

先把这个 bundle 解压。然后在你本地的 `Website` repo 根目录下,**复制以下五项**进去:

```
你解压出的 watchlist_for_existing_repo/
├── .github/                ← 复制整个文件夹到 Website/.github/
├── _analyzer/              ← 复制整个文件夹到 Website/_analyzer/
├── watchlist/              ← 复制整个文件夹到 Website/watchlist/
├── _config.yml             ← 复制到 Website/_config.yml (如果已有,见前提 1)
└── requirements.txt        ← 复制到 Website/requirements.txt
```

操作命令(macOS / Linux 终端,假设两个文件夹都在 `~/Documents/` 下):

```bash
cd ~/Documents/Website   # 切换到你现有的 repo
cp -r ~/Documents/watchlist_for_existing_repo/.github ./
cp -r ~/Documents/watchlist_for_existing_repo/_analyzer ./
cp -r ~/Documents/watchlist_for_existing_repo/watchlist ./
cp ~/Documents/watchlist_for_existing_repo/_config.yml ./
cp ~/Documents/watchlist_for_existing_repo/requirements.txt ./
```

或者直接用 Finder / GitHub Desktop 拖进去。

### 步骤 2：检查 Workflow 权限

在浏览器打开你的 repo：

1. **Settings** → 左侧栏 **Actions** → **General**
2. 滑到底部找到 **Workflow permissions**
3. 选择 **Read and write permissions**
4. 点 **Save**

如果不做这步，workflow 没法把生成的 `report.html` 提交回 repo。

### 步骤 3：提交并推送

```bash
git add .github _analyzer watchlist requirements.txt
git commit -m "Add quant watchlist analyzer + daily report"
git push
```

### 步骤 4：手动触发第一次运行

推送后 workflow 会因为 `paths` 触发器自动运行一次（因为我们改动了 `_analyzer/` 和 `requirements.txt`）。但保险起见，也可以手动触发一下：

1. 仓库页面 → **Actions** 标签
2. 左侧栏点 **Generate watchlist report**
3. 右上方 **Run workflow** → **Run workflow**（绿色按钮）
4. 等 3-4 分钟。绿色 ✓ 出现就成功了

### 步骤 5：验证

打开浏览器访问：

- **`https://yifanova.com/watchlist/`** → 应该看到入口页
- 点击 "View latest report →" 按钮 → 应该看到完整报告

如果你之前推送之后立刻访问发现是 404，等几分钟（GitHub Pages 部署有缓存延迟）。

## 可能遇到的问题及对策

### 问题 1: 提示 "Actions is currently unavailable for your repository, and your Pages site requires a Jekyll build step"

这意味着你的 repo 把 Actions 功能关掉了。这不光会让我们的 workflow 跑不起来,**连 GitHub Pages 默认的 Jekyll 构建也会停**——所以现有的 `chess/`、`religion/` 页面也会停止更新。修复:

- Settings → Actions(左侧栏)→ General
- 顶部 **Actions permissions**:选 **Allow all actions and reusable workflows**(或 "Allow YOUR-USERNAME, and select non-YOUR-USERNAME, actions and reusable workflows")
- 点 **Save**
- 同一页面下面 **Workflow permissions**:选 **Read and write permissions**
- 点 **Save**

启用后 Actions 标签会出现在 repo 顶部菜单,Pages 也会重新开始构建。

### 问题 2:Workflow 失败,提示 "Permission denied"(推送回 repo 时)

跟上面一样,去 Settings → Actions → General → Workflow permissions,确保选了 "Read and write permissions"。这是最常见的第一次设置时的疏漏。

### 问题 2：访问 `yifanova.com/watchlist/` 显示 404

第一次推送后等 1-2 分钟。GitHub Pages 部署有几十秒到一分钟的延迟。如果还是 404，去 Settings → Pages 确认部署源是 main 分支根目录。

### 问题 3：Workflow 跑成功了，但 `report.html` 没出现在 repo 的 `watchlist/` 下

这意味着 workflow 跑完了但没成功提交。查看最后一步 "Commit and push" 的输出。可能是没改动（如果你已经手动放了一份 report.html 占位，git diff 可能为空）；也可能是权限问题（见问题 1）。

### 问题 4：`yifanova.com/watchlist/report.html` 报错或样式乱

正常 watchlist 的 report.html 是完全自包含的（所有 CSS 和 JS 都内联或从 CDN 加载，不依赖你站点的 `/assets/`）。如果出错，先在 Actions 的 workflow 日志里检查"Generate report"步骤是否成功——可能是 yfinance 一时拿不到数据。下次定时任务会自动重试。

## 后续维护

- **改 watchlist 里的股票**：编辑 `_analyzer/quant_watchlist/core.py` 找到 `DEFAULT_WATCHLIST` 常量，修改后 commit + push。Workflow 会因为 `paths` 触发器自动重新生成报告。
- **改运行时间**：编辑 `.github/workflows/build-report.yml` 里的 `cron: '0 1 * * *'`（UTC 时间）。
- **手动重新生成报告**：Actions 标签 → Run workflow。
- **改入口页的样式或文字**：编辑 `watchlist/index.html`（这是手写的静态页面，不会被 workflow 覆盖）。
- **如果想统一使用你站点的全局样式**：把 `watchlist/index.html` 里 `<style>` 块替换为引用你的 `/assets/style.css` 之类，按照 `chess/` 和 `religion/` 的模式来。

## 隐私确认

这个 watchlist 工具分析的全是公开股票（VOO, AAPL, NVDA, TSLA 等），**没有任何你的个人持仓数据**。可以安全公开托管。如果将来你想把那个有真实持仓的 portfolio analyzer 也部署，那需要不同的方案（认证、私有 repo、Cloudflare Access 等），不是简单的"再加一个子目录"。
