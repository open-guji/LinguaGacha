

<div align=center><img src="https://github.com/user-attachments/assets/cdf990fb-cf03-4370-a402-844f87b2fab8" width="256px;"></div>
<div align=center><img src="https://img.shields.io/github/v/release/neavo/LinguaGacha"/>   <img src="https://img.shields.io/github/license/neavo/LinguaGacha"/>   <img src="https://img.shields.io/github/stars/neavo/LinguaGacha"/></div>
<p align='center'>使用 AI 能力一键翻译 小说、游戏、字幕 等文本内容的次世代文本翻译器</p>

## README 🌍
- [ [中文](./README.md) ] | [ [English](./README_EN.md) ] | [ [日本語](./README_JA.md) ]

## 概述 📢
- [LinguaGacha](https://github.com/neavo/LinguaGacha) (/ˈlɪŋɡwə ˈɡɑːtʃə/)，使用 AI 技术次世代文本翻译器
- 开箱即用，（几乎）无需设置，功能的强大，不需要通过繁琐的设置来体现
- 支持 `中` `英` `日` `韩` `俄` `德` `法` `意` 等 16 种语言的一键互译
- 支持 `字幕`、`电子书`、`游戏文本` 等多种文本类型与文本格式
- 支持 `OpenAI` `Google` `Anthropic` `SakuraLLM` 等各种本地或在线接口

> <img width="2570" height="1605" alt="01" src="https://github.com/user-attachments/assets/898f6606-9c74-47db-b63e-33d544cfdf15" />

> <img width="2570" height="1605" alt="02" src="https://github.com/user-attachments/assets/7f6d6556-d6b2-4fb1-b509-2d8272814290" />

## 特别说明 ⚠️
- 如您在翻译过程中使用了 [LinguaGacha](https://github.com/neavo/LinguaGacha) ，请在作品信息或发布页面的显要位置进行说明！
- 如您的项目涉及任何商业行为或者商业收益，在使用 [LinguaGacha](https://github.com/neavo/LinguaGacha) 前，请先与作者联系以获得授权！

## 本 Fork 新增：文言文加标点 🖋️
- 本 fork 在原版基础上新增了「给未标点文言文加标点」的专用能力，不是通用翻译功能的附带效果
- 使用方法：
  1. 正常拖入待处理文件创建工程
  2. 在 `基础设置` 中，将 `译文语言` 设置为 `中文（繁体，文言文）`
  3. 在 `工作台` 中执行 `翻译`，输出即为原文逐字保留、只添加了标点的文本
- 该目标语言由代码层面强制走固定的标点复原提示词，与自定义提示词、预设开关无关，选中它就不可能被当成普通翻译误用：
  - 只允许插入或修正标点符号，原文的错字、异体字、生僻字一律逐字保留，不纠正、不替换、不转换简繁字形
  - 严禁将文言文转换为白话文，严禁意译、改写或补全原文没有的内容
- `校对` 页相应新增了 `未添加标点` 警告：当模型对某条内容原样返回、完全没有添加标点时会被单独标出，不再和正常结果一起被笼统地判定为「相似度过高」
- 新增内置预设模型 `荀子大模型`（[xunziallm.njau.edu.cn](http://xunziallm.njau.edu.cn/)，古汉语专用、OpenAI 兼容接口），在 `模型管理` 的预设模型卡片中直接选用即可，效果请自行实测
- 新增支持"谷水书页" JSON 格式（`{"id": ..., "pages": [...]}` 结构）的导入导出，用于对接谷水藏书类文言文原始素材

## 功能优势 📌
- 极快的翻译速度，十秒钟一份字幕，一分钟一本小说，五分钟一部游戏
- 一键生成术语表，保证角色姓名等专有名词在整部作品中的译名统一　`👈👈 独家绝技`
- 最优的翻译质量，无论是 旗舰模型 `诸如 DeepSeek-R1` 还是 本地小模型　`诸如 Qwen2.5-7B`
- 同类应用中最强的样式与代码保留能力，显著减少后期工作量，是制作内嵌汉化的最佳选择
  - `.md` `.ass` `.epub` 格式几乎可以保留所有原有样式
  - 大部分的 `WOLF`、`RenPy`、`RPGMaker`、`Kirikiri` 引擎游戏无需人工处理，即翻即玩　`👈👈 独家绝技`

## 基本流程 🛸
- 从 [发布页](https://github.com/neavo/LinguaGacha/releases) 下载应用
  - Windows:
    - 根据 CPU 类型下载 `*_Windows_x64.zip` 或 `*_Windows_arm64.zip`
    - 解压后双击 `app.exe` 启动
  - macOS:
    - 根据 CPU 类型下载 `*_macOS_x64.dmg` 或 `*_macOS_arm64.dmg`
    - 拖拽到应用程序文件夹，先不要启动
    - 打开终端输入 `sudo xattr -rd com.apple.quarantine /Applications/LinguaGacha.app` 然后回车
    - 输入系统密码，关闭终端，可以正常运行了
  - Linux:
    - 根据 CPU 类型下载 `*_Linux_x64.AppImage` 或 `*_Linux_arm64.AppImage`
    - 添加执行权限 `chmod +x LinguaGacha*.AppImage`
    - 运行 `./LinguaGacha*.AppImage`
- 获取一个可靠的 AI 大模型接口，建议选择其一：
  - [ [本地接口](https://github.com/neavo/OneClickLLAMA) ]，免费，需至少 8G 显存的独立显卡，Nvidia 显卡为佳
  - [ [DeepSeek](https://github.com/neavo/LinguaGacha/wiki/DeepSeek) ]，最便宜，速度快，质量高，无显卡要求
  - [ [VolcEngine](https://github.com/neavo/LinguaGacha/wiki/VolcEngine) ]，贵一点点，**当前最佳翻译模型**，无显卡要求 `👈👈 推荐`
- 准备要翻译的文本
  - `字幕`、`电子书` 等一般不需要预处理
  - `游戏文本` 需要根据游戏引擎选择合适的工具进行提取
- 启动应用
  - 将 `待翻译的文件` 拖到页面上创建项目
  - 在 `模型管理` 中设置并激活要使用的模型
  - 在 `基础设置` 中设置原文语言、译文语言等必要信息
  - 在 `工作台` 中执行 `分析` 提取术语表
  - 在 `工作台` 中执行 `翻译` 完成翻译
  - Enjoy!

## 使用教程 📝
- 综合
  - [基础教程](https://github.com/neavo/LinguaGacha/wiki/BasicTutorial)　`👈👈 手把手教学，有手就行，新手必看`
  - [高质量翻译 WOLF 引擎游戏的最佳实践](https://github.com/neavo/LinguaGacha/wiki/BestPracticeForWOLF)
  - [高质量翻译 RenPy 引擎游戏的最佳实践](https://github.com/neavo/LinguaGacha/wiki/BestPracticeForRenPy)
  - [高质量翻译 RPGMaker 系列引擎游戏的最佳实践](https://github.com/neavo/LinguaGacha/wiki/BestPracticeForRPGMaker)
- 视频教程
  - [How to Translate RPGMV with LinguaGacha and Translator++ (English)](https://www.youtube.com/watch?v=wtV_IODzi8I)
- 功能说明
  - [命令行模式](https://github.com/neavo/LinguaGacha/wiki/CLIMode)
  - [术语表](https://github.com/neavo/LinguaGacha/wiki/Glossary)　　[文本保护](https://github.com/neavo/LinguaGacha/wiki/TextPreserve)　　[文本替换](https://github.com/neavo/LinguaGacha/wiki/Replacement)　　
  - [MTool 优化器](https://github.com/neavo/LinguaGacha/wiki/MToolOptimizer) [百宝箱 - 繁简转换](https://github.com/neavo/LinguaGacha/wiki/TSConversion)
- 你可以在 [Wiki](https://github.com/neavo/LinguaGacha/wiki) 找到各项功能的更详细介绍，也欢迎在 [讨论区](https://github.com/neavo/LinguaGacha/discussions) 投稿你的使用心得

## 文本格式 🏷️
- 字幕（.srt .ass）
- 电子书（.txt .epub）
- Markdown（.md）
- [RenPy](https://www.renpy.org) 导出游戏文本（.rpy）
- [MTool](https://mtool.app) 导出游戏文本（.json）
- [SExtractor](https://github.com/satan53x/SExtractor) 导出游戏文本（.txt .json .xlsx）
- [VNTextPatch](https://github.com/arcusmaximus/VNTranslationTools) 导出游戏文本（.json）
- [Translator++](https://dreamsavior.net/translator-plusplus) 项目文件（.trans）
- [Translator++](https://dreamsavior.net/translator-plusplus) 导出游戏文本（.xlsx）
- [WOLF 官方翻译工具](https://silversecond.booth.pm/items/5151747) 导出游戏文本（.xlsx）
- 谷水书页 `id`/`pages` 结构（.json）　`👈👈 本 fork 新增`
- 具体示例可见 [Wiki - 支持的文件格式](https://github.com/neavo/LinguaGacha/wiki/%E6%94%AF%E6%8C%81%E7%9A%84%E6%96%87%E4%BB%B6%E6%A0%BC%E5%BC%8F)，更多格式将持续添加，你也可以在 [ISSUES](https://github.com/neavo/LinguaGacha/issues) 中提出你的需求

## 近期更新 📅
- 20260725 v0.103.0
  - 增加 `德语` 界面 @Errorism1
  - 调整与改进 [#597](https://github.com/neavo/LinguaGacha/issues/597) [#658](https://github.com/neavo/LinguaGacha/issues/658) [#665](https://github.com/neavo/LinguaGacha/issues/665) [#666](https://github.com/neavo/LinguaGacha/issues/666) [#667](https://github.com/neavo/LinguaGacha/issues/667)

## 开发指南 🛠️
- 安装 [ [Go](https://go.dev) ] 和 [ [`Node.js`](https://nodejs.org) ]，然后 `npm install`
- 更新依赖 `npm update`
- 运行应用 `npm run dev`
- 提交 PR 前请根据改动范围执行 [`docs/WORKFLOW.md`](./docs/WORKFLOW.md) 中的对应验证
- 非开发者请直接在 [发布页](https://github.com/neavo/LinguaGacha/releases) 下载打包版本

## 问题反馈 😥
- 运行时的日志保存在应用根目录下的 `log` 等文件夹
- 反馈问题的时候请附上这些日志文件
- 你也可以来群组讨论与反馈
  - QQ - 41763231⑥
  - Discord - https://discord.gg/pyMRBGse75

## Star History

<a href="https://www.star-history.com/?repos=neavo%2FLinguaGacha&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=neavo/LinguaGacha&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=neavo/LinguaGacha&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=neavo/LinguaGacha&type=date&legend=top-left" />
 </picture>
</a>
