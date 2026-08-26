# -*- coding: utf-8 -*-
"""数学公式提取/渲染管线的冒烟测试"""
import markdown
from markdown_editor import (extract_math, restore_math, get_katex_assets,
                             KATEX_RENDER_SCRIPT, WEBENGINE_AVAILABLE)

src = """# 标题

行内公式 $E = mc^2$ 和 $\\alpha_i + \\beta^2$ 测试。

$$
\\int_0^1 x^2 \\,dx = \\frac{1}{3}
$$

```python
# 代码里的 $x$ 不应被解析
y = 1
```

行内代码 `$not_math$` 也不应解析。

表格里的 | $a_b$ | 公式。

转义 \\$100 不是公式。
"""

text, math_list = extract_math(src)
print("提取到 %d 个公式:" % len(math_list))
for tex, display in math_list:
    print("  [%s] %r" % ("block" if display else "inline", tex))

assert len(math_list) == 4, "应提取 4 个公式"
texs = {(t, d) for t, d in math_list}
assert ("E = mc^2", False) in texs
assert ("\\alpha_i + \\beta^2", False) in texs
assert ("a_b", False) in texs
assert any(d and "int_0^1" in t for t, d in math_list)
assert "not_math" not in [t for t, _ in math_list]
assert "$x$" not in [t for t, _ in math_list]

html = markdown.markdown(text, extensions=["extra", "sane_lists"])
html = restore_math(html, math_list)

assert html.count('class="math-inline"') == 3, html
assert html.count('class="math-display"') == 1, html
assert "<div" in html and "int_0^1" in html
# 块级公式不应残留 <p> 包裹占位符
assert "\x00" not in html, "存在未替换的占位符"
# 代码块内容未被破坏
assert "$x$" in html and "$not_math$" in html

assets = get_katex_assets()
assert assets, "KaTeX 资源未找到"
css, js = assets
assert "file:///" in css and "fonts/" in css
script = KATEX_RENDER_SCRIPT % js
assert "katex.render" in script

print("WEBENGINE_AVAILABLE =", WEBENGINE_AVAILABLE)
print("KaTeX css %d bytes, js %d bytes" % (len(css), len(js)))
print("ALL TESTS PASSED")
