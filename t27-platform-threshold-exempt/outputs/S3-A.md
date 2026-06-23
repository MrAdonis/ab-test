---
name: html-email-template
description: Generate HTML email templates with correct client compatibility (600px table layout, inline CSS) and good visual taste (line height, color restraint, typographic hierarchy). Triggers on requests to "write an email template", "make an HTML email", "build email newsletter", "邮件模板", or any email design/coding task.
---

# HTML Email Template Skill

## When to Use

触发：用户要求生成 HTML 邮件模板、邮件 newsletter、transactional email、促销邮件正文 HTML。

不适用（用其他工具）：

- 纯文字邮件草稿（用写作工具，不需要 HTML） 
- 邮件发送 API 集成（用 ESP 的 SDK 文档，本 skill 只管模板本身）
- 落地页 / 网页（用 web 组件，不受邮件客户端约束）

## Platform Constraints（邮件客户端硬性要求，不可绕过）

邮件客户端不是浏览器。以下约束是**兼容性底线**，违反任一条将导致主流客户端（Gmail / Outlook / Apple Mail）渲染错乱。

### 布局

**必须用 `<table>` 布局，禁止 `flexbox` / `grid` / `position: absolute`。**

Outlook 使用 Word 渲染引擎，只认 table 布局。Gmail 剥离 `<head>` 里的 `<style>`，任何非 inline 样式都可能失效。

```html
<!-- Good：table 嵌套布局 -->
<table width="600" cellpadding="0" cellspacing="0" border="0" align="center">
  <tr>
    <td style="padding: 24px 32px;">
      正文内容
    </td>
  </tr>
</table>

<!-- Bad：div + flex -->
<div style="display: flex; max-width: 600px;">
  <div>正文内容</div>
</div>
```

### 宽度

正文容器固定 **width="600"**（属性，不是 style）。外层加一个 100% 宽的容器背景色兼容宽屏：

```html
<table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5;">
  <tr>
    <td align="center">
      <table width="600" cellpadding="0" cellspacing="0" border="0">
        <!-- 实际内容 -->
      </table>
    </td>
  </tr>
</table>
```

### CSS

**所有样式必须 inline**（`style="..."` 直接写在元素上）。禁止 `<link>` 外部 CSS，`<head>` 里的 `<style>` 仅作为辅助（支持它的客户端会用，不支持的忽略）。

```html
<!-- Good -->
<td style="font-family: Arial, sans-serif; font-size: 16px; color: #1a1a1a; line-height: 1.6;">

<!-- Bad：class 引用外部样式 -->
<td class="body-text">
```

### 字体

只用系统安全字体栈，不引 Google Fonts（会被部分客户端过滤）：

```
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
```

衬线场景：`Georgia, 'Times New Roman', serif;`

### 图片

必须带 `alt`，宽度用属性而非 style，不依赖图片传递关键信息（大量客户端默认屏蔽图片）：

```html
<img src="..." width="600" alt="产品截图" style="display: block; max-width: 100%;" />
```

## Visual Quality Thresholds（品味维度，带依据的可测阈值）

### 排版层级

字号层级最多 3 级（主标题 / 正文 / 辅助说明），避免层级膨胀导致视觉噪音：

| 用途 | 字号 | 字重 |
|------|------|------|
| 主标题 (H1) | 24–28px | 700 |
| 副标题 / 节标题 | 18–20px | 600 |
| 正文 | 16px | 400 |
| 辅助说明 / footer | 12–14px | 400 |

**依据**：WCAG 2.1 §1.4.4 要求正文最小 16px（100% 缩放无障碍基线）；主标题不超过正文 1.75x 是 Bringhurst《The Elements of Typographic Style》的视觉层级黄金比例上限。

### 行高

正文行高 **1.6–1.7**，标题 **1.2–1.3**。

**依据**：Baymard Institute 2022 邮件可读性研究——行高 < 1.4 显著增加 skimming 跳读率；> 1.8 使段落感消失、变成散列感。

```html
<!-- Good -->
<td style="font-size: 16px; line-height: 1.65;">

<!-- Bad：行高过紧 -->
<td style="font-size: 16px; line-height: 1.2;">
```

### 配色约束

主色 ≤ 2 种（品牌色 + 中性色），强调色单独 1 种仅用于 CTA 按钮。背景色与正文对比度 ≥ 4.5:1（WCAG AA）；CTA 按钮对比度 ≥ 3:1（WCAG AA 大文本）。

**依据**：WCAG 2.1 §1.4.3 最低对比度标准；Cleveland & McGill 1984 研究表明人眼在单一视野内辨别超过 5 种颜色时认知负担显著上升，邮件场景下 3 色是实践上限。

```html
<!-- Good：单一品牌色 + 中性色，CTA 有强对比 -->
<a style="background-color: #0052cc; color: #ffffff; padding: 12px 24px; border-radius: 4px; text-decoration: none; font-weight: 600;">
  立即查看
</a>

<!-- Bad：多色竞争 -->
<a style="background-color: #e63946; color: #ffd166;">...</a>
```

### 内容密度

单封邮件**主 CTA 只有 1 个**（次级链接可多，但视觉层级明显低于主 CTA）。正文段落每段 ≤ 4 句，段间距 ≥ 16px（`padding-bottom: 16px` 或 `margin-bottom: 16px`，邮件用 padding 更安全）。

