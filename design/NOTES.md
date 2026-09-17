# Profile V2

GitHub Profile README，账号 bluedinosaur233，显示名 Ancuo Loewe。

## 预览

在仓库根目录运行 python3 -m http.server 8082 --bind 127.0.0.1，打开 http://127.0.0.1:8082/preview.html 。可切换原版、新版、深浅色及暂停动效。侧栏引用现有 GitHub 头像；预览样式仅模拟 GitHub，实际站点以 GitHub 渲染为准。

## 主视觉与句子

- WELCOME TO MY WORLD 主标题，冷白网格、蓝粉渐变、斜体、切角卡片与两个链接按钮。
- 原有角色图及本次提供的三张图，共四张循环。每张停留 4.6 秒、淡化过渡 0.5 秒，共 20.4 秒。新增横图完整展示，背景柔化延伸。停留期间蓝色细条持续往返移动，桌面保留微型跳动柱；10 fps 小范围变化通过 WebP 差分压缩保持文件轻量。
- 图片轮播使用全彩动画 WebP（质量 95），桌面 1440×740 / 约 1.97 MB，手机 720×880 / 约 1.70 MB。避免 GIF 的 256 色量化与色带；减少动态效果时使用静态 PNG。
- design/gallery/ 保存用于生成的三张新增图片，已缩放并移除源图片 EXIF 元数据；原始下载文件保持不变。
- 六句话由 design/quotes.json 管理，保持用户给出的原文。逐字出现、停留后切换，总循环约 34 秒。SVG 使用 SMIL，不需要远程动画服务或 JavaScript。
- 英文使用同一 SVG text 内的 tspan 逐字显现，由字体本身决定字宽和字距，避免 M 等宽字母重叠。长句在手机上分行；静态模式显示第一句完整诗句。预览暂停按钮同步暂停图片轮换、文字和贡献日历动效。
- 个人介绍仅保留两行，技术图标沿用 Devicon / Simple Icons 原始标志；来源与许可证位于 design/icons/。

重新生成：

    python3 design/generate-assets.py
    python3 design/generate-quotes.py

主视觉生成需要 Pillow 与 macOS Arial 字体；诗句生成只需要 Python 标准库。

## GitHub 活跃状态

由 design/update-activity.py 从 GitHub 官方公开贡献日历读取真实日期、贡献数与等级，不需要 PAT 或第三方统计服务。卡片显示滚动 365 天贡献总数、最近 30 天贡献数、365 天内活跃天数。桌面显示完整日历，手机显示最近 26 周。日期标注在图片底部，源数据保存在 assets/profile-v2/activity-data.json。

贡献格按周渐入，蓝粉扫光和分隔线光条持续循环；最近 30 天中最后三次实际活跃日期带呼吸描边。动效不改变贡献数或色阶。activity-static.svg 与 activity-mobile-static.svg 提供无动效版本，系统减少动态效果设置和预览暂停按钮均可切换。

    python3 design/test-activity.py
    python3 design/update-activity.py

解析缺失或不完整数据时直接失败，保留上次成功生成的图片。

.github/workflows/update-profile-activity.yml 在发布到仓库默认分支后运行：每天 UTC 02:23（北京时间 10:23）更新，也可手动运行。使用仓库的内置 GITHUB_TOKEN 提交五份活跃状态文件，不需要额外密钥。仓库需启用 Actions 并允许工作流写入内容；GitHub 的计划任务可能延迟，长期无活动的公共仓库也可能停用计划任务。

当前已验证公开数据抓取、图形生成和解析测试；工作流尚未在线运行，因为这次只修改本地文件，未提交或推送。

## 备份

design/README.original.md 保留最初本地 README 原样备份。
