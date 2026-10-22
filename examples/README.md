# examples

## vertical-1080x1920.html

1080×1920 竖屏的完整参考实现：**33 镜 / 224 拍 / 120.8 秒**，主题《享乐适应》。

读这份文件时可以按这个顺序看：

1. `SHOTS` 表：每镜的起始拍、拍数、用哪台"机器"（`fn`）、音效。拍数就是镜头长度，改节奏只改这里。
2. `draw(t)`：逐帧入口。切点三件套（甩镜 / 压暗 / 缩放回弹）都在这里，不在各镜内部。
3. `scene*` 函数：每台机器一个函数，参数用 `p` 传（水位、曲线、文字、数字）。
4. `hud()`：贯穿全片的「第 N 次回放 + t = xxx ms」。
5. `grainLayer() / rain()`：质感层。注意颗粒是**慢速平移**，不是每帧随机跳。

依赖同目录同级工程的 `vendor/om.js` 与 `assets/fonts/`（huashu-motion 的 `om new` 会生成），
直接放在别的目录里跑不起来。

### 想改成自己的片子

- 换文案：`data-composition-variables` 里的 `title` / `subtitle` / `mark` / `nextLine`
- 换节奏：只改 `add(fn, p, d)` 的第三个参数（拍数）
- 换机器：写一个新的 `sceneXxx(u, p)`，在 `EASE` 映射里登记
- 换配色：`CY` / `OR` / `INK` 三个常量
