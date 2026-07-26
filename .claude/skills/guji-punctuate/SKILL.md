---
name: guji-punctuate
description: Batch-add punctuation to unpunctuated Classical Chinese (文言文) JSON files ({"id":..., "pages":[...]} structure, e.g. daizhige.org / guishui exports) via LinguaGacha's headless CLI mode with the LZH target language. Use when asked to punctuate, 加标点, or batch-process a directory of classical-Chinese text JSON files.
---

# 文言文批量加标点

调用 LinguaGacha 仓库自带的 `--cli translate` 命令，目标语言固定用 `LZH`
（`中文（繁体，文言文）`，见 `src/domain/language.ts`）——这个目标语言在
代码层面被硬编码为标点复原提示词，不会被当成普通翻译，选它就只做“给原文
逐字保留、加标点”这一件事。

## 前置条件（一次性）

1. 仓库已 `npm install`。
2. 至少用 GUI 跑过一次 `npm run dev` 并在「模型管理」里配置好一个可用模型
   （CLI 复用当前应用设置里的激活模型，不在命令行传 Key）。
3. 构建产物 `build/dist-electron/index.js` 存在——`batch-punctuate.sh` 会在
   缺失时自动跑一次 `electron-vite build`（比 `npm run build` 轻，不打包安
   装包）。

## 用法

```bash
.claude/skills/guji-punctuate/batch-punctuate.sh <输入文件或目录...> --output-dir <目录>
```

- 输入可以是单个 `{"id": ..., "pages": [...]}` JSON 文件，也可以是一个目录
  （内部所有匹配格式的 `.json` 都会被处理），可重复传入多个。
- 一次脚本调用只起一个 Electron 进程，内部任务引擎自己按并发处理所有输
  入条目，**不需要外层再套 for 循环逐文件调用**——那样每次都要重新拉起
  一个 Electron 进程，纯属浪费。真正要循环的场景只有“输入源分散在多个不
  连续的目录/文件”，直接把它们都列在参数里即可。
- 输出文件名与输入同名，写入 `--output-dir`；`id` 字段原样保留。若输入是
  目录，输出会在 `--output-dir` 下保留一层同名子目录（例如输入目录叫
  `skill-test-src`，输出就落在 `<output-dir>/skill-test-src/00155.json`），
  这是引擎保留源目录结构的既有行为，不是脚本 bug。
- stdout 是逐行 JSON（`started` / `progress` / `finished`），可直接喂给别
  的脚本解析进度；机器可读，不需要另外截屏或轮询 GUI。
- 退出码：成功 0，运行期错误（如模型请求失败）1，参数错误 2。

## 示例：批量处理一批连续编号的文件

```bash
mkdir -p /tmp/guji-src /tmp/guji-out
for id in $(seq -w 155 165); do
  curl -sS -o "/tmp/guji-src/00${id}.json" \
    "https://shuiluo-jinmen-classics.daizhige.org/data/text/00${id}.json"
done

.claude/skills/guji-punctuate/batch-punctuate.sh /tmp/guji-src --output-dir /tmp/guji-out
```

下载环节的 for 循环是必要的（每个 URL 独立请求），但转换本身只调一次
`batch-punctuate.sh`，把整个目录一起丢给它。

## 转换后必须校验：模型会偷偷"纠正"原文用字

实测发现（不是理论风险）：即使提示词明确要求逐字保留原文，仍有相当比例
的页面（实测两个样本文件里约 35%~40%）被模型悄悄换掉了个别字——常见
模式是把它认为的"错字/异体字/简体字"换成"正确写法"（如 户→戶、並→
并），少数情况下还会整字替换或丢字。这种改动去标点之后一比对就能发
现，但表面读起来通顺，光看输出内容根本看不出来。**跑完一定要校验，不
要直接信任输出。**

```bash
python3 .claude/skills/guji-punctuate/verify-fidelity.py <源目录> <输出目录>
```

- 逐页去掉标点符号后比对原文和输出，报告"完全没加标点"和"疑似改字"两
  类问题页面的下标，退出码非 0 表示发现问题。
- 报告的页面需要人工用原文核对，不能自动改回去——因为脚本没法区分"模
  型改错了"和"原文本来就该这样但恰好长得像"这种边界情况。
- 已经在 `resource/translation_prompt/template/{zh,en}/base_lzh.txt` 里加
  了一条专门针对这个失败模式的强调（举了 户/戶、並/并 的具体例子），能
  降低一部分误改，但不保证归零，模型本身有"自作主张纠错"的倾向，换个
  模型误改率可能不一样，批量跑大量文件前建议先抽样校验。

## 已知限制

- 目标语言硬编码为 `LZH`，不支持真正的多语言翻译；如果需要普通翻译，直
  接用 `--target-language` 传别的语言码，不要用这个脚本包装的默认值。
- `verify-fidelity.py` 只能发现"变了"，不能自动判断哪个版本对；改字问题
  发现后目前只能靠重跑该页（更换模型/降低批量大小/手动修正）解决。
- CLI 依赖 GUI 侧已保存的当前激活模型和其 `input_token_limit` 等设置；
  批量跑之前如果发现效率低（一次只处理一两句），先去「模型管理」调大对
  应模型的「输入 Token 限制」。
