# AI Stock Assistant

一个可以直接部署为网页使用的 A 股交易辅助原型。

> 注意：本项目仅用于个人研究和交易辅助，不构成投资建议，不承诺收益。

## 在线使用

GitHub Pages 开启后，可访问：

```text
https://jason-star888.github.io/stock-assistant/
```

## 目前能力

- 纯前端运行，不需要本地启动 Python 后端
- 输入 A 股股票代码，例如 `600519`、`000001`、`300750`
- 获取近期日线行情
- 计算 MA5 / MA10 / MA20 / MA60、RSI、MACD、成交量变化
- 输出趋势判断、量能判断、风险等级、操作状态和关键价位
- 支持手机浏览器访问

## 使用方式

直接打开网页，输入 6 位 A 股代码：

```text
600519
000001
300750
002594
```

## 建议状态

| 分数 | 建议 |
|---|---|
| 80-100 | 强观察，可轻仓试错 |
| 65-80 | 观察，不追高 |
| 50-65 | 持有为主 |
| 35-50 | 减仓/谨慎 |
| 0-35 | 止损/回避 |

## GitHub Pages 部署

本仓库已添加 GitHub Pages 自动部署工作流：

```text
.github/workflows/pages.yml
```

如果页面没有自动生效，请到仓库：

```text
Settings → Pages → Build and deployment → Source 选择 GitHub Actions
```

然后进入 Actions 页面查看部署结果。

## 免责声明

本工具仅作为个人研究和交易辅助，不构成证券投资建议。市场有风险，交易需谨慎。