无法量化，保留文字描述：正文与留白有呼吸感——内容区左右内边距不少于 24px，不要把 600px 塞满。

## Workflow

**Step 1：明确类型和内容**

接收到邮件模板需求后，先确认：

- 邮件类型：transactional（验证码/订单/通知）/ newsletter / 促销 / 欢迎邮件
- 主色 / 品牌色（十六进制，没有则用 `#0052cc` 默认蓝）
- 关键内容结构（有无图片、几个 section、CTA 文案）

类型决定结构，transactional 最简（logo + 正文 + CTA），newsletter 最复杂（多 section）。

**Step 2：生成 HTML**

按以下顺序输出：

1. `<!DOCTYPE html>` 开头，`<html lang="zh">` 或对应语言
2. `<head>` 内含 `<meta charset="UTF-8">` + `<meta name="viewport" ...>` + 可选的 `<style>` 辅助样式（媒体查询做响应式降级）
3. 全局外层 100% 宽背景 table
4. 600px 内容 table（header / body sections / footer 各一个 `<tr>`）
5. 所有样式 inline

**Step 3：交付物**

输出完整的 `.html` 文件内容，可直接复制到 ESP（Mailchimp / SendGrid / 自建）。如有多个版本（A/B test 变体），分开输出并标注差异点。

## Template Skeleton

以下是最小可用骨架，所有项目在此基础上扩展：

```html
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <title>邮件标题</title>
  <!--[if mso]>
  <noscript>
    <xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml>
  </noscript>
  <![endif]-->
</head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;">

  <!-- 外层背景 -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f5f5f5;">
    <tr>
      <td align="center" style="padding: 32px 16px;">

        <!-- 内容容器 600px -->
        <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden;">

          <!-- Header -->
          <tr>
            <td style="padding: 32px; background-color: #ffffff; border-bottom: 1px solid #e8e8e8;">
              <img src="logo.png" width="120" alt="品牌 Logo" style="display: block;" />
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding: 40px 32px;">
              <h1 style="margin: 0 0 16px; font-size: 26px; font-weight: 700; color: #1a1a1a; line-height: 1.3;">
                标题文字
              </h1>
              <p style="margin: 0 0 16px; font-size: 16px; color: #4a4a4a; line-height: 1.65;">
                正文段落，简洁说明核心信息。一段不超过 4 句。
              </p>
              <!-- CTA 按钮 -->
              <table cellpadding="0" cellspacing="0" border="0" style="margin-top: 32px;">
                <tr>
                  <td style="border-radius: 6px; background-color: #0052cc;">
                    <a href="{{CTA_URL}}" style="display: inline-block; padding: 14px 28px; font-size: 16px; font-weight: 600; color: #ffffff; text-decoration: none; border-radius: 6px;">
                      立即查看
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 24px 32px; background-color: #f8f8f8; border-top: 1px solid #e8e8e8;">
              <p style="margin: 0; font-size: 12px; color: #999999; line-height: 1.6;">
                你收到这封邮件，是因为 xxx。
                <a href="{{UNSUBSCRIBE_URL}}" style="color: #999999;">退订</a>
              </p>
            </td>
          </tr>

        </table>
        <!-- /内容容器 -->

      </td>
    </tr>
  </table>
  <!-- /外层背景 -->

</body>
</html>
```

## Gotchas

> 以下是邮件 HTML 的高发坑，覆盖兼容性和品味两个维度。

- **Outlook 不识别 `border-radius` on `<td>`** → 根因：Word 渲染引擎忽略 CSS border-radius。规避：圆角按钮用嵌套 `<table>` 套 `<td>` 方式（见 skeleton 中 CTA 部分），不直接给 `<a>` 或 `<td>` 设 border-radius；容器圆角用图片背景或接受 Outlook 直角降级。

- **Gmail 剥离 `<head>` 内 `<style>` 里的伪类（`:hover`）** → 根因：Gmail 的 CSS 白名单不含交互伪类。规避：不依赖 `:hover` 状态做关键视觉，按钮颜色写死 inline style。

- **`margin` 在部分客户端不生效，用 `padding` 替代** → 根因：Outlook 2007-2019 对 block 元素 margin 支持不一致。规避：所有间距一律用 `padding`，`<p>` / `<h1>` 的默认 margin 要在 inline style 里显式重置（`margin: 0 0 16px`）。

- **图片在宽度上同时设 `width` 属性和 `max-width: 100%` style** → 根因：`width` 属性让老 Outlook 识别尺寸，`max-width` 让移动端响应式缩小；两者互补，缺任一条在某个场景下破相。

- **CTA 按钮不用 `<a>` 套 `background-color`，用嵌套 table** → 根因：纯 `<a>` 的 background-color 在 Outlook 完全不渲染（white box）。规避：CTA 用 `<table><tr><td style="background-color:...">` 包住 `<a>`，这是唯一跨客户端可靠路径。

- **字号别用 `px` 以外的单位** → 根因：`em` / `rem` 在多个邮件客户端计算基准不统一。规避：字号、行高、padding 全用 `px`（行高例外，用无单位数字如 `1.65` 更健壮）。

- **Preheader 文字（预览摘要）不加会显示乱码** → 根因：邮件客户端用正文第一段文字做预览；如不控制，table 的空格/零宽字符会被显示出来。规避：`<body>` 第一个元素加隐藏的 preheader `<span style="display:none; max-height:0; overflow:hidden;">`，填写 40-90 字的预览摘要。
