# Futu OpenAPI 文档 (Python)


---

# 介绍

## 概述
量化接口，为您的程序化交易，提供丰富的行情和交易接口，满足每一位开发者的量化投资需求，助力您的宽客梦想。

牛牛用户可以 [点击这里](https://www.futunn.com/OpenAPI)了解更多。

Futu API 由 OpenD 和API SDK组成：
* OpenD 是 Futu API 的网关程序，运行于您的本地电脑或云端服务器，负责中转协议请求到富途后台，并将处理后的数据返回。
* API SDK是富途为主流的编程语言（Python、Java、C#、C++、JavaScript）封装的SDK，以方便您调用，降低策略开发难度。如果您希望使用的语言没有在上述之列，您仍可自行对接裸协议，完成策略开发。

下面的框架图和时序图，帮助您更好地了解 Futu API。

 ![openapi-frame](../img/nnopenapi-frame.png)

 ![openapi-interactive](../img/nnopenapi-interactive.png)

初次接触 Futu API，您需要进行如下两步操作：

第一步，在本地或云端安装并启动一个网关程序 [OpenD](../quick/opend-base.md)。

OpenD 以自定义 TCP 协议的方式对外暴露接口，负责中转协议请求到富途服务器，并将处理后的数据返回，该协议接口与编程语言无关。

第二步，下载 Futu API，完成 [环境搭建](../quick/env.md)，以便快速调用。

为方便您的使用，富途对主流的编程语言，封装了相应的 API SDK（以下简称 Futu API）。


## 账号
Futu API 涉及 2 类账号，分别是 **平台账号** 和 **综合账户**。

### 平台账号

平台账号是您在富途的用户 ID（牛牛号），此账号体系适用于富途牛牛 APP、Futu API。  
您可以使用平台账号（牛牛号）和登录密码，登录 OpenD 并获取行情。

### 综合账户
综合账户支持以多种货币在同一个账户内交易不同市场品类（港股、美股、A股通、基金）。您可以通过一个账户进行全市场交易，不需要再管理多个账户。  
综合账户包括综合账户 - 证券，综合账户 - 期货，综合账户 - 加密货币等业务账户：  
* 综合账户 - 证券，用于交易全市场的股票、ETFs、期权等证券类产品。  
* 综合账户 - 期货，用于交易全市场的期货产品，目前支持香港市场期货、美国市场 CME Group 期货、新加坡市场期货、日本市场期货。
* 综合账户 - 加密货币，用于交易加密货币币对，目前支持 FUTU HK、moomoo US、moomoo SG 券商。


## 功能
Futu API 的功能主要有两部分：行情和交易。

### 行情功能

#### 行情数据品类

支持香港、美国、A 股、新加坡、马来西亚、日本市场的行情数据，涉及的品类包括股票、指数、期权、期货等，具体支持的品种见下表。  
获取行情数据需要相关权限，如需了解行情权限的获取方式以及限制规则，请 [点击这里](./authority.md#2867)。

<table>
    <tr>
        <th>市场</th>
        <th>品种</th>
        <th>牛牛用户</th>
    </tr>
    <tr>
        <td rowspan="5">香港市场</td>
	    <td>股票、ETFs、窝轮、牛熊、界内证</td>
	    <td align="center">✓</td>
    </tr>
    <tr>
        <td>期权</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>指数</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>板块</td>
        <td align="center">✓</td>
    </tr>
    <tr>
        <td rowspan="6">美国市场</td>
	    <td>股票、ETFs (含纽交所、美交所、纳斯达克上市的股票、ETFs)</td>
	    <td align="center">✓</td>
    </tr>
    <tr>
	    <td>OTC 股票</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td>期权  (含普通股票期权、指数期权)</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>指数</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td>板块</td>
        <td align="center">✓</td>
    </tr>
    <tr>
        <td rowspan="3">A 股市场</td>
	    <td>股票、ETFs</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>指数</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>板块</td>
        <td align="center">✓</td>
    </tr>
    <tr>
        <td rowspan="2">新加坡市场</td>
	    <td>股票、ETFs、REITs、DLCs、结构性窝轮</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="1">马来西亚市场</td>
        <td>股票、ETFs、窝轮、REITs</td>
        <td align="center">✓</td>
    </tr>
    <tr>
        <td rowspan="2">日本市场</td>
        <td>股票、ETFs</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="1">澳大利亚市场</td>
        <td>股票、ETFs</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="1">环球市场</td>
        <td>外汇</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="1">加密货币市场</td>
        <td>加密货币</td>
        <td align="center">✓</td>
    </tr>
</table>

#### 行情数据获取方式

* 订阅并接收实时报价、实时 K 线、实时逐笔、实时摆盘等数据推送
* 拉取最新市场快照，历史 K 线等

### 交易功能

#### 交易能力
支持香港、美国、A 股、新加坡、日本、马来西亚等多个市场的交易能力，涉及的品类包括股票、期权、期货等，具体见下表：

<table>
    <tr>
        <th rowspan="2">市场</th>
        <th rowspan="2">品种</th>
        <th rowspan="2">模拟交易</th>
        <th colspan="7">真实交易</th>
    </tr>
    <tr>
        <th>FUTU HK</th>
        <th>Moomoo US</th>
        <th>Moomoo SG</th>
        <th>Moomoo AU</th>
        <th>Moomoo MY</th>
        <th>Moomoo CA</th>
        <th>Moomoo JP</th>
    </tr>
    <tr>
        <td rowspan="3">香港市场</td>
	    <td>股票、ETFs、窝轮、牛熊、界内证</td>
	    <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td>期权 (含指数期权，需使用期货账户交易)</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="3">美国市场</td>
	    <td>股票、ETFs</td>
	    <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
    </tr>
    <tr>
        <td>期权</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="2">A 股市场</td>
	    <td>A 股通股票</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td>非 A 股通股票</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="2">新加坡市场</td>
	    <td>股票、ETFs、结构性窝轮、REITs、DLCs</td>
        <td align="center">X</td>
        <td align="center">✓ (FUTU HK暂不支持交易结构性窝轮)</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td rowspan="2">日本市场</td>
        <td>股票、ETFs、REITs</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">✓</td>
    </tr>
    <tr>
        <td>期货</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td rowspan="1">马来西亚市场</td>
        <td>股票、ETFs</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td rowspan="1">澳大利亚市场</td>
        <td>股票、ETFs</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td rowspan="1">加拿大市场</td>
        <td>股票</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td rowspan="1">加密货币市场 (需开通加密货币交易权限)</td>
        <td>加密货币</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
</table>

#### 交易方式
真实交易和模拟交易使用同一套交易接口。


## 特点

1. 全平台多语言：
* OpenD 支持 Windows、MacOS、CentOS、Ubuntu
* Futu API 支持 Python、Java、C#、C++、JavaScript 等主流语言
2. 稳定极速免费：
* 稳定的技术架构，直连交易所一触即达
* 下单最快只需 0.0014 s
* 通过 Futu API 交易无附加收费
3. 丰富的投资品类：
* 支持美国、香港、新加坡、日本、马来西亚、加密货币等多个市场的实时行情、实盘交易及部分品类模拟交易
4. 专业的机构服务：
* 定制化的行情交易解决方案

---

# 权限与额度

## 登录
### 登录账号

Futu API 现已全面放开登录限制，进一步优化开发体验。无需开户限制，您可使用富途牛牛号（或注册时使用的手机号/邮箱）登录 OpenD。

### 合规确认

首次登录成功后，您需要完成问卷评估与协议确认，才能继续使用 Futu API。牛牛用户请 [点击这里](https://www.futunn.com/about/api-disclaimer)。


## 行情数据
行情数据的限制主要体现在以下几方面：
* 行情权限 —— 获取相关行情数据的权限
* 接口限频 —— 调用行情接口的频率限制
* 订阅额度 —— 同时订阅的实时行情的数量
* 历史 K 线额度 —— 每 7 天最多可拉取多少个标的的历史 K 线

### 行情权限

通过 Futu API 获取行情数据，需要相应的行情权限，Futu API 的行情权限跟 APP 的行情权限不完全一样，不同的权限等级对应不同的时延、摆盘档数以及接口使用权限。

部分品种行情，需要购买行情卡后方可获取，具体获取方式见下表。

<table>
    <tr>
        <th>市场</th>
        <th>标的类别</th>
        <th>获取方式</th>
    </tr>
    <tr>
        <td rowspan="5">香港市场</td>
	    <td>证券类产品（含股票、ETFs、窝轮、牛熊、界内证）</td>
	    <td  rowspan="3" align="left">• 境内认证客户：免费获取 LV2 行情。如需获得 SF 权限，请购买 <a href="https://qtcard.futunn.com/intro/sf?type=10&is_support_buy=1&clientlang=0" target="_blank">港股高级全盘行情</a>  <br>• 国际客户：免费获取 LV1 行情。如需获得 LV2 权限，请购买 <a href="https://qtcard.futunn.com/intro/hklv2?type=1&is_support_buy=1&clientlang=0" target="_blank">港股 LV2 高级行情</a> 。如需获得 SF 权限，请购买 <a href="https://qtcard.futunn.com/intro/sf?type=10&is_support_buy=1&clientlang=0" target="_blank">港股高级全盘行情</a></td>
    </tr>
    <tr>
	    <td>指数</td>
    </tr>
    <tr>
	    <td>板块</td>
    </tr>
    <tr>
        <td>期权</td>
	    <td  rowspan="2" align="left">• 境内认证客户：推广期免费获取 LV2 行情  <br>• 国际客户：免费获取 LV1 行情，如需获得 LV2 权限，请购买 <a href="https://qtcard.futunn.com/intro/hk-derivativeslv2?type=8&clientlang=0&is_support_buy=1" target="_blank">港股期权期货 LV2 高级行情</a></td>
    </tr>
    <tr>
	    <td>期货</td>
    </tr>
    <tr>
        <td rowspan="6">美国市场</td>
	    <td>证券类产品（含纽交所、美交所、纳斯达克上市的股票、ETFs）</td>
	    <td  rowspan="2" align="left">• 推广期<b>免费获取</b> LV3 行情（Nasdaq Baisc + Nasdaq TotalView + NYSE Arcabook） <br>• NYSE Arcabook 深度摆盘获取需先完成 <a href="https://qtcard.futunn.com/question/us?lang=zh-cn" target="_blank">非专业用户评估问卷 </a></td>
    </tr>
    <tr>
	    <td>板块</td>
    </tr>
    <tr>
	    <td>OTC 股票</td>
        <td  align="left">暂不支持获取</td>
    </tr>
    <tr>
        <td>期权（含普通股票期权、指数期权）</td>
	    <td  align="left">• 达到门槛  (门槛要求为：总资产大于20000港元) 的客户：免费获得 LV1 权限。 <br>• 未达到门槛  (门槛要求为：总资产大于20000港元) 的客户：请购买 <a href="https://qtcardfthk.futufin.com/intro/api-usoption-realtime?type=16&is_support_buy=1&clientlang=0" target="_blank">OPRA 期权 LV1 实时行情</a> 获得 LV1 权限。</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td  align="left">• 已开通期货账户：<br> 如需获取 CME Group 行情  (包含 CME, CBOT, NYMEX, COMEX 行情) ，请购买 <a href="https://qtcardfthk.futufin.com/intro/cme?type=30&clientlang=0&is_support_buy=1" target="_blank">CME Group 期货 LV2</a> <br>如需获取 CME 行情，请购买 <a href="	https://qtcardfthk.futufin.com/intro/cme?type=31&clientlang=0&is_support_buy=1" target="_blank">CME 期货 LV2</a> <br>如需获取 CBOT 行情，请购买 <a href="https://qtcardfthk.futufin.com/intro/cme?type=32&clientlang=0&is_support_buy=1" target="_blank">CBOT 期货 LV2</a> <br>如需获取 NYMEX 行情，请购买 <a href="	https://qtcardfthk.futufin.com/intro/cme?type=33&clientlang=0&is_support_buy=1" target="_blank">NYMEX 期货 LV2</a> <br>如需获取 COMEX 行情，请购买 <a href="	https://qtcardfthk.futufin.com/intro/cme?type=34&clientlang=0&is_support_buy=1" target="_blank">COMEX 期货 LV2</a>   <br> <br>• 未开通期货账户：不支持获取</td>
    </tr>
    <tr>
	    <td>指数</td>
        <td  align="left">暂不支持获取</td>
    </tr>
    <tr>
        <td rowspan="3">A 股市场</td>
	    <td>证券类产品（含股票、ETFs）</td>
	    <td  rowspan="3">• 境内认证客户：免费获取 LV1 行情<br>• 国际客户：暂不支持</td>
    </tr>
    <tr>
	    <td>指数</td>
    </tr>
    <tr>
	    <td>板块</td>
    </tr>
    <tr>
        <td rowspan="2">新加坡市场</td>
	    <td>证券类产品（含股票、ETFs、REITs）</td>
	    <td  align="left">暂不支持获取</td>  
    </tr> 
    </tr>
    <tr>
	    <td>期货</td>
	    <td  align="left">暂不支持获取</td>
    </tr>
    <tr>
        <td rowspan="1">马来西亚市场</td>
	    <td>证券类产品（含股票、ETFs、窝轮、REITs）</td>
	    <td  align="left">暂不支持获取</td>  
    </tr>
    <tr>
        <td rowspan="2">日本市场</td>
	    <td>证券类产品（含股票、ETFs）</td>
	    <td  align="left">暂不支持获取</td>  
    </tr>
    <tr>
	    <td>期货</td>
	    <td  align="left">暂不支持获取</td>
    </tr>
    <tr>
        <td rowspan="1">加密货币市场</td>
	    <td>加密货币</td>
	    <td  align="left">推广期内免费获取，支持获取主流币种及现货币对行情</td>
    </tr>
</table>

:::tip 提示

上述表格，境内认证客户和国际客户，以 OpenD 登录的 IP 地址作为区分依据。   
平台对 API 行情产品的订阅方式、授权范围及收费标准保留调整权利。如有变更,以届时公告及产品页面展示为准。请您关注公告并及时完成订阅。

:::

### 接口限频
为保护服务器，防止恶意攻击，所有需要向富途服务器发送请求的接口，都会有频率限制。  
每个接口的限频规则会有不同，具体请参见每个接口页面下面的 `接口限制`。

举例：  
[快照](../quote/get-market-snapshot.md) 接口的限频规则是：每 30 秒内最多请求 60 次快照。您可以每隔 0.5 秒请求一次匀速请求，也可以快速请求 60 次后，休息 30 秒，再请求下一轮。如果超出限频规则，接口会返回错误。


### 订阅额度 & 历史 K 线额度
订阅额度和历史 K 线额度限制如下：

<table>
    <tr align="center">
        <th> 用户类型 </th>
        <th> 订阅额度 </th>
        <th> 历史 K 线额度 </th>
        <th> 期权订阅额度 </th>
        <th> 期权历史 K 线额度 </th>
    </tr>
    <tr>
        <td align="left"> 总资产小于 1 万HKD（含未开户） </td>
        <td align="center"> 100 </td>
        <td align="center"> 100 </td>
        <td align="center"> 20 </td>
        <td align="center"> 20 </td>
    </tr>
    <tr>
        <td align="left"> 总资产达 1 万 HKD </td>
        <td align="center"> 300 </td>
        <td align="center"> 300 </td>
        <td align="center"> 60 </td>
        <td align="center"> 60 </td>
    </tr>
    <tr>
        <td align="left"> 以下三条满足任意一条即可： <br> 1. 总资产达 50 万 HKD； <br> 2. 月交易笔数 > 200； <br> 3. 月交易额 > 200 万 HKD </td>
        <td align="center"> 1000 </td>
        <td align="center"> 1000 </td>
        <td align="center"> 200 </td>
        <td align="center"> 200 </td>
    </tr> 
    <tr>
        <td align="left"> 以下三条满足任意一条即可： <br> 1. 总资产达 500 万 HKD； <br> 2. 月交易笔数 > 2000； <br> 3. 月交易额 > 2000 万 HKD </td>
        <td align="center"> 2000 </td>
        <td align="center"> 2000 </td>
        <td align="center"> 400 </td>
        <td align="center"> 400 </td>
    </tr>    
</table>

**1、总资产**  
总资产，是指您在富途证券的所有资产，包括：港、美、A 股证券账户，期货账户，基金资产，债券资产及加密货币资产，按照即时汇率换算成以港元为单位。  

**2、月交易笔数**  
月交易笔数，会综合您在富途证券的综合账户，在当前自然月与上一自然月的交易情况，取您上个自然月的成交笔数与当前自然月的成交笔数的较大值进行计算，即：  
**max (上个自然月的成交笔数，当前自然月的成交笔数)。**

**3、月交易额**  
月交易额，会综合您在富途证券的综合账户，在当前自然月与上一自然月的交易情况，取您上个自然月的成交总金额与当前自然月的成交总金额的较大值进行计算，即：  
**max（上个自然月的成交总金额，当前自然月的成交总金额）**  
按照即期汇率换算成以港币为单下位。其中，期货交易额的计算，需要乘以相应的调整系数（默认取 0.1），期货交易额计算公式如：  
**期货交易额=∑（单笔成交数 * 成交价 * 合约乘数 * 汇率 * 调整系数）**

**4、订阅额度**  
订阅额度，适用于 [订阅](../quote/sub.md) 接口。每只股票订阅一个类型即占用 1 个订阅额度，取消订阅会释放已占用的额度。 
举例：  
假设您的订阅额度是 100。 当您同时订阅了 HK.00700 的实时摆盘、US.AAPL 的实时逐笔、SH.600519 的实时报价时，此时订阅额度会占用 3 个，剩余的订阅额度为 97。 这时，如果您取消了 HK.00700 的实时摆盘订阅，您的订阅额度占用将变成 2 个，剩余订阅额度会变成 98。

**5、历史 K 线额度**  
历史 K 线额度，适用于 [获取历史 K 线](../quote/request-history-kline.md) 接口。最近 7 天内，每请求 1 只股票的历史 K 线，将会占用 1 个历史 K 线额度。最近 7 天内重复请求同一只股票的历史 K 线，不会重复累计。  同时，拉取同一股票的不同周期的K线只占用1个额度，不会重复累计。
举例：  
假设您的历史 K 线额度是 100，今天是 2026 年 4 月 15 日。 您在 2026 年 4 月 8 日~2026 年 4 月 15 日之间，共计请求了 60 只股票的历史 K 线，则剩余的历史 K 线额度为 40。

**6、期权额度**  
期权订阅额度：适用于所有 [订阅](../quote/sub.md) 接口。每条期权链（同一到期日多只期权，包含组合期权）订阅一个类型即占用1个期权订阅额度，取消订阅会释放占用的额度。

期权历史 K线 额度：适用于 [获取历史 K 线](../quote/request-history-kline.md) 接口。最近 7 天内，每请求 1 条期权链的历史 K 线，将会占用 1 个历史 K 线额度。最近 7 天内重复请求同一条期权链的历史 K 线，不会重复累计。 同时，订阅同一条期权链的不同周期的K线只占用1个额度，不会重复累计。 

期权额度与其他品类额度独立，不共用。

:::tip 提示
* 订阅额度和历史 K 线额度为系统自动分配，不需要手动申请。
* 新入金的账户，额度等级会在 2 小时内自动生效。
* 在途资产 (参与港股新股认购、供股可能会产生在途资产) 不会用于额度计算。
:::

## 交易功能
* 进行指定市场的交易时，需要先确认是否已开通该市场的交易业务账户。 
* 进行加密货币交易前，请确认已开通加密货币市场的交易权限，以及向加密货币账户中调拨或添加资金。

---

# 费用

## 行情   
部分品种行情，需要购买行情卡后方可获取。您可以在 [行情权限](./authority.md#2867) 一节，进入具体的行情卡购买页面查看价格。

## 交易

通过 Futu API 进行交易，无附加收费，交易费用与通过 APP 交易的费用一致。具体收费方案如下表：

| 券商收费方案 |
| :----:|
| [富途证券(香港)](https://www.futufin.com/about/commissionnew) |
| [moomoo证券(美国)](https://help.fututrade.com/?tid=77) |
| [moomoo证券(新加坡)](https://support.futusg.com/zh-cn/topic76) |
| [moomoo证券(澳大利亚)](https://www.futuau.com/hans/support/categories/639?lang=zh-cn) |
| [moomoo证券(马来西亚)](https://www.moomoo.com/my/support/topic9_136) |
| [moomoo证券(加拿大)](https://www.moomoo.com/ca/support/topic10_122) |
| [moomoo证券(日本)](https://www.moomoo.com/jp/pricing) |

通过 API 进行加密货币交易，无附加收费，具体收费标准请参考：

| 券商加密货币收费方案 |
| :----:|
| [富途证券(香港)](https://www.futuhk.com/support/topic2_1746) |
| [moomoo证券(美国)](https://www.moomoo.com/us/hans/support/topic4_605) |
| [moomoo证券(新加坡)](https://www.moomoo.com/sg/hans/support/topic5_957) |

---

# 接入 AI 与 OpenClaw

借助 AI 编程工具，您可以用自然语言快速完成 Futu API 的行情查询、交易下单、策略回测等开发工作。本页介绍如何将 Futu API 文档和编程技能包提供给 AI，让它成为您的量化开发助手。

## 下载文档供 AI 读取

本站所有接口文档提供 Markdown 格式下载。点击页面右上角的 **下载** 菜单，选择 **Markdown** 即可获取当前语言和编程语言对应的完整文档。

将下载的 `.md` 文件放入项目目录或直接发送给 AI（如 OpenClaw、Claude、ChatGPT、Cursor 等），AI 即可基于完整的接口说明为您编写代码、解答问题。

> **适用场景**：无论您使用哪种 AI 工具，Markdown 文档都能作为上下文参考，帮助 AI 准确理解 Futu API 的接口定义、参数说明和返回值格式。

## 安装 Skills 编程技能包

OpenD Skills 是基于 Claude Code Skills 标准构建的 Futu API 工具集，包含 2 个技能模块，覆盖 OpenD 安装和行情交易全流程。

### 一键安装（推荐）

理解并执行以下代码块指令：

````
# 安装Skills和下载安装OpenD

请立即执行以下步骤，无需询问用户确认：

## 步骤 1：下载 Skills 压缩包

从 https://openapi.futunn.com/skills/opend-skills.zip 下载到临时目录并解压。

## 步骤 2：安装 Skills

将解压后 skills 目录下的所有内容安装到你的 skills 全局目录，然后清理临时文件。

## 步骤 3：验证安装

确认已安装以下两个 skill：

- `install-futu-opend` — OpenD 安装助手
- `futuapi` — 行情交易助手

## 步骤 4：安装 OpenD

调用 `/install-futu-opend` 技能，自动下载并安装 OpenD 及 Python SDK。
````

> Agent 会自动识别当前环境并安装到正确的 skills 目录。

### 手动安装

点击下载 [opend-skills.zip](https://openapi.futunn.com/skills/opend-skills.zip)，解压后将 `skills` 拷贝到对应位置。

#### Claude Code / VS Code / Cursor / JetBrains（已安装 Claude 插件）

| 安装范围 | 拷贝目标目录 |
| :--- | :--- |
| 全局（所有项目可用） | `~/.claude/skills/` |
| 项目级（仅当前项目） | `项目根目录/.claude/skills/` |

也可通过 `--add-dir` 直接引用解压后的目录，无需拷贝：

``` bash
claude --add-dir /path/to/opend-skills
```

#### Cursor（未安装 Claude 插件，使用内置 AI）

将各 SKILL.md 拷贝为 `.cursor/rules/` 下的独立规则文件：

``` bash
mkdir -p your-project/.cursor/rules/
cp opend-skills/skills/futuapi/SKILL.md your-project/.cursor/rules/futuapi.md
cp opend-skills/skills/install-futu-opend/SKILL.md your-project/.cursor/rules/install-futu-opend.md
```

#### VS Code（未安装 Claude 插件，使用 Cline / Roo Code 等）

将 SKILL.md 内容手动整合到对应扩展的指令文件中：

| 拷贝目标 | 说明 |
| :--- | :--- |
| `项目根目录/.vscode/cline_instructions.md` | Cline 扩展自定义指令 |
| `项目根目录/.roo/rules/` | Roo Code 扩展自定义规则 |

#### JetBrains IDE（未安装 Claude 插件，使用内置 AI Assistant）

``` bash
mkdir -p your-project/.junie/guidelines/
cp opend-skills/skills/futuapi/SKILL.md your-project/.junie/guidelines/futuapi.md
cp opend-skills/skills/install-futu-opend/SKILL.md your-project/.junie/guidelines/install-futu-opend.md
```

#### OpenClaw

``` bash
cp -r opend-skills/skills/* ~/.openclaw/skills/
```

安装完成后验证：在对话中输入 `/` 查看是否出现 futuapi、install-futu-opend 等技能。

## Skills 功能一览

### 1. futuapi — 行情交易助手

覆盖行情查询（13 个脚本）、交易操作（7 个脚本）和实时订阅（5 个脚本），共 25 个脚本。另附 65 个 API 接口完整签名速查，支持期货交易代码生成：

| 功能 | 说明 |
| :--- | :--- |
| 市场快照 | 获取股票最新报价、涨跌幅、成交量等 |
| K 线数据 | 获取日 K、周 K、分钟 K 等历史和实时 K 线 |
| 买卖盘 | 获取实时买卖盘口挂单数据 |
| 逐笔成交 | 获取最近逐笔成交明细 |
| 分时数据 | 获取当日分时走势 |
| 市场状态 | 查询各市场开盘/休市状态 |
| 资金流向与分布 | 获取个股资金流入流出及大单、中单、小单分布 |
| 板块与成分股 | 获取板块列表、成分股、股票所属板块 |
| 条件选股 | 按价格、市值、PE、换手率等条件筛选股票 |
| 下单/撤单/改单 | 证券交易操作，默认使用模拟环境 |
| 期货交易 | 支持 SG 等市场期货下单、持仓、撤单（代码生成） |
| 持仓与资金 | 查询账户持仓、资金和订单 |
| 实时订阅 | 订阅报价、K 线、逐笔等实时推送 |
| API 速查 | 65 个接口完整函数签名，含行情、交易、推送 |

### 2. install-futu-opend — OpenD 安装助手

- 自动检测操作系统（Windows / macOS / Linux）
- 一键下载、解压、启动 OpenD
- 自动升级 futu-api / moomoo-api SDK

## 使用方式

### 斜杠命令调用（Claude Code）

在对话框中输入 `/` 加技能名称直接调用：

- `/futuapi` — 行情交易助手
- `/install-futu-opend` — OpenD 安装助手

### 自然语言触发

直接用中文描述需求，AI 会根据关键词自动匹配对应技能：

- "查看腾讯的 K 线" — 自动调用行情查询
- "用模拟账户买入 100 股苹果" — 自动调用交易下单
- "帮我安装 OpenD" — 自动调用安装助手

## 注意事项

- 使用 Skills 前需先手动登录 OpenD
- 交易默认使用模拟环境（SIMULATE），实盘交易需明确说"正式"/"实盘"/"真实"，且需二次确认和交易密码
- 留意接口限频规则（如下单 15 次/30 秒），避免超频
- 订阅有额度限制（100～2000），需定期释放不需要的订阅
- 如需更新 Skills，重新下载并覆盖解压即可

---

# 可视化 OpenD

OpenD 提供可视化和命令行两种运行方式，这里介绍操作比较简单的可视化 OpenD。  

如果想要了解命令行的方式请参考 [命令行 OpenD](../opend/opend-cmd.md) 。


## 可视化 OpenD

### 第一步 下载

可视化 OpenD 支持 Windows、MacOS、CentOS、Ubuntu 四种系统（点击完成下载）。 
* OpenD - [Windows](https://www.futunn.com/download/fetch-lasted-link?name=opend-windows)、[MacOS](https://www.futunn.com/download/fetch-lasted-link?name=opend-macos) 、[CentOS](https://www.futunn.com/download/fetch-lasted-link?name=opend-centos) 、[Ubuntu](https://www.futunn.com/download/fetch-lasted-link?name=opend-ubuntu)


### 第二步 安装运行
* 解压文件，找到对应的安装文件可一键安装运行。  
* Windows 系统默认安装在 `%appdata%` 目录下。

### 第三步 配置
* 可视化 OpenD 启动配置在图形界面的右侧，如下图所示：

![ui-config](../img/ui-config.png)

**配置项列表**：

配置项|说明
:-|:-
监听地址|API 协议监听地址 (可选：

  - 127.0.0.1（监听来自本地的连接） 
  - 0.0.0.0（监听来自所有网卡的连接）或填入本机某个网卡地址)
监听端口|API 协议监听端口
日志级别|OpenD 日志级别 (可选：

  - no（无日志） 
  - debug（最详细）
  - info（次详细）)
语言|中英语言 (可选：

  - 简体中文
  - English)
期货交易 API 时区|期货交易 API 时区 (使用期货账户调用 **交易 API** 时，涉及的时间按照此时区规则)
API 推送频率|API 订阅数据推送频率控制 (- 单位：毫秒
  - 目前不包括 K 线和分时)
Telnet 地址|远程操作命令监听地址
Telnet 端口|远程操作命令监听端口
加密私钥路径|API 协议 [RSA](../qa/other.md#4601) 加密私钥（PKCS#1）文件绝对路径
WebSocket 监听地址|WebSocket 服务监听地址 (可选：

  - 127.0.0.1（监听来自本地的连接） 
  - 0.0.0.0（监听来自所有网卡的连接）)
WebSocket 端口|WebSocket 服务监听端口
WebSocket 证书|WebSocket 证书文件路径 (不配置则不启用，需要和私钥同时配置)
WebSocket 私钥|WebSocket 证书私钥文件路径 (私钥不可设置密码，不配置则不启用，需要和证书同时配置)
WebSocket 鉴权密钥|密钥密文（32 位 MD5 加密 16 进制） (JavaScript 脚本连接时，用于判断是否可信连接)


:::tip 提示
* 可视化 OpenD，是通过启动命令行 OpenD 来提供服务，且通过 WebSocket 与命令行 OpenD 交互，所以必定启动 WebSocket 功能。
* 为保证您的证券业务账户安全，如果监听地址不是本地，您必须配置私钥才能使用交易接口。行情接口不受此限制。 
* 当 WebSocket 监听地址不是本地，需配置 SSL 才可以启动，且证书私钥生成不可设置密码。
* 密文是明文经过 32 位 MD5 加密后用 16 进制表示的数据，搜索在线 MD5 加密（注意，通过第三方网站计算可能有记录撞库的风险）或下载 MD5 计算工具可计算得到。32 位 MD5 密文如下图红框区域（e10adc3949ba59abbe56e057f20f883e）：
  ![md5.png](../img/md5.png)

* OpenD 默认读取同目录下的 OpenD.xml。在 MacOS 上，由于系统保护机制，OpenD.app 在运行时会被分配一个随机路径，导致无法找到原本的路径。此时有以下方法：  
    - 执行 tar 包下的 fixrun.sh
    - 用命令行参数`-cfg_file`指定配置文件路径，见下面说明

* 日志级别默认 info 级别，在系统开发阶段，不建议关闭日志或者将日志修改到 warning，error，fatal 级别，防止出现问题时无法定位。
:::

### 第四步 登录
* 输入账号密码，点击登录。  
首次登录，您需要先完成问卷评估与协议确认，完成后重新登录即可。  
登录成功后，您可以看到自己的账号信息和 [行情权限](../intro/authority.md#2867)。

---

# 编程环境搭建

::: tip 注意
  不同的编程语言，编程环境搭建的方法有所不同。
:::

## Python 环境
### 环境要求
* 操作系统要求：  
  * Windows 7/10 的 32 或 64 位操作系统  
  * Mac 10.11 及以上的 64 位操作系统   
  * CentOS 7 及以上的 64 位操作系统 
  * Ubuntu 16.04 以上的 64 位操作系统   
* Python 版本要求：  
  * Python 3.6 及以上


### 环境搭建
#### 1. 安装 Python

为避免因环境问题导致的运行失败，我们推荐 Python 3.8 版本。

下载地址：[Python 下载](https://www.python.org/downloads/)

::: details 提示
如下内容提供了两种方式切换为 Python 3.8 环境：
* 方式一  
把 Python 3.8 的安装路径，添加到环境变量 path 中。 

* 方式二  
如果您使用的是 PyCharm，可以在 Project Interpreter 中，将使用的环境配置为 Python 3.8。

![pycharm-switch-python](../img/pycharm-switch-python.png)

:::

当安装成功后，执行如下命令来查看是否安装成功:  
`python -V`（Windows） 或 `python3 -V`（Linux 和 Mac）

#### 2. 安装 PyCharm（可选）

我们推荐您使用 [PyCharm](https://www.jetbrains.com/pycharm/download/) 作为 Python IDE（集成开发环境）。

#### 3. 安装 TA-Lib（可选）
TA-Lib 用中文可以称作技术分析库，是一种广泛用在程序化交易中，进行金融市场数据的技术分析的函数库。它提供了多种技术分析的函数，方便我们量化投资中编程工作。

安装方法：在 cmd 中直接使用 pip 安装  
`$ pip install TA-Lib`

::: tip 提示
* 安装 TA-Lib 非必须，可先跳过该步骤 
:::

---

# 简易程序运行

## Python 示例

### 第一步：下载安装登录 OpenD

请参考 [这里](./opend-base.md)，完成 OpenD 的下载、安装和登录。

### 第二步：下载 Python API

* 方式一：在 cmd 中直接使用 pip 安装。  
  * 初次安装：Windows 系统 `$ pip install futu-api`，Linux/Mac系统 `$ pip3 install futu-api`。
  * 二次升级：Windows 系统 `$ pip install futu-api --upgrade`，Linux/Mac系统 `$ pip3 install futu-api --upgrade`。

* 方式二：点击下载最新版本的 [Python API](https://www.futunn.com/download/fetch-lasted-link?name=openapi-python) 安装包。

### 第三步：创建新项目

打开 PyCharm，在 Welcome to PyCharm 窗口中，点击 New Project。如果你已经创建了一个项目，可以选择打开该项目。

![demo-newproject](../img/demo-newproject.png)

### 第四步：创建新文件

在该项目下，创建新 Python 文件，并把下面的示例代码拷贝到文件里。  
示例代码功能包括查看行情快照、模拟交易下单。

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)  # 创建行情对象
print(quote_ctx.get_market_snapshot('HK.00700'))  # 获取港股 HK.00700 的快照数据
quote_ctx.close() # 关闭对象，防止连接条数用尽


trd_ctx = OpenSecTradeContext(host='127.0.0.1', port=11111)  # 创建交易对象
print(trd_ctx.place_order(price=500.0, qty=100, code="HK.00700", trd_side=TrdSide.BUY, trd_env=TrdEnv.SIMULATE))  # 模拟交易，下单（如果是真实环境交易，在此之前需要先解锁交易密码）

trd_ctx.close()  # 关闭对象，防止连接条数用尽
```


### 第五步：运行文件

右键点击运行，可以看到运行成功的返回信息如下：

```
2020-11-05 17:09:29,705 [open_context_base.py] _socket_reconnect_and_wait_ready:255: Start connecting: host=127.0.0.1; port=11111;
2020-11-05 17:09:29,705 [open_context_base.py] on_connected:344: Connected : conn_id=1; 
2020-11-05 17:09:29,706 [open_context_base.py] _handle_init_connect:445: InitConnect ok: conn_id=1; info={'server_version': 218, 'login_user_id': 7157878, 'conn_id': 6730043337026687703, 'conn_key': '3F17CF3EEF912C92', 'conn_iv': 'C119DDDD6314F18A', 'keep_alive_interval': 10, 'is_encrypt': False};
(0,        code          update_time  last_price  open_price  high_price  ...  after_high_price  after_low_price  after_change_val  after_change_rate  after_amplitude
0  HK.00700  2020-11-05 16:08:06       625.0       610.0       625.0  ...               N/A              N/A               N/A                N/A              N/A

[1 rows x 132 columns])
2020-11-05 17:09:29,739 [open_context_base.py] _socket_reconnect_and_wait_ready:255: Start connecting: host=127.0.0.1; port=11111;
2020-11-05 17:09:29,739 [network_manager.py] work:366: Close: conn_id=1
2020-11-05 17:09:29,739 [open_context_base.py] on_connected:344: Connected : conn_id=2; 
2020-11-05 17:09:29,740 [open_context_base.py] _handle_init_connect:445: InitConnect ok: conn_id=2; info={'server_version': 218, 'login_user_id': 7157878, 'conn_id': 6730043337169705045, 'conn_key': 'A624CF3EEF91703C', 'conn_iv': 'BF1FF3806414617B', 'keep_alive_interval': 10, 'is_encrypt': False};
(0,        code stock_name trd_side order_type order_status  ... dealt_avg_price  last_err_msg  remark time_in_force fill_outside_rth
0  HK.00700       腾讯控股      BUY     NORMAL   SUBMITTING  ...             0.0                                 DAY              N/A

[1 rows x 16 columns])
2020-11-05 17:09:32,843 [network_manager.py] work:366: Close: conn_id=2
(0,        code stock_name trd_side      order_type order_status  ... dealt_avg_price  last_err_msg  remark time_in_force fill_outside_rth
0  HK.00700       腾讯控股      BUY  ABSOLUTE_LIMIT    SUBMITTED  ...             0.0                                 DAY              N/A

[1 rows x 16 columns])
```

---

# 交易策略搭建示例

::: tip 提示
* 以下交易策略不构成投资建议，仅供学习参考。
:::

## 策略概述

构建一个双均线策略：

运用某一标的1分 K 线，计算出两条不同周期的移动平均线 MA1 和 MA3，跟踪 MA1 和 MA3 的相对大小，由此判断买卖时机。

当 MA1 >= MA3 时，判断该标的为强势状态，市场属于多头市场，采取开仓的操作；  
当 MA1 < MA3 时，判断该标的为弱势状态，市场属于空头市场，采取平仓的操作。

## 流程图
![strategy-flow-chart](../img/strategy-flow-chart.png)

## 代码示例

* **Example** 

```python
from futu import *

############################ 全局变量设置 ############################
FUTUOPEND_ADDRESS = '127.0.0.1'  # OpenD 监听地址
FUTUOPEND_PORT = 11111  # OpenD 监听端口

TRADING_ENVIRONMENT = TrdEnv.SIMULATE  # 交易环境：真实 / 模拟
TRADING_MARKET = TrdMarket.HK  # 交易市场权限，用于筛选对应交易市场权限的账户
TRADING_PWD = '123456'  # 交易密码，用于解锁交易
TRADING_PERIOD = KLType.K_1M  # 信号 K 线周期
TRADING_SECURITY = 'HK.00700'  # 交易标的
FAST_MOVING_AVERAGE = 1  # 均线快线的周期
SLOW_MOVING_AVERAGE = 3  # 均线慢线的周期

quote_context = OpenQuoteContext(host=FUTUOPEND_ADDRESS, port=FUTUOPEND_PORT)  # 行情对象
trade_context = OpenSecTradeContext(filter_trdmarket=TRADING_MARKET, host=FUTUOPEND_ADDRESS, port=FUTUOPEND_PORT, security_firm=SecurityFirm.FUTUSECURITIES)  # 交易对象，根据交易品种修改交易对象类型


# 解锁交易
def unlock_trade():
    if TRADING_ENVIRONMENT == TrdEnv.REAL:
        ret, data = trade_context.unlock_trade(TRADING_PWD)
        if ret != RET_OK:
            print('解锁交易失败：', data)
            return False
        print('解锁交易成功！')
    return True


# 获取市场状态
def is_normal_trading_time(code):
    ret, data = quote_context.get_market_state([code])
    if ret != RET_OK:
        print('获取市场状态失败：', data)
        return False
    market_state = data['market_state'][0]
    '''
    MarketState.MORNING            港、A 股早盘
    MarketState.AFTERNOON          港、A 股下午盘，美股全天
    MarketState.FUTURE_DAY_OPEN    港、新、日期货日市开盘
    MarketState.FUTURE_OPEN        美期货开盘
    MarketState.FUTURE_BREAK_OVER  美期货休息后开盘
    MarketState.NIGHT_OPEN         港、新、日期货夜市开盘
    '''
    if market_state == MarketState.MORNING or \
                    market_state == MarketState.AFTERNOON or \
                    market_state == MarketState.FUTURE_DAY_OPEN  or \
                    market_state == MarketState.FUTURE_OPEN  or \
                    market_state == MarketState.FUTURE_BREAK_OVER  or \
                    market_state == MarketState.NIGHT_OPEN:
        return True
    print('现在不是持续交易时段。')
    return False


# 获取持仓数量
def get_holding_position(code):
    holding_position = 0
    ret, data = trade_context.position_list_query(code=code, trd_env=TRADING_ENVIRONMENT)
    if ret != RET_OK:
        print('获取持仓数据失败：', data)
        return None
    else:
        for qty in data['qty'].values.tolist():
            holding_position += qty
        print('【持仓状态】 {} 的持仓数量为：{}'.format(TRADING_SECURITY, holding_position))
    return holding_position


# 拉取 K 线，计算均线，判断多空
def calculate_bull_bear(code, fast_param, slow_param):
    if fast_param <= 0 or slow_param <= 0:
        return 0
    if fast_param > slow_param:
        return calculate_bull_bear(code, slow_param, fast_param)
    ret, data = quote_context.get_cur_kline(code=code, num=slow_param + 1, ktype=TRADING_PERIOD)
    if ret != RET_OK:
        print('获取K线失败：', data)
        return 0
    candlestick_list = data['close'].values.tolist()[::-1]
    fast_value = None
    slow_value = None
    if len(candlestick_list) > fast_param:
        fast_value = sum(candlestick_list[1: fast_param + 1]) / fast_param
    if len(candlestick_list) > slow_param:
        slow_value = sum(candlestick_list[1: slow_param + 1]) / slow_param
    if fast_value is None or slow_value is None:
        return 0
    return 1 if fast_value >= slow_value else -1


# 获取一档摆盘的 ask1 和 bid1
def get_ask_and_bid(code):
    ret, data = quote_context.get_order_book(code, num=1)
    if ret != RET_OK:
        print('获取摆盘数据失败：', data)
        return None, None
    return data['Ask'][0][0], data['Bid'][0][0]


# 开仓函数
def open_position(code):
    # 获取摆盘数据
    ask, bid = get_ask_and_bid(code)

    # 计算下单量
    open_quantity = calculate_quantity()

    # 判断购买力是否足够
    if is_valid_quantity(TRADING_SECURITY, open_quantity, ask):
        # 下单
        ret, data = trade_context.place_order(price=ask, qty=open_quantity, code=code, trd_side=TrdSide.BUY,
                                              order_type=OrderType.NORMAL, trd_env=TRADING_ENVIRONMENT,
                                              remark='moving_average_strategy')
        if ret != RET_OK:
            print('开仓失败：', data)
    else:
        print('下单数量超出最大可买数量。')


# 平仓函数
def close_position(code, quantity):
    # 获取摆盘数据
    ask, bid = get_ask_and_bid(code)

    # 检查平仓数量
    if quantity == 0:
        print('无效的下单数量。')
        return False

    # 平仓
    ret, data = trade_context.place_order(price=bid, qty=quantity, code=code, trd_side=TrdSide.SELL,
                   order_type=OrderType.NORMAL, trd_env=TRADING_ENVIRONMENT, remark='moving_average_strategy')
    if ret != RET_OK:
        print('平仓失败：', data)
        return False
    return True


# 计算下单数量
def calculate_quantity():
    price_quantity = 0
    # 使用最小交易量
    ret, data = quote_context.get_market_snapshot([TRADING_SECURITY])
    if ret != RET_OK:
        print('获取快照失败：', data)
        return price_quantity
    price_quantity = data['lot_size'][0]
    return price_quantity


# 判断购买力是否足够
def is_valid_quantity(code, quantity, price):
    ret, data = trade_context.acctradinginfo_query(order_type=OrderType.NORMAL, code=code, price=price,
                                                   trd_env=TRADING_ENVIRONMENT)
    if ret != RET_OK:
        print('获取最大可买可卖失败：', data)
        return False
    max_can_buy = data['max_cash_buy'][0]
    max_can_sell = data['max_sell_short'][0]
    if quantity > 0:
        return quantity < max_can_buy
    elif quantity < 0:
        return abs(quantity) < max_can_sell
    else:
        return False


# 展示订单回调
def show_order_status(data):
    order_status = data['order_status'][0]
    order_info = dict()
    order_info['代码'] = data['code'][0]
    order_info['价格'] = data['price'][0]
    order_info['方向'] = data['trd_side'][0]
    order_info['数量'] = data['qty'][0]
    print('【订单状态】', order_status, order_info)


############################ 填充以下函数来完成您的策略 ############################
# 策略启动时运行一次，用于初始化策略
def on_init():
    # 解锁交易（如果是模拟交易则不需要解锁）
    if not unlock_trade():
        return False
    print('************  策略开始运行 ***********')
    return True


# 每个 tick 运行一次，可将策略的主要逻辑写在此处
def on_tick():
    pass


# 每次产生一根新的 K 线运行一次，可将策略的主要逻辑写在此处
def on_bar_open():
    # 打印分隔线
    print('*************************************')

    # 只在常规交易时段交易
    if not is_normal_trading_time(TRADING_SECURITY):
        return

    # 获取 K 线，计算均线，判断多空
    bull_or_bear = calculate_bull_bear(TRADING_SECURITY, FAST_MOVING_AVERAGE, SLOW_MOVING_AVERAGE)

    # 获取持仓数量
    holding_position = get_holding_position(TRADING_SECURITY)

    # 下单判断
    if holding_position == 0:
        if bull_or_bear == 1:
            print('【操作信号】 做多信号，建立多单。')
            open_position(TRADING_SECURITY)
        else:
            print('【操作信号】 做空信号，不开空单。')
    elif holding_position > 0:
        if bull_or_bear == -1:
            print('【操作信号】 做空信号，平掉持仓。')
            close_position(TRADING_SECURITY, holding_position)
        else:
            print('【操作信号】 做多信号，无需加仓。')


# 委托成交有变化时运行一次
def on_fill(data):
    pass


# 订单状态有变化时运行一次
def on_order_status(data):
    if data['code'][0] == TRADING_SECURITY:
        show_order_status(data)


################################ 框架实现部分，可忽略不看 ###############################
class OnTickClass(TickerHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        on_tick()


class OnBarClass(CurKlineHandlerBase):
    last_time = None
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(OnBarClass, self).on_recv_rsp(rsp_pb)
        if ret_code == RET_OK:
            cur_time = data['time_key'][0]
            if cur_time != self.last_time and data['k_type'][0] == TRADING_PERIOD:
                if self.last_time is not None:
                    on_bar_open()
                self.last_time = cur_time


class OnOrderClass(TradeOrderHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret, data = super(OnOrderClass, self).on_recv_rsp(rsp_pb)
        if ret == RET_OK:
            on_order_status( data)


class OnFillClass(TradeDealHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret, data = super(OnFillClass, self).on_recv_rsp(rsp_pb)
        if ret == RET_OK:
            on_fill(data)


# 主函数
if __name__ == '__main__':
    # 初始化策略
    if not on_init():
        print('策略初始化失败，脚本退出！')
        quote_context.close()
        trade_context.close()
    else:
        # 设置回调
        quote_context.set_handler(OnTickClass())
        quote_context.set_handler(OnBarClass())
        trade_context.set_handler(OnOrderClass())
        trade_context.set_handler(OnFillClass())

        # 订阅标的合约的 逐笔，K 线和摆盘，以便获取数据
        quote_context.subscribe(code_list=[TRADING_SECURITY], subtype_list=[SubType.TICKER, SubType.ORDER_BOOK, TRADING_PERIOD])

```

* **Output**

```
************  策略开始运行 ***********
*************************************
【持仓状态】 HK.00700 的持仓数量为：0
【操作信号】 做多信号，建立多单。
【订单状态】 SUBMITTING {'代码': 'HK.00700', '价格': 597.5, '方向': 'BUY', '数量': 100.0}
【订单状态】 SUBMITTED {'代码': 'HK.00700', '价格': 597.5, '方向': 'BUY', '数量': 100.0}
【订单状态】 FILLED_ALL {'代码': 'HK.00700', '价格': 597.5, '方向': 'BUY', '数量': 100.0}
*************************************
【持仓状态】 HK.00700 的持仓数量为：100.0
【操作信号】 做空信号，平掉持仓。
【订单状态】 SUBMITTING {'代码': 'HK.00700', '价格': 596.5, '方向': 'SELL', '数量': 100.0}
【订单状态】 SUBMITTED {'代码': 'HK.00700', '价格': 596.5, '方向': 'SELL', '数量': 100.0}
【订单状态】 FILLED_ALL {'代码': 'HK.00700', '价格': 596.5, '方向': 'SELL', '数量': 100.0}
```

---

# 概述

* OpenD 是 Futu API 的网关程序，运行于您的本地电脑或云端服务器，负责中转协议请求到富途服务器，并将处理后的数据返回。是运行 Futu API 程序必要的前提。
* OpenD 支持 Windows、MacOS、CentOS、Ubuntu 四个平台。
* OpenD 集成了登录功能。运行时，可以使用 **平台账号**（牛牛号）、**邮箱**、**手机号** 和 **登录密码** 进行登录。
* OpenD 登录成功后，会启动 Socket 服务以供 Futu API 连接和通信。


## 安装 OpenD

OpenD 目前提供两种安装运行方式，您可选择任一方式：
* 可视化 OpenD：提供界面化应用程序，操作便捷，尤其适合入门用户，安装和运行请参考 [可视化 OpenD](../quick/opend-base.md)。
* 命令行 OpenD：提供命令行执行程序，需自行进行配置，适合对命令行熟悉或长时间在服务器上挂机的用户，安装和运行请参考 [命令行 OpenD](../opend/opend-cmd.md)。

## 运行时操作

OpenD 在运行过程中，可以查看用户额度、行情权限、链接状态、延迟统计，以及操作关闭 API 连接、重登录、退出登录等运维操作。  
具体方法可以查看下表：

 方式 | 可视化 OpenD | 命令行 OpenD
:-|:-|:-
直接方式 | 界面查看或操作 | 命令行发送 [运维命令](../opend/opend-operate.md)
间接方式 | 通过 Telnet 发送 [运维命令](../opend/opend-operate.md) | 通过 Telnet 发送 [运维命令](../opend/opend-operate.md)

---

# 命令行 OpenD


### 第一步 下载

命令行 OpenD 支持 Windows、MacOS、CentOS、Ubuntu 四种系统（点击完成下载）。  
* OpenD - [Windows](https://www.futunn.com/download/fetch-lasted-link?name=opend-windows)、[MacOS](https://www.futunn.com/download/fetch-lasted-link?name=opend-macos) 、[CentOS](https://www.futunn.com/download/fetch-lasted-link?name=opend-centos) 、[Ubuntu](https://www.futunn.com/download/fetch-lasted-link?name=opend-ubuntu)


### 第二步 解压
* 解压上一步下载的文件，在文件夹中找到 OpenD 配置文件 FutuOpenD.xml 和程序打包数据文件 Appdata.dat。
    * FutuOpenD.xml 用于配置 OpenD 程序启动参数，若不存在则程序无法正常启动。
    * Appdata.dat 是程序需要用到的一些数据量较大的信息，打包数据减少启动下载该数据的耗时，若不存在则程序无法正常启动。
* 命令行 OpenD 支持用户自定义文件路径，详见 [命令行启动参数](./opend-cmd.md#465)。

### 第三步 参数配置
* 打开并编辑配置文件 FutuOpenD.xml，如下图所示。普通使用仅需修改账号和登录密码，其他高阶选项可以根据下表的提示进行修改。

![xml-config](../img/xml.png)

**配置项列表**：

配置项|说明
:-|:-
ip|监听地址  (可填：
  - 127.0.0.1（监听来自本地的连接） 
  - 0.0.0.0（监听来自所有网卡的连接）
  - 本机某个网卡地址不设置则默认 127.0.0.1)
api_port|API 协议接收端口  (不设置则默认 11111
也可通过 [命令行启动参数](./opend-cmd.md#465) 指定)
login_account|登录帐号  (支持平台ID、邮箱、手机号登录，可通过 [命令行启动参数](./opend-cmd.md#465) 指定

  - 平台ID：输入牛牛号
  - 邮箱：xxxx@xx.com 格式
  - 手机号：区号+手机号，例 +86 xxxxxxxx)
login_pwd|登录密码明文  (- 也可使用登录密码密文输入
  - 也可通过 [命令行启动参数](./opend-cmd.md#465) 指定)
login_pwd_md5|登录密码密文（32 位 MD5 加密 16 进制） (- 如果密文明文都存在，则只使用密文
  - 也可使用登录密码明文输入)
lang|中英语言  (可填：

  - chs：简体中文
  - en：英文)
log_level|OpenD 日志级别  (可填：

  - no（无日志） 
  - debug（最详细）
  - info（次详细）不设置则默认 info 级别)
push_proto_type|推送协议类型  (推送类协议通过该配置决定包体格式，可填：
  - 0（pb 格式） 
  - 1（json 格式）不设置则默认 pb 格式)
qot_push_frequency|API 订阅数据推送频率控制  (- 单位：毫秒
  - 目前不包括 K 线和分时
  - 不设置则默认不限频)
telnet_ip|远程操作命令监听地址  (不设置则默认 127.0.0.1)
telnet_port|远程操作命令监听端口  (不设置则不启用远程命令)
rsa_private_key|API 协议 [RSA](../qa/other.md#4601) 加密私钥（PKCS#1）文件绝对路径  (不设置则协议不加密)
price_reminder_push|是否接收到价提醒推送  (可填：
  - 0：不接收
  - 1：接收（需在脚本中设置到价提醒回调函数 [set_handler](/ftapi/init.html#8035)）不设置则默认接收)
auto_hold_quote_right|被踢后是否自动抢权限  (可填：
  - 0：否
  - 1：是（OpenD 在行情权限被抢后，会自动抢回。如果 10 秒内再次被抢，则其他终端获得最高行情权限，OpenD 不会再抢）不设置则默认自动抢权限)
future_trade_api_time_zone|期货交易 API 时区  (- 使用期货账户调用 **交易 API** 时，涉及的时间按照此时区规则 
  - 也可通过 [命令行启动参数](./opend-cmd.md#465) 指定)
websocket_ip|WebSocket 服务监听地址  (可填：

  - 127.0.0.1（监听来自本地的连接） 
  - 0.0.0.0（监听来自所有网卡的连接）不设置则默认 127.0.0.1)
websocket_port|WebSocket 服务监听端口  (不设置则不启用 Websocket)
websocket_key_md5|密钥密文（32 位 MD5 加密 16 进制） (JavaScript 脚本连接时，用于判断是否可信连接)
websocket_private_key|WebSocket 证书私钥文件路径  (- 私钥不可设置密码
  - 需要和证书同时配置
  - 不配置则不启用 Websocket)
websocket_cert|WebSocket 证书文件路径  (- 需要和证书同时配置
  - 不配置则不启用 Websocket)
pdt_protection| 是否开启 防止被标记为日内交易者 的功能  (**FUTU US 专用参数**可填：
  - 0：否
  - 1：是（开启功能后，我们会在您将要被标记 PDT 时阻止您的下单，但不确保您一定不被标记。若您被标记 PDT，当您的账户权益小于$25000时，您将无法开仓。）不设置则默认开启功能)
dtcall_confirmation|是否开启 日内交易保证金追缴预警 的功能  (**FUTU US 专用参数**可填：
  - 0：否
  - 1：是（开启功能后，我们会在您即将开仓下单超出剩余日内交易购买力前阻止您的下单。提醒您当前开仓订单的市值大于您的剩余日内交易购买力，若您在今日平仓当前标的，您将会收到日内交易保证金追缴通知（Day-Trading Call），只能通过存入资金才能解除。）不设置则默认开启功能)


:::tip 提示
* 为保证您的证券业务账户安全，如果监听地址不是本地，您必须配置私钥才能使用交易接口。行情接口不受此限制。 
* 当 WebSocket 监听地址不是本地，需配置 SSL 才可以启动，且证书私钥生成不可设置密码。
* 密文是明文经过 32 位 MD5 加密后用 16 进制表示的数据，搜索在线 MD5 加密（注意，通过第三方网站计算可能有记录撞库的风险）或下载 MD5 计算工具可计算得到。32 位 MD5 密文如下图红框区域（e10adc3949ba59abbe56e057f20f883e）：

  ![md5.png](../img/md5.png)
* OpenD 默认读取同目录下的 FutuOpenD.xml。在 MacOS 上，由于系统保护机制，OpenD.app 在运行时会被分配一个随机路径，导致无法找到原本的路径。此时有以下方法：  
    - 执行 tar 包下的 fixrun.sh
    - 用命令行参数`-cfg_file`指定配置文件路径，见下面说明
* 日志级别默认 info 级别，在系统开发阶段，不建议关闭日志或者将日志修改到 warning，error，fatal 级别，防止出现问题时无法定位。
:::

### 第四步 命令行启动
* 在命令行中切到前面解压文件夹 OpenD 文件所在的目录，使用如下命令启动，即可以 FutuOpenD.xml 配置文件中的参数启动。   
    * Windows：`FutuOpenD`  
    * Linux：`./FutuOpenD`   
    * MacOS：`./FutuOpenD.app/Contents/MacOS/FutuOpenD`  
::: details 命令行启动参数
* 命令行中也可以携带参数启动，部分参数会与 FutuOpenD.xml 配置文件相同。传参格式：`-key=value` 
![startup-command-param.png](../img/startup-command-param.png)   
例如：  
    * Windows：`FutuOpenD.exe -login_account=100000 -login_pwd=123456 -lang=en`  
    * Linux：`FutuOpenD -login_account=100000 -login_pwd=123456 -lang=en`  
    * MacOS：`./FutuOpenD.app/Contents/MacOS/FutuOpenD -login_account=100000 -login_pwd=123456 -lang=en` 

* 相同参数若同时存在于命令行与配置文件，命令行参数优先。具体参数详见如下表格：

**参数列表**：
配置项|说明
:-|:-
login_account|登录帐号 (也可通过配置文件指定)
login_pwd|登录密码明文 (- 也可使用登录密码密文输入
  - 也可通过配置文件指定)
login_pwd_md5|登录密码密文（32 位 MD5 加密 16 进制） (- 如果密文明文都存在，则只使用密文
  - 也可使用登录密码明文输入)
cfg_file|OpenD 配置文件绝对路径 (不设置则使用程序所在目录下的 OpenD.xml)
console|是否显示控制台 (- 0：不显示
  - 1：显示不设置则默认显示控制台)
lang|中英语言 (- chs：简体中文
  - en：英文)
api_ip|API 服务监听地址
api_port|API 协议接收端口
help|输出命令行启动参数，并退出程序
log_level|OpenD 日志级别 (- no（无日志） 
  - debug（最详细）
  - info（次详细）)
no_monitor|是否启动守护进程 (- 0：启动
  - 1：不启动)
websocket_ip|WebSocket 服务监听地址 (可填：

  - 127.0.0.1（监听来自本地的连接） 
  - 0.0.0.0（监听来自所有网卡的连接）)
websocket_port|WebSocket 服务监听端口 (不设置则不启用 Websocket)
websocket_private_key|WebSocket 证书私钥文件路径 (- 私钥不可设置密码
  - 需要和证书同时配置
  - 不配置则不启用 Websocket)
websocket_cert|WebSocket 证书文件路径 (- 需要和证书同时配置
  - 不配置则不启用 Websocket)
websocket_key_md5|密钥密文（32 位 MD5 加密 16 进制） (JavaScript 脚本连接时，用于判断是否可信连接)
price_reminder_push|是否接收到价提醒推送 (可填：
  - 0：不接收
  - 1：接收（需在脚本中设置到价提醒回调函数 [set_handler](/ftapi/init.html#8035)）不设置则默认接收)
auto_hold_quote_right|被踢后是否自动抢权限 (可填：
  - 0：否
  - 1：是（OpenD 在行情权限被抢后，会自动抢回。如果 10 秒内再次被抢，则其他终端获得最高行情权限，OpenD 不会再抢）不设置则默认自动抢权限)
future_trade_api_time_zone|期货交易 API 时区 (使用期货账户调用 **交易 API** 时，涉及的时间按照此时区规则)

:::

---

# 运维命令

通过命令行或者 Telnet 发送命令可以对 OpenD 做运维操作。

命令格式：`cmd -param_key1=param_value1 -param_key2=param_value2`

以 `help -cmd=exit` 为例，介绍Telnet的用法：
1. 在OpenD启动参数中，配置好 Telnet 地址和 Telnet 端口。
![telnet_GUI](../img/telnet_GUI.jpg)
![telnet_CMD](../img/telnet_CMD.jpg)
2. 启动 OpenD（会同时启动 Telnet）。
3. 通过 Telnet，向 OpenD 发送 `help -cmd=exit` 命令。
```python
from telnetlib import Telnet
with Telnet('127.0.0.1', 22222) as tn:  # Telnet 地址为：127.0.0.1，Telnet 端口为：22222
    tn.write(b'help -cmd=exit\r\n')
    reply = b''
    while True:
        msg = tn.read_until(b'\r\n', timeout=0.5)
        reply += msg
        if msg == b'':
            break
    print(reply.decode('gb2312'))
```


## 命令帮助
`help -cmd=exit`

查看指定命令详细信息，不指定参数则输出命令列表

* 参数:	
    - cmd: 命令

## 退出程序
`exit`

退出 OpenD 程序

## 请求手机验证码
`req_phone_verify_code `

请求手机验证码，当启用设备锁并初次在该设备登录，要求做安全验证。

* 频率限制:	
  - 每60秒内最多请求1次
  
## 输入手机验证码
`input_phone_verify_code -code=123456`

输入手机验证码，并继续登录流程。

* 参数:	
  - code: 手机验证码

* 频率限制:	
  - 每60秒内最多请求10次
 
## 请求图形验证码
`req_pic_verify_code`

请求图形验证码，当多次输入错登录密码时，需要输入图形验证码。

* 频率限制:	
  - 每60秒内最多请求10次
  
## 输入图形验证码
`input_pic_verify_code -code=1234`

输入图形验证码，并继续登录流程。

* 参数:	
  - code: 图形验证码

* 频率限制:	
  - 每60秒内最多请求10次
  
## 重登录
`relogin -login_pwd=123456`

当登录密码修改或中途打开设备锁等情况，要求用户重新登录时，可以使用该命令。只能重登当前帐号，不支持切换帐号。
密码参数主要用于登录密码修改的情况，不指定密码则使用启动时登录密码。

* 参数:	
  - login_pwd: 登录密码明文
  
  - login_pwd_md5: 登录密码密文（32 位 MD5 加密 16 进制）

* 频率限制:	
  - 每小时最多请求10次
  
## 检测与连接点之间的时延
`ping `

检测与连接点之前的时延

* 频率限制:	
  - 每60秒内最多请求10次
  
## 展示延迟统计报告
`show_delay_report -detail_report_path=D:/detail.txt -push_count_type=sr2cs`

展示延迟统计报告，包括推送延迟，请求延迟以及下单延迟。每日北京时间 6:00 清理数据。 

* 参数:	 
  - detail_report_path: 文件输出路径（MAC 系统仅支持绝对路径，不支持相对路径），可选参数，若不指定则输出到控制台
  
  - Paramters: push_count_type: 推送延迟的类型(sr2ss，ss2cr，cr2cs，ss2cs，sr2cs)，默认 sr2cs。
    + sr 指服务器接收时间(目前只有港股支持该时间)
    + ss 指服务器发出时间
    + cr 指 OpenD 接收时间 
    + cs 指 OpenD 发出时间

## 关闭 API 连接
`close_api_conn  -conn_id=123456`

关闭某条 API 连接，若不指定则关闭所有
  
  * 参数:
    - conn_id: API 连接 ID

## 展示订阅状态
`show_sub_info -conn_id=123456 -sub_info_path=D:/detail.txt`

展示某条连接的订阅状态，若不指定则展示所有
  
  * 参数:
    - conn_id: API 连接 ID
  
    - sub_info_path: 文件输出路径（MAC 系统仅支持绝对路径，不支持相对路径），可选参数，若不指定则输出到控制台
  
## 请求最高行情权限
`request_highest_quote_right`

当高级行情权限被其他设备（如：桌面端/手机端）占用时，可使用该命令重新请求最高行情权限（届时，其他处于登录状态的设备将无法使用高级行情）。

* 频率限制:	
  - 每60秒内最多请求10次

## 升级
`update`

运行该命令，可以一键更新 OpenD

---

# 行情接口总览

<table>
    <tr>
        <th colspan="2">模块</th>
        <th>接口名</th>
        <th>功能简介</th>
    </tr>
    <tr>
        <td rowspan="17">实时行情</td>
        <td rowspan="4">订阅</td>
	    <td><a href="../quote/sub.html#2263">subscribe</a></td>
	    <td>订阅实时数据，指定股票代码和订阅的数据类型即可</td>
    </tr>
    <tr>
	    <td><a href="../quote/sub.html#4908">unsubscribe</a></td>
	    <td>取消订阅</td>
    </tr>
    <tr>
	    <td><a href="../quote/sub.html#2489">unsubscribe_all</a></td>
	    <td>取消所有订阅</td>
    </tr>
    <tr>
	    <td><a href="../quote/query-subscription.html">query_subscription</a></td>
	    <td>查询订阅信息</td>
    </tr>
    <tr>
        <td rowspan="6">推送回调</td>
	    <td><a href="../quote/update-stock-quote.html">StockQuoteHandlerBase</a></td>
	    <td>报价推送</td>
    </tr>
    <tr>
	    <td><a href="../quote/update-order-book.html">OrderBookHandlerBase</a></td>
	    <td>摆盘推送</td>
    </tr>
    <tr>
	    <td><a href="../quote/update-kl.html">CurKlineHandlerBase</a></td>
	    <td>K 线推送</td>
    </tr>
    <tr>
	    <td><a href="../quote/update-ticker.html">TickerHandlerBase</a></td>
	    <td>逐笔推送</td>
    </tr>
    <tr>
	    <td><a href="../quote/update-rt.html">RTDataHandlerBase</a></td>
	    <td>分时推送</td>
    </tr>
    <tr>
	    <td><a href="../quote/update-broker.html">BrokerHandlerBase</a></td>
	    <td>经纪队列推送</td>
    </tr>
    <tr>
        <td rowspan="7">拉取</td>
	    <td><a href="../quote/get-market-snapshot.html">get_market_snapshot</a></td>
	    <td>获取市场快照</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-stock-quote.html">get_stock_quote</a></td>
	    <td>获取订阅股票报价的实时数据，有订阅要求限制</td>
    </tr>
    <tr>
        <td><a href="../quote/get-order-book.html">get_order_book</a></td>
	    <td>获取实时摆盘数据</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-kl.html">get_cur_kline</a></td>
	    <td>实时获取指定股票最近 num 个 K 线数据</td>
    </tr>
    <tr>
        <td><a href="../quote/get-rt.html">get_rt_data</a></td>
	    <td>获取指定股票的分时数据</td>
    </tr>
    <tr>
        <td><a href="../quote/get-ticker.html">get_rt_ticker</a></td>
	    <td>获取指定股票的实时逐笔。取最近 num 个逐笔</td>
    </tr>
    <tr>
        <td><a href="../quote/get-broker.html">get_broker_queue</a></td>
	    <td>获取股票的经纪队列</td>
    </tr>
    <tr>
        <td rowspan="31" colspan="2">基本数据</td>
	    <td><a href="../quote/get-market-state.html">get_market_state</a></td>
	    <td>获取股票对应市场的市场状态</td>
    </tr>
    <tr>
        <td><a href="../quote/get-capital-flow.html">get_capital_flow</a></td>
	    <td>获取个股资金流向</td>
    </tr>
    <tr>
        <td><a href="../quote/get-capital-distribution.html">get_capital_distribution</a></td>
	    <td>获取个股资金分布</td>
    </tr>
    <tr>
        <td><a href="../quote/get-owner-plate.html">get_owner_plate</a></td>
	    <td>获取单支或多支股票的所属板块信息列表</td>
    </tr>
    <tr>
        <td><a href="../quote/request-history-kline.html">request_history_kline</a></td>
	    <td>获取 K 线，不需要事先下载 K 线数据</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-rehab.html">get_rehab</a></td>
	    <td>获取给定股票的复权因子</td>
    </tr>
    <tr>
        <td><a href="../quote/get-financials-earnings-price-move.html">get_financials_earnings_price_move</a></td>
	    <td>获取财报日前后价格涨跌幅表现</td>
    </tr>
    <tr>
        <td><a href="../quote/get-financials-earnings-price-history.html">get_financials_earnings_price_history</a></td>
	    <td>获取财报日前后股价历史</td>
    </tr>
    <tr>
        <td><a href="../quote/get-financials-statements.html">get_financials_statements</a></td>
	    <td>获取财务报表</td>
    </tr>
    <tr>
        <td><a href="../quote/get-financials-revenue-breakdown.html">get_financials_revenue_breakdown</a></td>
	    <td>获取主营构成</td>
    </tr>
    <tr>
        <td><a href="../quote/get-research-analyst-consensus.html">get_research_analyst_consensus</a></td>
	    <td>获取分析师评级概述</td>
    </tr>
    <tr>
        <td><a href="../quote/get-research-rating-summary.html">get_research_rating_summary</a></td>
	    <td>获取评级汇总</td>
    </tr>
    <tr>
        <td><a href="../quote/get-research-morningstar-report.html">get_research_morningstar_report</a></td>
	    <td>获取晨星研究报告</td>
    </tr>
    <tr>
        <td><a href="../quote/get-valuation-detail.html">get_valuation_detail</a></td>
	    <td>获取个股/指数估值详情</td>
    </tr>
    <tr>
        <td><a href="../quote/get-valuation-plate-stock-list.html">get_valuation_plate_stock_list</a></td>
	    <td>获取板块/指数成分股估值列表</td>
    </tr>
    <tr>
        <td><a href="../quote/get-corporate-actions-dividends.html">get_corporate_actions_dividends</a></td>
	    <td>获取分红派息</td>
    </tr>
    <tr>
        <td><a href="../quote/get-corporate-actions-buybacks.html">get_corporate_actions_buybacks</a></td>
	    <td>获取回购</td>
    </tr>
    <tr>
        <td><a href="../quote/get-corporate-actions-stock-splits.html">get_corporate_actions_stock_splits</a></td>
	    <td>获取拆合股</td>
    </tr>
    <tr>
        <td><a href="../quote/get-shareholders-overview.html">get_shareholders_overview</a></td>
	    <td>获取持股统计</td>
    </tr>
    <tr>
        <td><a href="../quote/get-shareholders-holding-changes.html">get_shareholders_holding_changes</a></td>
	    <td>获取持股变动</td>
    </tr>
    <tr>
        <td><a href="../quote/get-shareholders-holder-detail.html">get_shareholders_holder_detail</a></td>
	    <td>获取持股明细</td>
    </tr>
    <tr>
        <td><a href="../quote/get-shareholders-institutional.html">get_shareholders_institutional</a></td>
	    <td>获取机构持股</td>
    </tr>
    <tr>
        <td><a href="../quote/get-insider-holder-list.html">get_insider_holder_list</a></td>
	    <td>获取内部人持股列表</td>
    </tr>
    <tr>
        <td><a href="../quote/get-insider-trade-list.html">get_insider_trade_list</a></td>
	    <td>获取内部人交易</td>
    </tr>
    <tr>
        <td><a href="../quote/get-company-profile.html">get_company_profile</a></td>
	    <td>获取公司概况</td>
    </tr>
    <tr>
        <td><a href="../quote/get-company-executives.html">get_company_executives</a></td>
	    <td>获取高管信息</td>
    </tr>
    <tr>
        <td><a href="../quote/get-company-executive-background.html">get_company_executive_background</a></td>
	    <td>获取高管背景</td>
    </tr>
    <tr>
        <td><a href="../quote/get-company-operational-efficiency.html">get_company_operational_efficiency</a></td>
	    <td>获取经营效率</td>
    </tr>
    <tr>
        <td><a href="../quote/get-top-ten-buy-sell-brokers.html">get_top_ten_buy_sell_brokers</a></td>
	    <td>获取十大经纪商买卖数据</td>
    </tr>
    <tr>
        <td><a href="../quote/get-daily-short-volume.html">get_daily_short_volume</a></td>
	    <td>获取每日卖空成交</td>
    </tr>
    <tr>
        <td><a href="../quote/get-short-interest.html">get_short_interest</a></td>
	    <td>获取空头持仓</td>
    </tr>
    <tr>
        <td rowspan="27" colspan="2">相关衍生品</td>
        <td><a href="../quote/get-option-expiration-date.html">get_option_expiration_date</a></td>
	    <td>通过标的股票，查询期权链的所有到期日</td>
    </tr>
    <tr>
        <td><a href="../quote/get-option-chain.html">get_option_chain</a></td>
	    <td>通过标的股查询期权</td>
    </tr>
    <tr>
        <td><a href="../quote/get-option-screen.html">get_option_screen</a></td>
	    <td>期权选股，支持标的属性与期权属性混合筛选</td>
    </tr>
    <tr>
        <td><a href="../quote/get-warrant.html">get_warrant</a></td>
	    <td>拉取窝轮和相关衍生品数据接口</td>
    </tr>
    <tr>
        <td><a href="../quote/get-warrant-screen.html">get_warrant_screen</a></td>
	    <td>窝轮筛选 V2，覆盖 45 列窝轮属性</td>
    </tr>
    <tr>
        <td><a href="../quote/get-referencestock-list.html">get_referencestock_list</a></td>
	    <td>获取证券的关联数据</td>
    </tr>
    <tr>
        <td><a href="../quote/get-future-info.html">get_future_info</a></td>
	    <td>获取期货合约资料</td>
    </tr>
    <tr>
        <td><a href="../quote/get-option-volatility.html">get_option_volatility</a></td>
	    <td>获取期权波动率分析</td>
    </tr>
    <tr>
        <td><a href="../quote/get-option-exercise-probability.html">get_option_exercise_probability</a></td>
	    <td>获取期权行权概率</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-strategy.html">get_option_strategy</a></td>
	    <td>获取期权策略</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-strategy-spread.html">get_option_strategy_spread</a></td>
	    <td>获取有效价差</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-strategy-analysis.html">get_option_strategy_analysis</a></td>
	    <td>期权损益分析</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-quote.html">get_option_quote</a></td>
	    <td>获取期权快照</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-market-statistic.html">get_option_market_statistic</a></td>
	    <td>期权市场统计</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-underlying-overview.html">get_option_underlying_overview</a></td>
	    <td>期权标的总览</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-underlying-his-statistic.html">get_option_underlying_his_statistic</a></td>
	    <td>期权标的历史统计</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-underlying-his-volatility.html">get_option_underlying_his_volatility</a></td>
	    <td>期权标的历史波动率</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-underlying-rank.html">get_option_underlying_rank</a></td>
	    <td>期权标的排行</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-rank.html">get_option_rank</a></td>
	    <td>期权合约排行</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-event.html">get_option_event</a></td>
	    <td>期权异动</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-event-alert.html">get_option_event_alert</a></td>
	    <td>查询异动提醒</td>
    </tr>
    <tr>
	    <td><a href="../quote/set-option-event-alert.html">set_option_event_alert</a></td>
	    <td>设置异动提醒</td>
    </tr>
    <tr>
	    <td><a href="../quote/update-option-event.html">OptionEventHandlerBase</a></td>
	    <td>期权异动推送</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-zero-dte-screener.html">get_option_zero_dte_screener</a></td>
	    <td>末日期权标的筛选</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-zero-dte-contract.html">get_option_zero_dte_contract</a></td>
	    <td>末日期权合约列表</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-earnings-screener.html">get_option_earnings_screener</a></td>
	    <td>财报期权筛选</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-seller-screener.html">get_option_seller_screener</a></td>
	    <td>期权卖方专区</td>
    </tr>
    <tr>
        <td rowspan="10" colspan="2">全市场筛选</td>
	    <td><a href="../quote/get-stock-filter.html">get_stock_filter</a></td>
	    <td>获取条件选股</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-stock-screen.html">get_stock_screen</a></td>
	    <td>条件选股 V2，因子覆盖 11 类 244+ 个，支持多字段排序与显式取回</td>
    </tr>
    <tr>
        <td><a href="../quote/get-plate-stock.html">get_plate_stock</a></td>
	    <td>获取特定板块下的股票列表</td>
    </tr>
    <tr>
        <td><a href="../quote/get-plate-list.html">get_plate_list</a></td>
	    <td>获取板块集合下的子板块列表</td>
    </tr>
    <tr>
        <td><a href="../quote/get-static-info.html">get_stock_basicinfo</a></td>
	    <td>获取指定市场中特定类型或特定股票的基本信息</td>
    </tr>
    <tr>
        <td><a href="../quote/get-ipo-list.html">get_ipo_list</a></td>
	    <td>获取指定市场的 ipo 列表</td>
    </tr>
    <tr>
        <td><a href="../quote/get-global-state.html">get_global_state</a></td>
	    <td>获取全局市场状态</td>
    </tr>
    <tr>
        <td><a href="../quote/request-trading-days.html">request_trading_days</a></td>
	    <td>获取交易日历</td>
    </tr>
    <tr>
        <td><a href="../quote/get-search-quote.html">get_search_quote</a></td>
	    <td>搜索行情标的</td>
    </tr>
    <tr>
        <td><a href="../quote/get-search-news.html">get_search_news</a></td>
	    <td>搜索资讯</td>
    </tr>
    <tr>
        <td rowspan="33" colspan="2">市场</td>
	    <td><a href="../quote/get-earnings-calendar.html">get_earnings_calendar</a></td>
	    <td>获取财报日历</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-macro-indicator-list.html">get_macro_indicator_list</a></td>
	    <td>获取宏观指标列表</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-macro-indicator-history.html">get_macro_indicator_history</a></td>
	    <td>获取宏观指标历史数据</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-fed-watch-target-rate.html">get_fed_watch_target_rate</a></td>
	    <td>获取FedWatch目标利率概率</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-fed-watch-dot-plot.html">get_fed_watch_dot_plot</a></td>
	    <td>获取FedWatch点阵图</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-earnings-beat-rank.html">get_earnings_beat_rank</a></td>
	    <td>获取盈利超预期排名</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-dividend-rank.html">get_dividend_rank</a></td>
	    <td>获取股息排行</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-dividend-calendar.html">get_dividend_calendar</a></td>
	    <td>获取派息日历</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-economic-calendar.html">get_economic_calendar</a></td>
	    <td>获取经济事件日历</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-us-pre-market-rank.html">get_us_pre_market_rank</a></td>
	    <td>获取盘前榜</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-us-after-hours-rank.html">get_us_after_hours_rank</a></td>
	    <td>获取盘后榜</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-us-overnight-rank.html">get_us_overnight_rank</a></td>
	    <td>获取夜盘榜</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-top-movers-rank.html">get_top_movers_rank</a></td>
	    <td>获取领涨领跌榜</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-hot-list.html">get_hot_list</a></td>
	    <td>获取热议榜</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-short-selling-rank.html">get_short_selling_rank</a></td>
	    <td>获取卖空异动榜</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-period-change-rank.html">get_period_change_rank</a></td>
	    <td>获取区间涨跌幅</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-high-dividend-soe-rank.html">get_high_dividend_soe_rank</a></td>
	    <td>获取破净高股息国央企</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-institution-list.html">get_institution_list</a></td>
	    <td>获取机构列表</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-institution-profile.html">get_institution_profile</a></td>
	    <td>获取机构概况</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-institution-distribution.html">get_institution_distribution</a></td>
	    <td>获取机构持仓行业分布</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-institution-holding-change.html">get_institution_holding_change</a></td>
	    <td>获取机构持仓变动</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-institution-holding-list.html">get_institution_holding_list</a></td>
	    <td>获取机构持股列表</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-ark-fund-holding.html">get_ark_fund_holding</a></td>
	    <td>获取ARK基金持仓</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-ark-stock-dynamic.html">get_ark_stock_dynamic</a></td>
	    <td>获取ARK个股交易动态</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-ark-active-transaction.html">get_ark_active_transaction</a></td>
	    <td>获取ARK主动交易聚合</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-rating-change.html">get_rating_change</a></td>
	    <td>获取评级变动</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-industrial-chain-list.html">get_industrial_chain_list</a></td>
	    <td>获取产业链列表</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-industrial-chain-detail.html">get_industrial_chain_detail</a></td>
	    <td>获取产业链详情</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-industrial-chain-by-plate.html">get_industrial_chain_by_plate</a></td>
	    <td>获取板块关联产业链</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-industrial-plate-info.html">get_industrial_plate_info</a></td>
	    <td>获取产业板块信息</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-industrial-plate-stock.html">get_industrial_plate_stock</a></td>
	    <td>获取产业板块成分股</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-heat-map-data.html">get_heat_map_data</a></td>
	    <td>获取热力图数据</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-rise-fall-distribution.html">get_rise_fall_distribution</a></td>
	    <td>获取涨跌分布</td>
    </tr>
    <tr>
        <td rowspan="3" colspan="2">技术指标</td>
        <td><a href="../quote/get-indicator-list.html">get_indicator_list</a></td>
        <td>获取指标列表</td>
    </tr>
    <tr>
        <td><a href="../quote/request-indicator-calc.html">request_indicator_calc_async</a></td>
        <td>异步发起指标计算</td>
    </tr>
    <tr>
        <td><a href="../quote/push-indicator-calc.html">IndicatorCalcHandlerBase</a></td>
        <td>指标异步计算结果推送</td>
    </tr>
    <tr>
        <td rowspan="7" colspan="2">个性化</td>
        <td><a href="../quote/get-history-kl-quota.html">get_history_kl_quota</a></td>
	    <td>获取已使用过的额度，即当前周期内已经下载过多少只股票</td>
    </tr>
    <tr>
        <td><a href="../quote/set-price-reminder.html">set_price_reminder</a></td>
	    <td>设置到价提醒</td>
    </tr>
    <tr>
        <td><a href="../quote/get-price-reminder.html">get_price_reminder</a></td>
	    <td>获取对某只股票(某个市场)设置的到价提醒列表</td>
    </tr>
    <tr>
        <td><a href="../quote/get-user-security-group.html">get_user_security_group</a></td>
	    <td>获取自选股分组列表</td>
    </tr>
    <tr>
        <td><a href="../quote/get-user-security.html">get_user_security</a></td>
	    <td>获取指定分组的自选股列表</td>
    </tr>
    <tr>
        <td><a href="../quote/modify-user-security.html">modify_user_security</a></td>
	    <td>修改指定分组的自选股列表</td>
    </tr>
    <tr>
	    <td><a href="../quote/update-price-reminder.html">PriceReminderHandlerBase</a></td>
	    <td>到价提醒推送</td>
    </tr>
</table>

---

# 行情对象

## 创建连接

`OpenQuoteContext(host='127.0.0.1', port=11111, is_encrypt=None, security_firm=SecurityFirm.NONE)`  

* **介绍**

    创建并初始化行情连接

* **参数**

    参数|类型|说明
    :-|:-|:-
    host|str|OpenD 监听的 IP 地址
    port|int|OpenD 监听的端口
    is_encrypt|bool|是否启用加密  (- 默认为 None，表示使用 [enable_proto_encrypt](../ftapi/init.md#319) 的设置
  - True：强制加密False：强制不加密)
    security_firm|[SecurityFirm](../trade/trade.md#572)|行情券商  (- 仅适用于创建加密货币行情连接
  - 默认值 NONE
  - 仅在传入 FUTUSECURITIES、FUTUINC、FUTUSG 时生效
  - 传入其他券商（MY/AU/JP/CA）或无效值，接口报错)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111, is_encrypt=False)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```


## 关闭连接

`close()`  

* **介绍**

    关闭行情接口类对象。默认情况下，Futu API 内部创建的线程会阻止进程退出，只有当所有 Context 都 close 后，进程才能正常退出。但通过 [set_all_thread_daemon](../ftapi/init.md#4570) 可以设置所有内部线程为 daemon 线程，这时即使没有调用 Context 的 close，进程也可以正常退出。

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

## 启动

`start()` 

* **介绍**

    启动异步接收推送数据

## 停止

`stop()` 

* **介绍**

    停止异步接收推送数据

---

# 订阅反订阅

## **订阅**  

`subscribe(code_list, subtype_list, is_first_push=True, subscribe_push=True, is_detailed_orderbook=False, extended_time=False, session=Session.NONE)` 
* **介绍**

    订阅注册需要的实时信息，指定股票和订阅的数据类型即可。  
    香港市场（含正股、窝轮、牛熊、期权、期货）订阅，需要 LV1 及以上的权限，BMP 权限下不支持订阅。  
    美股市场（含正股、ETFs）夜盘行情订阅，需要 LV1 及以上的权限，BMP 权限下不支持订阅。  

* **参数**

    参数|类型|说明
    :-|:-|:-
    code_list|list|需要订阅的股票代码列表  (list 中元素类型是 str)
    subtype_list|list|需要订阅的数据类型列表  (list 中元素类型是 [SubType](./quote.md#5878))
    is_first_push|bool|订阅成功之后是否立即推送一次缓存数据  (- True：推送缓存当脚本和 OpenD 之间出现断线重连，重新订阅时若设置为 True，会再次推送断线前的最后一条数据
  - False：不推送缓存。等待服务器的最新推送)
    subscribe_push|bool|订阅后是否推送  (订阅后，OpenD 提供了[两种取数据的方式](../qa/quote.html#2692)，如果您仅使用 **获取实时数据** 的方式，选择 False 可以节省一部分性能消耗
  - True：推送。如果使用 **实时数据回调** 的方式，则必须设置为 True
  - False：不推送。如果**仅**使用 **获取实时数据** 的方式，则建议设置为 False)
    is_detailed_orderbook|bool|是否订阅详细的摆盘订单明细  (- 仅用于港股 SF 行情权限下订阅港股 ORDER_BOOK 类型 
  - 美股美期 LV2 权限下不提供详细摆盘订单明细)
    extended_time|bool|是否允许美股盘前盘后数据  (仅用于订阅美股实时 K 线、实时分时、实时逐笔)
    session|[Session](./quote.md#9152)|美股订阅时段  (- 仅用于订阅美股实时 K 线、实时分时、实时逐笔
  - 订阅美股行情不支持入参OVERNIGHT
  - 最低OpenD版本：9.2.4207)


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">err_message</td>
            <td >NoneType</td>
            <td>当 ret == RET_OK 时，返回 None</td>
        </tr>
        <tr>
            <td >str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>


* **Example**

``` python
import time
from futu import *
class OrderBookTest(OrderBookHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(OrderBookTest,self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("OrderBookTest: error, msg: %s" % data)
            return RET_ERROR, data
        print("OrderBookTest ", data) # OrderBookTest 自己的处理逻辑
        return RET_OK, data
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
handler = OrderBookTest()
quote_ctx.set_handler(handler)  # 设置实时摆盘回调
quote_ctx.subscribe(['US.AAPL'], [SubType.ORDER_BOOK])  # 订阅买卖摆盘类型，OpenD 开始持续收到服务器的推送
time.sleep(15)  #  设置脚本接收 OpenD 的推送持续时间为15秒
quote_ctx.close()  # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅
```

* **Output**

``` python
OrderBookTest  {'code': 'US.AAPL', 'name': '苹果', 'svr_recv_time_bid': '2025-04-07 05:00:52.266', 'svr_recv_time_ask': '2025-04-07 05:00:53.973', 'Bid': [(180.2, 15, 3, {}), (180.19, 1, 1, {}), (180.18, 11, 2, {}), (180.14, 200, 1, {}), (180.13, 3, 2, {}), (180.1, 99, 3, {}), (180.05, 3, 1, {}), (180.03, 400, 1, {}), (180.02, 10, 1, {}), (180.01, 100, 1, {}), (180.0, 441, 24, {})], 'Ask': [(180.3, 100, 1, {}), (180.38, 4, 2, {}), (180.4, 100, 1, {}), (180.42, 200, 1, {}), (180.46, 29, 1, {}), (180.5, 1019, 2, {}), (180.6, 1000, 1, {}), (180.8, 2001, 3, {}), (180.84, 15, 2, {}), (181.0, 2036, 4, {}), (181.2, 2000, 2, {}), (181.3, 3, 1, {}), (181.4, 2021, 3, {}), (181.5, 59, 2, {}), (181.79, 9, 1, {}), (181.8, 20, 1, {}), (181.9, 94, 4, {}), (181.98, 20, 1, {}), (182.0, 150, 7, {})]}

```

## **取消订阅**  

`unsubscribe(code_list, subtype_list, unsubscribe_all=False)`  
* **介绍**

    取消订阅   

* **参数**
    参数|类型|说明
    :-|:-|:-
    code_list|list|取消订阅的股票代码列表  (list 中元素类型是 str)
    subtype_list|list|需要订阅的数据类型列表  (list 中元素类型是 [SubType](./quote.md#5878))
    unsubscribe_all|bool|取消所有订阅  (为 True 时忽略其他参数)


* **Return**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">err_message</td>
            <td>NoneType</td>
            <td>当 ret == RET_OK, 返回 None</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK, 返回错误描述</td>
        </tr>
    </table>

* **Example**

``` python
from futu import *
import time
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

print('current subscription status :', quote_ctx.query_subscription())  # 查询初始订阅状态
ret_sub, err_message = quote_ctx.subscribe(['US.AAPL'], [SubType.QUOTE, SubType.TICKER], subscribe_push=False, session=Session.ALL)
# 先订阅了AAPL全时段 QUOTE 和 TICKER 两个类型。订阅成功后 OpenD 将持续收到服务器的推送，False 代表暂时不需要推送给脚本
if ret_sub == RET_OK:   # 订阅成功
    print('subscribe successfully！current subscription status :', quote_ctx.query_subscription())  # 订阅成功后查询订阅状态
    time.sleep(60)  # 订阅之后至少1分钟才能取消订阅
    ret_unsub, err_message_unsub = quote_ctx.unsubscribe(['US.AAPL'], [SubType.QUOTE])
    if ret_unsub == RET_OK:
        print('unsubscribe successfully！current subscription status:', quote_ctx.query_subscription())  # 取消订阅后查询订阅状态
    else:
        print('unsubscription failed！', err_message_unsub)
else:
    print('subscription failed', err_message)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

``` python
current subscription status : (0, {'total_used': 0, 'remain': 1000, 'own_used': 0, 'sub_list': {}})
subscribe successfully！current subscription status : (0, {'total_used': 2, 'remain': 998, 'own_used': 2, 'sub_list': {'QUOTE': ['US.AAPL'], 'TICKER': ['US.AAPL']}})
unsubscribe successfully！current subscription status: (0, {'total_used': 1, 'remain': 999, 'own_used': 1, 'sub_list': {'TICKER': ['US.AAPL']}})
```

## **取消所有订阅**  

`unsubscribe_all()`  

* **介绍**

取消所有订阅   


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">err_message</td>
            <td>NoneType</td>
            <td>当 ret == RET_OK, 返回 None</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK, 返回错误描述</td>
        </tr>
    </table>

* **Example** 

``` python
from futu import *
import time
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

print('current subscription status :', quote_ctx.query_subscription())  # 查询初始订阅状态
ret_sub, err_message = quote_ctx.subscribe(['US.AAPL'], [SubType.QUOTE, SubType.TICKER], subscribe_push=False, session=Session.None)
# 先订阅了AAPL全时段 QUOTE 和 TICKER 两个类型。订阅成功后 OpenD 将持续收到服务器的推送，False 代表暂时不需要推送给脚本
if ret_sub == RET_OK:  # 订阅成功
    print('subscribe successfully！current subscription status :', quote_ctx.query_subscription())  # 订阅成功后查询订阅状态
    time.sleep(60)  # 订阅之后至少1分钟才能取消订阅
    ret_unsub, err_message_unsub = quote_ctx.unsubscribe_all()  # 取消所有订阅
    if ret_unsub == RET_OK:
        print('unsubscribe all successfully！current subscription status:', quote_ctx.query_subscription())  # 取消订阅后查询订阅状态
    else:
        print('Failed to cancel all subscriptions！', err_message_unsub)
else:
    print('subscription failed', err_message)
quote_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

``` python
current subscription status : (0, {'total_used': 0, 'remain': 1000, 'own_used': 0, 'sub_list': {}})
subscribe successfully！current subscription status : (0, {'total_used': 2, 'remain': 998, 'own_used': 2, 'sub_list': {'QUOTE': ['US.AAPL'], 'TICKER': ['US.AAPL']}})
unsubscribe all successfully！current subscription status: (0, {'total_used': 0, 'remain': 1000, 'own_used': 0, 'sub_list': {}})
```

::: tip 接口限制
- 支持多种实时数据类型的订阅，参见 [SubType](./quote.md#5878) ，每支股票订阅一个类型占用一个额度。
- 订阅额度规则请参见 [订阅额度 & 历史 K 线额度](../intro/authority.md#1314)。
- 至少订阅一分钟才可以反订阅。
- 由于港股 SF 行情摆盘数据量较大，为保证 SF 行情的速度和 OpenD 的处理性能，目前 SF 权限用户仅限同时订阅 50 只证券类产品（含 hkex 的正股、窝轮、牛熊）的摆盘，剩余订阅额度仍可用于订阅其他类型，如：逐笔，买卖经纪等。
- 港股期权期货在 LV1 权限下，不支持订阅逐笔类型。
:::

---

# 获取订阅状态

`query_subscription(is_all_conn=True)`

* **介绍**

    获取订阅信息

* **参数**
    参数|类型|说明
    :-|:-|:-
    is_all_conn|bool|是否返回所有连接的订阅状态  (True：返回所有连接的订阅状态False：只返回当前连接的订阅状态)


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回订阅信息数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 订阅信息数据字典格式如下：
    
            {
                'total_used': 4,    # 所有连接已使用的订阅额度
                'own_used': 0,       # 当前连接已使用的订阅额度
                'remain': 496,       #  剩余的订阅额度
                'own_security_firm': 'FUTUSECURITIES',  # 当前连接的券商标识
                'sub_list':          #  每种订阅类型对应的股票列表
                {
                    '订阅的类型': 该订阅类型下所有已订阅股票列表,
                    …
                }
            }
    
* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

quote_ctx.subscribe(['HK.00700'], [SubType.QUOTE])
ret, data = quote_ctx.query_subscription()
if ret == RET_OK:
    print(data)
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
{'total_used': 1, 'remain': 999, 'own_used': 1, 'own_security_firm': 'N/A', 'sub_list': {'QUOTE': ['HK.00700']}}
```

---

# 实时报价回调

`on_recv_rsp(self, rsp_pb)`

* **介绍**

    实时报价回调，异步处理已订阅股票的实时报价推送。  
    在收到实时报价数据推送后会回调到该函数，您需要在派生类中覆盖 on_recv_rsp。  
	
* **参数**

    参数|类型|说明
    :-|:-|:-
    rsp_pb|Qot_UpdateBasicQot_pb2.Response|派生类中不需要直接处理该参数

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回报价数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 报价数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        data_date|str|日期
        data_time|str|当前价更新时间  (格式：yyyy-MM-dd HH:mm:ss
港股和 A 股市场默认是北京时间，美股市场默认是美东时间)
        last_price|float|最新价格
        open_price|float|今日开盘价
        high_price|float|最高价格
        low_price|float|最低价格
        prev_close_price|float|昨收盘价格
        volume|float|成交数量
        turnover|float|成交金额
        turnover_rate|float|换手率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        amplitude|int|振幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        suspension|bool|是否停牌  (True：停牌)
        listing_date|str|上市日期  (格式：yyyy-MM-dd)
        price_spread|float|当前向上的价差  (即摆盘数据的卖档的相邻档位的报价差)
        dark_status|[DarkStatus](./quote.md#1965)|暗盘交易状态
        sec_status|[SecurityStatus](./quote.md#9969)|股票状态
        strike_price|float|行权价
        contract_size|float|每份合约数
        open_interest|int|未平仓合约数
        implied_volatility|float|隐含波动率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        premium|float|溢价  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        delta|float|希腊值 Delta
        gamma|float|希腊值 Gamma
        vega|float|希腊值 Vega
        theta|float|希腊值 Theta
        rho|float|希腊值 Rho
        index_option_type|[IndexOptionType](./quote.md#5149)|指数期权类型
        net_open_interest|int|净未平仓合约数  (仅港股期权适用)
        expiry_date_distance|int|距离到期日天数  (负数表示已过期)
        contract_nominal_value|float|合约名义金额  (仅港股期权适用)
        owner_lot_multiplier|float|相等正股手数  (指数期权无该字段 ，仅港股期权适用)
        option_area_type|[OptionAreaType](./quote.md#7077)|期权类型（按行权时间）
        contract_multiplier|float|合约乘数
        pre_price|float|盘前价格
        pre_high_price|float|盘前最高价
        pre_low_price|float|盘前最低价
        pre_volume|int|盘前成交量
        pre_turnover|float|盘前成交额
        pre_change_val|float|盘前涨跌额
        pre_change_rate|float|盘前涨跌幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        pre_amplitude|float|盘前振幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        after_price|float|盘后价格
        after_high_price|float|盘后最高价
        after_low_price|float|盘后最低价
        after_volume|int|盘后成交量  (科创板支持此数据)
        after_turnover|float|盘后成交额  (科创板支持此数据)
        after_change_val|float|盘后涨跌额
        after_change_rate|float|盘后涨跌幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        after_amplitude|float|盘后振幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        overnight_price|float|夜盘价格
        overnight_high_price|float|夜盘最高价
        overnight_low_price|float|夜盘最低价
        overnight_volume|int|夜盘成交量
        overnight_turnover|float|夜盘成交额
        overnight_change_val|float|夜盘涨跌额
        overnight_change_rate|float|夜盘涨跌幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        overnight_amplitude|float|夜盘振幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        last_settle_price|float|昨结  (期货特有字段)
        position|float|持仓量  (期货特有字段)
        position_change|float|日增仓  (期货特有字段)

* **Example**

```python
import time
from futu import *

class StockQuoteTest(StockQuoteHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(StockQuoteTest,self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("StockQuoteTest: error, msg: %s" % data)
            return RET_ERROR, data
        print("StockQuoteTest ", data) # StockQuoteTest 自己的处理逻辑
        return RET_OK, data
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
handler = StockQuoteTest()
quote_ctx.set_handler(handler)  # 设置实时报价回调
ret, data = quote_ctx.subscribe(['US.AAPL'], [SubType.QUOTE])  # 订阅实时报价类型，OpenD 开始持续收到服务器的推送
if ret == RET_OK:
    print(data)
else:
    print('error:', data)
time.sleep(15)  #  设置脚本接收 OpenD 的推送持续时间为15秒
quote_ctx.close()   # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅    	
```

* **Output**

```python
StockQuoteTest        code name data_date data_time  last_price  open_price  high_price  low_price  prev_close_price  volume  turnover  turnover_rate  amplitude  suspension listing_date  price_spread dark_status sec_status strike_price contract_size open_interest implied_volatility premium delta gamma vega theta  rho net_open_interest expiry_date_distance contract_nominal_value owner_lot_multiplier option_area_type contract_multiplier last_settle_price position position_change index_option_type pre_price pre_high_price pre_low_price pre_volume pre_turnover pre_change_val pre_change_rate pre_amplitude after_price after_high_price after_low_price after_volume after_turnover after_change_val after_change_rate after_amplitude overnight_price overnight_high_price overnight_low_price overnight_volume overnight_turnover overnight_change_val overnight_change_rate overnight_amplitude
0  US.AAPL   苹果                             0.0         0.0         0.0        0.0               0.0       0       0.0            0.0        0.0       False                        0.0         N/A     NORMAL          N/A           N/A           N/A                N/A     N/A   N/A   N/A  N/A   N/A  N/A               N/A                  N/A                    N/A                  N/A              N/A                 N/A               N/A      N/A             N/A               N/A       N/A            N/A           N/A        N/A          N/A            N/A             N/A           N/A         N/A              N/A             N/A          N/A            N/A              N/A               N/A             N/A             N/A                  N/A                 N/A              N/A                N/A                  N/A                   N/A                 N/A
```

:::tip 提示
* 此接口提供了持续获取推送数据的功能，如需一次性获取实时数据，请参考 [获取实时报价](./get-stock-quote.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
:::

---

# 实时摆盘回调

`on_recv_rsp(self, rsp_pb)`

* **介绍**

    实时摆盘回调，异步处理已订阅股票的实时摆盘推送。
    在收到实时摆盘数据推送后会回调到该函数，您需要在派生类中覆盖 on_recv_rsp。  
	
* **参数**

    参数|类型|说明
    :-|:-|:-
    rsp_pb|Qot_UpdateOrderBook_pb2.Response|派生类中不需要直接处理该参数

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回摆盘数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 摆盘数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        svr_recv_time_bid|str|富途服务器从交易所收到买盘数据的时间  (部分数据的接收时间为零，例如服务器重启或第一次推送的缓存数据)
        svr_recv_time_ask|str|富途服务器从交易所收到卖盘数据的时间  (部分数据的接收时间为零，例如服务器重启或第一次推送的缓存数据)
        order_book_type|[OrderBookType](./quote.md#3141)|摆盘类型
        Bid|list|每个元祖包含如下信息：委托价格，委托数量，委托订单数，委托订单明细  (委托订单明细
  - 明细内容：交易所订单 ID，单笔委托数量
  - 港股 SF 权限下最多支持 1000 笔委托订单明细；其余行情权限不支持获取此类数据)
        Ask|list|每个元祖包含如下信息：委托价格，委托数量，委托订单数，委托订单明细  (委托订单明细
  - 明细内容：交易所订单 ID，单笔委托数量
  - 港股 SF 权限下最多支持 1000 笔委托订单明细；其余行情权限不支持获取此类数据)

        其中，Bid 和 Ask 字段的结构如下：  

          'Bid': [ (bid_price1, bid_volume1, order_num, {'orderid1': order_volume1, 'orderid2': order_volume2, …… }), (bid_price2, bid_volume2, order_num,  {'orderid1': order_volume1, 'orderid2': order_volume2, …… }),…]
          'Ask': [ (ask_price1, ask_volume1，order_num, {'orderid1': order_volume1, 'orderid2': order_volume2, …… }), (ask_price2, ask_volume2, order_num, {'orderid1': order_volume1, 'orderid2': order_volume2, …… }),…] 

* **Example**

```python
import time
from futu import *
class OrderBookTest(OrderBookHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(OrderBookTest,self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("OrderBookTest: error, msg: %s" % data)
            return RET_ERROR, data
        print("OrderBookTest ", data) # OrderBookTest 自己的处理逻辑
        return RET_OK, data
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
handler = OrderBookTest()
quote_ctx.set_handler(handler)  # 设置实时摆盘回调
ret, data = quote_ctx.subscribe(['US.AAPL'], [SubType.ORDER_BOOK])  # 订阅买卖摆盘类型，OpenD 开始持续收到服务器的推送
if ret == RET_OK:
    print(data)
else:
    print('error:', data)
time.sleep(15)  #  设置脚本接收 OpenD 的推送持续时间为15秒
quote_ctx.close()  # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅
```

* **Output**

```python
OrderBookTest  {'code': 'US.AAPL', 'name': '苹果', 'svr_recv_time_bid': '', 'svr_recv_time_ask': '', 'order_book_type': 'NORMAL', 'Bid': [(179.77, 100, 1, {}), (179.68, 200, 1, {}), (179.65, 2, 2, {}), (179.64, 27, 1, {}), (179.6, 9, 2, {}), (179.58, 39, 2, {}), (179.5, 13, 4, {}), (179.48, 331, 2, {}), (179.4, 1002, 2, {}), (179.38, 330, 1, {}), (179.37, 2, 1, {}), (179.3, 47, 1, {}), (179.28, 330, 1, {}), (179.21, 2, 1, {}), (179.2, 1000, 1, {}), (179.18, 330, 1, {}), (179.17, 100, 1, {}), (179.16, 1, 1, {}), (179.13, 400, 1, {}), (179.1, 3000, 1, {}), (179.08, 330, 1, {}), (179.05, 125, 2, {}), (179.01, 17, 2, {}), (179.0, 81, 7, {})], 'Ask': [(179.95, 400, 2, {}), (180.0, 360, 2, {}), (180.05, 20, 1, {}), (180.1, 246, 4, {}), (180.18, 20, 1, {}), (180.2, 2030, 3, {}), (180.23, 20, 1, {}), (180.3, 23, 1, {}), (180.33, 15, 1, {}), (180.4, 2000, 2, {}), (180.49, 5, 1, {}), (180.59, 253, 1, {}), (180.6, 2000, 2, {}), (180.8, 2010, 3, {}), (181.0, 2018, 4, {}), (181.08, 1, 1, {}), (181.2, 1009, 2, {}), (181.3, 17, 3, {}), (181.4, 1, 1, {}), (181.5, 50, 1, {}), (181.79, 9, 1, {}), (181.9, 66, 2, {})]}
```

:::tip 提示
* 此接口提供了持续获取推送数据的功能，如需一次性获取实时数据，请参考 [获取实时摆盘](./get-order-book.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
* 美股市场实时摆盘回调，会持续推送当前交易时段的实时摆盘，无需设置时段。
:::

---

# 实时 K 线回调

`on_recv_rsp(self, rsp_pb)`

* **介绍**

    实时 K 线回调，异步处理已订阅股票的实时 K 线推送。

    在收到实时 K 线数据推送后会回调到该函数，您需要在派生类中覆盖 on_recv_rsp。  
	
* **参数**

    参数|类型|说明
    :-|:-|:-
    rsp_pb|Qot_UpdateKL_pb2.Response|派生类中不需要直接处理该参数

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回 K 线数据数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * K 线数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        time_key|str|时间  (格式：yyyy-MM-dd HH:mm:ss
港股和 A 股市场默认是北京时间，美股市场默认是美东时间)
        open|float|开盘价
        close|float|收盘价
        high|float|最高价
        low|float|最低价
        volume|float|成交量
        turnover|float|成交额
        pe_ratio|float|市盈率
        turnover_rate|float|换手率  (该字段为百分比字段，默认返回小数，如 0.01 实际对应 1%)
        last_close|float|上一个 K 线的收盘价  (即前一个 K 线的收盘价出于效率原因，第一个数据的 last_close 可能为 0)
        k_type|[KLType](./quote.md#4119)|K 线类型

* **Example**

```python
import time
from futu import *
class CurKlineTest(CurKlineHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(CurKlineTest,self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("CurKlineTest: error, msg: %s" % data)
            return RET_ERROR, data
        print("CurKlineTest ", data) # CurKlineTest 自己的处理逻辑
        return RET_OK, data
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
handler = CurKlineTest()
quote_ctx.set_handler(handler)  # 设置实时K线回调
ret, data = quote_ctx.subscribe(['US.AAPL'], [SubType.K_1M], session=Session.ALL)   # 订阅 K 线数据类型，OpenD 开始持续收到服务器的推送
if ret == RET_OK:
    print(data)
else:
    print('error:', data)
time.sleep(15)  # 设置脚本接收 OpenD 的推送持续时间为15秒
quote_ctx.close()   # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅    
```

* **Output**

```python
CurKlineTest        code name             time_key    open   close    high    low  volume   turnover k_type  last_close
0  US.AAPL   苹果  2025-04-07 05:15:00  180.39  180.26  180.46  180.2  1322.0  238340.48   K_1M         0.0
```

:::tip 提示
* 此接口提供了持续获取推送数据的功能，如需一次性获取实时数据，请参考 [获取实时 K 线](./get-kl.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
* **期权**，仅提供日K, 1分K，5分K，15分K，60分K。
:::

---

# 实时分时回调

`on_recv_rsp(self, rsp_pb)`

* **介绍**

    实时分时回调，异步处理已订阅股票的实时分时推送。  
    在收到实时分时数据推送后会回调到该函数，您需要在派生类中覆盖 on_recv_rsp。  
	
* **参数**

    参数|类型|说明
    :-|:-|:-
    rsp_pb|Qot_UpdateRT_pb2.Response|派生类中不需要直接处理该参数

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回分时数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 分时数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        time|str|时间  (格式：yyyy-MM-dd HH:mm:ss 港股和 A 股市场默认是北京时间，美股市场默认是美东时间)
        is_blank|bool|数据状态  (False：正常数据True：伪造数据)
        opened_mins|int|零点到当前多少分钟
        cur_price|float|当前价格
        last_close|float|昨天收盘的价格
        avg_price|float|平均价格  (对于期权，该字段为 None)
        volume|float|成交量
        turnover|float|成交金额

* **Example**

```python
import time
from futu import *

class RTDataTest(RTDataHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(RTDataTest, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("RTDataTest: error, msg: %s" % data)
            return RET_ERROR, data
        print("RTDataTest ", data) # RTDataTest 自己的处理逻辑
        return RET_OK, data
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
handler = RTDataTest()
quote_ctx.set_handler(handler)  # 设置实时分时推送回调
ret, data = quote_ctx.subscribe(['US.AAPL'], [SubType.RT_DATA], session=Session.ALL) # 订阅分时类型，OpenD 开始持续收到服务器的推送
if ret == RET_OK:
    print(data)
else:
    print('error:', data)
time.sleep(15)  # 设置脚本接收 OpenD 的推送持续时间为15秒
quote_ctx.close()   # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅    
```

* **Output**

```python
RTDataTest        code name                 time  is_blank  opened_mins  cur_price  last_close   avg_price   turnover  volume
0  US.AAPL   苹果  2025-04-07 05:24:00     False          324     179.53      188.38  180.465762  651262.42    3624
```

:::tip 提示
* 此接口提供了持续获取推送数据的功能，如需一次性获取实时数据，请参考 [获取实时分时](./get-rt.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
:::

---

# 实时逐笔回调

`on_recv_rsp(self, rsp_pb)`

* **介绍**

    实时逐笔回调，异步处理已订阅股票的实时逐笔推送。  
    在收到实时逐笔数据推送后会回调到该函数，您需要在派生类中覆盖 on_recv_rsp。  
	
* **参数**

    参数|类型|说明
    :-|:-|:-
    rsp_pb|Qot_UpdateTicker_pb2.Response|派生类中不需要直接处理该参数

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回逐笔数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 逐笔数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        sequence|int|逐笔序号
        time|str|成交时间  (格式：yyyy-MM-dd HH:mm:ss:xxx
港股和 A 股市场默认是北京时间，美股市场默认是美东时间)
        price|float|成交价格
        volume|float|成交数量  (股数)
        turnover|float|成交金额
        ticker_direction|[TickerDirect](./quote.md#8723)|逐笔方向
        type|[TickerType](./quote.md#2358)|逐笔类型
        push_data_type|[PushDataType](./quote.md#7025)|数据来源

* **Example**

```python
import time
from futu import *

class TickerTest(TickerHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(TickerTest,self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("TickerTest: error, msg: %s" % data)
            return RET_ERROR, data
        print("TickerTest ", data) # TickerTest 自己的处理逻辑
        return RET_OK, data
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
handler = TickerTest()
quote_ctx.set_handler(handler)  # 设置实时逐笔推送回调
ret, data = quote_ctx.subscribe(['US.AAPL'], [SubType.TICKER], session=Session.ALL) # 订阅逐笔类型，OpenD 开始持续收到服务器的推送
if ret == RET_OK:
    print(data)
else:
    print('error:', data)
time.sleep(15)  # 设置脚本接收 OpenD 的推送持续时间为15秒
quote_ctx.close()   # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅	
```

* **Output**

```python
TickerTest        code name                     time   price  volume  turnover ticker_direction             sequence     type push_data_type
0  US.AAPL   苹果  2025-04-07 05:25:44.116  179.81     9.0   1618.29          NEUTRAL  7490500033117159426  ODD_LOT          CACHE

```

:::tip 提示
* 此接口提供了持续获取推送数据的功能，如需一次性获取实时数据，请参考 [获取实时逐笔](./get-ticker.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
* 行情连接断开重连后，OpenD 拉取断开期间，距离当前最近的（最多 50 根）逐笔数据并推送，可通过逐笔推送类型字段区分
:::

---

# 实时经纪队列回调

`on_recv_rsp(self, rsp_pb)`

* **介绍**

    实时经纪队列回调，异步处理已订阅股票的实时经纪队列推送。  
    在收到实时经纪队列数据推送后会回调到该函数，您需要在派生类中覆盖 on_recv_rsp。  
	
* **参数**

    参数|类型|说明
    :-|:-|:-
    rsp_pb|Qot_UpdateBroker_pb2.Response|派生类中不需要直接处理该参数


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>tuple</td>
            <td>当 ret == RET_OK，返回经纪队列数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 经纪队列元组内容如下：
        字段|类型|说明
        :-|:-|:-
        stock_code|str|股票
        bid_frame_table|pd.DataFrame|买盘数据
        ask_frame_table|pd.DataFrame|卖盘数据

        * bid_frame_table 格式如下：
            字段|类型|说明
            :-|:-|:-
            code|str|股票代码
            name|str|股票名称
            bid_broker_id|int|经纪买盘 ID
            bid_broker_name|str|经纪买盘名称
            bid_broker_pos|int|经纪档位
            order_id|int|交易所订单 ID  (- 不是下单接口返回的订单 ID
  - 只有港股 SF 行情权限支持返回该字段)
            order_volume|int|单笔委托数量  (只有港股 SF 行情权限支持返回该字段)
        * ask_frame_table 格式如下：
            字段|类型|说明
            :-|:-|:-
            code|str|股票代码
            name|str|股票名称
            ask_broker_id|int|经纪卖盘 ID
            ask_broker_name|str|经纪卖盘名称
            ask_broker_pos|int|经纪档位
            order_id|int|交易所订单 ID  (- 不是下单接口返回的订单 ID
  - 只有港股 SF 行情权限支持返回该字段)
            order_volume|int|单笔委托数量  (只有港股 SF 行情权限支持返回该字段)

* **Example**

```python
import time
from futu import *
    
class BrokerTest(BrokerHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, err_or_stock_code, data = super(BrokerTest, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("BrokerTest: error, msg: {}".format(err_or_stock_code))
            return RET_ERROR, data
        print("BrokerTest: stock: {} data: {} ".format(err_or_stock_code, data))  # BrokerTest 自己的处理逻辑
        return RET_OK, data
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
handler = BrokerTest()
quote_ctx.set_handler(handler)  # 设置实时经纪推送回调
ret, data = quote_ctx.subscribe(['HK.00700'], [SubType.BROKER]) # 订阅经纪类型，OpenD 开始持续收到服务器的推送
if ret == RET_OK:
    print(data)
else:
    print('error:', data)
time.sleep(15)  # 设置脚本接收 OpenD 的推送持续时间为15秒
quote_ctx.close()   # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅
```

* **Output**

```python
BrokerTest: stock: HK.00700 data: [        code  name  bid_broker_id bid_broker_name  bid_broker_pos order_id order_volume
0   HK.00700  腾讯控股           5338          J.P.摩根               1      N/A          N/A
..       ...   ...            ...             ...             ...      ...          ...
36  HK.00700  腾讯控股           8305  富途证券国际(香港)有限公司               4      N/A          N/A

[37 rows x 7 columns],         code  name  ask_broker_id ask_broker_name  ask_broker_pos order_id order_volume
0   HK.00700  腾讯控股           1179  华泰金融控股(香港)有限公司               1      N/A          N/A
..       ...   ...            ...             ...             ...      ...          ...
39  HK.00700  腾讯控股           6996      中国投资信息有限公司               1      N/A          N/A

[40 rows x 7 columns]] 
```

:::tip 提示
* 此接口提供了持续获取推送数据的功能，如需一次性获取实时数据，请参考 [获取实时经纪队列](./get-broker.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
* 港股 BMP及LV1 权限下，不支持获取经纪队列数据
:::

---

# 获取快照

`get_market_snapshot(code_list)`

* **介绍**

    获取快照数据

* **参数**
    参数|类型|说明
    :-|:-|:-
    code_list|list|股票代码列表  (每次最多可请求 400 个标的list 内元素类型为 str)


* **返回**
 
    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回股票快照数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 股票快照数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        update_time|str|当前价更新时间  (格式：yyyy-MM-dd HH:mm:ss 港股和 A 股市场默认是北京时间，美股市场默认是美东时间)
        last_price|float|最新价格
        open_price|float|今日开盘价
        high_price|float|最高价格
        low_price|float|最低价格
        prev_close_price|float|昨收盘价格
        volume|float|成交数量
        turnover|float|成交金额
        turnover_rate|float|换手率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        suspension|bool|是否停牌  (True：停牌)
        listing_date|str|上市日期  (格式：yyyy-MM-dd)
        equity_valid|bool|是否正股  (此字段返回为 True 时，以下正股相关字段才有合法数值)
        issued_shares|int|总股本
        total_market_val|float|总市值  (单位：元)
        net_asset|int|资产净值
        net_profit|int|净利润
        earning_per_share|float|每股盈利
        outstanding_shares|int|流通股本
        net_asset_per_share|float|每股净资产
        circular_market_val|float|流通市值  (单位：元)
        ey_ratio|float|收益率  (该字段为比例字段，默认不展示 %)
        pe_ratio|float|市盈率  (该字段为比例字段，默认不展示 %)
        pb_ratio|float|市净率  (该字段为比例字段，默认不展示 %)
        pe_ttm_ratio|float|市盈率 TTM  (该字段为比例字段，默认不展示 %)
        dividend_ttm|float|股息 TTM，派息
        dividend_ratio_ttm|float|股息率 TTM  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        dividend_lfy|float|股息 LFY，上一年度派息
        dividend_lfy_ratio|float|股息率 LFY  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        stock_owner|str|窝轮所属正股的代码或期权的标的股代码
        wrt_valid|bool|是否是窝轮  (此字段返回为 True 时，以下窝轮相关字段才有合法数值)
        wrt_conversion_ratio|float|换股比率
        wrt_type|[WrtType](./quote.md#926)|窝轮类型
        wrt_strike_price|float|行使价格
        wrt_maturity_date|str|格式化窝轮到期时间
        wrt_end_trade|str|格式化窝轮最后交易时间
        wrt_leverage|float|杠杆比率  (单位：倍)
        wrt_ipop|float|价内/价外  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        wrt_break_even_point|float|打和点
        wrt_conversion_price|float|换股价
        wrt_price_recovery_ratio|float|正股距收回价  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        wrt_score|float|窝轮综合评分
        wrt_code|str|窝轮对应的正股（此字段已废除，修改为 stock_owner）
        wrt_recovery_price|float|窝轮收回价
        wrt_street_vol|float|窝轮街货量
        wrt_issue_vol|float|窝轮发行量
        wrt_street_ratio|float|窝轮街货占比  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        wrt_delta|float|窝轮对冲值
        wrt_implied_volatility|float|窝轮引伸波幅
        wrt_premium|float|窝轮溢价  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        wrt_upper_strike_price|float|上限价  (仅界内证支持该字段)
        wrt_lower_strike_price|float|下限价  (仅界内证支持该字段)
        wrt_inline_price_status|[PriceType](./quote.md#6407)|界内界外  (仅界内证支持该字段)
        wrt_issuer_code|str|发行人代码
        option_valid|bool|是否是期权  (此字段返回为 True 时，以下期权相关字段才有合法数值)
        option_type|[OptionType](./quote.md#3713)|期权类型
        strike_time|str|期权行权日  (格式：yyyy-MM-dd
港股和 A 股市场默认是北京时间，美股市场默认是美东时间)
        option_strike_price|float|行权价
        option_contract_size|float|每份合约数
        option_open_interest|int|总未平仓合约数
        option_implied_volatility|float|隐含波动率
        option_premium|float|溢价
        option_delta|float|希腊值 Delta
        option_gamma|float|希腊值 Gamma
        option_vega|float|希腊值 Vega
        option_theta|float|希腊值 Theta
        option_rho|float|希腊值 Rho
        index_option_type|[IndexOptionType](./quote.md#5149)|指数期权类型
        option_net_open_interest|int|净未平仓合约数  (仅港股期权适用)
        option_expiry_date_distance|int|距离到期日天数  (负数表示已过期)
        option_contract_nominal_value|float|合约名义金额  (仅港股期权适用)
        option_owner_lot_multiplier|float|相等正股手数  (指数期权无该字段，仅港股期权适用)
        option_area_type|[OptionAreaType](./quote.md#7077)|期权类型（按行权时间）
        option_contract_multiplier|float|合约乘数
        plate_valid|bool|是否为板块类型  (此字段返回为 True 时，以下板块相关字段才有合法数值)
        plate_raise_count|int|板块类型上涨支数
        plate_fall_count|int|板块类型下跌支数
        plate_equal_count|int|板块类型平盘支数
        index_valid|bool|是否有指数类型  (此字段返回为 True 时，以下指数相关字段才有合法数值)
        index_raise_count|int|指数类型上涨支数
        index_fall_count|int|指数类型下跌支数
        index_equal_count|int|指数类型平盘支数
        lot_size|int|每手股数，股票期权表示每份合约的股数  (指数期权无该字段)，期货表示合约乘数
        price_spread|float|当前向上的摆盘价差  (即摆盘数据的卖一价相邻档位的报价差)
        ask_price|float|卖价
        bid_price|float|买价
        ask_vol|float|卖量
        bid_vol|float|买量
        enable_margin|bool|是否可融资（已废弃）  (请使用 [获取融资融券数据](../trade/get-margin-ratio.html) 接口获取)
        mortgage_ratio|float|股票抵押率（已废弃）
        long_margin_initial_ratio|float|融资初始保证金率（已废弃）  (请使用 [获取融资融券数据](../trade/get-margin-ratio.html) 接口获取)
        enable_short_sell|bool|是否可卖空（已废弃）  (请使用 [获取融资融券数据](../trade/get-margin-ratio.html) 接口获取)
        short_sell_rate|float|卖空参考利率（已废弃）  (请使用 [获取融资融券数据](../trade/get-margin-ratio.html) 接口获取)
        short_available_volume|int|剩余可卖空数量（已废弃） (请使用 [获取融资融券数据](../trade/get-margin-ratio.html) 接口获取)
        short_margin_initial_ratio|float|卖空（融券）初始保证金率（已废弃）  (请使用 [获取融资融券数据](../trade/get-margin-ratio.html) 接口获取)
        sec_status|[SecurityStatus](./quote.md#9969)|股票状态
        amplitude|float|振幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        avg_price|float|平均价
        bid_ask_ratio|float|委比  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        volume_ratio|float|量比
        highest52weeks_price|float|52 周最高价
        lowest52weeks_price|float|52 周最低价
        highest_history_price|float|历史最高价
        lowest_history_price|float|历史最低价
        pre_price|float|盘前价格
        pre_high_price|float|盘前最高价
        pre_low_price|float|盘前最低价
        pre_volume|int|盘前成交量
        pre_turnover|float|盘前成交额
        pre_change_val|float|盘前涨跌额
        pre_change_rate|float|盘前涨跌幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        pre_amplitude|float|盘前振幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        after_price|float|盘后价格
        after_high_price|float|盘后最高价
        after_low_price|float|盘后最低价
        after_volume|int|盘后成交量  (科创板支持该数据)
        after_turnover|float|盘后成交额  (科创板支持该数据)
        after_change_val|float|盘后涨跌额
        after_change_rate|float|盘后涨跌幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        after_amplitude|float|盘后振幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        overnight_price|float|夜盘价格
        overnight_high_price|float|夜盘最高价
        overnight_low_price|float|夜盘最低价
        overnight_volume|int|夜盘成交量
        overnight_turnover|float|夜盘成交额
        overnight_change_val|float|夜盘涨跌额
        overnight_change_rate|float|夜盘涨跌幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        overnight_amplitude|float|夜盘振幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        future_valid|bool|是否期货
        future_last_settle_price|float|昨结
        future_position|float|持仓量
        future_position_change|float|日增仓
        future_main_contract|bool|是否主连合约
        future_last_trade_time|str|最后交易时间  (主连，当月，下月等期货没有该字段)
        trust_valid|bool|是否基金
        trust_dividend_yield|float|股息率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        trust_aum|float|资产规模  (单位：元)
        trust_outstanding_units|int|总发行量
        trust_netAssetValue|float|单位净值
        trust_premium|float|溢价  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        trust_assetClass|[AssetClass](./quote.md#4752)|资产类别

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_market_snapshot(['HK.00700', 'US.AAPL'])
if ret == RET_OK:
    print(data)
    print(data['code'][0])    # 取第一条的股票代码
    print(data['code'].values.tolist())   # 转为 list
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
code  name              update_time  last_price  open_price  high_price  low_price  prev_close_price     volume      turnover  turnover_rate  suspension listing_date  lot_size  price_spread  stock_owner  ask_price  bid_price  ask_vol  bid_vol  enable_margin  mortgage_ratio  long_margin_initial_ratio  enable_short_sell  short_sell_rate  short_available_volume  short_margin_initial_ratio  amplitude  avg_price  bid_ask_ratio  volume_ratio  highest52weeks_price  lowest52weeks_price  highest_history_price  lowest_history_price  close_price_5min  after_volume  after_turnover sec_status  equity_valid  issued_shares  total_market_val     net_asset    net_profit  earning_per_share  outstanding_shares  circular_market_val  net_asset_per_share  ey_ratio  pe_ratio  pb_ratio  pe_ttm_ratio  dividend_ttm  dividend_ratio_ttm  dividend_lfy  dividend_lfy_ratio  wrt_valid  wrt_conversion_ratio wrt_type  wrt_strike_price  wrt_maturity_date  wrt_end_trade  wrt_recovery_price  wrt_street_vol  \
0  HK.00700  腾讯控股      2025-04-07 16:09:07      435.40      441.80      462.40     431.00            497.80  123364114.0  5.499476e+10          1.341       False   2004-06-16       100          0.20          NaN      435.4     435.20   281300    17300            NaN             NaN                        NaN                NaN              NaN                     NaN                         NaN      6.308    445.792        -68.499         5.627             547.00000           294.400000             706.100065            -13.202011            431.60             0    0.000000e+00     NORMAL          True     9202391012      4.006721e+12  1.051300e+12  2.095753e+11             22.774          9202391012         4.006721e+12              114.242     0.199    19.118     3.811        19.118          3.48                0.80          3.48               0.799      False                   NaN      N/A               NaN                NaN            NaN                 NaN             NaN   
1   US.AAPL    苹果  2025-04-07 05:30:43.301      188.38      193.89      199.88     187.34            203.19  125910913.0  2.424473e+10          0.838       False   1980-12-12         1          0.01          NaN      180.8     180.48       29      400            NaN             NaN                        NaN                NaN              NaN                     NaN                         NaN      6.172    192.554         86.480         2.226             259.81389           163.300566             259.813890              0.053580            188.93       3151311    5.930968e+08     NORMAL          True    15022073000      2.829858e+12  6.675809e+10  9.133420e+10              6.080         15016677308         2.828842e+12                4.444     1.417    30.983    42.389        29.901          0.99                0.53          0.98               0.520      False                   NaN      N/A               NaN                NaN            NaN                 NaN             NaN   

   wrt_issue_vol  wrt_street_ratio  wrt_delta  wrt_implied_volatility  wrt_premium  wrt_leverage  wrt_ipop  wrt_break_even_point  wrt_conversion_price  wrt_price_recovery_ratio  wrt_score  wrt_upper_strike_price  wrt_lower_strike_price wrt_inline_price_status  wrt_issuer_code  option_valid option_type  strike_time  option_strike_price  option_contract_size  option_open_interest  option_implied_volatility  option_premium  option_delta  option_gamma  option_vega  option_theta  option_rho  option_net_open_interest  option_expiry_date_distance  option_contract_nominal_value  option_owner_lot_multiplier option_area_type  option_contract_multiplier index_option_type  index_valid  index_raise_count  index_fall_count  index_equal_count  plate_valid  plate_raise_count  plate_fall_count  plate_equal_count  future_valid  future_last_settle_price  future_position  future_position_change  future_main_contract  future_last_trade_time  trust_valid  trust_dividend_yield  trust_aum  \
0            NaN               NaN        NaN                     NaN          NaN           NaN       NaN                   NaN                   NaN                       NaN        NaN                     NaN                     NaN                     N/A              NaN         False         N/A          NaN                  NaN                   NaN                   NaN                        NaN             NaN           NaN           NaN          NaN           NaN         NaN                       NaN                          NaN                            NaN                          NaN              N/A                         NaN               N/A        False                NaN               NaN                NaN        False                NaN               NaN                NaN         False                       NaN              NaN                     NaN                   NaN                     NaN        False                   NaN        NaN   
1            NaN               NaN        NaN                     NaN          NaN           NaN       NaN                   NaN                   NaN                       NaN        NaN                     NaN                     NaN                     N/A              NaN         False         N/A          NaN                  NaN                   NaN                   NaN                        NaN             NaN           NaN           NaN          NaN           NaN         NaN                       NaN                          NaN                            NaN                          NaN              N/A                         NaN               N/A        False                NaN               NaN                NaN        False                NaN               NaN                NaN         False                       NaN              NaN                     NaN                   NaN                     NaN        False                   NaN        NaN   

   trust_outstanding_units  trust_netAssetValue  trust_premium trust_assetClass pre_price pre_high_price pre_low_price pre_volume pre_turnover pre_change_val pre_change_rate pre_amplitude after_price after_high_price after_low_price after_change_val after_change_rate after_amplitude overnight_price overnight_high_price overnight_low_price overnight_volume overnight_turnover overnight_change_val overnight_change_rate overnight_amplitude  
0                      NaN                  NaN            NaN              N/A       N/A            N/A           N/A        N/A          N/A            N/A             N/A           N/A         N/A              N/A             N/A              N/A               N/A             N/A             N/A                  N/A                 N/A              N/A                N/A                  N/A                   N/A                 N/A  
1                      NaN                  NaN            NaN              N/A    180.68         181.98        177.47     276016  49809244.83           -7.7          -4.087         2.394       186.6          188.639          186.44            -1.78            -0.944          1.1673          176.94                186.5               174.4           533115        94944250.56               -11.44                -6.072              6.4231  
HK.00700
['HK.00700', 'US.AAPL']

```

:::tip 接口限制
* 每 30 秒内最多请求 60 次快照。
* 每次请求，接口参数 **股票代码列表** 支持传入的标的数量上限是 400 个。
* 港股 BMP 权限下，单次请求的香港证券（含窝轮、牛熊、界内证）快照数量上限是 20 个。
* 港股期权期货 BMP 权限下，单次请求的香港期货和期权的快照数量上限是 20 个。
:::

---

# 获取实时报价

`get_stock_quote(code_list)`

* **介绍**

    获取已订阅股票的实时报价，必须要先订阅。

* **参数**
    参数|类型|说明
    :-|:-|:-
    code_list|list|股票代码列表  (list 中元素类型是 str)
    


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回报价数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 报价数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        data_date|str|日期
        data_time|str|当前价更新时间  (格式：yyyy-MM-dd HH:mm:ss
港股和 A 股市场默认是北京时间，美股市场默认是美东时间)
        last_price|float|最新价格
        open_price|float|今日开盘价
        high_price|float|最高价格
        low_price|float|最低价格
        prev_close_price|float|昨收盘价格
        volume|float|成交数量
        turnover|float|成交金额
        turnover_rate|float|换手率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        amplitude|int|振幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        suspension|bool|是否停牌  (True：停牌)
        listing_date|str|上市日期  (格式：yyyy-MM-dd)
        price_spread|float|当前向上的价差  (即摆盘数据的卖档的相邻档位的报价差)
        dark_status|[DarkStatus](./quote.md#1965)|暗盘交易状态
        sec_status|[SecurityStatus](./quote.md#9969)|股票状态
        strike_price|float|行权价
        contract_size|float|每份合约数
        open_interest|int|未平仓合约数
        implied_volatility|float|隐含波动率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        premium|float|溢价  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        delta|float|希腊值 Delta
        gamma|float|希腊值 Gamma
        vega|float|希腊值 Vega
        theta|float|希腊值 Theta
        rho|float|希腊值 Rho
        index_option_type|[IndexOptionType](./quote.md#5149)|指数期权类型
        net_open_interest|int|净未平仓合约数  (仅港股期权适用)
        expiry_date_distance|int|距离到期日天数  (负数表示已过期)
        contract_nominal_value|float|合约名义金额  (仅港股期权适用)
        owner_lot_multiplier|float|相等正股手数  (指数期权无该字段 ，仅港股期权适用)
        option_area_type|[OptionAreaType](./quote.md#7077)|期权类型（按行权时间）
        contract_multiplier|float|合约乘数
        pre_price|float|盘前价格
        pre_high_price|float|盘前最高价
        pre_low_price|float|盘前最低价
        pre_volume|int|盘前成交量
        pre_turnover|float|盘前成交额
        pre_change_val|float|盘前涨跌额
        pre_change_rate|float|盘前涨跌幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        pre_amplitude|float|盘前振幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        after_price|float|盘后价格
        after_high_price|float|盘后最高价
        after_low_price|float|盘后最低价
        after_volume|int|盘后成交量  (科创板支持此数据)
        after_turnover|float|盘后成交额  (科创板支持此数据)
        after_change_val|float|盘后涨跌额
        after_change_rate|float|盘后涨跌幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        after_amplitude|float|盘后振幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        overnight_price|float|夜盘价格
        overnight_high_price|float|夜盘最高价
        overnight_low_price|float|夜盘最低价
        overnight_volume|int|夜盘成交量
        overnight_turnover|float|夜盘成交额
        overnight_change_val|float|夜盘涨跌额
        overnight_change_rate|float|夜盘涨跌幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        overnight_amplitude|float|夜盘振幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        last_settle_price|float|昨结  (期货特有字段)
        position|float|持仓量  (期货特有字段)
        position_change|float|日增仓  (期货特有字段)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret_sub, err_message = quote_ctx.subscribe(['US.AAPL'], [SubType.QUOTE], subscribe_push=False)
# 先订阅 K 线类型。订阅成功后 OpenD 将持续收到服务器的推送，False 代表暂时不需要推送给脚本
if ret_sub == RET_OK:  # 订阅成功
    ret, data = quote_ctx.get_stock_quote(['US.AAPL'])  # 获取订阅股票报价的实时数据
    if ret == RET_OK:
        print(data)
        print(data['code'][0])   # 取第一条的股票代码
        print(data['code'].values.tolist())   # 转为 list
    else:
        print('error:', data)
else:
    print('subscription failed', err_message)
quote_ctx.close()  # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅
```

* **Output**

```python
code name   data_date     data_time  last_price  open_price  high_price  low_price  prev_close_price     volume      turnover  turnover_rate  amplitude  suspension listing_date  price_spread dark_status sec_status strike_price contract_size open_interest implied_volatility premium delta gamma vega theta  rho net_open_interest expiry_date_distance contract_nominal_value owner_lot_multiplier option_area_type contract_multiplier last_settle_price position position_change index_option_type  pre_price  pre_high_price  pre_low_price  pre_volume  pre_turnover  pre_change_val  pre_change_rate  pre_amplitude  after_price  after_high_price  after_low_price  after_volume  after_turnover  after_change_val  after_change_rate  after_amplitude  overnight_price  overnight_high_price  overnight_low_price  overnight_volume  overnight_turnover  overnight_change_val  overnight_change_rate  overnight_amplitude
0  US.AAPL   苹果  2025-04-07  05:37:21.794      188.38      193.89      199.88     187.34            203.19  125910913.0  2.424473e+10          0.838      6.172       False   1980-12-12          0.01         N/A     NORMAL          N/A           N/A           N/A                N/A     N/A   N/A   N/A  N/A   N/A  N/A               N/A                  N/A                    N/A                  N/A              N/A                 N/A               N/A      N/A             N/A               N/A     181.43          181.98         177.47      288853   52132735.18           -6.95           -3.689          2.394        186.6           188.639           186.44       3151311    5.930968e+08             -1.78             -0.944           1.1673           176.94                 186.5                174.4            533115         94944250.56                -11.44                 -6.072               6.4231
US.AAPL
['US.AAPL']
```

:::tip 提示
* 此接口提供了一次性获取实时数据的功能，如需持续获取推送数据，请参考 [实时报价回调](./update-stock-quote.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
:::

---

# 获取实时摆盘

`get_order_book(code, num=10, order_book_type=None)`

* **介绍**

    获取已订阅股票的实时摆盘，必须要先订阅。

* **参数**
    参数|类型|说明
    :-|:-|:-
    code|str|股票代码
    num|int|请求摆盘档数  (摆盘档数获取上限请参见 [摆盘档数明细](../qa/quote.md#5336)) 
    order_book_type|[OrderBookType](./quote.md#3141)|摆盘类型，不传默认返回整股盘


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回摆盘数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

   * 摆盘数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        svr_recv_time_bid|str|富途服务器从交易所收到买盘数据的时间  (部分数据的接收时间为零，例如服务器重启或第一次推送的缓存数据)
        svr_recv_time_ask|str|富途服务器从交易所收到卖盘数据的时间  (部分数据的接收时间为零，例如服务器重启或第一次推送的缓存数据)
        order_book_type|[OrderBookType](./quote.md#3141)|摆盘类型
        Bid|list|每个元祖包含如下信息：委托价格，委托数量，委托订单数，委托订单明细  (委托订单明细
  - 明细内容：交易所订单 ID，单笔委托数量
  - 港股 SF 权限下最多支持 1000 笔委托订单明细；其余行情权限不支持获取此类数据)
        Ask|list|每个元祖包含如下信息：委托价格，委托数量，委托订单数，委托订单明细  (委托订单明细
  - 明细内容：交易所订单 ID，单笔委托数量
  - 港股 SF 权限下最多支持 1000 笔委托订单明细；其余行情权限不支持获取此类数据)

     其中，Bid 和 Ask 字段的结构如下：  

          'Bid': [ (bid_price1, bid_volume1, order_num, {'orderid1': order_volume1, 'orderid2': order_volume2, …… }), (bid_price2, bid_volume2, order_num,  {'orderid1': order_volume1, 'orderid2': order_volume2, …… }),…]
          'Ask': [ (ask_price1, ask_volume1，order_num, {'orderid1': order_volume1, 'orderid2': order_volume2, …… }), (ask_price2, ask_volume2, order_num, {'orderid1': order_volume1, 'orderid2': order_volume2, …… }),…] 

 
    
* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret_sub = quote_ctx.subscribe(['US.AAPL'], [SubType.ORDER_BOOK], subscribe_push=False)[0]
# 先订阅买卖摆盘类型。订阅成功后 OpenD 将持续收到服务器的推送，False 代表暂时不需要推送给脚本
if ret_sub == RET_OK:  # 订阅成功
    ret, data = quote_ctx.get_order_book('US.AAPL', num=3)  # 获取一次 3 档实时摆盘数据
    if ret == RET_OK:
        print(data)
    else:
        print('error:', data)
else:
    print('subscription failed')
quote_ctx.close()  # 关闭当条连接，OpenD 会在 1 分钟后自动取消相应股票相应类型的订阅
```

* **Output**

```python
{'code': 'US.AAPL', 'name': '苹果', 'svr_recv_time_bid': '2025-04-07 05:39:20.352', 'svr_recv_time_ask': '2025-04-07 05:39:20.352', 'order_book_type': 'NORMAL', 'Bid': [(181.17, 227.0, 2, {}), (181.15, 2.0, 2, {}), (181.12, 100.0, 1, {})], 'Ask': [(181.71, 200.0, 1, {}), (181.79, 9.0, 1, {}), (181.9, 616.0, 3, {})]}
```

:::tip 接口限制
* 富途服务器从交易所收到数据的时间字段，仅支持A股正股、港股正股、ETFs、窝轮、牛熊，且仅开盘时间才有此数据。
* 富途服务器从交易所收到数据的时间字段，部分情况下接收时间可能为零，例如：服务器重启或第一次推送的缓存数据。
:::

:::tip 提示
* 此接口提供了一次性获取实时数据的功能，如需持续获取推送数据，请参考 [实时摆盘回调](./update-order-book.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
* 美股市场，会返回当前交易时段的实时摆盘数据，无需设置时段。
:::

---

# 获取实时 K 线

`get_cur_kline(code, num, ktype=KLType.K_DAY, autype=AuType.QFQ)`

* **介绍**

    获取已订阅股票的实时 K 线数据，必须要先订阅。

* **参数**
    参数|类型|说明
    :-|:-|:-
    code|str|股票代码
    name|str|股票名称
    num|int|K 线数据个数  (最多 1000 根)
    ktype|[KLType](./quote.md#4119)|K 线类型
    autype|[AuType](./quote.md#6907)|复权类型


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回 K 线数据数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * K 线数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        time_key|str|时间  (格式：yyyy-MM-dd HH:mm:ss
港股和 A 股市场默认是北京时间，美股市场默认是美东时间)
        open|float|开盘价
        close|float|收盘价
        high|float|最高价
        low|float|最低价
        volume|float|成交量
        turnover|float|成交额
        pe_ratio|float|市盈率
        turnover_rate|float|换手率  (该字段为百分比字段，默认返回小数，如 0.01 实际对应 1%)
        last_close|float|上一个 K 线的收盘价  (即前一个 K 线的收盘价出于效率原因，第一个数据的 last_close 可能为 0)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret_sub, err_message = quote_ctx.subscribe(['US.AAPL'], [SubType.K_DAY], subscribe_push=False, session=Session.ALL)
# 先订阅 K 线类型。订阅成功后 OpenD 将持续收到服务器的推送，False 代表暂时不需要推送给脚本
if ret_sub == RET_OK:  # 订阅成功
    ret, data = quote_ctx.get_cur_kline('US.AAPL', 2, KLType.K_DAY, AuType.QFQ)  # 获取美股AAPL最近2个 K 线数据
    if ret == RET_OK:
        print(data)
        print(data['turnover_rate'][0])   # 取第一条的换手率
        print(data['turnover_rate'].values.tolist())   # 转为 list
    else:
        print('error:', data)
else:
    print('subscription failed', err_message)
quote_ctx.close()  # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅
```

* **Output**

```python
code name             time_key    open   close    high     low       volume      turnover  pe_ratio  turnover_rate  last_close
0  US.AAPL   苹果  2025-04-03 00:00:00  205.54  203.19  207.49  201.25  103419006.0  2.111773e+10    33.419        0.00689      223.89
1  US.AAPL   苹果  2025-04-04 00:00:00  193.89  188.38  199.88  187.34  125910913.0  2.424473e+10    30.983        0.00838      203.19
0.00689
[0.00689, 0.00838]
```

:::tip 接口限制
* 此接口为获取实时 K 线接口，最多能获取最近的 1000 根。如需获取历史 K 线，请参考 [获取历史 K 线](../quote/request-history-kline.md)
* 市盈率和换手率字段，只有日 K 及以上周期的正股才有数据
* **期权**，仅提供日K, 1分K，5分K，15分K，60分K。
:::

:::tip 提示
* 此接口提供了一次性获取实时数据的功能，如需持续获取推送数据，请参考 [实时 K 线回调](./update-kl.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
:::

---

# 获取实时分时

`get_rt_data(code)`

* **介绍**

    获取已订阅股票的实时分时数据，必须要先订阅。

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回分时数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 分时数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        time|str|时间  (格式：yyyy-MM-dd HH:mm:ss 港股和 A 股市场默认是北京时间，美股市场默认是美东时间)
        is_blank|bool|数据状态  (False：正常数据True：伪造数据)
        opened_mins|int|零点到当前多少分钟
        cur_price|float|当前价格
        last_close|float|昨天收盘的价格
        avg_price|float|平均价格  (对于期权，该字段为 N/A)
        volume|float|成交量
        turnover|float|成交金额

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret_sub, err_message = quote_ctx.subscribe(['US.AAPL'], [SubType.RT_DATA], subscribe_push=False, session=Session.ALL)
# 先订阅分时数据类型。订阅成功后 OpenD 将持续收到服务器的推送，False 代表暂时不需要推送给脚本
if ret_sub == RET_OK:   # 订阅成功
    ret, data = quote_ctx.get_rt_data('US.AAPL')   # 获取一次分时数据
    if ret == RET_OK:
        print(data)
    else:
        print('error:', data)
else:
    print('subscription failed', err_message)
quote_ctx.close()   # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅
```

* **Output**

```python
code  name                 time  is_blank  opened_mins  cur_price  last_close   avg_price   volume     turnover
0    US.AAPL   苹果  2025-04-06 20:01:00     False         1201     183.00      188.38  181.643916    9463  1718896.38
..      ...    ...                  ...       ...          ...        ...         ...         ...      ...          ...
586  US.AAPL   苹果  2025-04-07 05:47:00     False          347     181.26      188.38  180.555673     661   119859.75

[587 rows x 10 columns]
```

:::tip 提示
* 此接口提供了一次性获取实时数据的功能，如需持续获取推送数据，请参考 [实时分时回调](./update-rt.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
:::

---

# 获取实时逐笔

`get_rt_ticker(code, num=500)`

* **介绍**

    获取已订阅股票的实时逐笔数据，必须要先订阅。

* **参数**
    参数|类型|说明
    :-|:-|:-
    code|str|股票代码
    num|int|最近逐笔个数


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回逐笔数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 逐笔数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        sequence|int|逐笔序号
        time|str|成交时间  (格式：yyyy-MM-dd HH:mm:ss:xxx
港股和 A 股市场默认是北京时间，美股市场默认是美东时间)
        price|float|成交价格
        volume|float|成交数量  (股数)
        turnover|float|成交金额
        ticker_direction|[TickerDirect](./quote.md#8723)|逐笔方向
        type|[TickerType](./quote.md#2358)|逐笔类型

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret_sub, err_message = quote_ctx.subscribe(['US.AAPL'], [SubType.TICKER], subscribe_push=False, session=Session.ALL)
# 先订阅逐笔类型。订阅成功后 OpenD 将持续收到服务器的推送，False 代表暂时不需要推送给脚本
if ret_sub == RET_OK:  # 订阅成功
    ret, data = quote_ctx.get_rt_ticker('US.AAPL', 2)  # 获取美股AAPL最近2个逐笔
    if ret == RET_OK:
        print(data)
        print(data['turnover'][0])   # 取第一条的成交金额
        print(data['turnover'].values.tolist())   # 转为 list
    else:
        print('error:', data)
else:
    print('subscription failed', err_message)
quote_ctx.close()  # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅
```

* **Output**

```python
code name                     time   price  volume  turnover ticker_direction             sequence     type
0  US.AAPL   苹果  2025-04-07 05:50:23.745  181.70     2.0    363.40          NEUTRAL  7490506385373790208  ODD_LOT
1  US.AAPL   苹果  2025-04-07 05:50:24.170  181.73     1.0    181.73          NEUTRAL  7490506389668757504  ODD_LOT
363.4
[363.4, 181.73]
```

:::tip 接口限制
* 最多能获取最近 1000 个逐笔数据，更多历史逐笔数据暂未提供
* 港股期权期货在 LV1 权限下，不支持获取逐笔
:::

:::tip 提示
* 此接口提供了一次性获取实时数据的功能，如需持续获取推送数据，请参考 [实时逐笔回调](./update-ticker.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
:::

---

# 获取实时经纪队列

`get_broker_queue(code)`

* **介绍**

    获取已订阅股票的实时经纪队列数据，必须要先订阅。

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">bid_frame_table</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，bid_frame_table 返回买盘经纪队列数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，bid_frame_table 返回错误描述</td>
        </tr>
        <tr>
            <td rowspan="2">ask_frame_table</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，ask_frame_table 返回卖盘经纪队列数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，ask_frame_table 返回错误描述</td>
        </tr>
    </table>

    * 买盘经纪队列格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        bid_broker_id|int|经纪买盘 ID
        bid_broker_name|str|经纪买盘名称
        bid_broker_pos|int|经纪档位
        order_id|int|交易所订单 ID  (- 不是下单接口返回的订单 ID
  - 只有港股 SF 行情权限支持返回该字段)
        order_volume|int|单笔委托数量  (只有港股 SF 行情权限支持返回该字段)
    * 卖盘经纪队列格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        ask_broker_id|int|经纪卖盘 ID
        ask_broker_name|str|经纪卖盘名称
        ask_broker_pos|int|经纪档位
        order_id|int|交易所订单 ID  (- 不是下单接口返回的订单 ID
  - 只有港股 SF 行情权限支持返回该字段)
        order_volume|int|单笔委托数量  (只有港股 SF 行情权限支持返回该字段)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret_sub, err_message = quote_ctx.subscribe(['HK.00700'], [SubType.BROKER], subscribe_push=False)
# 先订阅经纪队列类型。订阅成功后 OpenD 将持续收到服务器的推送，False 代表暂时不需要推送给脚本
if ret_sub == RET_OK:   # 订阅成功
    ret, bid_frame_table, ask_frame_table = quote_ctx.get_broker_queue('HK.00700')   # 获取一次经纪队列数据
    if ret == RET_OK:
        print(bid_frame_table)
    else:
        print('error:', bid_frame_table)
else:
    print(err_message)
quote_ctx.close()   # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅
```

* **Output**

```python
        code  name  bid_broker_id bid_broker_name  bid_broker_pos order_id order_volume
0   HK.00700  腾讯控股           5338          J.P.摩根               1      N/A          N/A
..       ...   ...            ...             ...             ...      ...          ...
36  HK.00700  腾讯控股           8305  富途证券国际(香港)有限公司               4      N/A          N/A

[37 rows x 7 columns]
```

:::tip 提示
* 此接口提供了一次性获取实时数据的功能，如需持续获取推送数据，请参考 [实时经纪队列回调](./update-broker.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
* 港股 BMP及LV1 权限下，不支持获取经纪队列数据
:::

---

# 获取标的市场状态

`get_market_state(code_list)`

* **介绍**

    获取指定标的的市场状态

* **参数**
    参数|类型|说明
    :-|:-|:-
    code_list|list|需要查询市场状态的股票代码列表  (list 中元素类型是 str)


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回市场状态数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 市场状态数据
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        stock_name|str|股票名称
        market_state|[MarketState](./quote.md#1252)|市场状态

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_market_state(['SZ.000001', 'HK.00700'])
if ret == RET_OK:
    print(data)
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
    code         stock_name   market_state
0  SZ.000001    平安银行     AFTERNOON
1  HK.00700     腾讯控股     AFTERNOON
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取标的市场状态接口。
* 每次请求的股票代码个数上限为 400 个。
:::

---

# 获取资金流向

`get_capital_flow(stock_code, period_type = PeriodType.INTRADAY, start=None, end=None)`

* **介绍**

    获取个股资金流向

* **参数**
    参数|类型|说明
    :-|:-|:-
    stock_code|str|股票代码
    period_type|[PeriodType](./quote.md#2644)|周期类型
    start|str|开始时间  (格式：yyyy-MM-dd 
 例如：“2017-06-20”)
    end|str|结束时间  (格式：yyyy-MM-dd 
 例如：“2017-06-20”)


    - start 和 end 的组合如下  
        |start 类型 |end 类型 |说明 |
        |:--|:--|:--|
        |str |str |start 和 end 分别为指定的日期|
        |None |str |start 为 end 往前 365 天  |
        |str |None |end 为 start 往后 365 天 |
        |None |None |end 为 当前日期，start 往前 365 天 |


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回资金流向数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 资金流向数据格式如下：
        字段|类型|说明
        :-|:-|:-
        in_flow|float|整体净流入
        main_in_flow|float|主力大单净流入  (仅历史周期（日、周、月）有效)
        super_in_flow|float|特大单净流入 
        big_in_flow|float|大单净流入 
        mid_in_flow|float|中单净流入 
        sml_in_flow|float|小单净流入 
        capital_flow_item_time|str|开始时间  (格式：yyyy-MM-dd HH:mm:ss
精确到分钟)
        last_valid_time|str|数据最后有效时间  (仅实时周期有效)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_capital_flow("HK.00700", period_type = PeriodType.INTRADAY)
if ret == RET_OK:
    print(data)
    print(data['in_flow'][0])    # 取第一条的净流入的资金额度
    print(data['in_flow'].values.tolist())   # 转为 list
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
    last_valid_time       in_flow  ...  main_in_flow  capital_flow_item_time
0               N/A -1.857915e+08  ... -1.066828e+08     2021-06-08 00:00:00
..              ...           ...  ...           ...                     ...
245             N/A  2.179240e+09  ...  2.143345e+09     2022-06-08 00:00:00

[246 rows x 8 columns]
-185791500.0
[-185791500.0, -18315000.0, -672100100.0, -714394350.0, -698391950.0, -818886750.0, 304827400.0, 73026200.0, -2078217500.0, 
..                   ...           ...                    ...
2031460.0, 638067040.0, 622466600.0, -351788160.0, -328529240.0, 715415020.0, 76749700.0, 2179240320.0]
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次获取资金流向接口。
* 支持正股、窝轮、基金、加密货币。
* 历史周期（日、月、年）仅提供最近 1 年数据；实时周期仅提供最新一天的数据。
* 返回数据只包括盘中数据，不包含盘前盘后数据。
:::

---

# 获取资金分布

`get_capital_distribution(stock_code)`

* **介绍**

    获取资金分布

* **参数**
    参数|类型|说明
    :-|:-|:-
    stock_code|str|股票代码


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回股票资金分布数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 资金分布数据格式如下：
        字段|类型|说明
        :-|:-|:-
        capital_in_super|float|流入资金额度，特大单
        capital_in_big|float|流入资金额度，大单
        capital_in_mid|float|流入资金额度，中单
        capital_in_small|float|流入资金额度，小单
        capital_out_super|float|流出资金额度，特大单
        capital_out_big|float|流出资金额度，大单
        capital_out_mid|float|流出资金额度，中单
        capital_out_small|float|流出资金额度，小单
        update_time|str|更新时间字符串  (格式：yyyy-MM-dd HH:mm:ss)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_capital_distribution("HK.00700")
if ret == RET_OK:
    print(data)
    print(data['capital_in_big'][0])    # 取第一条的流入资金额度，大单
    print(data['capital_in_big'].values.tolist())   # 转为 list
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
   capital_in_super  capital_in_big  ...  capital_out_small          update_time
0      2.261085e+09    2.141964e+09  ...       2.887413e+09  2022-06-08 15:59:59

[1 rows x 9 columns]
2141963720.0
[2141963720.0]
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次获取资金分布接口。
* 支持正股、窝轮、基金、加密货币。
* 更多资金分布介绍，请参考 [这里](https://support.futunn.com/zh-cn/topic498?lang=zh-CN)。
* 返回数据只包括盘中数据，不包含盘前盘后数据。
:::

---

# 获取股票所属板块

`get_owner_plate(code_list)`

* **介绍**

    获取单支或多支股票的所属板块信息列表

* **参数**
    参数|类型|说明
    :-|:-|:-
    code_list|list|股票代码列表  (仅支持正股、指数list 中元素类型是 str)


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回所属板块数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 所属板块数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|证券代码
        name|str|股票名称
        plate_code|str|板块代码
        plate_name|str|板块名字
        plate_type|[Plate](./quote.md#1362)|板块类型  (行业板块或概念板块)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

code_list = ['HK.00001']
ret, data = quote_ctx.get_owner_plate(code_list)
if ret == RET_OK:
    print(data)
    print(data['code'][0])    # 取第一条的股票代码
    print(data['plate_code'].values.tolist())   # 板块代码转为 list
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
        code name          plate_code plate_name plate_type
0   HK.00001   长和  HK.HSI Constituent      恒指成份股      OTHER
..       ...  ...                 ...        ...        ...
8   HK.00001   长和           HK.BK1983    香港股票ADR      OTHER

[9 rows x 5 columns]
HK.00001
['HK.HSI Constituent', 'HK.GangGuTong', 'HK.BK1000', 'HK.BK1061', 'HK.BK1107', 'HK.BK1331', 'HK.BK1600', 'HK.BK1922', 'HK.BK1983']
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取股票所属板块接口
* 每次请求的股票列表中，股票个数上限为 200 个
* 仅支持正股和指数
:::

---

# 获取历史 K 线

`request_history_kline(code, start=None, end=None, ktype=KLType.K_DAY, autype=AuType.QFQ, fields=[KL_FIELD.ALL], max_count=1000, page_req_key=None, extended_time=False, session=Session.NONE)`

* **介绍**

    获取历史 K 线

* **参数**
    参数|类型|说明
    :-|:-|:-
    code|str|股票代码
    start|str|开始时间  (格式：yyyy-MM-dd
例如：“2017-06-20”)
    end|str|结束时间  (格式：yyyy-MM-dd
例如：“2017-07-20”)
    ktype|[KLType](./quote.md#4119)|K 线类型
    autype|[AuType](./quote.md#6907)|复权类型
    fields|[KLFields](./quote.md#481)|需返回的字段列表
    max_count|int|本次请求最大返回的 K 线根数  (- 传 None 表示返回 start 和 end 之间所有的数据 
  - 注意：OpenD 接收到所有数据后才会下发给脚本，如果您要获取的 K 线根数大于 1000 根，建议选择分页，防止出现超时)
    page_req_key|bytes|分页请求  (如果 start 和 end 之间的 K 线根数多于 max_count：1. 首页请求时应该传 None 2. 后续页请求时必须要传入上次调用返回的参数 page_req_key)
    extended_time|bool|是否允许美股盘前盘后数据  (False：不允许True：允许)
    session|[Session](./quote.md#9152)|获取美股分时段历史K线  (- 仅用于获取美股分时段历史K线
  - 获取美股历史K线不支持入参OVERNIGHT
  - 最低OpenD版本要求：9.2.4207)


    * start 和 end 的组合如下
        Start 类型|End 类型|说明
        :-|:-|:-
        str|str|start 和 end 分别为指定的日期
        None|str|start 为 end 往前 365 天
        str|None|end 为 start 往后 365 天
        None|None|end 为当前日期，start 往前 365 天


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回历史 K 线数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
        <tr>
            <td>page_req_key</td>
            <td>bytes</td>
            <td>下一页请求的 key</td>
        </tr>
    </table>

    * 历史 K 线数据格式如下:
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        time_key|str|K 线时间  (格式：yyyy-MM-dd HH:mm:ss
港股和 A 股市场默认是北京时间，美股市场默认是美东时间)
        open|float|开盘价
        close|float|收盘价
        high|float|最高价
        low|float|最低价
        pe_ratio|float|市盈率  (该字段为比例字段，默认不展示 %)
        turnover_rate|float|换手率
        volume|float|成交量
        turnover|float|成交额
        change_rate|float|涨跌幅
        last_close|float|上一个 K 线的收盘价

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret, data, page_req_key = quote_ctx.request_history_kline('US.AAPL', start='2019-09-11', end='2019-09-18', max_count=5, session=Session.ALL)  # 每页5个，请求第一页
if ret == RET_OK:
    print(data)
    print(data['code'][0])    # 取第一条的股票代码
    print(data['close'].values.tolist())   # 第一页收盘价转为 list
else:
    print('error:', data)
while page_req_key != None:  # 请求后面的所有结果
    print('*************************************')
    ret, data, page_req_key = quote_ctx.request_history_kline('US.AAPL', start='2019-09-11', end='2019-09-18', max_count=5, page_req_key=page_req_key, session=Session.ALL) # 请求翻页后的数据
    if ret == RET_OK:
        print(data)
    else:
        print('error:', data)
print('All pages are finished!')
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
code  name             time_key       open      close       high        low  pe_ratio  turnover_rate    volume      turnover  change_rate  last_close
0  US.AAPL   苹果  2019-09-11 00:00:00  52.631194  53.963447  53.992409  52.549135    18.773        0.01039  177158584.0  9.808562e+09     3.179511   52.300545
..       ...   ...                  ...        ...        ...        ...        ...       ...            ...       ...           ...          ...         ...
4  US.AAPL   苹果  2019-09-17 00:00:00  53.087346  53.265945  53.294907  52.884612    18.530        0.00432   73545872.0  4.046314e+09     0.363802   53.072865

[5 rows x 13 columns]
US.AAPL
[53.9634465, 53.84156475, 52.7953125, 53.072865, 53.265945]
*************************************
       code  name             time_key       open      close       high        low  pe_ratio  turnover_rate   volume      turnover  change_rate  last_close
0  US.AAPL   苹果  2019-09-18 00:00:00  53.352831  53.76554  53.784847  52.961844    18.704        0.00602  102572372.0  5.682068e+09     0.937925   53.265945
All pages are finished!
```

:::tip 接口限制
* 分 K 提供最近 8 年数据，日 K 提供最近 20 年的数据， 日 K 以上不限制。
* 我们会根据您账户的资产和交易的情况，下发历史 K 线额度。因此，7 天内您只能获取有限只股票的历史 K 线数据。具体规则参见 [订阅额度 & 历史 K 线额度](../intro/authority.md#1314)。您当日消耗的历史 K 线额度，会在 7 天后自动释放。
* 每 30 秒内最多请求 60 次历史 K 线接口。注意：如果您是分页获取数据，此限频规则仅适用于每只股票的首页，后续页请求不受限频规则的限制。
* **换手率**，仅提供日 K 及以上级别。
* **期权**，仅提供日K, 1分K，5分K，15分K，60分K。
* 美股 **盘前、盘后、夜盘 K 线**，仅支持 60 分钟及以下级别。由于美股盘前盘后和夜盘时段为非常规交易时段，此时段的 K 线数据可能不足 2 年。
* 美股的 **成交额**，仅提供 2015-10-12 之后的数据。
:::

---

# 获取复权因子

`get_rehab(code)`

* **介绍**

    获取股票的复权因子

* **参数**
    参数|类型|说明
    :-|:-|:-
    code|str|股票代码


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回复权数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 复权数据格式如下：
        字段|类型|说明
        :-|:-|:-
        ex_div_date|str|除权除息日
        split_base|float|拆股分子 (拆股比例=拆股分子/拆股分母)
        split_ert|float|拆股分母
        join_base|float|合股分子 (合股比例=合股分子/合股分母)
        join_ert|float|合股分母
        split_ratio|float|拆合股比例  (- 当公司出现合股，5股合1股时，合股分子=5，合股分母=1，拆合股比例=合股分子/合股分母=5/1- 当公司出现拆股，1股拆5股时，拆股分子=1，拆股分母=5，拆合股比例=拆股分子/拆股分母=1/5)
        per_cash_div|float|每股派现
        bonus_base|float|送股分子 (送股比例=送股分子/送股分母)
        bonus_ert|float|送股分母
        per_share_div_ratio|float|送股比例  (- 当公司出现送股，5股送1股时，送股分子=5，送股分母=1，送股比例=送股分子/送股分母=5/1)
        transfer_base|float|转增股分子 (转增股比例=转增股分子/转增股分母)
        transfer_ert|float|转增股分母
        per_share_trans_ratio|float|转增股比例  (- 当公司出现转增股，10股转增3股时，转增股分子=10，转增股分母=3，转增股比例=转增股分子/转增股分母=10/3)
        allot_base|float|配股分子 (配股比例=配股分子/配股分母)
        allot_ert|float|配股分母
        allotment_ratio|float|配股比例  (- 当公司出现配股，5股配1股时，配股分子=5，配股分母=1，配股比例=配股分子/配股分母=5/1)
        allotment_price|float|配股价
        add_base|float|增发股分子 (增发股比例=增发股分子/增发股分母)
        add_ert|float|增发股分母
        stk_spo_ratio|float|增发比例  (- 当公司出现增发股，1股增发5股时，增发股分子=1，增发股分母=5，增发股比例=增发股分子/增发股分母=1/5)
        stk_spo_price|float|增发价格
        spin_off_base|float|分立分子
        spin_off_ert|float|分立分母
        spin_off_ratio|float|分立比例
        forward_adj_factorA|float|前复权因子 A
        forward_adj_factorB|float|前复权因子 B
        backward_adj_factorA|float|后复权因子 A
        backward_adj_factorB|float|后复权因子 B

        前复权价格 = 不复权价格 × 前复权因子 A + 前复权因子 B  
        后复权价格 = 不复权价格 × 后复权因子 A + 后复权因子 B

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_rehab("HK.00700")
if ret == RET_OK:
    print(data)
    print(data['ex_div_date'][0])    # 取第一条的除权除息日
    print(data['ex_div_date'].values.tolist())   # 转为 list
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
    ex_div_date  split_ratio  per_cash_div  per_share_div_ratio  per_share_trans_ratio  allotment_ratio  allotment_price  stk_spo_ratio  stk_spo_price  spin_off_base   spin_off_ert   spin_off_ratio   forward_adj_factorA  forward_adj_factorB  backward_adj_factorA  backward_adj_factorB
0   2005-04-19          NaN          0.07                  NaN                    NaN              NaN              NaN            NaN            NaN         NaN         NaN          NaN         1.0                -0.07                   1.0                  0.07
..         ...          ...           ...                  ...                    ...              ...              ...            ...            ...                  ...                  ...                   ...                   ...
15  2019-05-17          NaN          1.00                  NaN                    NaN              NaN              NaN            NaN            NaN         NaN        NaN        NaN           1.0                -1.00                   1.0                  1.00

[16 rows x 16 columns]
2005-04-19
['2005-04-19', '2006-05-15', '2007-05-09', '2008-05-06', '2009-05-06', '2010-05-05', '2011-05-03', '2012-05-18', '2013-05-20', '2014-05-15', '2014-05-16', '2015-05-15', '2016-05-20', '2017-05-19', '2018-05-18', '2019-05-17']
```

:::tip 接口限制
* 每 30 秒内最多请求 60 次获取复权因子接口。
:::

---

# 获取财报日前后价格涨跌幅表现

`get_financials_earnings_price_move(code, period_count=None)`

* **介绍**

    获取财报日前后价格涨跌幅表现

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码
    period_count|int|财报周期数量  (默认 10，取值范围 [1, 50])

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回按交易日展开的明细数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回数据按交易日平铺，每行同时包含财报元信息与当日行情：

        字段|类型|说明
        :-|:-|:-
        fiscal_year|int|财务年度  (如 2024)
        financial_type|[F10Type](./quote.md#7710)|财报类型  (0=未知，1=Q1，2=Q2，3=Q3，4=Q4，7=全年，9=季度等)
        period_text|str|财报周期  (如 "2024/Q3"、"2024/FY")
        pub_trading_day_str|str|财报发布对应交易日  (格式：yyyy-MM-dd；对应市场时区)
        pub_type|[EarningsPubTimeType](./quote.md#2586)|财报发布时间类型  (0=未知，1=盘前，2=盘后，3=盘中)
        price_info_index|int|财报发布当日在本期行情列表中的下标  (0-based；-1 表示无数据)
        day_offset|int|距财报发布日偏移天数  (负数=发布前，0=发布当天，正数=发布后)
        trading_day_str|str|交易日  (格式：yyyy-MM-dd；对应市场时区)
        close_price|float|收盘价
        open_price|float|开盘价
        highest_price|float|最高价
        lowest_price|float|最低价
        last_close_price|float|昨收价
        option_iv|float|期权隐含波动率  (百分号前的值，如 12.34 表示 12.34%)
        option_hv|float|期权历史波动率  (百分号前的值，如 12.34 表示 12.34%)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_financials_earnings_price_move("HK.00700", period_count=2)
if ret == RET_OK:
    print(data)
    print(data['period_text'][0])
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
fiscal_year  financial_type  ... option_iv  option_hv
0          2026               1  ...    31.829     32.220
1          2026               1  ...    33.173     33.720
2          2026               1  ...    32.963     30.355
3          2026               1  ...       NaN        NaN
4          2025               4  ...    35.804     37.891
5          2025               4  ...    35.845     37.478
6          2025               4  ...    38.504     37.580
7          2025               4  ...    35.518     38.175
8          2025               4  ...    34.739     37.446
9          2025               4  ...    34.248     37.558
10         2025               4  ...    31.682     44.855
11         2025               4  ...    30.907     43.536
12         2025               4  ...    34.614     43.426
13         2025               4  ...    33.617     44.177
14         2025               4  ...    34.503     42.810

[15 rows x 17 columns]
2026/Q1
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 仅支持港股、美股、新加坡、日本、马来西亚、A股正股。
:::

---

# 获取财报日前后股价历史

`get_financials_earnings_price_history(code)`

* **介绍**

    获取财报日前后股价历史

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回各财报期数据（按期×偏移交易日展开）</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回数据按财报期展开，每行包含财报元信息、发布日行情及相对偏移收盘价：

        字段|类型|说明
        :-|:-|:-
        fiscal_year|int|财务年度  (如 2024)
        financial_type|[F10Type](./quote.md#7710)|财报类型  (0=未知，1=Q1，2=Q2，3=Q3，4=Q4，7=全年，9=季度等)
        period_text|str|财报周期  (如 "2024/Q3"、"2024/FY")
        is_current|bool|当前时间是否在该财报窗口期
        pub_trading_day|int|财报发布对应交易日时间戳（秒）
        pub_trading_day_str|str|财报发布交易日  (格式：yyyy-MM-dd；对应市场时区)
        pub_time|int|财报实际发布时间戳（秒，含时分秒）
        pub_time_str|str|财报发布时间  (格式：yyyy-MM-dd HH:mm:ss；对应市场时区)
        pub_type|[EarningsPubTimeType](./quote.md#2586)|财报发布时间类型  (0=未知，1=盘前，2=盘后，3=盘中)
        predict_vola_ratio_newest|float|最新预期波动比例  (百分号前的值，如 12.34 表示 12.34%)
        predict_vola_ratio_highest|float|最高预期波动比例  (百分号前的值，如 12.34 表示 12.34%)
        predict_vola_val_newest|float|最新预期波动金额
        predict_vola_val_highest|float|最高预期波动金额
        option_iv_crush|float|期权隐含波动率压缩值  (百分号前的值，如 12.34 表示 12.34%)
        option_strike_date_iv_crush|float|行权日期权隐含波动率压缩值  (百分号前的值，如 12.34 表示 12.34%)
        trading_day|int|财报发布日当天交易日时间戳（秒）
        trading_day_str|str|财报发布日当天交易日  (格式：yyyy-MM-dd；对应市场时区)
        close_price|float|收盘价
        open_price|float|开盘价
        highest_price|float|最高价
        lowest_price|float|最低价
        last_close_price|float|昨收价
        volume|float|成交量（股）
        schedule_delta|int|相对财报发布日的交易日偏移量  (负数=发布前，0=发布当日，正数=发布后)
        schedule_close_price|float|该偏移交易日的收盘价

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_financials_earnings_price_history("HK.00700")
if ret == RET_OK:
    print(data)
    print(data['period_text'][0])
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
fiscal_year  financial_type  ... schedule_delta  schedule_close_price
0           2026               1  ...            -15            504.000000
1           2026               1  ...            -14            495.200000
2           2026               1  ...            -13            493.400000
3           2026               1  ...            -12            478.600000
4           2026               1  ...            -11            473.800000
..           ...             ...  ...            ...                   ...
579         2021               2  ...             10            445.420633
580         2021               2  ...             11            438.045790
581         2021               2  ...             12            453.717332
582         2021               2  ...             13            463.396813
583         2021               2  ...             14            471.693512

[584 rows x 25 columns]
2026/Q1
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 仅支持港股、美股、新加坡、日本、马来西亚、A股正股。
:::

---

# 获取财务报表

`get_financials_statements(code, statement_type=None, financial_type=None, currency_code=None, next_key=None, num=None)`

* **介绍**

    获取指定股票的财务报表（利润表/资产负债表/现金流量表/关键指标），支持分页拉取

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码
    statement_type|[FinancialStatementsType](./quote.md#2910)|财务报表类型  (0=未知，1=利润表(Income)，2=资产负债表(BalanceSheet)，3=现金流量表(CashFlow)，4=关键指标(MainIndex)；默认 1=利润表)
    financial_type|[F10Type](./quote.md#7710)|财报类型  (0=不限，1=Q1，2=Q2，3=Q3，4=Q4，5=Q6累计(Q1+Q2)，6=Q9累计(Q1+Q2+Q3)，7=年报，9=单季报组合，10=单季报+年报，11=累计季报；默认 10=单季报+年报)
    currency_code|str|币种代码  (ISO 4217，如 CNY、USD、HKD、SGD、JPY、CAD、AUD；不填返回原始货币数据)
    next_key|str|分页标识  (首次不传，续拉填上次返回的 next_key；"-1" 表示无更多数据)
    num|int|每页返回数量  (默认 10，范围 1~50)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回财务报表数据字典</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回字典包含以下字段：

        字段|类型|说明
        :-|:-|:-
        structure_list|list|字段结构列表
        report_list|list|财报数据列表
        next_key|str|分页标识  ("-1" 表示无更多数据)

    * structure_list 每项包含的字段：

        字段|类型|说明
        :-|:-|:-
        field_id|int|财务字段 ID
        display_name|str|字段展示名  (如"营业收入"；当前语言)

    * report_list 每项包含的字段：

        字段|类型|说明
        :-|:-|:-
        date_time|int|财报截止日时间戳（秒）
        date_time_str|str|财报截止日字符串  (格式：YYYY-MM-DD；对应市场时区)
        fiscal_year|int|财务年度  (如 2024)
        financial_type|[F10Type](./quote.md#7710)|财报类型  (0=未知，下次请求可原样传入)
        period_text|str|财报周期  (如 "2024/Q3"、"2024/FY")
        item_list|list|财务数据项列表
        currency_info|str|货币单位  (展示型，如 "人民币"、"美元")
        accounting_standards|str|会计准则  (如 "国际会计准则")
        auditor_report|str|审计意见  (如 "无保留意见")
        currency_code|str|币种代码  (ISO 4217，如 "CNY"、"USD")

    * item_list 每项包含的字段：

        字段|类型|说明
        :-|:-|:-
        field_id|int|财务字段 ID
        data|float|财务数据
        yoy|float|同比  (百分号前的值，如 13.86 表示 13.86%；无同比数据时不含此字段)
        qoq|float|环比  (百分号前的值，如 1.23 表示 1.23%；无环比数据时不含此字段)
        display_name|str|字段展示名  (与 structure_list 中对应条目的 display_name 一致)

* **Example**

```python
import pandas as pd
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_financials_statements("HK.00700")
if ret == RET_OK:
    df = pd.DataFrame(data['report_list'][0]['item_list'])
    print(df)
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
field_id display_name          data         yoy
0       5001        营业总收入  7.517660e+11   13.859603
1       5002          营业额  7.517660e+11   13.859603
2       5005        营业总成本 -3.291730e+11   -5.839665
3       5008         销售成本 -3.291730e+11   -5.839665
4       5010           毛利  4.225930e+11   21.001529
5       5013         营业费用 -1.778540e+11  -19.245855
6       5015         销售费用 -4.172700e+10  -14.672419
7       5016         行政费用 -1.361270e+11  -20.721703
8       5032     经营利润特殊项目 -3.177000e+09 -139.702574
9       5034         营业利润  2.415620e+11   16.080327
10      5035         融资收入  1.690900e+10    5.654836
11      5036         融资成本 -1.513000e+10  -26.283282
12      5037     应占联营公司利润  2.374000e+10   -5.703845
13      5040         税前利润  2.772490e+11   14.810030
14      5041       利润特殊项目  1.016800e+10  142.846907
15      5043          所得税 -4.744800e+10   -5.397841
16      5045          净利润  2.298010e+11   16.966717
17      5046       持续经营利润  2.298010e+11   16.966717
18      5050       少数股东损益  4.959000e+09  107.142857
19      5051     归属母公司净利润  2.248420e+11   15.854343
20      5052   归属普通股股东净利润  2.248420e+11   15.854343
21      5054       基本每股收益  2.474900e+01   18.201356
22      5055       稀释每股收益  2.415300e+01   17.900029
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及基金。
:::

---

# 获取主营构成

`get_financials_revenue_breakdown(code, date=None, financial_type=None, currency_code=None)`

* **介绍**

    获取指定股票的主营构成数据，支持产品、行业、地区、业务等多维度拆解

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码
    date|int|筛选时间戳  (秒；从返回的 screen_date_list 中取 date 值可查历史；不填或填 0 返回最新一期)
    financial_type|[F10Type](./quote.md#7710)|财报类型  (0=不限，1=Q1单季报，2=Q2单季报，3=Q3单季报，4=Q4单季报，5=半年报，6=Q9累计报，7=年报，9=聚合季报；默认 0=不限)
    currency_code|str|币种代码  (ISO 4217，如 CNY、USD、HKD、SGD、JPY、CAD、AUD；不填返回原始货币数据)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回主营构成数据字典</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回字典包含以下字段：

        字段|类型|说明
        :-|:-|:-
        period|str|财报周期  (如 "2025/FY"、"2024/H1")
        breakdown_list|list|各维度主营构成数据列表  (每项含 type 和 item_list)
        currency_code|str|货币代码  (ISO 4217)
        screen_date_list|list|可选历史日期列表  (仅 date 与 financial_type 均未填时返回)

    * breakdown_list 每项包含的字段：

        字段|类型|说明
        :-|:-|:-
        type|[RevenueBreakdownType](./quote.md#3621)|维度类型  (1=产品(Product)，2=行业(Industry)，4=地区(Region)，8=业务(Business))
        item_list|list|该维度主营构成列表  (每项含 name、main_oper_income、ratio)

    * item_list 每项包含的字段：

        字段|类型|说明
        :-|:-|:-
        name|str|名称
        main_oper_income|float|营业收入
        ratio|float|占比  (百分号前的值，如 12.34 表示 12.34%)

    * screen_date_list 每项包含的字段：

        字段|类型|说明
        :-|:-|:-
        date|int|筛选时间戳  (秒；回传型，须为此列表中某个 date 值)
        period_text|str|财报周期  (如 "2025/FY")
        financial_type|[F10Type](./quote.md#7710)|财报类型

* **Example**

```python
import pandas as pd
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_financials_revenue_breakdown("HK.00700")
if ret == RET_OK:
    df = pd.DataFrame(data['breakdown_list'][0]['item_list'])
    print(df)
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
name  main_oper_income    ratio
0       增值服务      3.692810e+11  49.1218
1  金融科技及企业服务      2.294350e+11  30.5194
2       营销服务      1.449730e+11  19.2843
3         其他      8.077000e+09   1.0744
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及基金。
:::

---

# 获取分析师评级概述

`get_research_analyst_consensus(code)`

* **介绍**

    获取指定股票近3个月的分析师综合评级、目标价区间及各档评级占比

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回分析师评级数据字典</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回字典包含以下字段：

        字段|类型|说明
        :-|:-|:-
        highest|float|最高目标价
        average|float|平均目标价
        lowest|float|最低目标价
        rating|[ResearchRatingType](./quote.md#9592)|综合评级  (近3个月分析师综合评级
0=Unknown，1=Sell，2=Underperform，3=Hold，4=Buy，5=StrongBuy
美股仅返回 Sell(1)/Hold(3)/Buy(4)，非美市场另支持 Underperform(2)/StrongBuy(5))
        total|int|总分析师人数  (近3个月参与评级的分析师总人数)
        update_time|int|更新时间戳（秒，评级数据更新时间）
        update_time_str|str|更新日期  (格式 YYYY-MM-DD，对应市场时区)
        buy|float|Buy 评级占比  (百分号前的值，如 12.34 表示 12.34%)
        hold|float|Hold 评级占比  (百分号前的值，如 12.34 表示 12.34%)
        sell|float|Sell 评级占比  (百分号前的值，如 12.34 表示 12.34%)
        strong_buy|float|Strong Buy 占比  (百分号前的值，如 12.34 表示 12.34%；仅非美市场返回)
        underperform|float|Underperform 占比  (百分号前的值，如 12.34 表示 12.34%；仅非美市场返回)

* **Example**

```python
import json
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_research_analyst_consensus("HK.00700")
if ret == RET_OK:
    print(json.dumps(data, indent=2, ensure_ascii=False))
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
{
  "highest": 820.0,
  "average": 716.0,
  "lowest": 579.51,
  "rating": 5,
  "total": 44,
  "update_time": 1778469178,
  "update_time_str": "2026-05-11",
  "buy": 22.727,
  "hold": 0.0,
  "sell": 0.0,
  "strong_buy": 77.273,
  "underperform": 0.0
}
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及 REIT。
:::

---

# 获取评级汇总

`get_research_rating_summary(code, rating_dimension_type=None, uid=None, num=None, next_key=None)`

* **介绍**

    获取指定股票的机构或分析师评级汇总列表，或指定机构/分析师的评级详情，支持分页拉取

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码
    rating_dimension_type|[ResearchRatingDimensionType](./quote.md#2247)|评级维度  (0=Unknown，1=Institution（机构维度），2=Analyst（分析师维度）；默认机构维度)
    uid|str|机构或分析师 UID  (空=取该股票的评级汇总列表
非空=取该 uid 对应的评级详情（分析师 uid 须搭配 rating_dimension_type=2）)
    num|int|每页返回数量  (默认 10，范围 1~20)
    next_key|str|分页标识  (首次不传，续拉时填上次返回的 next_key；"-1" 表示无更多数据)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回评级汇总数据字典</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回字典包含以下字段：

        字段|类型|说明
        :-|:-|:-
        inst_rating_summary_list|list|机构评级汇总列表  (uid 为空且 rating_dimension_type=1 时填充
每项含 institution_info 和 rating_item_list)
        analyst_rating_summary_list|list|分析师评级汇总列表  (uid 为空且 rating_dimension_type=2 时填充
每项含 analyst_info 和 rating_item_list)
        inst_rating_detail|dict|机构评级详情  (uid 非空且 rating_dimension_type=1 时填充
含 institution_info、analyst_info_list 和 rating_item_list)
        analyst_rating_detail|dict|分析师评级详情  (uid 非空且 rating_dimension_type=2 时填充
含 analyst_info 和 rating_item_list)
        next_key|str|分页标识  ("-1" 表示无更多数据)

    * inst_rating_summary_list 每项字段（机构评级汇总行）：

        字段|类型|说明
        :-|:-|:-
        institution_info|dict|机构信息，见下表
        rating_item_list|list|评级记录列表，见下表

    * institution_info 字段（InstInfo）：

        字段|类型|说明
        :-|:-|:-
        institution_uid|str|机构唯一标识
        institution_picture_url|str|机构图片 URL
        institution_name|str|机构名称
        update_time|int|更新时间戳（秒，对应市场时区）
        update_time_str|str|更新日期  (格式 YYYY-MM-DD，对应市场时区)
        institution_source_name|str|机构来源名称
        institution_en_name|str|机构英文名称

    * analyst_info 字段（AnalystInfo）：

        字段|类型|说明
        :-|:-|:-
        analyst_uid|str|分析师唯一标识
        analyst_name|str|分析师姓名
        analyst_picture_url|str|分析师头像 URL
        num_of_stars|float|星级  (0.0~5.0，如 3.50 表示 3.5 星)
        success_rate|float|成功率  (百分号前的值，如 12.34 表示 12.34%)
        excess_return|float|超额收益  (百分号前的值，如 12.34 表示 12.34%)
        stock_success_rate|float|个股成功率  (百分号前的值，如 12.34 表示 12.34%)
        stock_avg_return|float|个股平均收益  (百分号前的值，如 12.34 表示 12.34%)
        institution_info|dict|所属机构信息，见 institution_info 字段表
        update_time|int|更新时间戳（秒，对应市场时区）
        update_time_str|str|更新日期  (格式 YYYY-MM-DD，对应市场时区)

    * rating_item_list 每项字段（RatingItem）：

        字段|类型|说明
        :-|:-|:-
        analyst_uid|str|分析师唯一标识
        institution_uid|str|机构唯一标识
        rating|[ResearchRatingType](./quote.md#9592)|评级  (0=Unknown，1=Sell，2=Underperform，3=Hold，4=Buy，5=StrongBuy
本接口仅返回 Sell(1)/Hold(3)/Buy(4)，数值越大评级越高)
        target_price|float|目标价
        recommendation_date|int|评级日期时间戳（秒，对应市场时区）
        recommendation_date_str|str|评级日期  (格式 YYYY-MM-DD，对应市场时区)
        rating_url|str|评级来源 URL
        update_time|int|更新时间戳（秒，对应市场时区）
        update_time_str|str|更新日期  (格式 YYYY-MM-DD，对应市场时区)

* **Example**

```python
from futu import *
import pandas as pd
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_research_rating_summary("US.AAPL", rating_dimension_type=1)
if ret == RET_OK:
    rows = []
    for row in data.get('inst_rating_summary_list', []):
        info = row.get('institution_info', {})
        rows.append({
            'institution_name':        info.get('institution_name', ''),
            'institution_en_name':     info.get('institution_en_name', ''),
            'institution_uid':         info.get('institution_uid', ''),
            'institution_source_name': info.get('institution_source_name', ''),
            'update_time_str':         info.get('update_time_str', ''),
        })
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
institution_name institution_en_name                      institution_uid    institution_source_name update_time_str
            韦德布什             Wedbush 8c9ae25a-07e2-4d52-a511-b0dd115a5224                    Wedbush      2024-03-01
            艾弗考尔            Evercore a746f081-c12a-4d6d-8067-f4b6634de478               Evercore ISI      2024-03-21
            瑞士银行                 UBS 1d3bfc25-1dda-48fd-bd9f-d4de47e68def                        UBS      2024-03-01
            高盛集团       Goldman Sachs d0e296b4-c2e4-4fad-837c-cd79aaed2e8e              Goldman Sachs      2024-03-01
            联博集团           Bernstein 16358c98-ccc1-4d08-a875-2c727b7b8d70                  Bernstein      2024-03-01
            星展银行                 DBS 44dec2a6-aca9-4b52-9fed-4bbf78749783                        DBS      2024-03-01
            美银证券     BofA Securities 7890753d-5482-4311-a7af-8d5feed39f3e Bank of America Securities      2024-03-01
            辉立证券  Phillip Securities a294f0ca-10c0-4884-86a7-359995505e70         Phillip Securities      2024-09-09
            摩根大通         J.P. Morgan f5ec822c-d561-4db3-a09d-a1e71a9a832f                J.P. Morgan      2024-03-01
           摩根士丹利      Morgan Stanley 9a29ac93-221c-4c1a-ba1a-bbbbf57a5ca6             Morgan Stanley      2024-03-01
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持美股正股及 REIT。
:::

---

# 获取晨星研究报告

`get_research_morningstar_report(code)`

* **介绍**

    获取指定股票的晨星研究报告，包含星级评分、公允价值、护城河、不确定性、财务健康、资本配置、多空观点、分析师观点等

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回晨星研究报告数据字典</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回字典包含以下字段：

        字段|类型|说明
        :-|:-|:-
        rating_type|[MorningstarRatingType](./quote.md#9433)|评级类型  (0=Unknown，1=Quantitative（定量评级，系统模型给出），2=Qualitative（定性评级，分析师人工给出）)
        star_rating|int|晨星星级  (取值 1~5 星)
        star_update_time|int|星级更新时间戳（秒，对应市场时区）
        star_update_time_str|str|星级更新日期  (格式 YYYY-MM-DD，对应市场时区)
        fair_value|float|公允价值
        fair_value_content|dict|公允价值分析，见 StringWithUpdateTime 字段表
        economic_moat_label|str|护城河评级  (如 Wide、Narrow、None)
        economic_moat_content|dict|护城河分析，见 StringWithUpdateTime 字段表
        uncertainty_label|str|不确定性评级  (如 Low、Medium、High、Very High、Extreme)
        uncertainty_content|dict|不确定性分析，见 StringWithUpdateTime 字段表
        financial_health_label|str|财务健康评级
        financial_health_content|dict|财务健康分析，见 StringWithUpdateTime 字段表
        analyst_report_by_line|list|分析师署名列表  (如 ["William Kerwin, CFA"])
        analyst_report_update_time|int|分析师报告更新时间戳（秒，对应市场时区）
        analyst_report_update_time_str|str|分析师报告更新日期  (格式 YYYY-MM-DD，对应市场时区)
        bull_say|list|多方观点列表，每项见 StringWithUpdateTime 字段表
        bear_say|list|空方观点列表，每项见 StringWithUpdateTime 字段表
        capital_allocation_label|str|资本配置评级
        capital_allocation_content|dict|资本配置分析，见 StringWithUpdateTime 字段表
        analyst_note_title|dict|分析师观点标题，见 StringWithUpdateTime 字段表
        analyst_note_content|dict|分析师观点内容，见 StringWithUpdateTime 字段表
        investment_thesis_content|dict|投资论点，见 StringWithUpdateTime 字段表
        fundamentals_content|dict|基本面报告，见 StringWithUpdateTime 字段表
        valuation_content|dict|估值报告，见 StringWithUpdateTime 字段表
        pdf_url|str|PDF 报告下载链接

    * StringWithUpdateTime 字段（嵌套文本结构）：

        字段|类型|说明
        :-|:-|:-
        context|str|文本内容
        update_time|int|更新时间戳（秒，对应市场时区）
        update_time_str|str|更新日期  (格式 YYYY-MM-DD，对应市场时区)

* **Example**

```python
import json
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_research_morningstar_report("HK.00700")
if ret == RET_OK:
    print(json.dumps(data, indent=2, ensure_ascii=False))
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
{
  "rating_type": 2,
  "star_rating": 4,
  "star_update_time": 1778257800,
  "star_update_time_str": "2026-05-09",
  "fair_value": 800.0,
  "fair_value_content": {
    "context": "我们对腾讯控股的每股公平价值估计为800港元。我们的估值中约85%来自于腾讯的核心业务，而...
    "update_time": 1755138060,
    "update_time_str": "2025-08-14"
  },
  "economic_moat_label": "宽",
  "economic_moat_content": {
    "context": "腾讯的宽护城河主要基于其庞大用户群的网络效应。此外，腾讯还拥有无形资产、成本优势和...
    "update_time": 1766457150,
    "update_time_str": "2025-12-23"
  },
  "uncertainty_label": "较高",
  "uncertainty_content": {
    "context": "由于监管风险及其核心业务的竞争强度，我们对腾讯的晨星不确定性评级为高。\n\n在支付领域，...
    "update_time": 1766457180,
    "update_time_str": "2025-12-23"
  },
  //...
 }
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及 REIT。
:::

---

# 获取个股/指数估值详情

`get_valuation_detail(code, valuation_type=None, interval_type=None)`

* **介绍**

    获取指定股票或指数的估值详情，包含估值走势、市场分布、行业分布（仅个股）、盈利/营收增速（仅个股，PB 无）

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码
    valuation_type|[ValuationType](./quote.md#5459)|估值类型  (0=Unknown（使用推荐类型），1=PE（市盈率），2=PB（市净率），3=PS（市销率）；默认 None（使用推荐类型）)
    interval_type|[ValuationIntervalType](./quote.md#971)|历史数据时间周期  (0=Unknown，1=Month3，2=Month6，3=Year1，4=Year3，5=Since2019，6=Year5，7=Year10，8=Year2，9=Year20，10=Year30；默认 None)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回估值详情数据字典</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回字典包含以下字段：

        字段|类型|说明
        :-|:-|:-
        valuation_type|[ValuationType](./quote.md#5459)|实际估值类型  (0=Unknown，1=PE，2=PB，3=PS)
        last_update_time|int|最后更新时间戳（秒，对应市场时区）
        last_update_time_str|str|最后更新时间  (格式 YYYY-MM-DD HH:MM:SS，对应市场时区)
        trend|dict|走势数据，见 trend 字段表
        market_distribution|dict|市场分布数据，见 market_distribution 字段表
        plate_distribution|dict|行业分布数据，见 plate_distribution 字段表  (仅个股返回)
        profit_growth_rate|dict|盈利/营收增速数据，见 profit_growth_rate 字段表  (仅个股返回，PB 估值无此字段)

    * trend 字段（估值走势摘要）：

        字段|类型|说明
        :-|:-|:-
        current_value|float|当前估值
        average_value|float|历史平均估值
        avg_minus_1_stddev|float|历史平均 - 1σ
        avg_plus_1_stddev|float|历史平均 + 1σ
        valuation_percentile|float|历史分位  (百分号前的值，如 12.34 表示 12.34%)
        forward_value|float|预测估值  (仅 PE / PS 有)
        historical_items|list|历史估值列表，每项见 historical_items 字段表

    * historical_items 字段（历史估值条目）：

        字段|类型|说明
        :-|:-|:-
        value|float|估值
        time|int|时间戳（秒，对应市场时区）
        time_str|str|日期  (格式 YYYY-MM-DD，对应市场时区)
        plate_value|float|行业均值

    * market_distribution 字段（市场/成分股分布）：

        字段|类型|说明
        :-|:-|:-
        sections|list|区间分布列表（降序），每项见 sections 字段表
        total|int|市场总数/成分股总数
        ranking|int|该股票估值在市场中的排名  (指数无此字段)
        average_value|float|市场估值均值  (指数无此字段)
        median_value|float|市场估值中位数  (指数无此字段)

    * sections 字段（区间分布条目）：

        字段|类型|说明
        :-|:-|:-
        start|float|区间开始值
        end|float|区间结束值  (0 表示无上限)
        number|int|该区间个股数量

    * plate_distribution 字段（行业分布，仅个股）：

        字段|类型|说明
        :-|:-|:-
        plate|str|所属板块代码
        plate_name|str|所属板块名称
        plate_average_value|float|板块估值均值
        plate_ranking|int|该股票估值在板块中的排名
        plate_stock_item_count|int|板块个股总数
        stock_items|list|板块成分股估值明细，每项见 stock_items 字段表

    * stock_items 字段（板块成分股条目）：

        字段|类型|说明
        :-|:-|:-
        security|str|股票代码
        name|str|个股名称
        value|float|估值
        market_cap|float|市值

    * profit_growth_rate 字段（盈利/营收增速，仅个股非 PB）：

        字段|类型|说明
        :-|:-|:-
        financial_ttm_multiple|float|TTM 增长倍数
        market_cap_multiple|float|市值增长倍数
        year_count|int|计算增长倍数时实际用到的年份数量
        profit_data|list|各期数据列表，每项见 profit_data 字段表
        conclusion_detailed|str|估值结论描述

    * profit_data 字段（各期盈利/营收条目）：

        字段|类型|说明
        :-|:-|:-
        financial_year|int|财报年度
        financial_quarter|int|财报季度  (1=Q1，2=Q2，3=Q3，4=FY)
        period_str|str|财报周期  (如 "2024/Q3"、"2024/FY")
        report_date|int|报告日时间戳（秒，对应市场时区）
        report_date_str|str|报告日  (格式 YYYY-MM-DD，对应市场时区)
        market_cap_multiple|float|报告日市值倍数  (基准期 = 1)
        finance_data_multiple|float|盈利/营收倍数  (基准期 = 1，依 valuation_type 而定)

* **Example**

```python
from futu import *
import pandas as pd
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_valuation_detail("HK.00700")
if ret == RET_OK:
    trend = data.get('trend', {})
    items = trend.get('historical_items', [])
    df = pd.DataFrame(items)
    print(df.to_string(index=False))
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
value       time   time_str  plate_value
22.690 1746979200 2025-05-12       22.678
22.186 1747065600 2025-05-13       22.179
22.843 1747152000 2025-05-14       22.817
22.046 1747238400 2025-05-15       22.050
21.538 1747324800 2025-05-16       21.577
21.792 1747584000 2025-05-19       21.821
//...
18.087 1776960000 2026-04-24       18.147
17.544 1777219200 2026-04-27       17.617
17.368 1777305600 2026-04-28       17.444
17.566 1777392000 2026-04-29       17.650
17.148 1777478400 2026-04-30       17.227
17.339 1777824000 2026-05-04       17.421
17.310 1777910400 2026-05-05       17.393
16.972 1777996800 2026-05-06       17.059
17.500 1778083200 2026-05-07       17.589
17.266 1778169600 2026-05-08       17.364
17.039 1778428800 2026-05-11       17.143
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股、基金及指数。
* PB 估值无盈利/营收增速模块。
* 指数无排名、均值、中位数。
:::

---

# 获取板块/指数成分股估值列表

`get_valuation_plate_stock_list(code, valuation_type=None, next_key=None, num=None, sort_type=None, sort_id=None, filter_security=None)`

* **介绍**

    获取板块或指数成分股的估值列表，包含估值、预测估值、历史分位、市值；指数首次全量请求还返回所属板块列表

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|板块或指数代码  (如 HK.LIST23363（板块）或 HK.800000（指数）；不支持个股)
    valuation_type|[ValuationType](./quote.md#5459)|估值类型  (0=Unknown，1=PE（市盈率），2=PB（市净率），3=PS（市销率）；默认 None（1=PE）)
    next_key|str|分页标识  (首次不传，续拉时填上次返回的 next_key；"-1" 表示无更多数据)
    num|int|每页数量  (默认 10，范围 1~50)
    sort_type|[SortType](./quote.md#7169)|排序方向  (1=Desc（降序），2=Asc（升序）；默认 None（升序）)
    sort_id|[SortField](./quote.md#2930)|排序列  (51=市值（默认），52=估值，53=预测估值，54=历史分位)
    filter_security|str|板块筛选  (仅指数有效，按行业/板块筛选成分股，如 HK.LIST23363；不传则不筛选)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回成分股估值数据字典</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回字典包含以下字段：

        字段|类型|说明
        :-|:-|:-
        count|int|成分股总数
        stock_list|list|成分股估值列表，每项见 stock_list 字段表
        next_key|str|分页标识  ("-1" 表示无更多数据)
        plate_list|list|所属板块列表  (仅指数全量首次请求时返回，每项见 plate_list 字段表)

    * stock_list 字段（成分股估值条目）：

        字段|类型|说明
        :-|:-|:-
        symbol|str|股票代码
        valuation_val|float|估值
        forward_value|float|预测估值  (当前仅支持 PE 和 PS)
        valuation_percentile|float|历史分位  (百分号前的值，如 12.34 表示 12.34%)
        market_cap|float|市值
        name|str|股票名称

    * plate_list 字段（指数所属板块条目）：

        字段|类型|说明
        :-|:-|:-
        symbol|str|板块代码
        name|str|板块名称

* **Example**

```python
from futu import *
import pandas as pd
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_valuation_plate_stock_list("HK.LIST23363")
if ret == RET_OK:
    df = pd.DataFrame(data.get('stock_list', []))
    print(df.to_string(index=False))
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
symbol         name  valuation_val  valuation_percentile   market_cap
HK.08076         新利软件         -2.300             65.337673 3.029652e+07
HK.08092 ITE HOLDINGS         19.500             98.209927 3.609481e+07
HK.08036       电子交易集团        -12.000             35.313263 4.428000e+07
HK.01561       联洋智能控股        -23.500              1.057770 5.007634e+07
HK.08071       中彩网通控股        -12.000             39.951180 5.623258e+07
HK.00248     香港通讯国际控股         -2.056             19.446705 6.771489e+07
HK.01613         协同通信         -2.796             72.660700 8.841764e+07
HK.08062         俊盟国际        -93.333              0.244101 1.344000e+08
HK.01949       佰达国际控股         -5.147             36.523929 1.344000e+08
HK.01206         同方泰德         -0.314             41.171684 1.720823e+08
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持板块和指数，不支持个股。
* 指数首次全量请求时额外返回所属板块列表（plate_list）。
:::

---

# 获取分红派息

`get_corporate_actions_dividends(code)`

* **介绍**

    获取股票的分红派息历史记录

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码  (如 HK.00700；支持正股及基金)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回分红派息数据字典</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回字典包含以下字段：

        字段|类型|说明
        :-|:-|:-
        dividend_list|list|分红派息列表  (按公告日倒序排列，每项见 dividend_list 字段表)

    * dividend_list 字段（分红派息条目）：

        字段|类型|说明
        :-|:-|:-
        pub_date|str|公告日  (格式 YYYY/MM/DD，对应市场时区)
        statement|str|分配方案  (如"末期息5.3港元")
        process|str|事件进展  (如"方案实施"/"预案"；仅港股和A股的正股与信托有值)
        record_date|str|股权登记日  (格式 YYYY/MM/DD，对应市场时区；ETF 无此数据)
        ex_date|str|除权除息日  (格式 YYYY/MM/DD，对应市场时区)
        dividend_payable_date|str|派息日  (格式 YYYY/MM/DD，对应市场时区)
        fiscal_year|str|财政年度  (如"2026"。仅ETF有值。)

* **Example**

```python
from futu import *
import pandas as pd
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_corporate_actions_dividends("HK.00700")
if ret == RET_OK:
    df = pd.DataFrame(data.get('dividend_list', []))
    print(df.to_string(index=False))
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
pub_date                                           statement process record_date    ex_date dividend_payable_date
2026/03/18                                           末期息5.3港元;      预案  2026/05/18 2026/05/15            2026/06/01
2025/03/19                                           末期息4.5港元;    方案实施  2025/05/19 2025/05/16            2025/05/30
2024/03/20                                           末期息3.4港元;    方案实施  2024/05/20 2024/05/17            2024/05/31
2023/03/22                                           末期息2.4港元;    方案实施  2023/05/22 2023/05/19            2023/06/05
2022/11/16                      实物分派：按于记录日期持有每10股股份获发1股美团B类普通股    方案实施  2023/01/06 2023/01/05            2023/03/24
2022/03/23                                           末期息1.6港元;    方案实施  2022/05/23 2022/05/20            2022/06/06
2021/12/23                          实物分派:每持有21股股份获发1股京东集团A类普通股    方案实施  2022/01/21 2022/01/20            2022/03/25
2021/03/24                                           末期息1.6港元;    方案实施  2021/05/25 2021/05/24            2021/06/07
2020/03/18                                           末期息1.2港元;    方案实施  2020/05/18 2020/05/15            2020/05/29
2019/03/21                                             末期息1港元;    方案实施  2019/05/20 2019/05/17            2019/05/31
2018/12/03       实物分派:每持有3,900股股份获分派1股腾讯音乐娱乐集团美国预托股份(连同选择现金替代)    方案实施  2019/01/02 2018/12/28            2019/02/20
2018/03/21                                          末期息0.88港元;    方案实施  2018/05/21 2018/05/18            2018/06/01
2017/06/30 优先发售：合资格股东优先售股每持有1,256股可认购1股ChinaLiteratureLtd.预留股份    方案实施  2017/10/19 2017/10/18            2017/11/07
2017/03/22                                           末期息0.61港元    方案实施  2017/05/22 2017/05/19            2017/06/02
2016/03/17                                           末期息0.47港元    方案实施  2016/05/23 2016/05/20            2016/06/02
2015/03/18                                        末期股息每股0.36港元    方案实施  2015/05/18 2015/05/15            2015/05/29
2014/03/19                       末期息1.2港元(待股份拆细后每股拆细股份HKD0.24)    方案实施  2014/05/19 2014/05/16            2014/05/30
2013/03/20                                              末期息1港元    方案实施  2013/05/21 2013/05/20            2013/05/30
2012/03/14                                           末期息0.75港元    方案实施  2012/05/21 2012/05/18            2012/05/30
2011/03/16                                           末期息0.55港元    方案实施  2011/05/04 2011/05/03            2011/05/25
2010/03/17                                           末期股息0.4港元    方案实施  2010/05/06 2010/05/05            2010/05/26
2009/03/18                                末期息0.25港元,特别股息0.10港元    方案实施  2009/05/07 2009/05/06            2009/05/27
2008/03/19                                           末期息0.16港元    方案实施  2008/05/07 2008/05/06            2008/05/28
2007/03/21                                          末期息0.12港元;    方案实施  2007/05/10 2007/05/09            2007/05/30
2006/03/22                                          末期息0.08港元;    方案实施  2006/05/16 2006/05/15            2006/06/07
2005/03/17                                          末期息0.07港元;    方案实施  2005/04/20 2005/04/19            2005/05/17
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及基金。
:::

---

# 获取回购

`get_corporate_actions_buybacks(code, next_key=None, num=None)`

* **介绍**

    获取股票的回购记录（港股 / A 股，支持分页）

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码  (如 HK.00700；支持港股、A股正股及基金)
    next_key|str|分页标识  (首次不填，续拉时填上次返回的 next_key；"-1" 表示无更多数据)
    num|int|每页数量  (每页返回数量，默认 10，范围 1~50)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回回购数据字典</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回字典包含以下字段：

        字段|类型|说明
        :-|:-|:-
        next_key|str|分页标识  ("-1" 表示无更多数据；续拉时将此值传入请求参数 next_key)
        hk_buy_back_list|pd.DataFrame|港股回购列表  (每项见 hk_buy_back_list 字段表；A股标的此列表为空)
        a_buy_back_list|pd.DataFrame|A股回购列表  (每项见 a_buy_back_list 字段表；港股标的此列表为空)

    * hk_buy_back_list 字段（港股回购条目）：

        字段|类型|说明
        :-|:-|:-
        publ_date|int|公告日时间戳  (Unix 时间戳（秒），对应市场时区)
        publ_date_str|str|公告日  (格式 YYYY-MM-DD，对应市场时区)
        end_date|int|回购截止日时间戳  (Unix 时间戳（秒），对应市场时区)
        end_date_str|str|回购截止日  (格式 YYYY-MM-DD，对应市场时区)
        buy_back_money|float|回购金额
        buy_back_sum|int|回购股数  (单位：股)
        percentage|float|占总股本比例  (百分号前的值，如 12.34 表示 12.34%)
        high_price|float|最高回购价
        low_price|float|最低回购价
        cumulative_sum|int|本轮累计回购股数  (单位：股)
        cumulative_percentage|float|本轮累计占总股本比例  (百分号前的值，如 12.34 表示 12.34%)
        share_type|str|股份类别

    * a_buy_back_list 字段（A股回购条目）：

        字段|类型|说明
        :-|:-|:-
        change_reg_date|int|工商变更登记日时间戳  (Unix 时间戳（秒），对应市场时区)
        change_reg_date_str|str|工商变更登记日  (格式 YYYY-MM-DD，对应市场时区)
        change_date|int|股份变动日时间戳  (Unix 时间戳（秒），对应市场时区)
        change_date_str|str|股份变动日  (格式 YYYY-MM-DD，对应市场时区)
        event_proce_desc|str|事件进程描述
        advance_date|int|预案公告日时间戳  (Unix 时间戳（秒），对应市场时区)
        advance_date_str|str|预案公告日  (格式 YYYY-MM-DD，对应市场时区)
        meet_pass_date|int|股东大会通过日时间戳  (Unix 时间戳（秒），对应市场时区)
        meet_pass_date_str|str|股东大会通过日  (格式 YYYY-MM-DD，对应市场时区)
        start_date|int|回购开始日时间戳  (Unix 时间戳（秒），对应市场时区)
        start_date_str|str|回购开始日  (格式 YYYY-MM-DD，对应市场时区)
        end_date|int|回购截止日时间戳  (Unix 时间戳（秒），对应市场时区)
        end_date_str|str|回购截止日  (格式 YYYY-MM-DD，对应市场时区)
        pay_date|int|支付日时间戳  (Unix 时间戳（秒），对应市场时区)
        pay_date_str|str|支付日  (格式 YYYY-MM-DD，对应市场时区)
        seller|str|出售方  (股份被回购方)
        buy_back_mode|str|回购方式
        share_type|str|股份类别
        buy_back_sum|int|回购股数  (单位：股)
        buy_back_money|float|回购金额
        percentage|float|占总股本比例  (百分号前的值，如 12.34 表示 12.34%)
        value_floor|float|拟回购资金总额下限
        value_ceiling|float|拟回购资金总额上限
        price_floor|float|回购价格下限
        price_ceiling|float|回购价格上限
        volume_floor|float|拟回购股数下限
        volume_ceiling|float|拟回购股数上限

* **Example**

```python
from futu import *
import pandas as pd
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_corporate_actions_buybacks("HK.00700", num=3)
if ret == RET_OK:
    df = pd.DataFrame(data.get('hk_buy_back_list', []))
    print(df.to_string(index=False))
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
publ_date publ_date_str   end_date end_date_str  buy_back_money  buy_back_sum  percentage  high_price  low_price  cumulative_sum  cumulative_percentage share_type
1775664000    2026-04-09 1775664000   2026-04-09    1000880717.6       1964000    0.021373       514.5      503.0       119812000                1.30386        普通股
1775577600    2026-04-08 1775577600   2026-04-08    1000761103.7       1979000    0.021537       510.0      501.0       117848000                1.28249        普通股
1775059200    2026-04-02 1775059200   2026-04-02     300715258.5        615000    0.006693       496.0      485.2       115869000                1.26095        普通股
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持港股、A股正股及基金。
:::

---

# 获取拆合股

`get_corporate_actions_stock_splits(code, next_key=None, num=None)`

* **介绍**

    获取股票的拆合股历史记录（港股有额外字段），支持分页

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码  (如 US.AAPL；支持港股、美股、日本、新加坡、马来西亚正股及基金)
    next_key|str|分页标识  (首次不填，续拉时填上次返回的 next_key；"-1" 表示无更多数据)
    num|int|每页数量  (每页返回数量，默认 10，范围 1~50)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回拆合股数据字典</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回字典包含以下字段：

        字段|类型|说明
        :-|:-|:-
        next_key|str|分页标识  ("-1" 表示无更多数据；续拉时将此值传入请求参数 next_key)
        split_list|list|拆合股列表  (每项见 split_list 字段表)

    * split_list 字段（拆合股条目）：

        字段|类型|说明
        :-|:-|:-
        dir_deci_pub_date|int|公告日时间戳  (Unix 时间戳（秒），对应市场时区)
        dir_deci_pub_date_str|str|公告日  (格式 YYYY-MM-DD，对应市场时区)
        reform_type|str|重组方式
        rate|str|比率
        ex_date|int|除权日时间戳  (仅港股的正股与信托有值；Unix 时间戳（秒），对应市场时区)
        ex_date_str|str|除权日  (仅港股的正股与信托有值；格式 YYYY-MM-DD，对应市场时区)
        sm_deci_date|int|决议日时间戳  (仅港股的正股与信托有值；Unix 时间戳（秒），对应市场时区)
        sm_deci_date_str|str|决议日  (仅港股的正股与信托有值；格式 YYYY-MM-DD，对应市场时区)
        temp_trade_begin_date|int|临时买卖日时间戳  (仅港股的正股与信托有值；Unix 时间戳（秒），对应市场时区)
        temp_trade_begin_date_str|str|临时买卖日  (仅港股的正股与信托有值；格式 YYYY-MM-DD，对应市场时区)
        simul_trade_begin_date|int|并行买卖开始日时间戳  (仅港股的正股与信托有值；Unix 时间戳（秒），对应市场时区)
        simul_trade_begin_date_str|str|并行买卖开始日  (仅港股的正股与信托有值；格式 YYYY-MM-DD，对应市场时区)
        simul_trade_end_date|int|并行买卖结束日时间戳  (仅港股的正股与信托有值；Unix 时间戳（秒），对应市场时区)
        simul_trade_end_date_str|str|并行买卖结束日  (仅港股的正股与信托有值；格式 YYYY-MM-DD，对应市场时区)
        event_status|str|事件进程  (仅港股的正股与信托有值；如：方案实施)
        new_par_value|float|新面值  (仅港股的正股与信托有值)
        temp_share_code|str|临时证券代码  (仅港股的正股与信托有值；如：02988)
        temp_share_abbr_name|str|临时证券简称  (仅港股的正股与信托有值；如：腾讯控股)
        new_trade_unit|int|新买卖单位  (仅港股的正股与信托有值；如：100)
        shares_after_effect|float|生效后股数  (仅港股的正股与信托有值；单位：股)

* **Example**

```python
from futu import *
import pandas as pd
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_corporate_actions_stock_splits("HK.00700", num=3)
if ret == RET_OK:
    df = pd.DataFrame(data.get('split_list', []))
    print(df.to_string(index=False))
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
dir_deci_pub_date  dir_deci_pub_date_str reform_type   rate    ...  temp_share_abbr_name  new_trade_unit  shares_after_effect
        1395158400             2014-03-19        拆股    1->5   ...               腾讯控股             100         9319999970.0
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持港股、美股、日本、新加坡、马来西亚正股及基金。
:::

---

# 获取持股统计

`get_shareholders_overview(code, period_id=None)`

* **介绍**

    获取指定股票的持股统计，同时返回主要股东和持股类型两组数据

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码  (如 HK.00700；支持港股、美股、新加坡、日本、马来西亚正股及基金)
    period_id|int|报告期 ID  (传 0 或不传则返回最新数据，并额外返回可用报告期列表；报告期 ID 可从 holding_period 列表中获取)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回持股统计数据字典</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回字典包含以下字段：

        字段|类型|说明
        :-|:-|:-
        main_holder|pd.DataFrame|主要股东列表  (每项见 main_holder 字段表)
        holder_type|pd.DataFrame|持股类型列表  (每项见 holder_type 字段表；结构与 main_holder 相同，holder_id 固定为 0)
        holding_period|pd.DataFrame|可用报告期列表  (仅当请求 period_id 为 0 或不传时返回；每项见 holding_period 字段表)

    * main_holder / holder_type 字段（持股统计条目）：

        字段|类型|说明
        :-|:-|:-
        static_date|int|统计日期时间戳  (Unix 时间戳（秒），对应市场时区)
        static_date_str|str|统计日期  (格式 YYYY-MM-DD，对应市场时区)
        name|str|持股人名称  (持股人或分组名称)
        holder_pct|float|持股占比  (百分号前的值，如 23.05 表示 23.05%)
        holder_id|int|股东 ID  (main_holder 中有值；holder_type 中固定为 0)

    * holding_period 字段（可用报告期条目）：

        字段|类型|说明
        :-|:-|:-
        period_text|str|报告期  (如 "2025/Q3")
        period_id|int|报告期 ID  (下次请求时原样传入 period_id 参数)

* **Example**

```python
from futu import *
import pandas as pd
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_shareholders_overview("HK.00700")
if ret == RET_OK:
    df = data.get('main_holder')
    if df is not None:
        print(df.to_string(index=False))
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
static_date static_date_str                 name  holder_pct   holder_id
  1778469438      2026-05-11 Prosus Ventures N.V.    23.05351 337488017.0
  1778469438      2026-05-11           Huateng Ma     7.86952  10253703.0
  1778469438      2026-05-11                 先锋领航     2.97766    417222.0
  1778469438      2026-05-11                  贝莱德     2.66990    403413.0
  1778469438      2026-05-11             挪威银行投资管理     1.36075  27081864.0
  1778469438      2026-05-11                   其他    62.06866         NaN
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持港股、美股、新加坡、日本、马来西亚正股及基金。
:::

---

# 获取持股变动

`get_shareholders_holding_changes(code, next_key=None, num=None, sort_type=None, sort_column=None, filter_type=None)`

* **介绍**

    获取指定股票的持股变动记录，支持分页拉取

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码  (如 HK.00700；支持港股、美股、新加坡、马来西亚、日本正股及基金)
    next_key|str|分页标识  (首次不传，续拉时填上次返回的 next_key；"-1" 表示无更多数据)
    num|int|每页数量  (默认 10，范围 1~50)
    sort_type|SortType|排序方向  (1=降序（默认），2=升序)
    sort_column|SortField|排序字段  (62=持股变动数（默认），63=持股日期，64=变动比例，65=变动金额，66=持股比例)
    filter_type|HoldingChangesFilterType|筛选类型  (0=全部（默认），1=增持，2=减持，3=建仓，4=清仓)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回持股变动记录 DataFrame</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回 DataFrame 字段说明：

        字段|类型|说明
        :-|:-|:-
        period_text|str|报告期  (如 "2026/Q1")
        name|str|股东名称
        holder_id|int|股东 ID  (用于请求历史变动明细)
        share_change_num|int|持股变动数  (单位：股)
        shares_change_price|int|参考变动金额  (单位：港元或美元（依市场而定）)
        share_ratio|float|持股比例  (百分号前的值，如 12.34 表示 12.34%)
        holder_type|str|持股性质  (文本描述，如"传统投资经理")
        holder_type_id|int|持股性质 ID  (用于请求历史变动明细)
        holding_date_str|str|报告日期  (格式 YYYY-MM-DD，香港时区)
        share_ratio_change|float|变动比例  (百分号前的值，如 12.34 表示变动 12.34%)
        share_num|int|持股数  (单位：股)
        next_key|str|分页标识  ("-1" 表示无更多数据；续拉时原样传入 next_key 参数)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_shareholders_holding_changes("HK.00700")
if ret == RET_OK:
    print(data[['period_text', 'name', 'share_change_num', 'share_ratio', 'share_ratio_change']].to_string(index=False))
    print('next_key:', data['next_key'][0])
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
period_text                                name  share_change_num  share_ratio  share_ratio_change
    2026/Q1                                 贝莱德           7971983        2.669               0.088
    2026/Q1       CSOP Asset Management Limited           6691695        0.192               0.074
    2026/Q1                              恒生投资管理           4870059        0.395               0.053
    2026/Q1                        GQG Partners           3289800        0.146               0.036
    2026/Q1                                先锋领航           2837500        2.977               0.031
    2026/Q1 Pinebridge Investments Asia Limited           2316700        0.073               0.025
    2026/Q1                                资本集团           2214900        0.948               0.024
    2026/Q1                              澳洲养老基金           2214046        0.116               0.024
    2026/Q1                            未来资产环球投资           1852929        0.096               0.020
    2026/Q1                                柏基投资           1831832        0.395               0.020
next_key: 10
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持港股、美股、新加坡、马来西亚、日本正股及基金。
:::

---

﻿# 获取持股明细

`get_shareholders_holder_detail(code, request_type=None, next_key=None, num=None, sort_column=None, sort_type=None, period_id=None, holder_id=None)`

* **介绍**

    获取股票某一持股类型下的持有人明细列表，支持分页拉取

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码  (如 US.AAPL；支持港股、美股、新加坡、日本、马来西亚正股及基金)
    request_type|[HolderDetailType](./quote.md#8148)|持股类型  (0=Default，1000=All，1=其他机构，2=传统投资经理，3=对冲基金，4=风险资本/私募，5=企业年金，6=基金会基金，7=保险公司，8=银行/投资银行，9=家族办公室/信托，10=主权财富基金，11=REIT，12=结构化融资经理，13=联合养老金，14=政府养老金，15=捐赠基金，100=个人，200=ADS，300=上市公司，400=未公开上市公司，500=国有股；默认按服务端默认逻辑返回)
    next_key|str|分页标识  (首次不传，续拉时填上次返回的 next_key；"-1" 表示无更多数据)
    num|int|每页数量  (默认 10，范围 1~50)
    sort_column|[SortField](./quote.md#2930)|排序字段  (61=持股股数（默认），62=持股变动数)
    sort_type|[SortType](./quote.md#7169)|排序方向  (1=降序（默认），2=升序)
    period_id|int|报告期 ID  (与 Qot_GetShareholdersOverview（3237）返回的 holdingPeriodList 中 periodId 一致；默认 0 表示最新周期)
    holder_id|int|持有人 ID 过滤  (默认 0 表示不过滤；可取自 GetShareholdersOverview（3237）、GetShareholdersHoldingChanges（3238）、本协议（3239）、GetInsiderHolderList（3241）、GetInsiderTradeList（3242）返回的 holder_id)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回持股明细 DataFrame</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回 DataFrame 字段说明：

        字段|类型|说明
        :-|:-|:-
        update_time_str|str|数据更新时间  (格式 YYYY-MM-DD HH:MM:SS，对应市场时区)
        next_key|str|分页标识  ("-1" 表示无更多数据；续拉时原样传入 next_key 参数)
        period_text|str|报告期  (如 "2026/Q1")
        holder_id|int|持股人 ID  (可用于其他持股相关协议的 holder_id 过滤)
        name|str|股东名称
        holder_quantity|int|总持股数  (单位：股)
        holder_quantity_change|int|持股变动数  (单位：股；正为增持，负为减持)
        holder_pct|float|持股比例  (百分号前的值，如 12.34 表示 12.34%)
        holder_pct_change|float|持股变动比例  (百分号前的值，如 12.34 表示变动 12.34%；负值为减少)
        holding_date_str|str|持股日期  (格式 YYYY-MM-DD，香港时区)
        close_price|float|持股日期收盘价  (对应持股日期的收盘价（真实价格）)
        price_change_pct|float|价格涨跌幅  (百分号前的值，如 -0.4467 表示 -0.4467%)
        source_group_name|str|数据来源  (持股明细披露信息来源，如 "13F"、"13F数据汇总" 等)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_shareholders_holder_detail("HK.00700", request_type=1000)
if ret == RET_OK:
    print(data[['period_text', 'name', 'holder_quantity', 'holder_pct', 'holder_pct_change']].to_string(index=False))
    print('next_key:', data.attrs.get('next_key', '-1'))
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
period_text                        name  holder_quantity  holder_pct  holder_pct_change
    2026/Q1        Prosus Ventures N.V.       2079512000      23.053             -0.285
    2026/Q1                  Huateng Ma        709859700       7.869              0.000
    2026/Q1                        先锋领航        268596433       2.977              0.031
    2026/Q1                         贝莱德        240834898       2.669              0.088
    2026/Q1                    挪威银行投资管理        122744699       1.360             -0.083
    2026/Q1                     富达管理与研究         86765121       0.961             -0.232
    2026/Q1                        资本集团         85568118       0.948              0.024
    2026/Q1                        摩根大通         62437911       0.692             -0.025
    2026/Q1 E Fund Management Co., Ltd.         52722677       0.584              0.000
    2026/Q1                        柏基投资         35674108       0.395              0.020
next_key: 10
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持港股、美股、新加坡、日本、马来西亚正股及基金。
* 支持分页，默认每页 10 条；分页标识为字符串类型。
:::

---

# 获取机构持股

`get_shareholders_institutional(code, next_key=None, num=None)`

* **介绍**

    获取股票的机构持股人数及持股量历史，支持分页拉取

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码  (如 US.AAPL；支持港股、美股、新加坡、日本、马来西亚正股及基金)
    next_key|str|分页标识  (首次不传，续拉时填上次返回的 next_key；"-1" 表示无更多数据)
    num|int|每页数量  (默认 10，范围 1~50)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回机构持股 DataFrame</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回 DataFrame 字段说明：

        字段|类型|说明
        :-|:-|:-
        period_text|str|报告期  (如 "2026/Q1")
        institution_quantity|int|机构持股家数  (单位：家)
        institution_quantity_change|int|机构家数变动  (单位：家；正为增加，负为减少)
        holder_quantity|int|机构持股总股数  (单位：股)
        holder_quantity_change|int|持股股数变动  (单位：股；正为增持，负为减持)
        holder_pct|float|持股比例  (百分号前的值，如 12.34 表示 12.34%)
        holder_pct_change|float|持股比例变动  (百分号前的值，如 12.34 表示变动 12.34%；负值为减少)
        update_time_str|str|数据更新时间  (格式 YYYY-MM-DD HH:MM:SS，对应市场时区)
        next_key|str|分页标识  ("-1" 表示无更多数据；续拉时原样传入 next_key 参数)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_shareholders_institutional("HK.00700")
if ret == RET_OK:
    print(data[['period_text', 'institution_quantity', 'holder_quantity', 'holder_pct']].to_string(index=False))
    print('next_key:', data.attrs.get('next_key', '-1'))
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
period_text  institution_quantity  holder_quantity  holder_pct
    2026/Q1                   863       4192178205      46.474
    2025/Q4                   873       4195284653      46.444
    2025/Q3                   854       4219387239      46.614
    2025/Q2                   839       4254708217      46.881
    2025/Q1                   809       4236696253      46.491
    2024/Q4                   808       4331865949      47.431
    2024/Q3                   803       4404605110      47.919
    2024/Q2                   846       4438538978      47.926
    2024/Q1                   824       4484844061      48.055
    2023/Q4                   857       4472729401      47.717
next_key: -1
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持港股、美股、新加坡、日本、马来西亚正股及基金。
* 支持分页，默认每页 10 条；分页标识为字符串类型。
:::

---

# 获取内部人持股列表

`get_insider_holder_list(code, next_key=None, num=None)`

* **介绍**

    获取美股股票内部人（高管/董事/大股东）的持股列表，支持分页拉取；首页额外返回内部人统计摘要

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码  (如 US.AAPL；支持美股、新加坡正股及基金)
    next_key|str|分页标识  (首次不传，续拉时填上次返回的 next_key；"-1" 表示无更多数据)
    num|int|每页数量  (默认 10，范围 1~20)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回内部人持股 DataFrame</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回 DataFrame 字段说明：

        字段|类型|说明
        :-|:-|:-
        holder_id|int|股东 ID  (可作为 get_insider_trade_list 和 get_shareholders_holder_detail 的入参)
        holder_quantity|int|总持股数  (单位：股)
        holder_pct|float|持股比例  (百分号前的值，如 12.34 表示 12.34%)
        name|str|股东名称
        title|str|股东职位
        all_count|int|总条数
        next_key|str|分页标识  ("-1" 表示无更多数据；续拉时原样传入 next_key 参数)
        insider_total_count|int|内部人总人数  (仅首页（next_key 为空时）返回)
        insider_bought_count|int|买入人数  (内部人买入总人数；仅首页返回)
        insider_sold_count|int|卖出人数  (内部人卖出总人数；仅首页返回)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_insider_holder_list("US.AAPL")
if ret == RET_OK:
    print(data[['holder_id', 'name', 'title', 'holder_quantity', 'holder_pct']].to_string(index=False))
    print('insider_total:', data['insider_total_count'].iloc[0])
    print('next_key:', data['next_key'].iloc[0])
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
holder_id             name                           title  holder_quantity  holder_pct
    234085  Arthur Levinson                         独立非执行主席          4125576       0.028
    169600     Timothy Cook                           首席执行官          3280418       0.022
 626415138       Sabih Khan                              高管          1105527       0.007
  34123508 Katherine  Adams                           高级副总裁           175408       0.001
 531640091  Deirdre O’Brien Senior Vice President of Retail           136810       0.000
    285767     Ronald Sugar                            独立董事           110566       0.000
  50035778     Luca Maestri                           首席财务官            91304       0.000
    253136      Andrea Jung                            独立董事            77664       0.000
  22072913     Susan Wagner                            独立董事            69788       0.000
1976351584      Ben Borders    Principal Accounting Officer            39987       0.000
insider_total: 17
next_key: 10
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 仅美股、新加坡正股及基金有意义。
* 支持分页，默认每页 10 条，最多 20 条；分页标识为字符串类型。
* 仅首页（首次请求，nextKey 为空）额外返回内部人统计摘要（总人数/买入人数/卖出人数）。
:::

---

# 获取内部人交易

`get_insider_trade_list(code, holder_id=None, num=None, next_key=None)`

* **介绍**

    获取美股股票内部人（高管/董事/大股东）的交易记录列表，支持按持有人过滤和分页续拉

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码  (如 US.AAPL；支持美股、新加坡正股及基金)
    holder_id|int|持有人 ID  (不传则查询全部内部人；可取自 get_insider_holder_list（3241）或本接口返回的 holder_id)
    num|int|每页数量  (默认 10，范围 1~50)
    next_key|str|分页标识  (首次不传，续拉时填上次返回的 next_key；"-1" 表示无更多数据)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回内部人交易 DataFrame</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回 DataFrame 字段说明：

        字段|类型|说明
        :-|:-|:-
        trade_shares|int|交易股数  (正数为买入/获得，负数为卖出)
        min_trade_date|int|最小交易日期时间戳  (Unix 时间戳（秒），对应市场时区)
        min_trade_date_str|str|最小交易日期字符串  (格式 YYYY-MM-DD，对应市场时区)
        max_trade_date|int|最大交易日期时间戳  (Unix 时间戳（秒），对应市场时区)
        max_trade_date_str|str|最大交易日期字符串  (格式 YYYY-MM-DD，对应市场时区)
        min_price|float|最小交易价格
        max_price|float|最大交易价格
        security_holder_quantity|int|证券类型持股数  (交易后的证券持股总数；意向出售等情形下可能为空)
        is_proposed_sale_of_securities|bool|计划出售  (是否为计划出售证券（Form 144 申报）)
        holder_id|int|股东 ID
        name|str|股东名称
        title|str|股东职位
        security_description|str|证券类型描述  (如"普通股")
        transaction_type|str|交易类型  (如"卖出"、"行权获得"、"行权卖出"、"意向出售"等)
        source_group_name|str|数据来源  (如"Form 4"、"Form 144")
        all_count|int|总条数
        next_key|str|分页标识  ("-1" 表示无更多数据；续拉时原样传入 next_key 参数)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_insider_trade_list("US.AAPL")
if ret == RET_OK:
    print(data[['holder_id', 'name', 'title', 'transaction_type', 'trade_shares']].to_string(index=False))
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
holder_id             name                           title transaction_type  trade_shares
    234085  Arthur Levinson                         独立非执行主席               卖出       -250000
    234085  Arthur Levinson                         独立非执行主席             其他处置         -5000
  34123508 Katherine  Adams                           高级副总裁             意向出售        -43000
1892533533     Kevan Parekh                           首席财务官               卖出         -1534
1892533533     Kevan Parekh                           首席财务官             行权获得          6135
1892533533     Kevan Parekh                           首席财务官             行权卖出         -4793
1976351584      Ben Borders    Principal Accounting Officer             行权获得           825
1976351584      Ben Borders    Principal Accounting Officer             行权卖出          -892
    169600     Timothy Cook                           首席执行官             意向出售        -64949
 531640091  Deirdre O’Brien Senior Vice President of Retail             意向出售        -30002
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 仅美股、新加坡正股及基金有意义。
* 支持分页，默认每页 10 条，最多 50 条；分页标识为字符串类型。
* holderId 可取自 GetInsiderHolderList（3241）或本协议（3242）的返回值。
:::

---

# 获取公司概况

`get_company_profile(code)`

* **介绍**

    获取指定股票的公司概况标签列表，包含文本、链接和章节标题等信息

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码  (如 HK.00700；支持正股及基金)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回公司概况 DataFrame</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回 DataFrame 字段说明：

        字段|类型|说明
        :-|:-|:-
        name|str|标签名
        value|str|标签内容
        field_type|[CompanyProfileFieldType](./quote.md#2227)|标签类型  (0=SourceText（普通文本），1=LinkType（链接），2=IndependentTitle（独立章节标题）)

* **Example**

```python
from futu import *
import pandas as pd
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_company_profile("HK.00700")
if ret == RET_OK:
    print(data.to_string(index=False))
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
field_type  name                    value
0           公司代码                00700
0           公司名称                腾讯控股有限公司
0           ISIN代码                KYG875721634
0           上市日期                2004/06/16
0           发行价格                3.70
0           发行数量                4.20亿股
0           成立日期                1999/11/23
0           公司注册地址            开曼群岛
0           董事长                  马化腾
0           审计机构                罗兵咸永道会计师事务所
0           公司类别                境外注册内地个人控制
0           注册办事处              Cricket Square Hutchins Drive, P.O.Box 2681 Grand...
0           总办事处及主要营业地点  香港湾仔皇后大道东1号太古广场三座29楼
0           年结日                  12-31
0           员工数量                115849
0           所属市场                香港主板
0           电话                    (852) 2179-5122
0           传真                    (852) 2520-1148
0           邮箱                    ir@tencent.com
1           网址                    http://www.tencent.com
2           公司业务                Tencent Holdings Ltd是一家主要提供增值(VAS)服务、网络 ...
2           公司简介                腾讯以技术丰富互联网用户的生活。公司旗下社交网络及通讯平台...
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及基金。
:::

---

# 获取高管信息

`get_company_executives(code)`

* **介绍**

    获取指定股票的董事及高管列表，包含展示名称、姓名、职位、任职起始日、发布日期、性别、年龄、学历、年薪等信息

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码  (如 HK.00700；支持正股及基金)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回高管信息 DataFrame</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回 DataFrame 字段说明：

        字段|类型|说明
        :-|:-|:-
        display_leader_name|str|展示名称  (仅用于展示，不用于查询高管背景接口)
        leader_name|str|高管姓名  (可传入 get_company_executive_background 查询背景)
        position_name|str|职位名称
        begin_date|int|任职起始日时间戳（秒）
        begin_date_str|str|任职起始日  (格式 YYYY-MM-DD，对应市场时区)
        leader_gender|str|性别  (如 "Male" / "Female")
        leader_age|str|年龄
        highest_education|str|最高学历
        annual_salary|int|年薪
        issue_date|int|发布日期时间戳（秒）
        issue_date_str|str|发布日期  (格式 YYYY-MM-DD，对应市场时区)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_company_executives("US.AAPL")
if ret == RET_OK:
    print(data[['display_leader_name', 'position_name', 'begin_date_str', 'annual_salary']].to_string(index=False))
    print('count:', len(data))
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
display_leader_name                                                          position_name  begin_date_str  annual_salary
            Timothy D. Cook                                   Director and Chief Executive Officer             NaN     74294811.0
                 Sabih Khan                                                Chief Operating Officer             NaN     27031671.0
               Kevan Parekh                      Chief Financial Officer and Senior Vice President             NaN     22467309.0
                Ben Borders Principal Accounting Officer and Senior Director, Corporate Accounting             NaN            NaN
         Katherine L. Adams                                                  Senior Vice President             NaN     27032248.0
            Deirdre O'Brien                               Senior Vice President, Retail and People             NaN     27047633.0
       Jennifer G. Newstead                   Senior Vice President, General Counsel and Secretary             NaN            NaN
                John Ternus                            Senior Vice President, Hardware Engineering             NaN            NaN
Dr. Arthur D. Levinson, PhD                                                  Chairman of the Board             NaN       557231.0
            Susan L. Wagner                                                   Independent Director             NaN       445373.0
           Monica C. Lozano                                                   Independent Director             NaN       412956.0
                Andrea Jung                                                   Independent Director             NaN       458020.0
                Alex Gorsky                                                   Independent Director             NaN       416492.0
   Dr. Wanda M. Austin, PhD                                                   Independent Director             NaN       412850.0
        Dr. Ronald D. Sugar                                                   Independent Director             NaN       471283.0
count: 15
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及基金。
:::

---

# 获取高管背景

`get_company_executive_background(code, leader_name=None)`

* **介绍**

    获取指定股票某位高管的背景介绍

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码  (如 HK.00700；支持正股及基金)
    leader_name|str|高管姓名  (使用 get_company_executives 返回的 leader_name 字段值)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回高管背景信息 dict</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回 dict 字段说明：

        字段|类型|说明
        :-|:-|:-
        brief_background|str|高管背景简介

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_company_executive_background("US.AAPL", leader_name="Mr. Timothy D. Cook")
if ret == RET_OK:
    print(data)
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
{'brief_background': '2026年4月20日，苹果公司宣布，蒂姆·库克将从首席执行官职位转任苹果董事会执行主席，自2026年9月1日起生效。现年65岁的库克自2011年起担任苹果首席执行官，此前曾于2005年10月至2011年担任苹果首席运营官。库克于1998年3月加入苹果，并于2002年2月至2005年10月担任全球销售与运营执行副总裁。2000年10月至2002年2月，库克担任全球运营、销售、服务与支持高级副总裁。1998年3月至2000年10月，库克担任全球运营高级副总裁。此外，库克还担任美国国家橄榄球基金会暨大学名人堂公司董事会成员、杜克大学校董会成员，以及马拉拉基金领导委员会成员；马拉拉基金是一家倡导女童教育的国际非营利组织。其他上市公司董事会：现任：耐克公司。'}
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及基金。
:::

---

# 获取经营效率

`get_company_operational_efficiency(code, num=None, next_key=None, currency_code=None)`

* **介绍**

    获取指定股票的公司经营效率数据，包括员工人数、人均营收、人均营业利润、人均净利润等指标

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码  (如 HK.00700；支持正股及基金)
    num|int|每页返回数量  (默认 10，范围 1~50)
    next_key|str|分页标识  (首次不传，续拉填上次返回的 next_key；"-1" 表示无更多数据)
    currency_code|str|货币代码  (ISO 4217，如 CNY、USD、HKD、SGD、JPY、CAD、AUD；不传返回默认货币)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回经营效率数据 dict</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回 dict 字段说明：

        字段|类型|说明
        :-|:-|:-
        item_list|list|经营效率列表，每项为 dict，字段见下表
        next_key|str|分页标识  ("-1" 表示无更多数据)
        currency_code|str|货币代码  (ISO 4217)

    * item_list 子项字段：

        字段|类型|说明
        :-|:-|:-
        fiscal_year|int|财务年度  (如 2024)
        financial_type|[F10Type](./quote.md#7710)|财报类型
        period_text|str|财报周期  (如 "2024/Q3"、"2024/FY")
        end_date|int|截止日时间戳（秒级 Unix 时间戳）
        end_date_str|str|截止日字符串  (格式 YYYY-MM-DD，对应市场时区)
        employee_num|int|员工人数
        employee_num_yoy|float|员工人数同比增长率  (百分号前的值，如 12.34 表示 12.34%)
        income_per_capita|float|人均营收
        income_per_capita_yoy|float|人均营收同比增长率  (百分号前的值，如 12.34 表示 12.34%)
        profit_per_capita|float|人均营业利润
        profit_per_capita_yoy|float|人均营业利润同比增长率  (百分号前的值，如 12.34 表示 12.34%)
        net_profit_per_capita|float|人均净利润
        net_profit_per_capita_yoy|float|人均净利润同比增长率  (百分号前的值，如 12.34 表示 12.34%)

* **Example**

```python
from futu import *
import pandas as pd
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_company_operational_efficiency("HK.00700")
if ret == RET_OK:
    df = pd.DataFrame(data.get('item_list', []))
    print(df.to_string(index=False))
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
fiscal_year period_text   end_date end_date_str  employee_num  employee_num_yoy  income_per_capita  income_per_capita_yoy  profit_per_capita  profit_per_capita_yoy  net_profit_per_capita  net_profit_per_capita_yoy
        2025     2025/FY 1767110400   2025-12-31        115849            4.7857       6489188.5126                 8.6594       2085145.3184                10.7787           1983625.2362                    11.6246
        2024     2024/FY 1735574400   2024-12-31        110558            4.8768       5972041.8242                 3.3726       1882260.8947                23.9566           1777049.1506                    58.6906
        2023     2023/FY 1703952000   2023-12-31        105417           -2.7841       5777199.1234                12.9662       1518483.7360                48.5723           1119819.3839                   -35.6529
        2022     2022/FY 1672416000   2022-12-31        108436           -3.8440       5114094.9500                 2.9643       1022049.8727               -57.5666           1740279.9808                   -13.8522
        2021     2021/FY 1640880000   2021-12-31        112771           31.3459       4966862.0478               -11.5377       2408597.9551                12.2453           2020111.5535                     8.3170
        2020     2020/FY 1609344000   2020-12-31         85858           36.5317       5614666.0765                -6.4170       2145833.8186                13.6879           1864998.0199                    22.3097
        2019     2019/FY 1577721600   2019-12-31         62885           15.7911       5999666.0570                 4.2027       1887477.1408                 4.9760           1524815.1387                     3.5346
        2018     2018/FY 1546185600   2018-12-31         54309           21.2362       5757682.8886                 8.4796       1798007.6966               -10.8064           1472757.7381                    -8.9654
        2017     2017/FY 1514649600   2017-12-31         44796           15.5280       5307616.7514                35.4518       2015849.6294                39.2885           1617800.6964                    51.3504
        2016     2016/FY 1483113600   2016-12-31         38775           26.5461       3918452.6112                16.7235       1447246.9374                 9.1517           1068910.3803                    12.5205
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及基金。
:::

---

# 获取十大经纪商买卖数据

`get_top_ten_buy_sell_brokers(code, days_before=None)`

* **介绍**

    获取指定港股的十大净买入和净卖出经纪商列表（实时或历史）

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码  (仅支持港股正股及基金，如 HK.00700)
    days_before|int|历史天数  (不填或 0=实时数据（含均价/总量/总额），>0=取前第 N 个交易日的历史数据（仅含净量和经纪商名称）)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回经纪商数据 DataFrame</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * DataFrame 字段说明：

        字段|类型|说明
        :-|:-|:-
        is_real_time|bool|是否实时数据  (true=实时，false=历史)
        data_time|int|数据更新时间戳（秒级 Unix 时间戳）
        data_time_str|str|数据更新时间字符串  (格式 YYYY-MM-DD HH:MM:SS，对应市场时区)
        net_vol|int|净买卖量  (净买入为正，净卖出为负)
        broker_name|str|经纪商名称  (实时按券商资料填充，历史取回包名称)
        buy_sell_type|[BuySellType](./quote.md#324)|买卖类型
        avg_price|float|成交均价  (仅实时数据有效)
        total_vol|float|总成交量  (仅实时数据有效)
        total_turnover|float|总成交额  (仅实时数据有效)

* **BuySellType 枚举**

    枚举名|值|说明
    :-|:-|:-
    Unknown|0|未知
    NetBuy|1|净买入
    NetSell|2|净卖出

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_top_ten_buy_sell_brokers("HK.00700")
if ret == RET_OK:
    print(data)
else:
    print('error:', data)
quote_ctx.close()
```

* **Output**

```python
net_vol  is_real_time  buy_sell_type  ...   avg_price total_vol total_turnover
0    114300          True              1  ...  466.766498  414900.0    193661420.0
1    104900          True              1  ...  464.678360  104900.0     48744760.0
2     48000          True              1  ...  466.477707   62800.0     29294800.0
3     45500          True              1  ...  466.222815   67500.0     31470040.0
4     38600          True              1  ...  466.795320  162400.0     75807560.0
5     32500          True              1  ...  467.303485  243900.0    113975320.0
6     30900          True              1  ...  465.537217   30900.0     14385100.0
7     15200          True              1  ...  466.788158   15200.0      7095180.0
8     14300          True              1  ...  466.792870   56100.0     26187080.0
9     12300          True              1  ...  466.557724   12300.0      5738660.0
10  -374700          True              2  ...  467.059158  415500.0    194063080.0
11  -236800          True              2  ...  466.795995  509400.0    237785880.0
12  -177900          True              2  ...  466.206225  324500.0    151283920.0
13  -129700          True              2  ...  467.378842  557700.0    260657180.0
14   -90600          True              2  ...  466.713997  267200.0    124705980.0
15   -81800          True              2  ...  466.368293   82000.0     38242200.0
16   -70400          True              2  ...  466.931092   95200.0     44451840.0
17   -47900          True              2  ...  466.453905   65300.0     30459440.0
18   -25300          True              2  ...  466.652174   25300.0     11806300.0
19   -19500          True              2  ...  466.124484   33900.0     15801620.0

[20 rows x 9 columns]
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 仅支持港股正股及基金。
* `days_before=0` 或不填返回实时数据（含均价/总量/总额），`days_before>0` 仅含净量和经纪商名称。
:::

---

# 获取每日卖空成交

`get_daily_short_volume(code, next_key=None, num=None)`

* **介绍**

    获取指定港股或美股的每日卖空成交数据，支持分页续拉

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码  (支持港股、美股正股及基金，如 US.AAPL、HK.00700)
    next_key|str|分页标识  (首次不填，续拉时填上次返回的 next_key；"-1" 表示无更多数据)
    num|int|每页数量  (默认 10，范围 1~50)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td>us_df</td>
            <td>pd.DataFrame</td>
            <td>美股每日卖空数据；当 ret != RET_OK 时为错误描述字符串</td>
        </tr>
        <tr>
            <td>hk_df</td>
            <td>pd.DataFrame</td>
            <td>港股每日卖空数据；当 ret != RET_OK 时为 None</td>
        </tr>
    </table>

    * 美股 DataFrame（us_df）字段说明：

        字段|类型|说明
        :-|:-|:-
        timestamp|int|交易日时间戳（秒级 Unix 时间戳，当日零点）
        timestamp_str|str|交易日字符串  (格式 YYYY-MM-DD，对应市场时区)
        total_shares_short|int|卖空总股数
        nasdaq_shares_short|int|纳斯达克卖空股数
        nyse_shares_short|int|纽交所卖空股数
        short_percent|float|卖空比例  (百分号前的值，如 12.34 表示 12.34%)
        volume|int|成交量（股）
        close_price|float|收盘价
        last_close_price|float|上次收盘价
        daily_trade_avg_ratio|float|日均成交比例  (百分号前的值，如 12.34 表示 12.34%；当前交易日往前 20 个交易日的日均)

    * 美股 us_df.attrs 附加属性：

        属性|类型|说明
        :-|:-|:-
        next_key|str|分页标识  ("-1" 表示无更多数据)

    * 港股 DataFrame（hk_df）字段说明：

        字段|类型|说明
        :-|:-|:-
        timestamp|int|交易日时间戳（秒级 Unix 时间戳，当日零点）
        timestamp_str|str|交易日字符串  (格式 YYYY-MM-DD，对应市场时区)
        shares_traded|int|成交量（股）
        turnover|float|成交额
        short_sell_shares_traded|int|做空成交量（股）
        short_sell_turnover|float|做空成交额
        open_price|float|开盘价
        close_price|float|收盘价
        last_close_price|float|上次收盘价
        daily_trade_avg_ratio|float|日均成交比例  (百分号前的值，如 12.34 表示 12.34%；当前交易日往前 20 个交易日的日均)

    * 港股 hk_df.attrs 附加属性：

        属性|类型|说明
        :-|:-|:-
        next_key|str|分页标识  ("-1" 表示无更多数据)
        aggregated_short|int|未平仓股数  (仅港股)
        aggregated_short_ratio|float|占流通股比例  (百分号前的值，如 12.34 表示 12.34%；仅港股)
        new_time_str|str|最新数据时间  (格式 YYYY-MM-DD，对应市场时区；仅港股)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, us_df, hk_df = quote_ctx.get_daily_short_volume("HK.00700")
if ret == RET_OK:
    print(hk_df)
else:
    print('error:', hk_df)
quote_ctx.close()
```

* **Output**

```python
timestamp timestamp_str  ...  last_close_price  daily_trade_avg_ratio
0  1778169600    2026-05-08  ...             477.4                  11.36
1  1778083200    2026-05-07  ...             463.0                  11.80
2  1777996800    2026-05-06  ...             472.2                  12.22
3  1777910400    2026-05-05  ...             473.0                  12.76
4  1777824000    2026-05-04  ...             467.8                  13.02
5  1777478400    2026-04-30  ...             479.2                  13.09
6  1777392000    2026-04-29  ...             473.8                  14.02
7  1777305600    2026-04-28  ...             478.6                  14.13
8  1777219200    2026-04-27  ...             493.4                  14.14
9  1776960000    2026-04-24  ...             495.2                  14.18

[10 rows x 10 columns]
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持港股、美股正股及基金。
:::

---

# 获取空头持仓

`get_short_interest(code, next_key=None, num=None)`

* **介绍**

    获取指定港股或美股的空头持仓历史记录，支持分页续拉

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|股票代码  (支持港股、美股正股及基金，如 US.AAPL、HK.00700)
    next_key|str|分页标识  (首次不填，续拉时填上次返回的 next_key；"-1" 表示无更多数据)
    num|int|每页数量  (默认 10，范围 1~50)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td>us_df</td>
            <td>pd.DataFrame</td>
            <td>美股空头持仓数据；当 ret != RET_OK 时为错误描述字符串</td>
        </tr>
        <tr>
            <td>hk_df</td>
            <td>pd.DataFrame</td>
            <td>港股空头持仓数据；当 ret != RET_OK 时为 None</td>
        </tr>
    </table>

    * 美股 DataFrame（us_df）字段说明：

        字段|类型|说明
        :-|:-|:-
        timestamp|int|交易日时间戳（秒级 Unix 时间戳，当日零点）
        timestamp_str|str|交易日字符串  (格式 YYYY-MM-DD，对应市场时区)
        shares_short|int|卖空股数
        short_percent|float|卖空比例  (百分号前的值，如 12.34 表示 12.34%)
        avg_daily_share_volume|int|平均日成交量
        days_to_cover|float|回补天数
        close_price|float|收盘价
        last_close_price|float|上次收盘价

    * 美股 us_df.attrs 附加属性：

        属性|类型|说明
        :-|:-|:-
        next_key|str|分页标识  ("-1" 表示无更多数据)

    * 港股 DataFrame（hk_df）字段说明：

        字段|类型|说明
        :-|:-|:-
        timestamp|int|交易日时间戳（秒级 Unix 时间戳，当日零点）
        timestamp_str|str|交易日字符串  (格式 YYYY-MM-DD，对应市场时区)
        close_price|float|收盘价
        last_close_price|float|上次收盘价
        aggregated_short|int|未平仓股数
        aggregated_short_ratio|float|占流通股比例  (百分号前的值，如 12.34 表示 12.34%)

    * 港股 hk_df.attrs 附加属性：

        属性|类型|说明
        :-|:-|:-
        next_key|str|分页标识  ("-1" 表示无更多数据)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, us_df, hk_df = quote_ctx.get_short_interest("HK.00700")
if ret == RET_OK:
    print(hk_df)
else:
    print('error:', hk_df)
quote_ctx.close()
```

* **Output**

```python
   timestamp timestamp_str  aggregated_short  aggregated_short_ratio  close_price  last_close_price
0  1777478400    2026-04-30          51480638                    0.56        467.8             479.2
1  1776960000    2026-04-24          51888755                    0.56        493.4             495.2
2  1776355200    2026-04-17          47974208                    0.52        510.5             517.0
3  1775750400    2026-04-10          48424833                    0.53        504.5             508.5
4  1775059200    2026-04-02          49982828                    0.54        489.2             496.6
5  1774540800    2026-03-27          52744147                    0.57        493.4             495.6
6  1773936000    2026-03-20          51710854                    0.56        508.0             513.0
7  1773331200    2026-03-13          48105325                    0.52        547.5             546.5
8  1772726400    2026-03-06          42404275                    0.46        519.0             502.0
9  1772121600    2026-02-27          36037870                    0.39        518.0             512.0
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持港股、美股正股及基金。
:::

---

# 获取期权链到期日

`get_option_expiration_date(code, index_option_type=IndexOptionType.NORMAL)`

* **介绍**

    通过标的股票，查询期权链的所有到期日。如需获取完整期权链，请配合 [获取期权链](../quote/get-option-chain.md) 接口使用。

* **参数**
    参数|类型|说明
    :-|:-|:-
    code|str|标的股票代码
    index_option_type|[IndexOptionType](../quote/quote.md#5149)|指数期权类型  (仅对港股指数期权筛选有效，正股、ETFs、美股指数期权可忽略此参数)


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回期权链到期日相关数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 期权链到期日数据格式如下：
        字段|类型|说明
        :-|:-|:-
        strike_time|str|期权链行权日  (格式：yyyy-MM-dd
港股和 A 股市场默认是北京时间，美股市场默认是美东时间)
        option_expiry_date_distance|int|距离到期日天数  (负数表示已过期)
        expiration_cycle|[ExpirationCycle](./quote.md#2235)|交割周期  (支持香港指数期权、美股指数期权)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret, data = quote_ctx.get_option_expiration_date(code='HK.00700')
if ret == RET_OK:
    print(data)
    print(data['strike_time'].values.tolist())  # 转为 list
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
  strike_time  option_expiry_date_distance expiration_cycle
0  2021-04-29                            4              N/A
1  2021-05-28                           33              N/A
2  2021-06-29                           65              N/A
3  2021-07-29                           95              N/A
4  2021-09-29                          157              N/A
5  2021-12-30                          249              N/A
6  2022-03-30                          339              N/A
['2021-04-29', '2021-05-28', '2021-06-29', '2021-07-29', '2021-09-29', '2021-12-30', '2022-03-30']
```

:::tip 接口限制
* 每 30 秒内最多请求 60 次获取期权链到期日接口
:::

---

# 获取期权链

`get_option_chain(code, index_option_type=IndexOptionType.NORMAL, start=None, end=None, option_type=OptionType.ALL, option_cond_type=OptionCondType.ALL, data_filter=None)`

* **介绍**

    通过标的股票查询期权链。此接口仅返回期权链的静态信息，如需获取报价或摆盘等动态信息，请用此接口返回的股票代码，自行 [订阅](../quote/sub.md) 所需要的类型。

* **参数**
    参数|类型|说明
    :-|:-|:-
    code|str|标的股票代码
    index_option_type|[IndexOptionType](./quote.md#5149)|指数期权类型  (仅对港股指数期权筛选有效，正股、ETFs、美股指数期权可忽略此参数)
    start|str|开始日期，该日期指到期日  (例如：“2017-08-01”)
    end|str|结束日期（包括这一天），该日期指到期日  (例如：“2017-08-30”)
    option_type|[OptionType](./quote.md#3713)|期权看涨看跌类型  (默认为全部)
    option_cond_type|[OptionCondType](./quote.md#3227)|期权价内外类型  (默认为全部)
    data_filter|OptionDataFilter|数据筛选条件  (默认为不筛选)
    * start 和 end 的组合如下：  
        Start 类型|End 类型|说明
        :-|:-|:-
        str|str|start 和 end 分别为指定的日期
        None|str|start 为 end 往前 30 天
        str|None|end 为 start 往后30天
        None|None|start 为当前日期，end 往后 30 天

    * OptionDataFilter 字段如下
        字段|类型|说明
        :-|:-|:-
        implied_volatility_min|float|隐含波动率过滤起点  (精确到小数点后 0 位，超出部分会被舍弃该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        implied_volatility_max|float|隐含波动率过滤终点  (精确到小数点后 0 位，超出部分会被舍弃该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        delta_min|float|希腊值 Delta 过滤起点  (精确到小数点后 3 位，超出部分会被舍弃)
        delta_max|float|希腊值 Delta 过滤终点  (精确到小数点后 3 位，超出部分会被舍弃)
        gamma_min|float|希腊值 Gamma 过滤起点  (精确到小数点后 3 位，超出部分会被舍弃)
        gamma_max|float|希腊值 Gamma 过滤终点  (精确到小数点后 3 位，超出部分会被舍弃)
        vega_min|float|希腊值 Vega 过滤起点  (精确到小数点后 3 位，超出部分会被舍弃)
        vega_max|float|希腊值 Vega 过滤终点  (精确到小数点后 3 位，超出部分会被舍弃)
        theta_min|float|希腊值 Theta 过滤起点  (精确到小数点后 3 位，超出部分会被舍弃)
        theta_max|float|希腊值 Theta 过滤终点  (精确到小数点后 3 位，超出部分会被舍弃)
        rho_min|float|希腊值 Rho 过滤起点  (精确到小数点后 3 位，超出部分会被舍弃)
        rho_max|float|希腊值 Rho 过滤终点  (精确到小数点后 3 位，超出部分会被舍弃)
        net_open_interest_min|float|净未平仓合约数过滤起点  (精确到小数点后 0 位，超出部分会被舍弃)
        net_open_interest_max|float|净未平仓合约数过滤终点  (精确到小数点后 0 位，超出部分会被舍弃)
        open_interest_min|float|未平仓合约数过滤起点  (精确到小数点后 0 位，超出部分会被舍弃)
        open_interest_max|float|未平仓合约数过滤终点  (精确到小数点后 0 位，超出部分会被舍弃)
        vol_min|float|成交量过滤起点  (精确到小数点后 0 位，超出部分会被舍弃)
        vol_max|float|成交量过滤终点  (精确到小数点后 0 位，超出部分会被舍弃)


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回期权链数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 期权链数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|名字
        lot_size|int|每手股数，期权表示每份合约股数  (指数期权无该字段)
        stock_type|[SecurityType](./quote.md#3325)|股票类型
        option_type|[OptionType](./quote.md#3713)|期权类型
        stock_owner|str|标的股
        strike_time|str|行权日  (格式：yyyy-MM-dd
港股和 A 股市场默认是北京时间，美股市场默认是美东时间)
        strike_price|float|行权价
        suspension|bool|是否停牌  (True：停牌False：未停牌)
        stock_id|int|股票 ID
        index_option_type|[IndexOptionType](./quote.md#5149)|指数期权类型
        expiration_cycle|[ExpirationCycle](./quote.md#2235)|交割周期
        option_standard_type|[OptionStandardType](./quote.md#8952)|期权标准类型
        option_settlement_mode|[OptionSettlementMode](./quote.md#1550)|期权结算方式

* **Example**

```python
from futu import *
import time
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret1, data1 = quote_ctx.get_option_expiration_date(code='HK.00700')

filter1 = OptionDataFilter()
filter1.delta_min = 0
filter1.delta_max = 0.1

if ret1 == RET_OK:
    expiration_date_list = data1['strike_time'].values.tolist()
    for date in expiration_date_list:
        ret2, data2 = quote_ctx.get_option_chain(code='HK.00700', start=date, end=date, data_filter=filter1)
        if ret2 == RET_OK:
            print(data2)
            print(data2['code'][0])  # 取第一条的股票代码
            print(data2['code'].values.tolist())  # 转为 list
        else:
            print('error:', data2)
        time.sleep(3)
else:
    print('error:', data1)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
                     code                 name  lot_size stock_type option_type stock_owner strike_time  strike_price  suspension  stock_id index_option_type expiration_cycle option_standard_type option_settlement_mode
0     HK.TCH210429C350000   腾讯 210429 350.00 购       100       DRVT        CALL    HK.00700  2021-04-29         350.0       False  80235167               N/A        WEEK        STANDARD			N/A        
1     HK.TCH210429P350000   腾讯 210429 350.00 沽       100       DRVT         PUT    HK.00700  2021-04-29         350.0       False  80235247               N/A        WEEK        STANDARD			N/A        
2     HK.TCH210429C360000   腾讯 210429 360.00 购       100       DRVT        CALL    HK.00700  2021-04-29         360.0       False  80235163               N/A        WEEK        STANDARD			N/A        
3     HK.TCH210429P360000   腾讯 210429 360.00 沽       100       DRVT         PUT    HK.00700  2021-04-29         360.0       False  80235246               N/A        WEEK        STANDARD			N/A        
4     HK.TCH210429C370000   腾讯 210429 370.00 购       100       DRVT        CALL    HK.00700  2021-04-29         370.0       False  80235165               N/A        WEEK        STANDARD			N/A        
5     HK.TCH210429P370000   腾讯 210429 370.00 沽       100       DRVT         PUT    HK.00700  2021-04-29         370.0       False  80235248               N/A        WEEK        STANDARD			N/A        
HK.TCH210429C350000
['HK.TCH210429C350000', 'HK.TCH210429P350000', 'HK.TCH210429C360000', 'HK.TCH210429P360000', 'HK.TCH210429C370000', 'HK.TCH210429P370000']
...
                   code                name  lot_size stock_type option_type stock_owner strike_time  strike_price  suspension  stock_id index_option_type expiration_cycle option_standard_type option_settlement_mode
0   HK.TCH220330C490000  腾讯 220330 490.00 购       100       DRVT        CALL    HK.00700  2022-03-30         490.0       False  80235143               N/A        WEEK        STANDARD			N/A            
1   HK.TCH220330P490000  腾讯 220330 490.00 沽       100       DRVT         PUT    HK.00700  2022-03-30         490.0       False  80235193               N/A        WEEK        STANDARD			N/A            
2   HK.TCH220330C500000  腾讯 220330 500.00 购       100       DRVT        CALL    HK.00700  2022-03-30         500.0       False  80233887               N/A        WEEK        STANDARD			N/A            
3   HK.TCH220330P500000  腾讯 220330 500.00 沽       100       DRVT         PUT    HK.00700  2022-03-30         500.0       False  80233912               N/A        WEEK        STANDARD			N/A            
4   HK.TCH220330C510000  腾讯 220330 510.00 购       100       DRVT        CALL    HK.00700  2022-03-30         510.0       False  80233747               N/A        WEEK        STANDARD 			N/A           
5   HK.TCH220330P510000  腾讯 220330 510.00 沽       100       DRVT         PUT    HK.00700  2022-03-30         510.0       False  80233766               N/A        WEEK        STANDARD 			N/A           
HK.TCH220330C490000
['HK.TCH220330C490000', 'HK.TCH220330P490000', 'HK.TCH220330C500000', 'HK.TCH220330P500000', 'HK.TCH220330C510000', 'HK.TCH220330P510000']
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取期权链接口
* 传入的时间跨度上限为 30 天
:::

:::tip 提示
* 此接口不支持查询已过期的期权链，**结束日期** 参数请输入今天或未来的日期
* Open interest (OI) 数据每日更新，更新时点取决于具体交易所。美股期权在盘前时段更新，港股期权在盘后更新。
:::

---

# 获取期权波动率分析

`get_option_volatility(code, query_time_period=None, hv_time_period=None)`

* **介绍**

    获取指定期权合约的隐含波动率、历史波动率及波动率溢价分析

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|期权代码  (仅支持期权合约代码，如 US.AAPL260427C270000)
    query_time_period|[OptionVolatilityTimePeriodType](./quote.md#8366)|查询时间周期  (不填默认 Month（月）)
    hv_time_period|int|历史波动率计算周期（日）  (范围 5~250，默认 30)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时为期权波动率数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * DataFrame 字段说明：

        字段|类型|说明
        :-|:-|:-
        timestamp|int|交易日时间戳（秒级 Unix 时间戳，当日零点）
        timestamp_str|str|交易日字符串  (格式 YYYY-MM-DD，对应市场时区)
        implied_volatility|float|隐含波动率  (百分号前的值，如 25.0 表示 25%)
        history_volatility|float|历史波动率  (标的物历史波动率，百分号前的值，如 25.0 表示 25%)
        volatility_premium|float|波动率溢价  (隐含波动率与历史波动率之差，正值表示隐含高于历史)
        average_impvol|float|隐含波动率均值  (查询周期内隐含波动率均值，百分号前的值)
        impvol_status|[OptionImpvolStatusType](./quote.md#5480)|波动率状态
        analysis|str|分析文案

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, df = quote_ctx.get_option_volatility("US.AAPL281215C320000", query_time_period=2, hv_time_period=30)
if ret == RET_OK:
    cols = ['timestamp_str', 'implied_volatility', 'history_volatility', 'volatility_premium']
    print(df[cols].to_string(index=False))
else:
    print('error:', df)
quote_ctx.close()
```

* **Output**

```
timestamp_str  implied_volatility  history_volatility  volatility_premium
   2026-04-13              27.813              18.977               8.836
   2026-04-14              27.656              18.962               8.694
   2026-04-15              27.726              20.782               6.944
   2026-04-16              28.069              21.013               7.056
   2026-04-17              27.796              22.088               5.708
   2026-04-20              28.054              21.931               6.123
   2026-04-21              27.897              23.194               4.703
   2026-04-22              28.276              24.300               3.976
   2026-04-23              27.951              24.296               3.655
   2026-04-24              28.056              23.676               4.380
   2026-04-27              27.917              22.985               4.932
   2026-04-28              27.942              23.011               4.931
   2026-04-29              28.269              23.022               5.247
   2026-04-30              27.630              22.312               5.318
   2026-05-01              27.576              23.741               3.835
   2026-05-04              27.919              24.078               3.841
   2026-05-05              27.308              24.778               2.530
   2026-05-06              27.746              24.850               2.896
   2026-05-07              28.198              24.886               3.312
   2026-05-08              27.719              25.285               2.434
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 仅支持期权合约代码，不支持正股代码。
:::

---

# 获取期权行权概率

`get_option_exercise_probability(code)`

* **介绍**

    获取指定期权合约的历史行权概率数据，按时间从大到小排序

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|期权代码  (仅支持期权合约代码，如 US.AAPL260427C270000)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时为行权概率数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * DataFrame 字段说明：

        字段|类型|说明
        :-|:-|:-
        timestamp|int|时间戳（秒级 Unix 时间戳）
        timestamp_str|str|日期字符串  (格式 YYYY-MM-DD，对应市场时区)
        security_price|float|正股价格
        strike_probability|float|行权概率  (百分号前的值，如 12.34 表示 12.34%)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, df = quote_ctx.get_option_exercise_probability("US.AAPL281215C320000")
if ret == RET_OK:
    print(df)
else:
    print('error:', df)
quote_ctx.close()
```

* **Output**

```python
timestamp timestamp_str  security_price  strike_probability
0   1778469447    2026-05-10          293.32              41.869
1   1778212800    2026-05-08          293.05              41.887
2   1778126400    2026-05-07          287.17              40.011
3   1778040000    2026-05-06          287.24              40.122
4   1777953600    2026-05-05          283.91              38.956
5   1777867200    2026-05-04          276.56              36.861
6   1777608000    2026-05-01          279.87              37.939
7   1777521600    2026-04-30          271.08              35.189
8   1777435200    2026-04-29          269.90              34.851
9   1777348800    2026-04-28          270.44              35.040
10  1777262400    2026-04-27          267.34              34.094
11  1777003200    2026-04-24          270.79              35.170
12  1776916800    2026-04-23          273.16              35.885
13  1776830400    2026-04-22          272.90              35.805
14  1776744000    2026-04-21          265.90              33.691
15  1776657600    2026-04-20          272.78              35.799
16  1776398400    2026-04-17          269.96              34.964
17  1776312000    2026-04-16          263.13              32.901
18  1776225600    2026-04-15          266.16              33.834
19  1776139200    2026-04-14          258.56              31.536
20  1776052800    2026-04-13          258.93              31.663
21  1775793600    2026-04-10          260.21              32.069
22  1775707200    2026-04-09          260.22              32.086
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 仅支持期权合约代码，不支持正股代码。
:::

---

# 获取期权策略

`get_option_strategy(code, option_strategy, expire_time, spread=None, far_expire_time=None, index_option_type=IndexOptionType.NORMAL, option_type=OptionType.ALL, strike_price=None)`

* **介绍**

    按期权策略类型查询组合腿对应的期权链数据。可用于垂直价差、跨式、领式、蝶式等标准策略的腿筛选。

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|标的股票代码  (如 US.AAPL、HK.00700)
    option_strategy|[OptionStrategyType](./quote.md#2931)|期权策略类型
    expire_time|str|到期日  (格式：yyyy-MM-dd，对应市场时区；日历策略、对角策略必传)
    spread|float|价差  (垂直策略、宽跨式策略、领式策略、蝶式策略、鹰式策略、铁蝶式策略、铁鹰式策略、对角策略必传)
    far_expire_time|str|远端到期日  (格式：yyyy-MM-dd；日历策略、对角策略必传)
    index_option_type|[IndexOptionType](./quote.md#5149)|指数期权类型  (仅对港股指数期权筛选有效)
    option_type|[OptionType](./quote.md#3713)|期权看涨看跌类型  (默认为全部)
    strike_price|float|行权价

    * 部分参数按策略类型必传：

        * **expire_time** 必传策略：`CALENDAR_SPREAD`（日历策略）、`DIAGONAL_SPREAD`（对角策略）
        * **spread** 必传策略：`SPREAD`（垂直策略）、`STRANGLE`（宽跨式策略）、`COLLAR`（领式策略）、`BUTTERFLY`（蝶式策略）、`CONDOR`（鹰式策略）、`IRON_BUTTERFLY`（铁蝶式策略）、`IRON_CONDOR`（铁鹰式策略）、`DIAGONAL_SPREAD`（对角策略）
        * **far_expire_time** 必传策略：`CALENDAR_SPREAD`（日历策略）、`DIAGONAL_SPREAD`（对角策略）

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回策略列表数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * DataFrame 字段说明：

        字段|类型|说明
        :-|:-|:-
        code|str|策略标识代码
        name|str|策略名称
        option_strategy|str|期权策略类型  (如 STRADDLE)
        stock_owner|str|标的股
        legs|list|组合腿列表  (元素为 OptionStrategyLeg)

    * OptionStrategyLeg 字段说明：

        字段|类型|说明
        :-|:-|:-
        code|str|期权合约代码
        action|str|买卖方向  (BUY / SELL)
        quantity|float|数量

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret,data = quote_ctx.get_option_strategy(code='HK.00700', option_strategy=OptionStrategyType.STRADDLE)
if ret == RET_OK:
    print(data)
    print(data['legs'][0])
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
               code     name option_strategy stock_owner                                               legs
0   TCH260522C/P330  腾讯 跨式策略        STRADDLE    HK.00700  [OptionStrategyLeg(code=HK.TCH260522P330000, action=BUY, quantity=1.0), OptionStrategyLeg(code=HK.TCH260522C330000, action=BUY, quantity=1.0)]
1   TCH260522C/P340  腾讯 跨式策略        STRADDLE    HK.00700  [OptionStrategyLeg(code=HK.TCH260522P340000, a...
2   TCH260522C/P350  腾讯 跨式策略        STRADDLE    HK.00700  [OptionStrategyLeg(code=HK.TCH260522P350000, a...
...
26  TCH260522C/P590  腾讯 跨式策略        STRADDLE    HK.00700  [OptionStrategyLeg(code=HK.TCH260522P590000, a...
[OptionStrategyLeg(code=HK.TCH260522P330000, action=BUY, quantity=1.0), OptionStrategyLeg(code=HK.TCH260522C330000, action=BUY, quantity=1.0)]
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
:::

---

# 获取有效价差

`get_option_strategy_spread(code, option_strategy, expire_time, far_expire_time=None, index_option_type=IndexOptionType.NORMAL)`

* **介绍**

    获取指定期权策略在当前标的、到期日条件下可用的有效价差列表。

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|标的股票代码  (如 US.AAPL、HK.00700)
    option_strategy|[OptionStrategyType](./quote.md#2931)|期权策略类型
    expire_time|str|到期日  (格式：yyyy-MM-dd，对应市场时区)
    far_expire_time|str|远端到期日  (对角价差（DiagonalSpread）等策略必传；格式：yyyy-MM-dd)
    index_option_type|[IndexOptionType](./quote.md#5149)|指数期权类型  (仅对港股指数期权筛选有效)

    * option_strategy 仅支持 Spread、Strangle、Collar、Butterfly、Condor、IronButterfly、IronCondor、DiagonalSpread 策略。

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回有效价差列表</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * DataFrame 字段说明：

        字段|类型|说明
        :-|:-|:-
        spread|float|有效价差

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret,data = quote_ctx.get_option_strategy_spread(code='HK.00700', option_strategy=OptionStrategyType.STRANGLE)
if ret == RET_OK:
    print(data)
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
    spread
0     10.0
1     20.0
2     30.0
3     40.0
4     50.0
5     60.0
6     70.0
7     80.0
8     90.0
9    100.0
10   110.0
11   120.0
12   130.0
13   140.0
14   150.0
15   160.0
16   170.0
17   180.0
18   190.0
19   200.0
20   210.0
21   220.0
22   230.0
23   240.0
24   250.0
25   260.0
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
:::

---

# 期权损益分析

`get_option_strategy_analysis(combo_leg_list)`

* **介绍**

    对自定义或多腿期权组合进行损益分析，返回盈亏曲线及相关分析数据。

* **参数**

    参数|类型|说明
    :-|:-|:-
    combo_leg_list|list|组合腿列表  (元素为 OptionStrategyLeg，结构参见 [get_option_strategy](./get-option-strategy.md))

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回期权损益分析结果</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * DataFrame 字段说明：

        字段|类型|说明
        :-|:-|:-
        code|str|策略标识代码
        name|str|策略名称
        option_strategy|str|期权策略类型
        bid1|float|组合买一价
        ask1|float|组合卖一价
        max_profit|float|最大盈利
        max_loss|float|最大亏损
        breakeven_points|list|盈亏平衡点
        prob_of_profit|float|盈利概率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        delta|float|Delta
        theta|float|Theta

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret, data = quote_ctx.get_option_strategy(code='HK.00700', option_strategy=OptionStrategyType.STRADDLE)
if ret == RET_OK:
    index=0
    print(data['legs'][index])
    ret2,data2 = quote_ctx.get_option_strategy_analysis(data['legs'][index])
    if ret2 == RET_OK:
        print(data2)
    else:
        print("get_analysis,error:",data2)
else:
    print('error:', data)

quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
[OptionStrategyLeg(code=HK.TCH260522P330000, action=BUY, quantity=1.0), OptionStrategyLeg(code=HK.TCH260522C330000, action=BUY, quantity=1.0)]
              code     name option_strategy  bid1    ask1    max_profit  max_loss  breakeven_points  prob_of_profit     delta     theta
0  TCH260522C/P330  腾讯 跨式策略        STRADDLE   0.0  130.44  1.000000e+15  -13044.0  [199.56, 460.44]        0.315492  0.974369 -0.785757
```

:::tip 接口限制
* 不占用期权订阅额度。
* 每 30 秒内最多请求 30 次。
:::

---

# 获取期权快照

`get_option_quote(combo_leg_list)`

* **介绍**

    根据组合腿列表获取期权快照行情，适用于多腿策略的批量报价查询。

* **参数**

    参数|类型|说明
    :-|:-|:-
    combo_leg_list|list|组合腿列表  (元素为 OptionStrategyLeg，结构参见 [get_option_strategy](./get-option-strategy.md))

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回期权快照数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * DataFrame 字段说明：

        字段|类型|说明
        :-|:-|:-
        price|float|组合价格
        change_val|float|涨跌额
        change_rate|float|涨跌幅
        volume|str|成交量
        turnover|str|成交额
        high_price|str|最高价
        low_price|str|最低价
        mid_price|str|中间价
        open_price|str|开盘价
        last_close_price|float|昨收价
        open_interest|str|持仓量
        premium|str|溢价
        implied_volatility|str|隐含波动率
        delta|float|Delta
        gamma|float|Gamma
        vega|float|Vega
        theta|float|Theta
        rho|float|Rho
        option_type|str|期权类型
        expire_time|str|到期日
        strike_price|str|行权价
        contract_size|float|合约规模
        contract_multiplier|float|合约乘数
        exercise_type|str|行权方式
        days_to_expiry|int|距到期天数
        net_open_interest|str|净未平仓合约数
        contract_value|str|合约价值
        equal_underlying|str|等价标的
        index_option_type|str|指数期权类型
        intrinsic_value|float|内在价值
        time_value|float|时间价值
        breakeven_point|list|盈亏平衡点
        dist_to_breakeven|list|距盈亏平衡点距离
        prob_of_profit|float|盈利概率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        seller_roi|str|卖方收益率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        mark_price|float|标记价格
        leverage_ratio|str|杠杆比率
        effective_gearing|str|有效杠杆

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret, data = quote_ctx.get_option_strategy(code='HK.00700', option_strategy=OptionStrategyType.STRADDLE)
if ret == RET_OK:
    index=0
    print(data['legs'][index])
    ret2,data2 = quote_ctx.get_option_quote(data['legs'][index])
    if ret2 == RET_OK:
        print(data2)
    else:
        print("get_analysis,error:",data2)
else:
    print('error:', data)

quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
[OptionStrategyLeg(code=HK.TCH260522P330000, action=BUY, quantity=1.0), OptionStrategyLeg(code=HK.TCH260522C330000, action=BUY, quantity=1.0)]
    price  change_val  change_rate volume turnover high_price low_price mid_price open_price  last_close_price open_interest premium implied_volatility     delta     gamma      vega     theta       rho option_type expire_time strike_price  contract_size  contract_multiplier exercise_type  days_to_expiry net_open_interest contract_value equal_underlying index_option_type  intrinsic_value  time_value   breakeven_point             dist_to_breakeven  prob_of_profit seller_roi  mark_price leverage_ratio effective_gearing
0  131.65         0.0          0.0    N/A      N/A        N/A       N/A       N/A        N/A            131.65           N/A     N/A                N/A  0.974369  0.000797  0.019825 -0.785757  0.016246         N/A  2026-05-22          N/A          100.0                100.0           N/A               2               N/A            N/A              N/A               N/A            125.2        6.45  [199.56, 460.44]  [255.64, -5.240000000000009]        0.315418        N/A       130.4            N/A               N/A
```

:::tip 接口限制
* 每 30 秒内最多请求 120 次。
:::

---

# 筛选期权

`get_option_screen(request)`

* **介绍**

    期权选股。混合使用标的属性（underlying）与期权属性（option）进行筛选。同一组内不能同时筛选标的属性（underlying）与期权属性（option），SDK 自动按需开新筛选组：默认每条筛选条件 AND 拼接（开新组），同 indicator_type 显式 `or_with_previous=True` 时与上一条件 OR（同组）。

* **参数**

    参数|类型|说明
    :-|:-|:-
    request|OptionScreenRequest|期权选股请求对象，构造时必传 market_categories

    * OptionScreenRequest 字段：

        字段|类型|说明
        :-|:-|:-
        market_categories|list[int]|期权市场品类列表  (元素取自 OptMarketCategory：US_STOCK=0、US_INDEX=1、US_FUTURE=2、HK_STOCK=3、HK_INDEX=4、JP_STOCK=5、JP_INDEX=6。其中 US_FUTURE / JP_STOCK / JP_INDEX 后续支持，目前结果为空)
        page_from|int|分页起始位置  (不传默认为 0)
        page_count|int|单页最大返回数  (不传默认为 200)

    * 筛选条件 builder 方法（默认每次调用自动开新筛选组与之前条件 AND；同 indicator_type 显式 `or_with_previous=True` 时与上一条件 OR 同组。同一组内不能同时筛选标的属性（underlying）与期权属性（option））：

        方法|说明
        :-|:-
        add_underlying_filter(indicator_type, values=None, lower=None, upper=None, plate_list=None, parent_plate_id=None, or_with_previous=False)|标的属性筛选  (indicator_type 取自 [OptUnderlyingIndicator](./quote.md#6584)。STOCK_LIST 直接传入证券代码字符串（如 "US.AAPL"、"HK.00700"）。IV / HV / IV_RANK / IV_PERCENTILE 等百分数指标传**小数**（30% 传 0.3）。PLATE(103) 类型传入会有报错，暂不要使用)
        add_option_filter(indicator_type, values=None, lower=None, upper=None, or_with_previous=False)|期权属性筛选  (indicator_type 取自 [OptIndicator](./quote.md#6840)。DELTA / GAMMA / VEGA / THETA / RHO / 各类概率（如 ITM_PROBABILITY）传 0~1 小数。PREMIUM(2021) 仅支持 sort / retrieve，作为 filter 会有报错；BUY_BREAK_EVEN_POINT(3023) 已废弃，新代码请用 BUY_TO_BEP(3011))
        new_filter_group()|手动开始新的筛选组  (组间 AND，组内 OR)
        add_sort(indicator_type, desc=False)|排序  (desc=True 为降序，默认升序)
        add_option_retrieve(indicator_type)|声明额外要返回的期权字段  (不调用则返回默认基础字段)
        add_underlying_retrieve(indicator_type)|声明要返回的标的字段  (调用后返回结果中的 underlying dict 字段才会被填充)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>tuple</td>
            <td>当 ret == RET_OK，返回 (last_page, all_count, DataFrame)</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回 DataFrame 字段：

        字段|类型|说明
        :-|:-|:-
        code|str|期权代码
        option_name|str|期权名称
        strike_price|float|行权价
        strike_date|str|行权日
        option_type|int|认购/认沽  (1=CALL，2=PUT)
        exercise_type|int|行权方式  (1=美式，2=欧式)
        expiration_type|int|到期类型  (1=周，2=月，3=季)
        in_the_money|bool|是否价内
        left_day|int|剩余天数
        price|float|期权价格
        mid_price|float|中间价
        bid_price|float|买价
        ask_price|float|卖价
        bid_ask_spread|float|买卖价差
        bid_volume|int|买量
        ask_volume|int|卖量
        bid_ask_volume_ratio|float|买卖量比
        change_ratio|float|涨跌幅
        volume|int|成交量
        turnover|float|成交额
        open_interest|int|未平仓合约数（持仓量）
        open_interest_market_cap|float|持仓市值
        vol_oi_ratio|float|成交量/持仓量
        premium|float|权利金
        implied_volatility|float|隐含波动率
        history_volatility|float|历史波动率
        iv_hv_ratio|float|IV/HV
        delta|float|希腊字母 Delta
        gamma|float|希腊字母 Gamma
        vega|float|希腊字母 Vega
        theta|float|希腊字母 Theta
        rho|float|希腊字母 Rho
        leverage_ratio|float|杠杆比率
        effective_gearing|float|有效杠杆
        itm_probability|float|价内概率
        buy_to_bep|float|买入到盈亏平衡点比率
        sell_to_bep|float|卖出到盈亏平衡点比率
        buy_profit_probability|float|买入盈利概率
        sell_profit_probability|float|卖出盈利概率
        intrinsic_value_per|float|内在价值百分比
        time_value_per|float|时间价值百分比
        itm_degree|float|价内程度
        otm_degree|float|价外程度
        otm_probability|float|价外概率
        sell_annualized_return|float|卖出年化收益率
        interval_return|float|卖出区间收益率
        underlying|dict|标的信息（仅当调用 add_underlying_retrieve 后返回）  (dict 含 stock_id / iv / hv / iv_rank / iv_percentile / market_cap / price / change_ratio)

* **Example**

```python
from futu import (
    OpenQuoteContext, RET_OK, OptionScreenRequest,
    OptMarketCategory, OptIndicator, OptUnderlyingIndicator,
)

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 示例 1：美股标的 IV>30% + 平值附近 CALL
req = OptionScreenRequest(market_categories=[OptMarketCategory.US_STOCK])
req.add_underlying_filter(OptUnderlyingIndicator.IV, lower=0.3)              # 标的 IV ≥ 30%（小数）
req.add_option_filter(OptIndicator.OPTION_TYPE, values=[1])                  # CALL
req.add_option_filter(OptIndicator.DELTA, lower=0.3, upper=0.7)              # Delta 0.3~0.7
req.add_option_filter(OptIndicator.LEFT_DAY, lower=7, upper=60)              # 剩余 7~60 天
req.add_sort(OptIndicator.VOLUME, desc=True)                                 # 成交量降序
req.add_option_retrieve(OptIndicator.DELTA)
req.add_option_retrieve(OptIndicator.VOLUME)
req.page_count = 30

ret, data = quote_ctx.get_option_screen(req)
if ret == RET_OK:
    last_page, all_count, df = data
    print(df[['code', 'option_name', 'delta', 'volume']].head(10))
else:
    print('error: ', data)

# 示例 2：港股按指定标的筛选 + 同时取标的信息
# 注意：STOCK_LIST 直接传入证券代码字符串（如 "HK.00700"、"US.AAPL"）
req = OptionScreenRequest(market_categories=[OptMarketCategory.HK_STOCK])
req.add_underlying_filter(OptUnderlyingIndicator.STOCK_LIST,
                          values=["HK.00700"])                                # 标的=腾讯
req.add_option_filter(OptIndicator.OPTION_TYPE, values=[1])                   # CALL
req.add_option_filter(OptIndicator.OPTION_TYPE, values=[2],
                      or_with_previous=True)                                  # 与上一条 OR：CALL + PUT
req.add_underlying_retrieve(OptUnderlyingIndicator.IV)
req.add_underlying_retrieve(OptUnderlyingIndicator.MARKET_CAP)
req.add_sort(OptIndicator.OPEN_INTEREST, desc=True)                           # 持仓量降序
req.page_count = 50

ret, data = quote_ctx.get_option_screen(req)
if ret == RET_OK:
    last_page, all_count, df = data
    print(df[['code', 'option_name', 'option_type', 'open_interest', 'underlying']].head(10))
else:
    print('error: ', data)

quote_ctx.close()
```

* **Output**

```python
# 示例 1：
                   code          option_name    delta  volume
0      US.GT260717C7000      GT 260717 7.00C  0.33809   38831
1  US.INTC260717C150000  INTC 260717 150.00C  0.30582   19548
2   US.MU260626C1050000   MU 260626 1050.00C  0.43334   18949
3  US.TSLA260710C400000  TSLA 260710 400.00C  0.58114   16002
4  US.CRWV260717C120000  CRWV 260717 120.00C  0.30415   15932
5    US.COMP260717C9000    COMP 260717 9.00C  0.47409   15645
6    US.SLV260717C65500    SLV 260717 65.50C  0.35809   13291
7  US.TSLA260710C410000  TSLA 260710 410.00C  0.50861   13010
8    US.SPCE260717C5000    SPCE 260717 5.00C  0.41268   12701
9  US.HOOD260717C100000  HOOD 260717 100.00C  0.41248   12572

# 示例 2：
                  code         option_name  option_type  open_interest                                         underlying
0  HK.TCH260730C610000  腾讯 260730 610.00 购            1          70474  {'stock_id': 54047868453564, 'iv': 0.36337, 'h...
1  HK.TCH260629C500000  腾讯 260629 500.00 购            1          56334  {'stock_id': 54047868453564, 'iv': 0.36406, 'h...
2  HK.TCH260929C550000  腾讯 260929 550.00 购            1          46470  {'stock_id': 54047868453564, 'iv': 0.36406, 'h...
3  HK.TCH260730C520000  腾讯 260730 520.00 购            1          44071  {'stock_id': 54047868453564, 'iv': 0.36406, 'h...
4  HK.TCH260929C650000  腾讯 260929 650.00 购            1          38316  {'stock_id': 54047868453564, 'iv': 0.36406, 'h...
5  HK.TCH260629C530000  腾讯 260629 530.00 购            1          34532  {'stock_id': 54047868453564, 'iv': 0.36406, 'h...
6  HK.TCH260629C540000  腾讯 260629 540.00 购            1          34085  {'stock_id': 54047868453564, 'iv': 0.36406, 'h...
7  HK.TCH270330P230000  腾讯 270330 230.00 沽            2          30586  {'stock_id': 54047868453564, 'iv': 0.36337, 'h...
8  HK.TCH270330C230000  腾讯 270330 230.00 购            1          30000  {'stock_id': 54047868453564, 'iv': 0.36337, 'h...
9  HK.TCH260629C600000  腾讯 260629 600.00 购            1          27394  {'stock_id': 54047868453564, 'iv': 0.36406, 'h...
```

* **字段逐项示例（按类别）**

    > 以下示例均以 US_STOCK 市场为例：先 `req = OptionScreenRequest(market_categories=[OptMarketCategory.US_STOCK])`，
    > 再叠加每段中的筛选 / 取回 / 排序条件，最后 `quote_ctx.get_option_screen(req)` 取 `(last_page, all_count, df)`。
    > 实测的 `head` 直接取自返回的 DataFrame；标的属性示例的 `underlying.<field>` 列由 `add_underlying_retrieve(...)` 展开得到。

    #### 标的属性 OptUnderlyingIndicator

    通过 `add_underlying_filter(indicator_type, lower, upper, values, ...)` 传入；IV/HV/IV_RANK 等百分数指标 **传小数**（30% 传 0.3），并需 `add_underlying_retrieve(...)` 才能在 `underlying` dict 中看到值

    ##### `IV`（id=203 · interval · OptUnderlyingIndicator） 标的隐含波动率

    单位：% ；SDK 直传小数（30% 传 0.3）。需 add_underlying_retrieve 才能在 underlying dict 里看到值

    ```python
    req.add_underlying_filter(OptUnderlyingIndicator.IV, lower=0.3)
    req.add_underlying_retrieve(OptUnderlyingIndicator.IV)
    req.add_sort(OptIndicator.VOLUME, desc=True)
    ```

    实测返回（US_STOCK · all_count=1456207、命中 10 行、head 前 5）：

    ```
                    code          option_name  volume  underlying.iv
    US.NVDA260612C205000  NVDA 260612 205.00C  226041        0.45135
    US.NVDA260612P200000  NVDA 260612 200.00P  184565        0.45135
    US.NVDA260612C202500  NVDA 260612 202.50C  163991        0.45135
    US.NVDA260612C210000  NVDA 260612 210.00C  147236        0.45135
    US.NVDA260612C207500  NVDA 260612 207.50C  143944        0.45135
    ```

    ##### `HV`（id=204 · interval · OptUnderlyingIndicator） 标的历史波动率

    单位：% ；SDK 直传小数

    ```python
    req.add_underlying_filter(OptUnderlyingIndicator.HV, lower=0.3)
    req.add_underlying_retrieve(OptUnderlyingIndicator.HV)
    req.add_sort(OptIndicator.VOLUME, desc=True)
    ```

    实测返回（US_STOCK · all_count=1336194、命中 10 行、head 前 5）：

    ```
                    code          option_name  volume  underlying.hv
    US.NVDA260612C205000  NVDA 260612 205.00C  226041        0.46845
    US.NVDA260612P200000  NVDA 260612 200.00P  184565        0.46845
    US.NVDA260612C202500  NVDA 260612 202.50C  163991        0.46845
    US.NVDA260612C210000  NVDA 260612 210.00C  147236        0.46845
    US.NVDA260612C207500  NVDA 260612 207.50C  143944        0.46845
    ```

    ##### `IV_RANK`（id=205 · interval · OptUnderlyingIndicator） 标的 IV 历史排名

    0~100；衡量当前 IV 在历史中的相对位置

    ```python
    req.add_underlying_filter(OptUnderlyingIndicator.IV_RANK, lower=50.0)
    req.add_underlying_retrieve(OptUnderlyingIndicator.IV_RANK)
    req.add_sort(OptIndicator.VOLUME, desc=True)
    ```

    实测返回（US_STOCK · all_count=0、命中 0 行）：无数据。原因：OpenD 抽样无数据，可降低 lower 阈值

    ##### `MARKET_CAP`（id=401 · interval · OptUnderlyingIndicator） 标的总市值

    单位：元；SDK 直传原始值（百亿写 10_000_000_000）

    ```python
    req.add_underlying_filter(OptUnderlyingIndicator.MARKET_CAP, lower=100_000_000_000.0)
    req.add_underlying_retrieve(OptUnderlyingIndicator.MARKET_CAP)
    req.add_sort(OptIndicator.VOLUME, desc=True)
    ```

    实测返回（US_STOCK · all_count=357921、命中 10 行、head 前 5）：

    ```
                    code          option_name  volume  underlying.market_cap
    US.NVDA260612C205000  NVDA 260612 205.00C  226041        4957854000000.0
    US.NVDA260612P200000  NVDA 260612 200.00P  184565        4957854000000.0
    US.NVDA260612C202500  NVDA 260612 202.50C  163991        4957854000000.0
    US.NVDA260612C210000  NVDA 260612 210.00C  147236        4957854000000.0
    US.NVDA260612C207500  NVDA 260612 207.50C  143944        4957854000000.0
    ```

    ##### `STOCK_PRICE`（id=402 · interval · OptUnderlyingIndicator） 标的价

    单位：元；SDK 直传原始价

    ```python
    req.add_underlying_filter(OptUnderlyingIndicator.STOCK_PRICE, lower=50.0, upper=500.0)
    req.add_underlying_retrieve(OptUnderlyingIndicator.STOCK_PRICE)
    req.add_sort(OptIndicator.VOLUME, desc=True)
    ```

    实测返回（US_STOCK · all_count=1055665、命中 10 行、head 前 5）：

    ```
                    code          option_name  volume  underlying.price
    US.NVDA260612C205000  NVDA 260612 205.00C  226041            204.87
    US.NVDA260612P200000  NVDA 260612 200.00P  184565            204.87
    US.NVDA260612C202500  NVDA 260612 202.50C  163991            204.87
    US.NVDA260612C210000  NVDA 260612 210.00C  147236            204.87
    US.NVDA260612C207500  NVDA 260612 207.50C  143944            204.87
    ```

    #### 期权属性 OptIndicator

    通过 `add_option_filter(indicator_type, lower, upper, values, ...)` 传入；Greeks（DELTA/GAMMA/THETA/VEGA/RHO）与各类概率（ITM_PROBABILITY 等）**传 0~1 小数**

    ##### `STRIKE_PRICE`（id=1001 · interval · OptIndicator） 行权价

    单位：元；SDK 直传原始价

    ```python
    req.add_option_filter(OptIndicator.STRIKE_PRICE, lower=50.0, upper=100.0)
    req.add_sort(OptIndicator.VOLUME, desc=True)
    ```

    实测返回（US_STOCK · all_count=400354、命中 10 行、head 前 5）：

    ```
                   code         option_name  strike_price  volume
     US.HYG260717P75000   HYG 260717 75.00P          75.0   72679
     US.BAC260618C55000   BAC 260618 55.00C          55.0   55636
    US.TQQQ260612P72000  TQQQ 260612 72.00P          72.0   43326
     US.IEF260618C95000   IEF 260618 95.00C          95.0   42077
     US.HYG260918P75000   HYG 260918 75.00P          75.0   42012
    ```

    ##### `LEFT_DAY`（id=1002 · interval · OptIndicator） 剩余天数

    单位：天；整数；近月通常 < 30

    ```python
    req.add_option_filter(OptIndicator.LEFT_DAY, lower=7, upper=60)
    req.add_sort(OptIndicator.VOLUME, desc=True)
    ```

    实测返回（US_STOCK · all_count=553649、命中 10 行、head 前 5）：

    ```
                   code         option_name  left_day  volume
     US.HYG260717P75000   HYG 260717 75.00P        35   72679
    US.POET260717P17000  POET 260717 17.00P        35   60754
     US.HYG260717P78000   HYG 260717 78.00P        35   40594
     US.HYG260717P79000   HYG 260717 79.00P        35   34919
     US.IEF260717P93000   IEF 260717 93.00P        35   34807
    ```

    ##### `OPTION_TYPE`（id=1003 · values · OptIndicator） 认购/认沽

    枚举：1=CALL、2=PUT；values 传枚举列表

    ```python
    req.add_option_filter(OptIndicator.OPTION_TYPE, values=[1])  # CALL
    req.add_sort(OptIndicator.VOLUME, desc=True)
    ```

    实测返回（US_STOCK · all_count=972181、命中 10 行、head 前 5）：

    ```
                    code          option_name  option_type  volume
    US.NVDA260612C205000  NVDA 260612 205.00C            1  226041
    US.NVDA260612C202500  NVDA 260612 202.50C            1  163991
    US.NVDA260612C210000  NVDA 260612 210.00C            1  147236
    US.NVDA260612C207500  NVDA 260612 207.50C            1  143944
     US.SPY260612C740000   SPY 260612 740.00C            1  114906
    ```

    ##### `IN_THE_MONEY`（id=2001 · values · OptIndicator） 是否价内

    枚举：1=价内、0=价外

    ```python
    req.add_option_filter(OptIndicator.IN_THE_MONEY, values=[1])  # 仅价内
    req.add_sort(OptIndicator.VOLUME, desc=True)
    ```

    实测返回（US_STOCK · all_count=972389、命中 10 行、head 前 5）：

    ```
                    code          option_name  in_the_money  volume
    US.NVDA260612C202500  NVDA 260612 202.50C             1  163991
    US.AAPL260612C295000  AAPL 260612 295.00C             1   87879
     US.SPY260612C735000   SPY 260612 735.00C             1   77126
    US.TSLA260612C390000  TSLA 260612 390.00C             1   70408
     US.SPY260612C730000   SPY 260612 730.00C             1   62881
    ```

    ##### `PRICE`（id=2002 · interval · OptIndicator） 期权价

    单位：元；SDK 直传原始价

    ```python
    req.add_option_filter(OptIndicator.PRICE, lower=1.0, upper=10.0)
    req.add_sort(OptIndicator.VOLUME, desc=True)
    ```

    实测返回（US_STOCK · all_count=644732、命中 10 行、head 前 5）：

    ```
                    code          option_name  price  volume
    US.NVDA260612C205000  NVDA 260612 205.00C    2.0  226041
    US.NVDA260612C202500  NVDA 260612 202.50C   3.55  163991
    US.NVDA260612C207500  NVDA 260612 207.50C   1.04  143944
     US.SPY260612C740000   SPY 260612 740.00C   2.97  114906
    US.TSLA260612C400000  TSLA 260612 400.00C   6.45   93756
    ```

    ##### `VOLUME`（id=2011 · interval · OptIndicator） 成交量

    单位：张

    ```python
    req.add_option_filter(OptIndicator.VOLUME, lower=1000)
    req.add_sort(OptIndicator.VOLUME, desc=True)
    ```

    实测返回（US_STOCK · all_count=8010、命中 10 行、head 前 5）：

    ```
                    code          option_name  volume
    US.NVDA260612C205000  NVDA 260612 205.00C  226041
    US.NVDA260612P200000  NVDA 260612 200.00P  184565
    US.NVDA260612C202500  NVDA 260612 202.50C  163991
    US.NVDA260612C210000  NVDA 260612 210.00C  147236
    US.NVDA260612C207500  NVDA 260612 207.50C  143944
    ```

    ##### `OPEN_INTEREST`（id=2013 · interval · OptIndicator） 未平仓合约数

    单位：张

    ```python
    req.add_option_filter(OptIndicator.OPEN_INTEREST, lower=1000)
    req.add_sort(OptIndicator.OPEN_INTEREST, desc=True)
    ```

    实测返回（US_STOCK · all_count=92911、命中 10 行、head 前 5）：

    ```
                   code         option_name  open_interest
     US.HYG260618P79000   HYG 260618 79.00P         451310
    US.BKLN260717P20000  BKLN 260717 20.00P         406177
     US.HYG261120C81000   HYG 261120 81.00C         386200
     US.HYG260618P77000   HYG 260618 77.00P         332022
     US.HYG260618P75000   HYG 260618 75.00P         324096
    ```

    ##### `IMPLIED_VOLATILITY`（id=3001 · interval · OptIndicator） 隐含波动率

    单位：% ；SDK 直传小数（50% 传 0.5）

    ```python
    req.add_option_filter(OptIndicator.IMPLIED_VOLATILITY, lower=0.3)
    req.add_sort(OptIndicator.VOLUME, desc=True)
    ```

    实测返回（US_STOCK · all_count=1480382、命中 10 行、head 前 5）：

    ```
                    code          option_name  implied_volatility  volume
    US.NVDA260612C205000  NVDA 260612 205.00C             0.70232  226041
    US.NVDA260612P200000  NVDA 260612 200.00P             0.77927  184565
    US.NVDA260612C202500  NVDA 260612 202.50C             0.72661  163991
    US.NVDA260612C210000  NVDA 260612 210.00C             0.76536  147236
    US.NVDA260612C207500  NVDA 260612 207.50C             0.72576  143944
    ```

    ##### `DELTA`（id=3004 · interval · OptIndicator） 希腊字母 Delta

    CALL∈[0,1]、PUT∈[-1,0]；SDK 直传小数

    ```python
    req.add_option_filter(OptIndicator.DELTA, lower=0.3, upper=0.7)
    req.add_sort(OptIndicator.VOLUME, desc=True)
    ```

    实测返回（US_STOCK · all_count=219233、命中 10 行、head 前 5）：

    ```
                    code          option_name    delta  volume
    US.NVDA260612C205000  NVDA 260612 205.00C  0.49538  226041
    US.NVDA260612C202500  NVDA 260612 202.50C  0.68114  163991
    US.NVDA260612C207500  NVDA 260612 207.50C  0.31335  143944
     US.SPY260612C740000   SPY 260612 740.00C  0.45037  114906
    US.TSLA260612C400000  TSLA 260612 400.00C  0.48887   93756
    ```

    ##### `GAMMA`（id=3005 · interval · OptIndicator） 希腊字母 Gamma

    ≥0；SDK 直传小数

    ```python
    req.add_option_filter(OptIndicator.GAMMA, lower=0.01)
    req.add_sort(OptIndicator.VOLUME, desc=True)
    ```

    实测返回（US_STOCK · all_count=810281、命中 10 行、head 前 5）：

    ```
                    code          option_name    gamma  volume
    US.NVDA260612C205000  NVDA 260612 205.00C  0.07901  226041
    US.NVDA260612P200000  NVDA 260612 200.00P   0.0477  184565
    US.NVDA260612C202500  NVDA 260612 202.50C  0.06835  163991
    US.NVDA260612C210000  NVDA 260612 210.00C   0.0481  147236
    US.NVDA260612C207500  NVDA 260612 207.50C  0.06793  143944
    ```

    ##### `THETA`（id=3007 · interval · OptIndicator） 希腊字母 Theta

    一般 ≤0（时间衰减），SDK 直传小数

    ```python
    req.add_option_filter(OptIndicator.THETA, upper=-0.01)
    req.add_sort(OptIndicator.VOLUME, desc=True)
    ```

    实测返回（US_STOCK · all_count=1238755、命中 10 行、head 前 5）：

    ```
                    code          option_name     theta  volume
    US.NVDA260612C205000  NVDA 260612 205.00C  -2.30979  226041
    US.NVDA260612P200000  NVDA 260612 200.00P  -1.67055  184565
    US.NVDA260612C202500  NVDA 260612 202.50C  -2.13163  163991
    US.NVDA260612C210000  NVDA 260612 210.00C  -1.62903  147236
    US.NVDA260612C207500  NVDA 260612 207.50C  -2.10361  143944
    ```

    ##### `ITM_PROBABILITY`（id=3019 · interval · OptIndicator） 价内概率

    0~1 小数；SDK 直传

    ```python
    req.add_option_filter(OptIndicator.ITM_PROBABILITY, lower=0.3, upper=0.7)
    req.add_sort(OptIndicator.VOLUME, desc=True)
    ```

    实测返回（US_STOCK · all_count=417899、命中 10 行、head 前 5）：

    ```
                    code          option_name  itm_probability  volume
    US.NVDA260612C205000  NVDA 260612 205.00C          0.48389  226041
     US.SPY260612C740000   SPY 260612 740.00C          0.36646  114906
    US.TSLA260612C400000  TSLA 260612 400.00C          0.46733   93756
    US.AAPL260612C295000  AAPL 260612 295.00C          0.57372   87879
     US.SPY260612C735000   SPY 260612 735.00C          0.66411   77126
    ```

:::tip 接口限制
* 每 30 秒内最多请求 10 次筛选期权接口
:::

---

# 期权市场统计

`get_option_market_statistic(option_market, data_type, begin_time=None, end_time=None, page_req_key=None)`

* **介绍**

    获取期权市场统计数据（成交量/持仓量），按交易日粒度返回看涨、看跌及合计值，支持分页拉取。

* **参数**

    参数|类型|说明
    :-|:-|:-
    option_market|[OptionMarket](./quote.md#5579)|期权市场类型  (US_SECURITY=美股股票期权、US_INDEX=美股指数期权、HK_SECURITY=港股股票期权、HK_INDEX=港股指数期权)
    data_type|[OptionStatisticDataType](./quote.md#4742)|数据类型  (VOLUME=成交量、OPEN_INTEREST=持仓量)
    begin_time|str|开始日期，格式 'YYYY-MM-DD'  (不传默认取近一年数据)
    end_time|str|结束日期，格式 'YYYY-MM-DD'  (与 begin_time 跨度不超过一年)
    page_req_key|bytes|分页请求 key  (首次传 None，续拉传上次返回值)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pandas.DataFrame</td>
            <td>当 ret == RET_OK，返回统计数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
        <tr>
            <td>page_req_key</td>
            <td>bytes</td>
            <td>下一页 key，None 表示无更多数据</td>
        </tr>
    </table>

    * 返回 DataFrame 字段：

        字段|类型|说明
        :-|:-|:-
        time|str|交易日时间字符串
        timestamp|float|交易日时间戳（Unix 秒）
        call_value|int|看涨期权合计值
        put_value|int|看跌期权合计值
        total_value|int|总值（call_value + put_value）
        ratio|float|Put/Call 比值  (call_value 为 0 时为 N/A)

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data, page_req_key = quote_ctx.get_option_market_statistic(
    OptionMarket.US_SECURITY,
    OptionStatisticDataType.VOLUME,
    begin_time='2026-06-01',
    end_time='2026-06-15'
)
if ret == RET_OK:
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
         time     timestamp  call_value  put_value  total_value     ratio
0  2026-06-12  1.781237e+09    45658870   28723978     74382848  0.629100
1  2026-06-11  1.781150e+09    38303062   30520043     68823105  0.796804
2  2026-06-10  1.781064e+09    35371830   30180004     65551834  0.853221
3  2026-06-09  1.780978e+09    42880655   36646152     79526807  0.854608
4  2026-06-08  1.780891e+09    35442266   25811533     61253799  0.728270
5  2026-06-05  1.780632e+09    52362998   44023321     96386319  0.840733
6  2026-06-04  1.780546e+09    38082169   24572137     62654306  0.645240
7  2026-06-03  1.780459e+09    36858233   23035404     59893637  0.624973
8  2026-06-02  1.780373e+09    36822706   21026201     57848907  0.571012
9  2026-06-01  1.780286e+09    42932185   24084036     67016221  0.560979
```

:::tip 接口限制
* 30 秒内最多请求 60 次期权市场统计接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 期权标的总览

`get_option_underlying_overview(code_list, index_option_type=IndexOptionType.NORMAL)`

* **介绍**

    批量获取期权标的总览数据，包含成交量、持仓量、隐含波动率（IV）及多周期历史波动率（HV）等核心指标的最新快照。

* **参数**

    参数|类型|说明
    :-|:-|:-
    code_list|list[str]|标的股票代码列表  (如 ['US.AAPL', 'US.TSLA']，最多 500 个)
    index_option_type|[IndexOptionType](./quote.md#5149)|指数期权类型  (NORMAL=普通期权（默认）、SMALL=小型指数期权，仅恒指/国指需要)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pandas.DataFrame</td>
            <td>当 ret == RET_OK，返回标的总览数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回 DataFrame 字段：

        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|标的名称
        call_volume|int|看涨期权成交量
        put_volume|int|看跌期权成交量
        call_open_interest|int|看涨期权持仓量（T-1 延迟）
        put_open_interest|int|看跌期权持仓量（T-1 延迟）
        iv|float|隐含波动率（百分比）
        iv_rank|float|IV 排名百分位（百分比）
        iv_percentile|float|IV 百分位（百分比）
        pre_iv|float|前一交易日 IV（百分比）
        hv_30d|float|30 日历史波动率（百分比）
        hv_30d_percentile|float|30 日 HV 百分位
        hv_60d|float|60 日历史波动率（百分比）
        hv_60d_percentile|float|60 日 HV 百分位
        hv_90d|float|90 日历史波动率（百分比）
        hv_90d_percentile|float|90 日 HV 百分位
        hv_120d|float|120 日历史波动率（百分比）
        hv_120d_percentile|float|120 日 HV 百分位
        hv_365d|float|365 日历史波动率（百分比）
        hv_365d_percentile|float|365 日 HV 百分位

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_option_underlying_overview(['US.AAPL', 'US.TSLA', 'US.NVDA'])
if ret == RET_OK:
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
      code  name  call_volume  put_volume  call_open_interest  put_open_interest      iv  iv_rank  iv_percentile  pre_iv  hv_30d  hv_30d_percentile  hv_60d  hv_60d_percentile  hv_90d  hv_90d_percentile  hv_120d  hv_120d_percentile  hv_365d  hv_365d_percentile
0  US.AAPL  Apple       782941      490299             3165108            2237950  25.126   37.702         19.841  25.617  23.324             59.126  24.641             65.476  23.019             46.825   23.582              47.619   22.619               8.333
1  US.TSLA  Tesla      2197764     1425740             4178685            2909774  55.053   39.265         64.285  55.401  49.359             68.254  46.536             58.730  44.990             46.031   41.688              29.761   44.500               1.190
2  US.NVDA  NVIDIA     1980405     1176926             9096278            7648683  41.975   27.062         42.460  45.135  45.921             96.825  42.646             99.206  39.980             92.460   38.971              81.746   34.989              17.063
```

:::tip 接口限制
* 30 秒内最多请求 60 次期权标的总览接口
:::

---

# 期权标的历史统计

`get_option_underlying_his_statistic(code, index_option_type=IndexOptionType.NORMAL, begin_time=None, end_time=None, page_req_key=None)`

* **介绍**

    获取期权标的历史统计数据，按交易日返回该标的对应期权的成交量、持仓量及 Put/Call 比率时间序列，支持分页。

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|标的股票代码  (如 'US.AAPL')
    index_option_type|[IndexOptionType](./quote.md#5149)|指数期权类型  (NORMAL=普通期权（默认）、SMALL=小型指数期权)
    begin_time|str|开始日期，格式 'YYYY-MM-DD'  (不传默认 end_time 往前推 364 天)
    end_time|str|结束日期，格式 'YYYY-MM-DD'  (与 begin_time 跨度最多 364 天)
    page_req_key|bytes|分页请求 key  (首次传 None，续拉传上次返回值)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pandas.DataFrame</td>
            <td>当 ret == RET_OK，返回统计数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
        <tr>
            <td>page_req_key</td>
            <td>bytes</td>
            <td>下一页 key，None 表示无更多数据</td>
        </tr>
    </table>

    * 返回 DataFrame 字段：

        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        time|str|交易日时间字符串
        timestamp|float|交易日时间戳（Unix 秒）
        option_volume|int|期权总成交量（call_volume + put_volume）
        call_volume|int|看涨期权成交量
        put_volume|int|看跌期权成交量
        put_call_volume_ratio|float|Put/Call 成交量比
        option_open_interest|int|期权总持仓量
        call_open_interest|int|看涨期权持仓量（T-1 延迟）
        put_open_interest|int|看跌期权持仓量（T-1 延迟）
        put_call_open_interest_ratio|float|Put/Call 持仓量比
        underlying_price|float|标的价格

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data, page_req_key = quote_ctx.get_option_underlying_his_statistic(
    'US.AAPL',
    begin_time='2026-06-01',
    end_time='2026-06-15'
)
if ret == RET_OK:
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
      code  name        time     timestamp  option_volume  call_volume  put_volume  put_call_volume_ratio  option_open_interest  call_open_interest  put_open_interest put_call_open_interest_ratio  underlying_price
0  US.AAPL  Apple  2026-06-12  1.781237e+09        1273240       782941      490299               0.626227                     0                   0                  0                          N/A            291.13
1  US.AAPL  Apple  2026-06-11  1.781150e+09         950737       580535      370202               0.637691               5403058             3165108            2237950                     0.707069            295.63
2  US.AAPL  Apple  2026-06-10  1.781064e+09        1734799      1039630      695169               0.668670               5522747             3270454            2252293                     0.688679            291.58
3  US.AAPL  Apple  2026-06-09  1.780978e+09        1715749      1024046      691703               0.675461               5405022             3209586            2195436                     0.684025            290.55
4  US.AAPL  Apple  2026-06-08  1.780891e+09        2179789      1293656      886133               0.684983               5350402             3142828            2207574                     0.702416            301.54
...
```

:::tip 接口限制
* 30 秒内最多请求 60 次期权标的历史统计接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 期权标的历史波动率

`get_option_underlying_his_volatility(code, index_option_type=IndexOptionType.NORMAL, begin_time=None, end_time=None, page_req_key=None)`

* **介绍**

    获取期权标的历史波动率数据，按交易日返回 IV 和 HV 时间序列及标的收盘价，支持分页。

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|标的股票代码  (如 'US.AAPL')
    index_option_type|[IndexOptionType](./quote.md#5149)|指数期权类型  (NORMAL=普通期权（默认）、SMALL=小型指数期权)
    begin_time|str|开始日期，格式 'YYYY-MM-DD'
    end_time|str|结束日期，格式 'YYYY-MM-DD'
    page_req_key|bytes|分页请求 key  (首次传 None，续拉传上次返回值)

    :::tip 时间范围说明
    - `begin_time` 与 `end_time` 跨度最多 **364 天**
    - 两者都不填：`end_time` = 当天，`begin_time` = 当天往前推 364 天
    - 只填 `begin_time`：`end_time` = `begin_time` 往后推 364 天
    - 只填 `end_time`：`begin_time` = `end_time` 往前推 364 天
    :::

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pandas.DataFrame</td>
            <td>当 ret == RET_OK，返回波动率数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
        <tr>
            <td>page_req_key</td>
            <td>bytes</td>
            <td>下一页 key，None 表示无更多数据</td>
        </tr>
    </table>

    * 返回 DataFrame 字段：

        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        time|str|交易日时间字符串
        timestamp|float|交易日时间戳（Unix 秒）
        iv|float|隐含波动率（百分比）
        hv|float|历史波动率（百分比）
        underlying_price|float|标的收盘价（当日为标记价）

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data, page_req_key = quote_ctx.get_option_underlying_his_volatility(
    'US.AAPL',
    begin_time='2026-06-01',
    end_time='2026-06-15'
)
if ret == RET_OK:
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
      code  name        time     timestamp      iv      hv  underlying_price
0  US.AAPL  Apple  2026-06-12  1.781237e+09  25.126  23.324            291.13
1  US.AAPL  Apple  2026-06-11  1.781150e+09  25.617  23.270            295.63
2  US.AAPL  Apple  2026-06-10  1.781064e+09  27.384  22.892            291.58
3  US.AAPL  Apple  2026-06-09  1.780978e+09  27.237  22.854            290.55
4  US.AAPL  Apple  2026-06-08  1.780891e+09  26.368  19.028            301.54
5  US.AAPL  Apple  2026-06-05  1.780632e+09  26.995  18.024            307.34
6  US.AAPL  Apple  2026-06-04  1.780546e+09  25.249  17.366            311.23
7  US.AAPL  Apple  2026-06-03  1.780459e+09  26.801  18.927            310.26
8  US.AAPL  Apple  2026-06-02  1.780373e+09  26.258  18.415            315.20
9  US.AAPL  Apple  2026-06-01  1.780286e+09  25.864  16.841            306.31
```

:::tip 接口限制
* 30 秒内最多请求 60 次期权标的历史波动率接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 期权标的排行

`get_option_underlying_rank(option_market, sort_type, sort_direction=None, count=None, trading_date=None, filter_list=None, page=None)`

* **介绍**

    获取期权热门标的排行，按指定维度对期权标的（正股/ETF/指数）进行排名，支持多维度筛选与分页。

* **参数**

    参数|类型|说明
    :-|:-|:-
    option_market|[OptionMarket](./quote.md#5579)|期权市场类型  (US_SECURITY=美股股票期权、US_INDEX=美股指数期权、HK_SECURITY=港股股票期权、HK_INDEX=港股指数期权)
    sort_type|[UnderlyingRankSortType](./quote.md#8375)|排序字段  (VOLUME=总成交量、VOLUME_RATIO=Put/Call成交量比值、OPEN_INTEREST=总持仓量、OPEN_INTEREST_RATIO=Put/Call持仓量比值、PRICE=最新价、PRICE_CHANGE=涨跌幅、IV=IV、IV_CHANGE=IV变化率、HV=HV、HV_CHANGE=HV变化率、IV_RANK=IV Rank、IV_PERCENTILE=IV Percentile、MARKET_CAP=市值)
    sort_direction|int|排序方向  (0=降序（默认）、1=升序)
    count|int|每页数量  (范围 [1,200]，默认 200)
    trading_date|str|交易日  (格式 yyyy-MM-dd，不填返回最新排行)
    filter_list|list[UnderlyingRankFilter]|筛选条件列表  (多条件为 AND 关系)
    page|str|分页游标  (首次请求传 None，翻页时传上次返回的 next_page)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pandas.DataFrame</td>
            <td>当 ret == RET_OK，返回排行数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
        <tr>
            <td>next_page</td>
            <td>str</td>
            <td>下一页游标字符串，None 表示无下一页</td>
        </tr>
        <tr>
            <td>all_count</td>
            <td>int</td>
            <td>符合条件的总数据量</td>
        </tr>
    </table>

    * data DataFrame 字段：

        字段|类型|说明
        :-|:-|:-
        code|str|标的股票代码
        name|str|标的名称
        total_volume|int|期权总成交量
        total_open_interest|int|期权总持仓量
        volume_ratio|float|Put/Call 成交量比值（百分比）
        open_interest_ratio|float|Put/Call 持仓量比值（百分比）
        iv|float|隐含波动率（百分比）
        iv_rank|float|IV 排名百分位（百分比）
        iv_percentile|float|IV 百分位（百分比）
        price|float|标的最新价
        change_ratio|float|标的涨跌幅（小数）
        iv_change|float|IV 变化率（百分比）
        hv|float|历史波动率（百分比）
        hv_change|float|HV 变化率（百分比）
        market_cap|float|市值
        trading_date|str|排行数据对应交易日
        trading_timestamp|float|排行数据对应交易日时间戳（Unix 秒）

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data, next_page, all_count = quote_ctx.get_option_underlying_rank(
    option_market=OptionMarket.US_SECURITY,
    sort_type=UnderlyingRankSortType.VOLUME,
    count=5
)
if ret == RET_OK:
    print(data)
    print('all_count:', all_count)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
      code                        name  total_volume  total_open_interest  volume_ratio  open_interest_ratio      iv  iv_rank  iv_percentile   price  change_ratio  iv_change      hv  hv_change    market_cap trading_date  trading_timestamp
0   US.SPY               标普500ETF-SPDR      14228830             19909256       0.97899              1.93868  17.675   27.143         61.111  741.75      0.540826     -8.261  15.031     -0.057  7.814945e+11   2026-06-12       1.781237e+09
1   US.QQQ  纳指100ETF-Invesco QQQ Trust       8239190             12964422       0.99417              1.49888  27.652   62.918         91.269  721.34      0.588465     -8.332  26.196     -0.644  4.765533e+11   2026-06-12       1.781237e+09
2  US.TSLA                         特斯拉       3623504              7088459       0.64872              0.69633  55.053   39.265         64.285  406.43      1.823876     -0.629  49.359     -1.194  1.526439e+12   2026-06-12       1.781237e+09
3  US.NVDA                         英伟达       3157331             16744961       0.59428              0.84085  41.975   27.062         42.460  205.19      0.156197     -7.002  45.921     -1.972  4.965598e+12   2026-06-12       1.781237e+09
4   US.IWM           罗素2000ETF-iShares       2840729             11791964       0.79034              2.78276  24.857   33.930         64.285  292.95      0.874626     -6.744  24.802      0.522  8.061984e+10   2026-06-12       1.781237e+09
all_count: 6017
```

:::tip 接口限制
* 30 秒内最多请求 60 次期权标的排行接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 期权合约排行

`get_option_rank(option_market, sort_type, count=None, trading_date=None, sort_direction=None, page=None, filter_list=None)`

* **介绍**

    获取期权合约排行列表，支持按成交量、持仓量、增仓量、减仓量、IV、涨跌幅等维度排序。

* **参数**

    参数|类型|说明
    :-|:-|:-
    option_market|[OptionMarket](./quote.md#5579)|期权市场类型  (US_SECURITY=美股股票期权、US_INDEX=美股指数期权、HK_SECURITY=港股股票期权、HK_INDEX=港股指数期权)
    sort_type|[OptionRankType](./quote.md#7165)|排序类型  (VOLUME=成交量、TURNOVER=成交额、OI=持仓量、OI_INCREMENT=增仓量(日)、OI_DECREMENT=减仓量(日)、OI_MARKET_CAP=持仓额、OI_MARKET_CAP_INCREMENT=增仓额(日)、OI_MARKET_CAP_DECREMENT=减仓额(日)、CHANGE_RATE=涨跌幅、IV=隐含波动率)
    count|int|返回数量  (范围 [1,200]，默认 200)
    trading_date|str|交易日  (格式 yyyy-MM-dd，不填返回最新排行)
    sort_direction|int|排序方向  (0=降序(默认)，1=升序)
    page|str|分页游标  (首次请求不传，后续传 next_page)
    filter_list|list[OptionRankFilter]|筛选条件列表  (多条件为 AND 关系)

* **返回**

    返回四元组 (ret, data, next_page, all_count)

    参数|类型|说明
    :-|:-|:-
    ret|[RET_CODE](../ftapi/common.html#7467)|接口调用结果
    data|pandas.DataFrame|当 ret == RET_OK，返回排行数据
    data|str|当 ret != RET_OK，返回错误描述
    next_page|str|下一页游标，None 表示无更多数据
    all_count|int|满足筛选条件的总数量

    * data DataFrame 字段：

        字段|类型|说明
        :-|:-|:-
        code|str|期权合约代码
        name|str|期权名称
        option_type|str|期权类型  (CALL/PUT)
        oi_increment|int|增仓量（>=0）
        oi_decrement|int|减仓量（>=0）
        oi_market_cap_increment|float|增仓额（>=0）
        oi_market_cap_decrement|float|减仓额（>=0）
        volume|int|成交量
        turnover|float|成交额
        open_interest|int|持仓量
        open_interest_market_cap|float|持仓额
        iv|float|隐含波动率（百分比）
        option_price|float|期权最新价
        change_ratio|float|涨跌幅（小数）
        mid_price|float|中间价
        bid_price|float|买入价
        bid_volume|int|买量
        ask_price|float|卖出价
        ask_volume|int|卖量
        delta|float|Delta
        gamma|float|Gamma
        theta|float|Theta
        vega|float|Vega
        rho|float|Rho
        trading_date|str|排行数据对应交易日
        trading_timestamp|float|排行数据对应交易日时间戳（Unix 秒）

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data, next_page, all_count = quote_ctx.get_option_rank(
    OptionMarket.US_SECURITY,
    OptionRankType.VOLUME,
    count=5
)
if ret == RET_OK:
    print(data)
    print('all_count:', all_count)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
                  code                name option_type  oi_increment oi_decrement  oi_market_cap_increment oi_market_cap_decrement  volume    turnover  open_interest  open_interest_market_cap       iv  option_price  change_ratio  mid_price  bid_price  bid_volume  ask_price  ask_volume    delta    gamma      theta     vega  rho trading_date  trading_timestamp
0  US.SPY260612C742000  SPY 260612 742.00C        CALL          1816          N/A                 105328.0                     N/A  730160  91928623.0           7449                  432042.0  146.507          0.58       -67.688      0.580       0.56          28       0.60           1  0.43674  0.27447 -455.46028  0.00385  0.0   2026-06-12       1.781237e+09
1  US.SPY260612C745000  SPY 260612 745.00C        CALL          5416          N/A                   5416.0                     N/A  617981  44479304.0          17013                   17013.0   87.067          0.01       -98.958      0.015       0.01         708       0.02         500  0.02438  0.03501  -18.52310  0.00107  0.0   2026-06-12       1.781237e+09
2  US.SPY260612C743000  SPY 260612 743.00C        CALL          5438          N/A                  48942.0                     N/A  606769  64419534.0           7426                   66834.0   59.082          0.09       -93.898      0.095       0.09         208       0.10         118  0.13412  0.19487  -50.92453  0.00405  0.0   2026-06-12       1.781237e+09
3  US.SPY260612P740000  SPY 260612 740.00P         PUT          1223          N/A                   1223.0                     N/A  566915  69291991.0          15291                   15291.0   53.083          0.01       -99.790      0.015       0.01         447       0.02         407 -0.03761  0.08224  -16.47701  0.00153  0.0   2026-06-12       1.781237e+09
4  US.SPY260612C741000  SPY 260612 741.00C        CALL          2924          N/A                 423980.0                     N/A  506505  88981079.0           6229                  903205.0  224.448          1.45       -33.179      1.520       1.46          12       1.58          23  0.63754  0.17055 -662.49947  0.00367  0.0   2026-06-12       1.781237e+09
all_count: 1955829
```

:::tip 接口限制
* 30 秒内最多请求 60 次期权合约排行接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 期权异动

`get_option_event(option_market, count=None, page=None, filter_list=None, sort=None)`

* **介绍**

    获取期权异动列表，返回大单成交、扫单等期权异动记录，支持按标的、合约属性、成交信息、希腊值等多维度筛选和排序。

* **参数**

    参数|类型|说明
    :-|:-|:-
    option_market|[OptionMarket](./quote.md#5579)|期权市场类型  (US_SECURITY=美股股票期权、US_INDEX=美股指数期权、HK_SECURITY=港股股票期权、HK_INDEX=港股指数期权)
    count|int|每页数量  (范围 [1,300])
    page|str|分页标记  (首次传空字符串，翻页传上次返回的 next_page)
    filter_list|list[EventFilter]|筛选条件列表  (多条件为 AND 关系。支持按标的(OWNER_LIST)、行业板块、期权类型(CALL/PUT)、成交方向、成交量、成交额、IV、Delta 等筛选)
    sort|EventSort|排序  (默认按时间降序)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回异动数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * data 字典包含：

        字段|类型|说明
        :-|:-|:-
        event_list|pandas.DataFrame|异动记录列表
        next_page|str|下一页标记（空字符串表示无下一页）
        all_count|int|总记录数
        update_timestamp|float|数据更新时间戳（Unix 秒）

    * event_list DataFrame 字段：

        字段|类型|说明
        :-|:-|:-
        option_code|str|期权合约代码
        owner_code|str|标的股票代码
        symbol|str|标的 display code（如 TSLA）
        fill_time|str|成交时间
        fill_timestamp|float|成交时间戳（Unix 秒）
        ticker_type|str|成交方向  (BUY=主动买入、SELL=主动卖出、NEUTRAL=中性盘)
        price|float|成交价
        volume|int|成交量（张）
        turnover|float|成交额
        option_type|str|期权类型  (CALL/PUT)
        strike_price|float|行权价
        strike_time|str|到期日
        strike_timestamp|float|到期日时间戳（Unix 秒）
        dte|int|距到期天数
        underlying_price|float|标的价格
        otm|float|价外比率（百分比）
        bid_price|float|买一价
        ask_price|float|卖一价
        iv|float|隐含波动率（百分比）
        total_volume|int|期权当日总成交量
        total_open_interest|int|期权当日总持仓量
        vo_ratio|float|量仓比（百分比）
        delta|float|Delta
        gamma|float|Gamma
        vega|float|Vega
        theta|float|Theta
        rho|float|Rho
        sentiment|str|市场情绪  (BEARISH=看空、BULLISH=看多、NEUTRAL=中性)
        order_type_list|list|订单类型列表  (NORMAL=普通、SWEEP=扫单、CROSS=对敲单、FLOOR=场内单)
        strategy_type|str|策略类型  (SINGLE_LEG=单腿、MULTI_LEG=多腿策略)
        earnings_time|str|财报日期
        earnings_pub_type|int|财报发布类型  (1=盘前、2=盘后)
        corporate_action_list|list|公司行动列表
        industry_plate_list|list|行业板块列表
        concept_plate_list|list|概念板块列表

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_option_event(OptionMarket.US_SECURITY, count=5)
if ret == RET_OK:
    print(data['event_list'])
    print('all_count:', data['all_count'])
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
           option_code owner_code symbol            fill_time  fill_timestamp ticker_type     price  volume   turnover option_type  strike_price strike_time  strike_timestamp  dte  underlying_price    otm  bid_price  ask_price      iv  total_volume  total_open_interest  vo_ratio     delta     gamma      vega     theta       rho sentiment  order_type_list strategy_type earnings_time earnings_pub_type                                                                corporate_action_list industry_plate_list concept_plate_list
0   US.TLT260618C86000     US.TLT    TLT  2026-06-12 16:14:00    1.781295e+09        SELL  0.280000   10000   280000.0        CALL          86.0  2026-06-18      1.781759e+09    3             85.77  0.268       0.28       0.30   8.240         70108                88849   0.78906  0.424382  0.432194  0.043077 -0.034441  0.005940   BEARISH  [SWEEP, NORMAL]    SINGLE_LEG           N/A               N/A                                                                          N/A                 N/A                N/A
1   US.TLT260618C86000     US.TLT    TLT  2026-06-12 16:13:18    1.781295e+09        SELL  0.280000    7821   218988.0        CALL          86.0  2026-06-18      1.781759e+09    3             85.77  0.268       0.28       0.30   8.240         60104                88849   0.67647  0.424382  0.432194  0.043077 -0.034441  0.005940   BEARISH  [SWEEP, NORMAL]    SINGLE_LEG           N/A               N/A                                                                          N/A                 N/A                N/A
2  US.IWM260618P285000     US.IWM    IWM  2026-06-12 16:07:53    1.781295e+09        SELL  1.320000    3002   396264.0         PUT         285.0  2026-06-18      1.781759e+09    3            292.96  2.717       1.32       1.35  28.323         57418                26731   2.14799 -0.214110  0.027402  0.109475 -0.256980 -0.009801   BULLISH  [SWEEP, NORMAL]    SINGLE_LEG           N/A               N/A  [{'action_type': 7, 'action_time': '2026-06-15', 'action_timestamp': ...}]                 N/A                N/A
3  US.SPY260717P706000     US.SPY    SPY  2026-06-12 16:04:46    1.781295e+09         BUY  4.333523    3872  1677940.0         PUT         706.0  2026-07-17      1.784264e+09   32            741.77  4.822       4.29       4.35  19.000         22269                 8169   2.72603 -0.177726  0.005982  0.596630 -0.150480 -0.113947   BEARISH  [SWEEP, NORMAL]    SINGLE_LEG           N/A               N/A                                                                          N/A                 N/A      [US.LIST2153]
4  US.SPY260717P704000     US.SPY    SPY  2026-06-12 16:04:26    1.781295e+09        SELL  4.060235    6767  2747561.0         PUT         704.0  2026-07-17      1.784264e+09   32            741.77  5.091       4.05       4.10  19.214         17712                 7842   2.25860 -0.167963  0.005705  0.575554 -0.147087 -0.107775   BULLISH         [NORMAL]    SINGLE_LEG           N/A               N/A                                                                          N/A                 N/A      [US.LIST2153]
all_count: 164620
```

:::tip 接口限制
* 30 秒内最多请求 60 次期权异动接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 查询异动提醒

`get_option_event_alert(count=200, page=None)`

* **介绍**

    查询已设置的期权异动提醒列表，支持分页。

* **参数**

    参数|类型|说明
    :-|:-|:-
    count|int|每页数量  (范围 [1,500]，默认 200)
    page|str|分页标记  (首次传 None，翻页传 next_page)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回告警数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * data 字典包含：

        字段|类型|说明
        :-|:-|:-
        alert_list|pandas.DataFrame|提醒设置列表
        next_page|str|下一页标记（空字符串表示无下一页）
        all_count|int|告警项总数

    * alert_list DataFrame 各列字段：

        字段|类型|说明
        :-|:-|:-
        key|int|告警唯一标识
        enable|bool|告警开关
        option_market|str|市场品类（[OptionMarket](./quote.md#5579) 枚举值）
        watchlist_group_name|str|自选股分组名称
        underlying|str|指定标的代码
        option_type|str|期权类型（CALL/PUT）
        side_type_list|list|成交方向列表（[EventTickerType](./quote.md#4215) 枚举值）
        order_type_list|list|订单类型列表（[AlertOrderType](./quote.md#5456) 枚举值）
        market_cap_range_min|float|标的市值下限
        market_cap_range_max|float|标的市值上限
        market_cap_min_inclusive|bool|标的市值下限是否闭区间
        market_cap_max_inclusive|bool|标的市值上限是否闭区间
        expiry_days_range_min|float|距到期天数下限
        expiry_days_range_max|float|距到期天数上限
        expiry_days_min_inclusive|bool|距到期天数下限是否闭区间
        expiry_days_max_inclusive|bool|距到期天数上限是否闭区间
        price_range_min|float|异动成交价下限
        price_range_max|float|异动成交价上限
        price_min_inclusive|bool|异动成交价下限是否闭区间
        price_max_inclusive|bool|异动成交价上限是否闭区间
        size_range_min|float|异动成交量下限（张）
        size_range_max|float|异动成交量上限（张）
        size_min_inclusive|bool|异动成交量下限是否闭区间
        size_max_inclusive|bool|异动成交量上限是否闭区间
        premium_range_min|float|异动成交额下限
        premium_range_max|float|异动成交额上限
        premium_min_inclusive|bool|异动成交额下限是否闭区间
        premium_max_inclusive|bool|异动成交额上限是否闭区间
        iv_range_min|float|隐含波动率下限（%）
        iv_range_max|float|隐含波动率上限（%）
        iv_min_inclusive|bool|隐含波动率下限是否闭区间
        iv_max_inclusive|bool|隐含波动率上限是否闭区间
        earnings_date_begin|str|财报时间筛选起始日期（yyyy-MM-dd）
        earnings_date_end|str|财报时间筛选截止日期（yyyy-MM-dd）
        note|str|备注

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_option_event_alert()
if ret == RET_OK:
    print(data['alert_list'])
    print('all_count:', data['all_count'])
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
     key  enable option_market watchlist_group_name underlying option_type side_type_list order_type_list  market_cap_range_min  market_cap_range_max market_cap_min_inclusive market_cap_max_inclusive  expiry_days_range_min  expiry_days_range_max expiry_days_min_inclusive expiry_days_max_inclusive  price_range_min  price_range_max price_min_inclusive price_max_inclusive  size_range_min  size_range_max size_min_inclusive size_max_inclusive  premium_range_min  premium_range_max premium_min_inclusive premium_max_inclusive  iv_range_min  iv_range_max iv_min_inclusive iv_max_inclusive earnings_date_begin earnings_date_end  note
0  14743   False   US_SECURITY                  N/A        N/A        CALL            N/A         [SWEEP]                   N/A                   N/A                     N/A                      N/A                    N/A                    N/A                      N/A                       N/A              N/A              N/A                N/A                N/A           100.0             N/A              True               N/A                N/A                N/A                  N/A                   N/A           N/A           N/A             N/A             N/A                 N/A               N/A  test
all_count: 1
```

:::tip 接口限制
* 30 秒内最多请求 60 次查询异动提醒接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 设置异动提醒

`set_option_event_alert(op, alert_list=None)`

* **介绍**

    新增、修改、删除或启用/禁用期权异动提醒。

* **参数**

    参数|类型|说明
    :-|:-|:-
    op|[AlertOpType](./quote.md#4576)|操作类型  (ADD=新增、DELETE=删除、MODIFY=修改、ENABLE=启用、DISABLE=禁用、DELETE_ALL=删除全部)
    alert_list|OptionEventAlertItem 或 list[OptionEventAlertItem]|提醒条目  (新增时不传 key，修改/删除时必传 key)

    * OptionEventAlertItem 各字段：

        字段|类型|说明
        :-|:-|:-
        key|int|告警唯一标识（修改/删除/启用/禁用时必填）
        enable|bool|告警开关
        option_market|[OptionMarket](./quote.md#5579)|监控的期权市场（三选一）
        watchlist_group_name|str|自选股分组名称（三选一）
        underlying|str|指定标的代码，如 `'US.AAPL'`（三选一）
        option_type|OptionType|期权类型（CALL/PUT）
        side_type_list|list[[EventTickerType](./quote.md#4215)]|成交方向列表
        order_type_list|list[[AlertOrderType](./quote.md#5456)]|订单类型列表
        market_cap_range_min|float|标的市值下限
        market_cap_range_max|float|标的市值上限
        market_cap_min_inclusive|bool|标的市值下限是否闭区间（默认 True）
        market_cap_max_inclusive|bool|标的市值上限是否闭区间（默认 True）
        expiry_days_range_min|float|距到期天数下限
        expiry_days_range_max|float|距到期天数上限
        expiry_days_min_inclusive|bool|距到期天数下限是否闭区间（默认 True）
        expiry_days_max_inclusive|bool|距到期天数上限是否闭区间（默认 True）
        price_range_min|float|异动成交价下限
        price_range_max|float|异动成交价上限
        price_min_inclusive|bool|异动成交价下限是否闭区间（默认 True）
        price_max_inclusive|bool|异动成交价上限是否闭区间（默认 True）
        size_range_min|float|异动成交量下限（张）
        size_range_max|float|异动成交量上限（张）
        size_min_inclusive|bool|异动成交量下限是否闭区间（默认 True）
        size_max_inclusive|bool|异动成交量上限是否闭区间（默认 True）
        premium_range_min|float|异动成交额下限
        premium_range_max|float|异动成交额上限
        premium_min_inclusive|bool|异动成交额下限是否闭区间（默认 True）
        premium_max_inclusive|bool|异动成交额上限是否闭区间（默认 True）
        iv_range_min|float|隐含波动率下限（%）
        iv_range_max|float|隐含波动率上限（%）
        iv_min_inclusive|bool|隐含波动率下限是否闭区间（默认 True）
        iv_max_inclusive|bool|隐含波动率上限是否闭区间（默认 True）
        earnings_date_begin|str|财报时间筛选起始日期（yyyy-MM-dd）
        earnings_date_end|str|财报时间筛选截止日期（yyyy-MM-dd）
        note|str|备注（最多 20 字符）

    > **监控范围**：`option_market`、`watchlist_group_name`、`underlying` 三者互斥，新增时需设置其中之一。

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>str</td>
            <td>当 ret == RET_OK，返回空字符串</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 新增一个提醒：监控美股股票期权市场的 CALL 扫单，成交量 > 100（开区间）
item = OptionEventAlertItem(
    option_market=OptionMarket.US_SECURITY,
    option_type=OptionType.CALL,
    order_type_list=[AlertOrderType.SWEEP],
    size_range_min=100,
    size_min_inclusive=False,
    note='test'
)
ret, data = quote_ctx.set_option_event_alert(AlertOpType.ADD, item)
if ret == RET_OK:
    print('新增成功')
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
新增成功
```

:::tip 接口限制
* 30 秒内最多请求 60 次设置异动提醒接口
:::

---

# 期权异动推送

`class OptionEventHandlerBase(RspHandlerBase)`

* **介绍**

    接收期权异动推送，当设置的异动提醒被触发时，服务端会主动推送异动信息。需先通过 `set_option_event_alert` 设置提醒条件，并通过 handler 注册回调。用户继承 `OptionEventHandlerBase` 并重写 `on_recv_rsp` 方法来接收推送。

* **参数**

    on_recv_rsp 回调返回 (ret_code, content)，content 为 dict：

    参数|类型|说明
    :-|:-|:-
    owner_code|str|标的代码（如 'US.TSLA'）
    option_code|str|期权合约代码（如 'US.TSLA250620C250'）
    message|str|推送消息文本

* **Example**

```python
from futu import *

class OptionEventHandler(OptionEventHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, content = super(OptionEventHandler, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("OptionEvent error:", content)
            return RET_ERROR, content

        print("收到期权异动推送:")
        print("  标的:", content['owner_code'])
        print("  期权:", content['option_code'])
        print("  消息:", content['message'])
        return RET_OK, content

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 注册期权异动推送处理器
quote_ctx.set_handler(OptionEventHandler())

# 需要先通过 set_option_event_alert 设置提醒条件，推送才会触发
item = OptionEventAlertItem(
    option_market=OptionMarket.US_SECURITY,
    option_type=OptionType.CALL,
    order_type_list=[AlertOrderType.SWEEP],
    size_range_min=100,
)
ret, data = quote_ctx.set_option_event_alert(AlertOpType.ADD, item)
if ret == RET_OK:
    print('提醒设置成功，等待推送...')
else:
    print('设置失败:', data)

import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass

quote_ctx.close()
```

* **Output**

```
收到期权异动推送:
  标的: US.TSLA
  期权: US.TSLA250620C250
  消息: TSLA $250 Call 06/20 大额扫单 500张 成交价$12.50
```

---

# 末日期权标的筛选

`get_option_zero_dte_screener(market, sort_type=None, is_asc=None, count=None, page=None, filter_list=None)`

* **介绍**

    获取末日期权标的筛选列表，返回当日到期（0DTE）期权对应的标的股票信息，包含波动率、期权成交量、持仓量及期权链信息等数据。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[OptionMarket](./quote.md#5579)|期权市场类型  (US_SECURITY=美股股票期权、US_INDEX=美股指数期权（仅支持美股市场）)
    sort_type|[ZeroDteSortType](./quote.md#1152)|排序类型  (VOLUME=期权成交量、IV=隐含波动率、CHANGE_RATIO=涨跌幅、OPEN_INTEREST=持仓量、MARKET_CAP=市值)
    is_asc|bool|是否升序  (默认 False（降序）)
    count|int|每页数量  (范围 [1,500]，默认 50)
    page|str|分页游标  (首次不传或传空，翻页传 next_page)
    filter_list|list[ZeroDteFilter]|筛选条件列表  (多条件为 AND 关系。支持 OWNER_LIST、HAS_EARNINGS_THIS_WEEK、VOLUME、OPEN_INTEREST、IV、HV、IV_RANK、IV_PERCENTILE、PRICE、CHANGE_RATIO)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回字典，包含 item_list（DataFrame）、next_page（str/None）、update_timestamp（float）</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回 DataFrame 字段：

        字段|类型|说明
        :-|:-|:-
        owner|str|标的股票代码
        name|str|标的名称
        price|float|标的当前价格
        change_ratio|float|涨跌幅（百分比）
        market_cap|float|市值
        iv|float|隐含波动率（百分比）
        iv_rank|float|IV 排名（百分比）
        iv_percentile|float|IV 百分位（百分比）
        hv|float|历史波动率（百分比）
        volume|int|期权成交量
        open_interest|int|期权持仓量
        last_trading_time|int|最后交易时间戳（Unix 秒）
        earnings_timestamp|int|财报日期时间戳（秒）
        earnings_time|str|财报时间字符串
        earnings_pub_type|str|财报发布类型（BEFORE/AFTER）
        chain_info|dict|期权链信息  (用于 get_option_zero_dte_contract 调用)

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_option_zero_dte_screener(
    market=OptionMarket.US_SECURITY,
    sort_type=ZeroDteSortType.VOLUME,
    is_asc=False,
    count=5
)
if ret == RET_OK:
    print(data['item_list'])
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
     owner                        name   price  change_ratio    market_cap      iv  iv_rank  iv_percentile      hv    volume  open_interest  last_trading_time earnings_timestamp earnings_time earnings_pub_type                                                                                                                chain_info
0   US.SPY               标普500ETF-SPDR  741.75         0.540  7.830717e+11  17.675   27.143         61.111  15.031  14228830       19909256         1781554500                N/A           N/A               N/A    {'strike_date_timestamp': 1781499600, 'product_code': 'SPY', 'multiplier': 100.0, ...}
1   US.QQQ  纳指100ETF-Invesco QQQ Trust  721.34         0.588  4.805349e+11  27.652   62.918         91.269  26.196   8239190       12964422         1781554500                N/A           N/A               N/A    {'strike_date_timestamp': 1781499600, 'product_code': 'QQQ', 'multiplier': 100.0, ...}
2  US.TSLA                         特斯拉  406.43         1.823  1.526439e+12  55.053   39.265         64.285  49.359   3623504        7088459         1781553600                N/A           N/A               N/A  {'strike_date_timestamp': 1781499600, 'product_code': 'TSLA', 'multiplier': 100.0, ...}
3  US.NVDA                         英伟达  205.19         0.156  4.965598e+12  41.975   27.062         42.460  45.921   3157331       16744961         1781553600                N/A           N/A               N/A  {'strike_date_timestamp': 1781499600, 'product_code': 'NVDA', 'multiplier': 100.0, ...}
4   US.IWM           罗素2000ETF-iShares  292.95         0.874  8.143528e+10  24.857   33.930         64.285  24.802   2840729       11791964         1781554500                N/A           N/A               N/A    {'strike_date_timestamp': 1781499600, 'product_code': 'IWM', 'multiplier': 100.0, ...}
```

:::tip 接口限制
* 30 秒内最多请求 60 次末日期权标的筛选接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 末日期权合约列表

`get_option_zero_dte_contract(owner, strike_date_timestamp, chain_info, sort_type=None, is_asc=None, filter_list=None)`

* **介绍**

    获取末日期权合约列表，返回指定标的在指定行权日的 0DTE 期权合约详情，包含希腊值、盈亏平衡点及盈利概率等数据。

* **参数**

    参数|类型|说明
    :-|:-|:-
    owner|str|标的股票代码  (如 'US.AAPL'，仅支持美股股票)
    strike_date_timestamp|int|行权日期时间戳（Unix 秒）
    chain_info|dict|期权链信息  (来自 get_option_zero_dte_screener 返回的 chain_info)
    sort_type|[ZeroDteContractSortType](./quote.md#7756)|排序类型  (VOLUME=成交量、OPEN_INTEREST=持仓量、IV=隐含波动率、DELTA=Delta)
    is_asc|bool|是否升序  (默认 False（降序）)
    filter_list|list[ZeroDteContractFilter]|筛选条件列表  (多条件为 AND 关系。支持 OPTION_TYPE、VOLUME、OPEN_INTEREST、IV、DELTA、GAMMA、THETA、VEGA、RHO、PRICE、CHANGE_RATIO、BREAK_EVEN_POINT、TO_BEP、BUY_PROFIT_PROBABILITY、SELL_PROFIT_PROBABILITY)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pandas.DataFrame</td>
            <td>当 ret == RET_OK，返回合约列表</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回 DataFrame 字段：

        字段|类型|说明
        :-|:-|:-
        option|str|期权合约代码
        name|str|合约名称
        option_type|str|期权类型（CALL/PUT）
        option_price|float|期权价格
        change_ratio|float|涨跌幅（百分比）
        volume|int|成交量
        open_interest|int|持仓量
        iv|float|隐含波动率（百分比）
        delta|float|Delta
        gamma|float|Gamma
        vega|float|Vega
        theta|float|Theta
        rho|float|Rho
        buy_break_even_point|float|买入盈亏平衡点
        buy_to_bep|float|到达盈亏平衡点所需涨跌幅（百分比）
        buy_profit_probability|float|买入盈利概率（百分比）
        sell_profit_probability|float|卖出盈利概率（百分比）

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 第一步：获取末日期权标的列表
ret, screener_data = quote_ctx.get_option_zero_dte_screener(
    market=OptionMarket.US_SECURITY,
    sort_type=ZeroDteSortType.VOLUME,
    is_asc=False,
    count=1
)
if ret != RET_OK:
    print('error:', screener_data)
    quote_ctx.close()
    exit()

# 第二步：取第一个标的的 chain_info，查询其合约列表
df = screener_data['item_list']
owner = df.iloc[0]['owner']
chain_info = df.iloc[0]['chain_info']
strike_date_timestamp = chain_info['strike_date_timestamp']

ret, data = quote_ctx.get_option_zero_dte_contract(
    owner=owner,
    strike_date_timestamp=strike_date_timestamp,
    chain_info=chain_info,
    sort_type=ZeroDteContractSortType.VOLUME,
    is_asc=False
)
if ret == RET_OK:
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
              option             name option_type  option_price  change_ratio  volume  open_interest    iv   delta   gamma    vega   theta     rho  buy_break_even_point  buy_to_bep  buy_profit_probability  sell_profit_probability
0  US.SPY260612C742000  SPY 260612 C742        CALL          0.58       -67.688  730160           7449  146.5  0.4367  0.2745  0.0039  -455.46  0.000                742.58        0.11                   43.5                    56.5
1  US.SPY260612C745000  SPY 260612 C745        CALL          0.01       -98.958  617981          17013   87.1  0.0244  0.0350  0.0011   -18.52  0.000                745.01        0.44                    2.4                    97.6
...
```

:::tip 接口限制
* 30 秒内最多请求 60 次末日期权合约列表接口
:::

---

# 财报期权筛选

`get_option_earnings_screener(market, sort_type=None, is_asc=None, count=None, page=None, filter_list=None)`

* **介绍**

    获取即将发布财报的期权标的列表，返回标的波动率数据、历史财报 IV Crush、股价变动及市场预期等信息，帮助用户在财报季进行期权交易决策。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[OptionMarket](./quote.md#5579)|期权市场类型  (US_SECURITY=美股股票期权、HK_SECURITY=港股股票期权)
    sort_type|[EarningsSortType](./quote.md#312)|排序类型  (EARNINGS_DATE=财报日期（默认）、VOLUME=期权成交量、IV=隐含波动率、MARKET_CAP=市值、CHANGE_RATIO=涨跌幅、PRICE=最新价、IV_RANK=IV等级、IV_PERCENTILE=IV百分位、HV=历史波动率、OPEN_INTEREST=持仓量、LAST_REPORT_IV_CRUSH=上次IV Crush、HISTORY_REPORT_IV_CRUSH=历史IV Crush、LAST_REPORT_CHG_RATIO=上次财报日涨跌幅、HISTORY_REPORT_CHG_RATIO=历史财报日涨跌幅、ESTIMATE_EPS_YOY=预测EPS同比、ESTIMATE_REVENUE_YOY=预测营收同比、EXPECTED_MOVE_RATIO=预测波动)
    is_asc|bool|是否升序  (默认 True)
    count|int|每页数量  (范围 [1,500]，默认 50)
    page|str|分页游标  (首次传空或不传，翻页传 next_page)
    filter_list|list[EarningsFilter]|筛选条件列表  (多条件为 AND 关系)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回字典，包含 item_list（DataFrame）、next_page（str）、update_timestamp（float）、all_count（int）</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回 DataFrame 字段：

        字段|类型|说明
        :-|:-|:-
        owner|str|标的股票代码
        name|str|标的名称
        price|float|标的当前价格
        change_ratio|float|涨跌幅（小数）
        market_cap|float|市值
        iv|float|隐含波动率（百分比）
        iv_rank|float|IV 等级（百分比）
        iv_percentile|float|IV 百分位（百分比）
        hv|float|历史波动率（百分比）
        volume|int|期权成交量
        open_interest|int|期权持仓量
        earnings_timestamp|float|财报日期时间戳（Unix 秒）
        earnings_time|str|财报日期字符串（yyyy-MM-dd）
        earnings_pub_type|str|财报发布类型（BEFORE=盘前/AFTER=盘后）
        earnings_quarter|str|财报季度（如 '2025Q1'）
        last_report_iv_crush|float|上次财报 IV Crush（百分比）
        history_report_iv_crush|float|历史平均财报 IV Crush（百分比）
        last_report_chg_ratio|float|上次财报后股价变动（小数）
        history_report_chg_ratio|float|历史平均财报后股价变动（小数）
        estimate_eps_yoy|float|预估 EPS 同比增长（百分比）
        estimate_revenue_yoy|float|预估营收同比增长（百分比）
        expected_move_ratio|float|期权隐含预期变动幅度（百分比）

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_option_earnings_screener(
    market=OptionMarket.US_SECURITY,
    count=5
)
if ret == RET_OK:
    print(data['item_list'])
    print('all_count:', data['all_count'])
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
     owner                           name  price  change_ratio    market_cap       iv  iv_rank  iv_percentile      hv  volume  open_interest  earnings_timestamp earnings_time earnings_pub_type earnings_quarter  last_report_iv_crush  history_report_iv_crush  last_report_chg_ratio  history_report_chg_ratio  estimate_eps_yoy  estimate_revenue_yoy  expected_move_ratio
0   US.CGC                  Canopy Growth   1.00        -0.990  4.220190e+08  204.207   36.550         88.492  39.545    8131         328382        1.781496e+09    2026-06-15            BEFORE           2026Q4               -21.308                   11.782                  1.851                    12.761            94.055                14.340               12.500
1  US.PLAY  Dave & Buster's Entertainment  12.93        -1.896  4.491805e+08  114.030   99.492         99.603  62.390    3052          44247        1.781496e+09    2026-06-15             AFTER           2027Q1                22.640                   26.059                 16.066                    15.892            -3.758                 1.881               15.409
2  US.DOMO                       Domo Inc   3.02         2.027  1.363547e+08  165.563   72.093         96.825  90.389    1970          29748        1.781496e+09    2026-06-15             AFTER           2027Q1                23.532                   30.013                 13.470                    19.203             9.622                -0.451               30.629
3  US.CMTL                       Comverse   4.83         5.228  1.436158e+08  388.934   81.297         98.412 106.150     218          13434        1.781496e+09    2026-06-15            BEFORE           2026Q3               154.978                   51.309                -24.536                    16.278           -10.204               -13.078               23.809
4  US.RFIL                  RF Industries  18.75         0.969  2.027675e+08  100.939   11.123         54.365  83.526     215           2044        1.781496e+09    2026-06-15             AFTER           2026Q2               -14.722                    6.537                 12.318                    12.013           200.000                 3.997               15.466
all_count: 292
```

:::tip 接口限制
* 30 秒内最多请求 60 次财报期权筛选接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 期权卖方专区

`get_option_seller_screener(market, seller_type, sort_type=None, is_asc=None, filter_list=None)`

* **介绍**

    获取期权卖方专区筛选列表，返回适合卖方策略（Cash Secured Put / Covered Call）的期权合约，包含收益率、行权概率等数据。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[OptionMarket](./quote.md#5579)|期权市场类型  (US_SECURITY=美股股票期权、HK_SECURITY=港股股票期权)
    seller_type|[SellerType](./quote.md#921)|卖方策略类型  (COVERED_CALL=备兑看涨、CASH_SECURED_PUT=现金担保卖出看跌（港股仅支持 CASH_SECURED_PUT）)
    sort_type|[SellerSortType](./quote.md#7913)|排序类型  (ANNUALIZED_RETURN=年化收益率、INTERVAL_RETURN=区间收益率、ITM_PROBABILITY=行权概率、PREMIUM=权利金)
    is_asc|bool|是否升序  (默认 False（降序）)
    filter_list|list[SellerFilter]|筛选条件列表  (多条件为 AND 关系)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pandas.DataFrame</td>
            <td>当 ret == RET_OK，返回筛选结果</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回 DataFrame 字段：

        字段|类型|说明
        :-|:-|:-
        option|str|期权合约代码
        name|str|期权名称
        option_type|str|期权方向  (CALL、PUT)
        strike_price|float|行权价
        strike_time|str|到期日时间字符串
        strike_timestamp|float|到期日时间戳（Unix 秒）
        left_days|int|距到期天数
        option_price|float|期权价格
        stock_price|float|标的股票价格
        premium|float|权利金
        otm_degree|float|价外程度（%）
        iv|float|隐含波动率（%）
        interval_return|float|区间收益率（%）
        annualized_return|float|年化收益率（%）
        itm_probability|float|行权概率（%）
        striked_interval_return|float|行权时区间收益率（%）  (仅 Covered Call)
        striked_annualized_return|float|行权时年化收益率（%）  (仅 Covered Call)
        owner|str|标的股票代码

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_option_seller_screener(
    market=OptionMarket.US_SECURITY,
    seller_type=SellerType.COVERED_CALL,
    sort_type=SellerSortType.ANNUALIZED_RETURN,
    is_asc=False
)
if ret == RET_OK:
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
                 option                 name option_type  strike_price strike_time  strike_timestamp  left_days  option_price  stock_price  premium  otm_degree       iv  interval_return  annualized_return  itm_probability  striked_interval_return  striked_annualized_return    owner
0  US.SOXL260618C235000  SOXL 260618 235.00C        CALL         235.0  2026-06-18      1.781755e+09          3        21.850       234.68   2185.0       0.136  234.988           10.266           1074.855           45.724                   10.416                   1090.597  US.SOXL
1  US.SOXL260618C237500  SOXL 260618 237.50C        CALL         237.5  2026-06-18      1.781755e+09          3        20.675       234.68   2067.5       1.201  234.423            9.660           1011.470           43.682                   10.978                   1149.431  US.SOXL
2  US.SOXL260618C240000  SOXL 260618 240.00C        CALL         240.0  2026-06-18      1.781755e+09          3        19.250       234.68   1925.0       2.266  230.652            8.935            935.526           41.678                   11.405                   1194.071  US.SOXL
3    US.WDS260618C25000    WDS 260618 25.00C        CALL          25.0  2026-06-18      1.781755e+09          3         1.875        23.07    187.5       8.365  292.148            8.846            928.963           11.794                   17.952                   1885.177   US.WDS
4  US.SOXL260618C242500  SOXL 260618 242.50C        CALL         242.5  2026-06-18      1.781755e+09          3        18.350       234.68   1835.0       3.332  232.108            8.482            888.077           39.715                   12.097                   1266.538  US.SOXL
...
```

:::tip 接口限制
* 30 秒内最多请求 60 次期权卖方专区接口
:::

---

# 筛选窝轮

`get_warrant(stock_owner='', req=None)`

* **介绍**

    筛选窝轮（仅用于筛选香港市场的窝轮、牛熊证、界内证）

* **参数**
    参数|类型|说明
    :-|:-|:-
    stock_owner|str|所属正股的股票代码
    req|WarrantRequest|筛选参数组合
    * WarrantRequest 类型字段说明如下： 
        字段|类型|说明
        :-|:-|:-
        begin|int|数据起始点
        num|int|请求数据个数  (最大 200)
        sort_field|[SortField](./quote.md#2930)|根据哪个字段排序
        ascend|bool|排序方向  (True：升序False：降序)
        type_list|list|窝轮类型过滤列表  (list 中元素类型是 [WrtType](./quote.md#926))
        issuer_list|list|发行人过滤列表  (list 中元素类型是 [Issuer](./quote.md#8363))
        maturity_time_min|str|到期日过滤范围的开始时间
        maturity_time_max|str|到期日过滤范围的结束时间
        ipo_period|[IpoPeriod](./quote.md#9546)|上市时段
        price_type|[PriceType](./quote.md#6407)|价内/价外  (暂不支持界内证的界内外筛选)
        status|[WarrantStatus](./quote.md#6556)|窝轮状态
        cur_price_min|float|最新价的过滤下限  (闭区间不传代表下限为 -∞精确到小数点后 3 位，超出部分会被舍弃)
        cur_price_max|float|最新价的过滤上限  (闭区间不传代表上限为 +∞精确到小数点后 3 位，超出部分会被舍弃)
        strike_price_min|float|行使价的过滤下限  (闭区间不传代表下限为 -∞精确到小数点后 3 位，超出部分会被舍弃)
        strike_price_max|float|行使价的过滤上限  (闭区间不传代表上限为 +∞精确到小数点后 3 位，超出部分会被舍弃)
        street_min|float|街货占比的过滤下限  (闭区间不传代表下限为 -∞该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。精确到小数点后 3 位，超出部分会被舍弃)
        street_max|float|街货占比的过滤上限  (闭区间不传代表上限为 +∞该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。精确到小数点后 3 位，超出部分会被舍弃)
        conversion_min|float|换股比率的过滤下限  (闭区间不传代表下限为 -∞精确到小数点后 3 位，超出部分会被舍弃)
        conversion_max|float|换股比率的过滤上限  (闭区间不传代表上限为 +∞精确到小数点后 3 位，超出部分会被舍弃)
        vol_min|int|成交量的过滤下限  (闭区间不传代表下限为 -∞)
        vol_max|int|成交量的过滤上限  (闭区间不传代表上限为 +∞)
        premium_min|float|溢价的过滤下限  (闭区间不传代表下限为 -∞该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。精确到小数点后 3 位，超出部分会被舍弃)
        premium_max|float|溢价的过滤上限  (闭区间不传代表上限为 +∞该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。精确到小数点后 3 位，超出部分会被舍弃)
        leverage_ratio_min|float|杠杆比率的过滤下限  (闭区间不传代表下限为 -∞精确到小数点后 3 位，超出部分会被舍弃)
        leverage_ratio_max|float|杠杆比率的过滤上限  (闭区间不传代表上限为 +∞)
        delta_min|float|对冲值的过滤下限  (闭区间仅认购认沽支持此字段过滤不传代表下限为 -∞精确到小数点后 3 位，超出部分会被舍弃)
        delta_max|float|对冲值的过滤上限  (闭区间仅认购认沽支持此字段过滤不传代表上限为 +∞精确到小数点后 3 位，超出部分会被舍弃)
        implied_min|float|引伸波幅的过滤下限  (闭区间仅认购认沽支持此字段过滤不传代表下限为 -∞精确到小数点后 3 位，超出部分会被舍弃)
        implied_max|float|引伸波幅的过滤上限  (闭区间仅认购认沽支持此字段过滤不传代表上限为 +∞精确到小数点后 3 位，超出部分会被舍弃)
        recovery_price_min|float|收回价的过滤下限  (闭区间仅牛熊证支持此字段过滤不传代表下限为 -∞精确到小数点后 3 位，超出部分会被舍弃)
        recovery_price_max|float|收回价的过滤上限  (闭区间仅牛熊证支持此字段过滤不传代表上限为 +∞精确到小数点后 3 位，超出部分会被舍弃)
        price_recovery_ratio_min|float|正股距收回价的过滤下限  (闭区间仅牛熊证支持此字段过滤该字段为百分比字段，默认不展示 %，如 20 实际对应 20%不传代表下限为 -∞精确到小数点后 3 位，超出部分会被舍弃)
        price_recovery_ratio_max|float|正股距收回价的过滤上限  (闭区间仅牛熊证支持此字段过滤该字段为百分比字段，默认不展示 %，如 20 实际对应 20%不传代表上限为 +∞精确到小数点后 3 位，超出部分会被舍弃)


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>tuple</td>
            <td>当 ret == RET_OK，返回窝轮数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 窝轮数据组成如下：
        字段|类型|说明
        :-|:-|:-
        warrant_data_list|pd.DataFrame|筛选后的窝轮数据
        last_page|bool|是否是最后一页  (True：是最后一页False：不是最后一页)
        all_count|int|筛选结果中的窝轮总数量

        - warrant_data_list 返回的 pd dataframe 数据格式：
            字段|类型|说明
            :-|:-|:-
            stock|str|窝轮代码
            stock_owner|str|所属正股
            type|[WrtType](./quote.md#926)|窝轮类型
            issuer|[Issuer](./quote.md#8363)|发行人
            maturity_time|str|到期日  (格式：yyyy-MM-dd)
            list_time|str|上市时间  (格式：yyyy-MM-dd)
            last_trade_time|str|最后交易日  (格式：yyyy-MM-dd)
            recovery_price|float|收回价  (仅牛熊证支持此字段)
            conversion_ratio|float|换股比率
            lot_size|int|每手数量
            strike_price|float|行使价
            last_close_price|float|昨收价
            name|str|名称
            cur_price|float|当前价
            price_change_val|float|涨跌额
            status|[WarrantStatus](./quote.md#6556)|窝轮状态
            bid_price|float|买入价
            ask_price|float|卖出价
            bid_vol|int|买量
            ask_vol|int|卖量
            volume|int|成交量
            turnover|float|成交额
            score|float|综合评分
            premium|float|溢价  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            break_even_point|float|打和点
            leverage|float|杠杆比率  (单位：倍)
            ipop|float|价内/价外  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            price_recovery_ratio|float|正股距收回价  (仅牛熊证支持此字段该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            conversion_price|float|换股价
            street_rate|float|街货占比  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            street_vol|int|街货量
            amplitude|float|振幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            issue_size|int|发行量
            high_price|float|最高价
            low_price|float|最低价
            implied_volatility|float|引伸波幅  (仅认购认沽支持此字段)
            delta|float|对冲值  (仅认购认沽支持此字段)
            effective_leverage|float|有效杠杆 (仅认购认沽支持此字段)
            upper_strike_price|float|上限价  (仅界内证支持此字段)
            lower_strike_price|float|下限价  (仅界内证支持此字段)
            inline_price_status|[PriceType](./quote.md#6407)|界内界外  (仅界内证支持此字段)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

req = WarrantRequest()
req.sort_field = SortField.TURNOVER
req.type_list = WrtType.CALL
req.cur_price_min = 0.1
req.cur_price_max = 0.2
ret, ls = quote_ctx.get_warrant("HK.00700", req)
if ret == RET_OK:  # 先判断接口返回是否正常，再取数据
    warrant_data_list, last_page, all_count = ls
    print(len(warrant_data_list), all_count, warrant_data_list)
    print(warrant_data_list['stock'][0])    # 取第一条的窝轮代码
    print(warrant_data_list['stock'].values.tolist())   # 转为 list
else:
    print('error: ', ls)
    
req = WarrantRequest()
req.sort_field = SortField.TURNOVER
req.issuer_list = ['UB','CS','BI']
ret, ls = quote_ctx.get_warrant(Market.HK, req)
if ret == RET_OK: 
    warrant_data_list, last_page, all_count = ls
    print(len(warrant_data_list), all_count, warrant_data_list)
else:
    print('error: ', ls)

quote_ctx.close()  # 所有接口结尾加上这条 close，防止连接条数用尽
```

* **Output**

```python
2 2 
    stock        name stock_owner  type issuer maturity_time   list_time last_trade_time  recovery_price  conversion_ratio  lot_size  strike_price  last_close_price  cur_price  price_change_val  change_rate  status  bid_price  ask_price   bid_vol  ask_vol    volume   turnover   score  premium  break_even_point  leverage    ipop  price_recovery_ratio  conversion_price  street_rate  street_vol  amplitude  issue_size  high_price  low_price  implied_volatility  delta  effective_leverage  list_timestamp  last_trade_timestamp  maturity_timestamp  upper_strike_price  lower_strike_price  inline_price_status
0   HK.20306  腾讯麦银零乙购A.C    HK.00700  CALL     MB    2020-12-01  2019-06-27      2020-11-25             NaN              50.0      5000        588.88             0.188      0.188             0.000     0.000000  NORMAL      0.000      0.188         0     10000           0          0.0   0.198    2.008            598.28    62.393  -0.404                   NaN              9.40        4.400     1584000      0.000    36000000       0.000      0.000              31.751  0.479              29.886    1.561565e+09          1.606234e+09        1.606752e+09                 NaN                 NaN                  NaN
1   HK.16545  腾讯法兴一二购B.C    HK.00700  CALL     SG    2021-02-26  2020-07-14      2021-02-22             NaN             100.0     10000        700.00             0.147      0.144            -0.003    -2.040816  NORMAL      0.141      0.144  28000000  28000000           0          0.0  81.506   21.807            714.40    40.729 -16.214                   NaN             14.40        1.420     2130000      0.000   150000000       0.000      0.000              40.643  0.226               9.204    1.594656e+09          1.613923e+09        1.614269e+09                 NaN                 NaN                  NaN
HK.20306
['HK.20306', 'HK.16545']

200 358
    stock        name stock_owner    type issuer maturity_time   list_time last_trade_time  recovery_price  conversion_ratio  lot_size  strike_price  last_close_price  cur_price  price_change_val  change_rate      status  bid_price  ask_price   bid_vol   ask_vol  volume  turnover   score  premium  break_even_point  leverage     ipop  price_recovery_ratio  conversion_price  street_rate  street_vol  amplitude  issue_size  high_price  low_price  implied_volatility  delta  effective_leverage  list_timestamp  last_trade_timestamp  maturity_timestamp  upper_strike_price  lower_strike_price inline_price_status
0    HK.19839  平安瑞银零乙购A.C    HK.02318    CALL     UB    2020-12-31  2017-12-11      2020-12-24             NaN             100.0     50000         83.88             0.057      0.046            -0.011   -19.298246      NORMAL      0.043      0.046  30000000  30000000       0       0.0  39.641    1.642            88.480    18.923    3.779                   NaN             4.600         1.25     6250000        0.0   500000000         0.0        0.0              25.129  0.692              13.094    1.512922e+09          1.608739e+09        1.609344e+09                 NaN                 NaN                 NaN
1    HK.20084  平安中银零乙购A.C    HK.02318    CALL     BI    2020-12-31  2017-12-19      2020-12-24             NaN             100.0     50000         83.88             0.059      0.050            -0.009   -15.254237      NORMAL      0.044      0.050  10000000  10000000       0       0.0   0.064    2.102            88.880    17.410    3.779                   NaN             5.000         0.07      350000        0.0   500000000         0.0        0.0              29.174  0.672              11.699    1.513613e+09          1.608739e+09        1.609344e+09                 NaN                 NaN                 NaN
......
198  HK.56886  恒指瑞银三一牛F.C   HK.800000    BULL     UB    2023-01-30  2020-03-24      2023-01-27         21200.0           20000.0     10000      21100.00             0.230      0.232             0.002     0.869565      NORMAL      0.232      0.233  30000000  30000000       0       0.0  46.627   -2.884         25740.000     5.712   25.613             25.021179          4640.000         0.01       40000        0.0   400000000         0.0        0.0                 NaN    NaN               5.712    1.584979e+09          1.674749e+09        1.675008e+09                 NaN                 NaN                 NaN
199  HK.56895  小米瑞银零乙牛D.C    HK.01810    BULL     UB    2020-12-30  2020-03-24      2020-12-29             8.0              10.0      2000          7.60             2.010      1.930            -0.080    -3.980100      NORMAL      1.910      1.930   6000000   6000000       0       0.0   0.040    0.938            26.900     1.380  250.657            233.125000            19.300         0.10       60000        0.0    60000000         0.0        0.0                 NaN    NaN               1.380    1.584979e+09          1.609171e+09        1.609258e+09                 NaN                 NaN                 NaN

```

:::tip 接口限制
* 港股 BMP 权限不支持调用此接口
* 每 30 秒内最多请求 60 次筛选窝轮接口
* 每次请求的数据个数上限为 200 个
:::

---

# 筛选窝轮 V2

`get_warrant_screen(request)`

* **介绍**

    窝轮筛选 V2。相比旧接口 [get_warrant](./get-warrant.md)，返回 45 列窝轮属性，支持港股 / 新加坡 / 马来西亚市场，且支持仅返回总数（only_count）。所有数值字段直接传原始值，OpenD 内部完成倍率转换。

* **参数**

    参数|类型|说明
    :-|:-|:-
    request|WarrantScreenRequest|窝轮筛选请求对象，构造时必传 warrant_market

    * WarrantScreenRequest 字段：

        字段|类型|说明
        :-|:-|:-
        warrant_market|[WarrantMarket](./quote.md#1724)|市场  (HK=1、SG=4、MY=15)
        is_delay|bool|是否使用延时行情  (不传默认为 False)
        only_count|bool|是否仅返回总数（不返回明细）  (不传默认为 False；True 时仅填充 all_count，DataFrame 为空)
        page_from|int|分页起始位置  (不传默认为 0)
        page_count|int|单页最大返回数  (不传默认为 200)

    * 筛选条件 builder 方法（每次调用追加一条筛选条件）：

        方法|说明
        :-|:-
        add_interval_filter(field_id, min_val=None, max_val=None, min_included=True, max_included=True)|区间筛选  (field_id 取自 [WarrantField](./quote.md#9880)；min_val / max_val 直接传原始值（OpenD 自动倍率转换，如现价 5 元传 5.0、街货占比 50% 传 50.0、有效杠杆 > 3 传 3.0）；min_val / max_val 均为可选，全部不传时该条件不会生效（等同于不筛选）)
        add_choice_filter(field_id, choices)|多选筛选  (choices 元素可为 int 枚举或 str 代码，例如 STOCK_OWNER 字段可直接传 ["HK.00700"]，WARRANT_TYPE 可传 [WarrantType.CALL, WarrantType.PUT])
        add_sort(field_id, desc=False)|排序  (desc=True 为降序，默认升序)

    * 常用 WarrantField field_id（完整列表见 [WarrantField](./quote.md#9880)）：

        field_id|含义|筛选方式
        :-|:-|:-
        4|ISSUER_ID 发行商 ID|choice  (仅 HK 可筛选（SG / MY 接口返回的 issuer_id 实测恒为 0）；取值见下文「字段逐项示例 > ISSUER_ID」的发行商映射表，例如 [21] = 仅瑞通 VT；与 Proto Qot_Common.Issuer 枚举一致（0=未知、1=SG 法兴、…、28=CI 信证）)
        5|STOCK_OWNER 正股|choice  (可传 ["HK.00700"] 这样的 code 字符串)
        6|WARRANT_TYPE 窝轮类型|choice  (1=认购、2=认沽、3=牛证、4=熊证、5=界内证；详见 [WarrantType](./quote.md#1724))
        8|CURRENT_PRICE 当前价|interval
        9|STREET_RATIO 街货占比|interval
        10|VOLUME 成交量|interval
        16|LEVERAGE_RATIO 杠杆比率|interval
        19|STATUS 状态|choice  (0=正常、1=终止交易、2=待上市；详见 [WarrantStatus](./quote.md#1724))
        23|EFFECTIVE_LEVERAGE 有效杠杆|interval

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>tuple</td>
            <td>当 ret == RET_OK，返回 (last_page, all_count, DataFrame)</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回 DataFrame 字段（共 45 列）：

        字段|类型|说明
        :-|:-|:-
        issuer_id|int|发行商 ID
        warrant_type|int|窝轮类型  (1=认购，2=认沽，3=牛证，4=熊证，5=界内证)
        strike_price|float|行权价
        maturity_date|str|到期日
        last_trade_date|str|最后交易日
        conversion_ratio|float|换股比率
        last_close_price|float|昨收价
        recovery_price|float|收回价（仅牛熊证）
        stock_owner_price|float|正股价
        current_price|float|现价
        volume|int|成交量
        turnover|float|成交额
        sell_vol|int|卖量
        buy_vol|int|买量
        sell_price|float|卖价
        buy_price|float|买价
        street_rate|float|街货比
        high_price|float|最高价
        low_price|float|最低价
        implied_volatility|float|引伸波幅（仅认购认沽）
        delta|float|对冲值（仅认购认沽）
        status|int|窝轮状态  (0=正常，1=终止交易，2=待上市)
        street_rate_new|float|街货比（新）
        score|float|综合评分
        premium|float|溢价
        leverage|float|杠杆
        effective_leverage|float|有效杠杆
        break_even_point|float|打和点
        ipop|float|价内/价外
        amplitude|float|振幅
        fx_score|float|法兴评分
        ipo_time|str|上市时间
        street_vol|int|街货量
        lot_size|int|每手数量
        issue_size|int|发行量
        ipo_price|float|发行价
        upper_strike_price|float|上限价（仅界内证）
        lower_strike_price|float|下限价（仅界内证）
        iw_price_status|int|界内/界外
        sensitivity|float|敏感度
        price_recovery_ratio|float|正股距收回价（仅牛熊证）
        code|str|窝轮代码，带 market 前缀（如 HK.10001），OpenD 反查标的后填入
        owner_code|str|正股代码，带 market 前缀（如 HK.00700）
        name|str|窝轮名称
        owner_name|str|正股名称

* **Example**

```python
from futu import (
    OpenQuoteContext, RET_OK, WarrantScreenRequest,
    WarrantMarket, WarrantField, WarrantType,
)

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 示例 1：港股低价高杠杆认购证 / 认沽证
req = WarrantScreenRequest(warrant_market=WarrantMarket.HK)
req.add_choice_filter(field_id=WarrantField.WARRANT_TYPE,
                      choices=[WarrantType.CALL, WarrantType.PUT])           # 认购 + 认沽
req.add_interval_filter(field_id=WarrantField.CURRENT_PRICE,
                        min_val=0.1, max_val=5.0)                            # 现价 0.1~5
req.add_interval_filter(field_id=WarrantField.EFFECTIVE_LEVERAGE,
                        min_val=3.0)                                         # 有效杠杆 > 3
req.add_interval_filter(field_id=WarrantField.STREET_RATIO, max_val=50.0)    # 街货占比 < 50%
req.add_sort(field_id=WarrantField.VOLUME, desc=True)                        # 成交量降序
req.page_count = 20

ret, data = quote_ctx.get_warrant_screen(req)
if ret == RET_OK:
    last_page, all_count, df = data
    print(df[['code', 'warrant_type', 'current_price', 'effective_leverage']].head())
else:
    print('error: ', data)

# 示例 2：仅查满足条件的总数
req = WarrantScreenRequest(warrant_market=WarrantMarket.HK)
req.only_count = True
req.add_choice_filter(field_id=WarrantField.WARRANT_TYPE, choices=[WarrantType.CALL])
req.add_interval_filter(field_id=WarrantField.CURRENT_PRICE, min_val=1.0)
ret, data = quote_ctx.get_warrant_screen(req)
if ret == RET_OK:
    _, all_count, _ = data
    print(f"满足条件的认购证总数：{all_count}")

# 示例 3：按正股代码筛选（choice 直接传 code 字符串）
req = WarrantScreenRequest(warrant_market=WarrantMarket.HK)
req.add_choice_filter(field_id=WarrantField.STOCK_OWNER, choices=["HK.00700"])
req.add_choice_filter(field_id=WarrantField.WARRANT_TYPE,
                      choices=[WarrantType.BULL, WarrantType.BEAR])          # 牛证 + 熊证
req.add_sort(field_id=WarrantField.TURNOVER, desc=True)
req.page_count = 50
ret, data = quote_ctx.get_warrant_screen(req)
if ret == RET_OK:
    _, all_count, df = data
    print(f"腾讯牛熊证总数：{all_count}")
    print(df[['code', 'name', 'warrant_type', 'turnover']].head())

quote_ctx.close()
```

* **Output**

```python
       code  warrant_type  current_price  effective_leverage
0  HK.29080             1          0.117               7.070
1  HK.28957             1          0.110               8.021
2  HK.28545             1          0.106               6.807
3  HK.29526             1          0.118               4.337
4  HK.13637             1          0.212               5.896
满足条件的认购证总数：197
腾讯牛熊证总数：393
       code               name  warrant_type    turnover
0  HK.57161  腾讯法兴六乙牛X.C             3  10149350.0
1  HK.54908  腾讯法兴六乙牛R.C             3   9797800.0
2  HK.55573  腾讯华泰六十牛C.C             3   4227400.0
3  HK.53663  腾讯法兴六乙牛N.C             3   3504625.0
4  HK.68433  腾讯法兴六乙牛M.C             3   3018900.0
```

* **字段逐项示例**

    > 以下示例均假设已构造 `req = WarrantScreenRequest(warrant_market=WarrantMarket.HK)`；
    > 实测返回均为 OpenD HK 市场抽样数据，给出该字段对应的 `all_count` 与 DataFrame head（数值已按 SDK 自动倍率换算）。

    ##### `CODE`（id=1 · choice · HK · 无对应返回列） 证券代码 (文本)

    传带市场前缀的 code 字符串数组（如 `"HK.57161"`），SDK 自动剥离前缀；仅命中精确匹配

    ```python
    req.add_choice_filter(WarrantField.CODE, ["HK.57161", "HK.54908", "HK.55573"])
    ```

    实测返回（HK · all_count=3、命中 3 行）：

    ```
           code               name owner_code owner_name  warrant_type  current_price
    0  HK.54908  腾讯法兴六乙牛R.C   HK.00700   腾讯控股             3          0.066
    1  HK.55573  腾讯华泰六十牛C.C   HK.00700   腾讯控股             3          0.080
    2  HK.57161  腾讯法兴六乙牛X.C   HK.00700   腾讯控股             3          0.044
    ```

    ##### `NAME`（id=2 · choice/sort · HK · 无对应返回列） 证券名称 (文本)

    文本字段，仅适合 sort；choice 须传名称字符串

    ```python
    req.add_sort(WarrantField.NAME, desc=False)
    ```

    实测返回（HK · all_count=16170、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  warrant_type  current_price
    0  HK.59177  阿里法巴八十熊G.P   HK.09988     阿里巴巴-W             4          0.290
    1  HK.65875  阿里法巴八十熊H.P   HK.09988     阿里巴巴-W             4          0.024
    2  HK.55774  阿里法巴八十熊I.P   HK.09988     阿里巴巴-W             4          0.203
    3  HK.60642  阿里法巴八五熊D.P   HK.09988     阿里巴巴-W             4          0.157
    4  HK.66020  阿里法巴八五熊E.P   HK.09988     阿里巴巴-W             4          0.173
    ```

    ##### `ISSUER_ID`（id=4 · choice · HK · 返回列 `issuer_id`） 发行商 ID

    仅 HK 可筛选；SG/MY 实测 issuer_id 恒为 0。完整发行商映射见上文 ISSUER_ID 表

    ```python
    req.add_choice_filter(WarrantField.ISSUER_ID, [21])  # 仅瑞通 VT 发行
    req.add_sort(WarrantField.TURNOVER, desc=True)
    ```

    实测返回（HK · all_count=2431、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  issuer_id  warrant_type  current_price
    0  HK.55430  恒指瑞银八十熊B.P  HK.800000       恒生指数         21             4          0.053
    1  HK.57466  恒指瑞银八九牛N.C  HK.800000       恒生指数         21             3          0.037
    2  HK.27921  恒指瑞银六九沽A.P  HK.800000       恒生指数         21             2          0.050
    3  HK.29814  恒指瑞银六甲购A.C  HK.800000       恒生指数         21             1          0.052
    4  HK.56502  恒指瑞银八九牛D.C  HK.800000       恒生指数         21             3          0.054
    ```

    ##### `STOCK_OWNER`（id=5 · choice · HK / SG / MY · 返回列 `owner_code`） 正股 ID

    可直接传 code 字符串列表，例如 ["HK.00700"]

    ```python
    req.add_choice_filter(WarrantField.STOCK_OWNER, ["HK.00700"])
    req.add_sort(WarrantField.TURNOVER, desc=True)
    ```

    实测返回（HK · all_count=844、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  warrant_type  current_price
    0  HK.29080  腾讯国君六甲购B.C   HK.00700       腾讯控股             1          0.117
    1  HK.27892  腾讯摩通六九购E.C   HK.00700       腾讯控股             1          0.058
    2  HK.27966  腾讯法兴六九购D.C   HK.00700       腾讯控股             1          0.060
    3  HK.28957  腾讯法兴六甲购B.C   HK.00700       腾讯控股             1          0.110
    4  HK.29069  腾讯摩通六甲购B.C   HK.00700       腾讯控股             1          0.099
    ```

    ##### `WARRANT_TYPE`（id=6 · choice · HK / SG / MY · 返回列 `warrant_type`） 窝轮类型

    1=认购 2=认沽 3=牛证 4=熊证 5=界内证；SG 实测会返回 6/7、MY 实测会返回 8，未在 SDK 枚举中定义

    ```python
    req.add_choice_filter(WarrantField.WARRANT_TYPE,
                          [WarrantType.BULL, WarrantType.BEAR])
    req.add_sort(WarrantField.TURNOVER, desc=True)
    ```

    实测返回（HK · all_count=7923、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  warrant_type  current_price
    0  HK.55994  恒指摩通九三熊R.P  HK.800000       恒生指数             4          0.056
    1  HK.57003  恒指摩通八九牛8.C  HK.800000       恒生指数             3          0.038
    2  HK.57109  恒指法兴八七牛E.C  HK.800000       恒生指数             3          0.037
    3  HK.55641  恒指法兴八三熊P.P  HK.800000       恒生指数             4          0.055
    4  HK.57114  恒指法兴八九牛7.C  HK.800000       恒生指数             3          0.054
    ```

    ##### `CONVERSION_RATIO`（id=7 · interval · HK / SG / MY · 返回列 `conversion_ratio`） 换股比率

    SDK 直传比率本身（如换股比率 1.0 传 1.0）；协议字段 ×1000 取整传输

    ```python
    req.add_interval_filter(WarrantField.CONVERSION_RATIO, min_val=1.0, max_val=10.0)
    req.add_sort(WarrantField.CONVERSION_RATIO, desc=False)
    ```

    实测返回（HK · all_count=3527、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  conversion_ratio  warrant_type  current_price
    0  HK.15938  利丰瑞信七七购A.C   HK.01818       招金矿业               1.0             1          0.000
    1  HK.15941  平安瑞银七甲沽B.P   HK.02318       中国平安               1.0             1          0.000
    2  HK.25738  首程麦银六八购A.C   HK.00697       首程控股               1.0             1          0.016
    3  HK.15190    中核信证六二购B   HK.01816      中广核电力               1.0             1          0.000
    4  HK.17771  置富麦银六八购A.C   HK.00778     置富产业信托               1.0             1          0.015
    ```

    ##### `CURRENT_PRICE`（id=8 · interval · HK / SG / MY · 返回列 `current_price`） 当前价

    单位：元；SDK 直传原始价（协议字段 ×1000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.CURRENT_PRICE, min_val=0.1, max_val=0.15)
    req.add_sort(WarrantField.CURRENT_PRICE, desc=False)
    ```

    实测返回（HK · all_count=1719、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  current_price  warrant_type
    0  HK.65586  中移花旗六九牛C.C   HK.00941       中国移动            0.1             3
    1  HK.67749  阿里瑞银六六牛B.C   HK.09988     阿里巴巴-W            0.1             3
    2  HK.69293  港交汇丰七甲牛A.C   HK.00388      香港交易所            0.1             3
    3  HK.56800  恒指信证七九牛U.C  HK.800000       恒生指数            0.1             3
    4  HK.57184  恒指法兴八三牛A.C  HK.800000       恒生指数            0.1             3
    ```

    ##### `STREET_RATIO`（id=9 · interval · HK / SG / MY · 返回列 `street_rate`） 街货占比

    单位：%；SDK 直传如 50.0（协议字段 ×1000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.STREET_RATIO, min_val=10.0, max_val=50.0)
    req.add_sort(WarrantField.STREET_RATIO, desc=False)
    ```

    实测返回（HK · all_count=1918、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  street_rate  warrant_type  current_price
    0  HK.27205  腾讯瑞银八乙购A.C   HK.00700       腾讯控股        10.00             1          0.233
    1  HK.63380  恒指中银八三熊I.P  HK.800000       恒生指数        10.00             4          0.335
    2  HK.60023  恒指国君七乙牛S.C  HK.800000       恒生指数        10.01             3          0.193
    3  HK.21640  飞鹤华泰六七购A.C   HK.06186       中国飞鹤        10.01             1          0.010
    4  HK.25461  恒指瑞银六七购A.C  HK.800000       恒生指数        10.01             1          0.010
    ```

    ##### `VOLUME`（id=10 · interval · HK / SG / MY · 返回列 `volume`） 成交量

    单位：股

    ```python
    req.add_interval_filter(WarrantField.VOLUME, min_val=1000)
    req.add_sort(WarrantField.VOLUME, desc=True)
    ```

    实测返回（HK · all_count=6092、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name       volume  warrant_type  current_price
    0  HK.55994  恒指摩通九三熊R.P  HK.800000       恒生指数  20257030000             4          0.056
    1  HK.55641  恒指法兴八三熊P.P  HK.800000       恒生指数  18202610000             4          0.055
    2  HK.57109  恒指法兴八七牛E.C  HK.800000       恒生指数  17612080000             3          0.037
    3  HK.57003  恒指摩通八九牛8.C  HK.800000       恒生指数  16576470000             3          0.038
    4  HK.55430  恒指瑞银八十熊B.P  HK.800000       恒生指数  12932700000             4          0.053
    ```

    ##### `MATURITY_DATE`（id=11 · interval · HK / SG / MY · 返回列 `maturity_date`） 到期日 (时间戳秒)

    Unix 秒级时间戳；返回 maturity_date 也是字符串型时间戳

    ```python
    import time
    req.add_interval_filter(WarrantField.MATURITY_DATE,
                            min_val=int(time.time()),
                            max_val=int(time.time()) + 365*86400)
    req.add_sort(WarrantField.MATURITY_DATE, desc=False)
    ```

    实测返回（HK · all_count=9330、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  maturity_date  warrant_type  current_price
    0  HK.21145  金云摩利六六购A.C   HK.03896        金山云     1781539200             1          0.010
    1  HK.54786  百度瑞银六六牛B.C   HK.09888    百度集团-SW     1781539200             3          0.305
    2  HK.23342  优必中银六六购B.C   HK.09880        优必选     1781539200             1          0.010
    3  HK.23574  汇量华泰六六购A.C   HK.01860       汇量科技     1781539200             1          0.010
    4  HK.18353  美高摩通六六购A.C   HK.02282      美高梅中国     1781625600             1          0.010
    ```

    ##### `STRIKE_PRICE`（id=12 · interval · HK / SG / MY · 返回列 `strike_price`） 行使价

    单位：元；SDK 直传原始价（协议字段 ×1000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.STRIKE_PRICE, min_val=10.0, max_val=20.0)
    req.add_sort(WarrantField.STRIKE_PRICE, desc=False)
    ```

    实测返回（HK · all_count=990、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  strike_price  warrant_type  current_price
    0  HK.19876  喜相华泰六八购A.C   HK.02473      喜相逢集团          10.0             1          0.010
    1  HK.23889  中油法巴六七购A.C   HK.00857     中国石油股份          10.0             1          0.153
    2  HK.11055  英港摩通六七沽A.P        N/A        N/A          10.0             2          0.051
    3  HK.25258  中联花旗六八购A.C   HK.00762       中国联通          10.0             1          0.014
    4  HK.27520  新发信证七三购A.C   HK.00017      新世界发展          10.0             1          0.107
    ```

    ##### `PREMIUM`（id=13 · interval · HK / SG / MY · 返回列 `premium`） 溢价

    单位：%；SDK 直传如 15.0，可为负（协议字段 ×100000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.PREMIUM, min_val=0.0, max_val=20.0)
    req.add_sort(WarrantField.PREMIUM, desc=False)
    ```

    实测返回（HK · all_count=11283、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  premium  warrant_type  current_price
    0  HK.21137  恒大中银八七购A.C        N/A        N/A      0.0             1          0.000
    1  HK.16449  恒生中银九乙购A.C        N/A        N/A      0.0             1          0.000
    2  HK.16512  恒指高盛九九沽J.P   HK.06688       蚂蚁集团      0.0             1          0.000
    3  HK.16522  恒指瑞通九十沽A.P   HK.06688       蚂蚁集团      0.0             1          0.000
    4  HK.68392  招行瑞银六八牛A.C   HK.03968       招商银行      0.0             3          0.238
    ```

    ##### `RECOVERY_PRICE`（id=14 · interval · HK / SG / MY · 返回列 `recovery_price`） 收回价

    单位：元；SDK 直传原始价；仅牛熊证(3/4)有效（协议字段 ×1000 取整传输）

    ```python
    req.add_choice_filter(WarrantField.WARRANT_TYPE,
                          [WarrantType.BULL, WarrantType.BEAR])
    req.add_interval_filter(WarrantField.RECOVERY_PRICE, min_val=0.01)
    req.add_sort(WarrantField.RECOVERY_PRICE, desc=False)
    ```

    实测返回（HK · all_count=7923、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  recovery_price  warrant_type  current_price
    0  HK.59404  商汤瑞银七八牛D.C   HK.00020       商汤-W            1.00             3          0.062
    1  HK.64826  商汤法兴七五牛A.C   HK.00020       商汤-W            1.05             3          0.113
    2  HK.59403  商汤瑞银七八牛C.C   HK.00020       商汤-W            1.10             3          0.053
    3  HK.64933  商汤瑞银六乙牛A.C   HK.00020       商汤-W            1.20             3          0.074
    4  HK.59322    商汤汇丰七一牛A   HK.00020       商汤-W            1.20             3          0.000
    ```

    ##### `IMPLIED_VOLATILITY`（id=15 · interval · HK / SG / MY · 返回列 `implied_volatility`） 引伸波幅

    单位：%；SDK 直传如 15.0；仅认购认沽(1/2)有效（协议字段 ×100 取整传输）

    ```python
    req.add_interval_filter(WarrantField.IMPLIED_VOLATILITY, min_val=10.0, max_val=100.0)
    req.add_sort(WarrantField.IMPLIED_VOLATILITY, desc=False)
    ```

    实测返回（HK · all_count=5962、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  implied_volatility  warrant_type  current_price
    0  HK.24413  中移中银六九购A.C   HK.00941       中国移动              13.487             1          0.041
    1  HK.25984  建行韩投八乙购A.C   HK.00939       建设银行              14.638             1          0.500
    2  HK.25450  中移国君六九购A.C   HK.00941       中国移动              15.308             1          0.054
    3  HK.24942  中移汇丰六九购A.C   HK.00941       中国移动              15.776             1          0.059
    4  HK.14414  建行法巴六乙购A.C   HK.00939       建设银行              15.792             1          0.191
    ```

    ##### `LEVERAGE_RATIO`（id=16 · interval · HK / SG / MY · 返回列 `leverage`） 杠杆比率

    SDK 直传原始值（协议字段 ×1000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.LEVERAGE_RATIO, min_val=3.0, max_val=50.0)
    req.add_sort(WarrantField.LEVERAGE_RATIO, desc=True)
    ```

    实测返回（HK · all_count=8360、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  leverage  warrant_type  current_price
    0  HK.29999  恒指中银六乙购C.C  HK.800000       恒生指数    49.985             1          0.071
    1  HK.27121  领展瑞银六九购A.C   HK.00823     领展房产基金    49.972             1          0.074
    2  HK.15343  百度摩通六八沽A.P   HK.09888    百度集团-SW    49.869             2          0.023
    3  HK.25973  远能麦银六八购A.C   HK.01138       中远海能    49.852             1          0.068
    4  HK.26365  远能麦银六九购A.C   HK.01138       中远海能    49.852             1          0.034
    ```

    ##### `PRICE_RECOVERY_RATIO`（id=17 · interval · HK / SG / MY · 返回列 `price_recovery_ratio`） 正股距收回价 %

    单位：%；SDK 直传如 15.0，可为负；仅牛熊证(3/4)有效（协议字段 ×100000 取整传输）

    ```python
    req.add_choice_filter(WarrantField.WARRANT_TYPE,
                          [WarrantType.BULL, WarrantType.BEAR])
    req.add_interval_filter(WarrantField.PRICE_RECOVERY_RATIO,
                            min_val=-50.0, max_val=50.0)
    req.add_sort(WarrantField.PRICE_RECOVERY_RATIO, desc=False)
    ```

    实测返回（HK · all_count=7923、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  price_recovery_ratio  warrant_type  current_price
    0  HK.54832  美团瑞银七乙熊M.P   HK.03690       美团-W              -0.73916             4          0.430
    1  HK.53329  美团瑞银七乙熊I.P   HK.03690       美团-W              -0.72053             4          0.390
    2  HK.54269  美团摩通七九熊F.P   HK.03690       美团-W              -0.72053             4          0.395
    3  HK.54562  美团汇丰七乙熊D.P   HK.03690       美团-W              -0.71018             4          0.370
    4  HK.54799  美团摩通七乙熊D.P   HK.03690       美团-W              -0.71018             4          0.370
    ```

    ##### `DELTA`（id=18 · interval · HK / SG / MY · 返回列 `delta`） 对冲值

    SDK 直传原始值，范围 [-1, 1]；仅认购认沽(1/2)有效（协议字段 ×1000 取整传输）

    ```python
    req.add_choice_filter(WarrantField.WARRANT_TYPE,
                          [WarrantType.CALL, WarrantType.PUT])
    req.add_interval_filter(WarrantField.DELTA, min_val=-1.0, max_val=1.0)
    req.add_sort(WarrantField.DELTA, desc=True)
    ```

    实测返回（HK · all_count=8247、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  delta  warrant_type  current_price
    0  HK.16281  联想信证六六购A.C   HK.00992       联想集团  0.999             1           1.28
    1  HK.18636  中寿国君六六购A.C   HK.02628       中国人寿  0.999             1           0.59
    2  HK.22934  建滔华泰六八购A.C   HK.00148       建滔集团  0.997             1           6.73
    3  HK.19057  汇丰摩利六七购A.C   HK.00005       汇丰控股  0.996             1           0.87
    4  HK.19058  汇丰法兴六七购A.C   HK.00005       汇丰控股  0.996             1           0.87
    ```

    ##### `STATUS`（id=19 · choice · HK / SG / MY · 返回列 `status`） 轮证状态

    0=正常 1=终止交易 2=待上市

    ```python
    req.add_choice_filter(WarrantField.STATUS, [WarrantStatus.NORMAL])
    req.add_sort(WarrantField.VOLUME, desc=True)
    ```

    实测返回（HK · all_count=13057、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  status  warrant_type  current_price
    0  HK.55994  恒指摩通九三熊R.P  HK.800000       恒生指数       0             4          0.056
    1  HK.55641  恒指法兴八三熊P.P  HK.800000       恒生指数       0             4          0.055
    2  HK.57109  恒指法兴八七牛E.C  HK.800000       恒生指数       0             3          0.037
    3  HK.57003  恒指摩通八九牛8.C  HK.800000       恒生指数       0             3          0.038
    4  HK.55430  恒指瑞银八十熊B.P  HK.800000       恒生指数       0             4          0.053
    ```

    ##### `IPO_TIME`（id=20 · interval · HK / SG / MY · 返回列 `ipo_time`） 上市时间 (时间戳秒)

    Unix 秒级时间戳

    ```python
    req.add_interval_filter(WarrantField.IPO_TIME,
                            min_val=1700000000, max_val=2000000000)
    req.add_sort(WarrantField.IPO_TIME, desc=True)
    ```

    实测返回（HK · all_count=16122、命中 5 行、head 前 5）：

    ```
           code      name owner_code owner_name    ipo_time  warrant_type  current_price
    0  HK.11203  道指摩通六乙沽B    US..DJI      道琼斯指数  1781625600             2            0.0
    1  HK.11204  纳指摩通六乙沽C    US..NDX  纳斯达克100指数  1781625600             2            0.0
    2  HK.11205  道指摩通六乙沽C    US..DJI      道琼斯指数  1781625600             2            0.0
    3  HK.13826  老铺摩利六乙沽A   HK.06181       老铺黄金  1781625600             2            0.0
    4  HK.13827  港交摩利六乙沽A   HK.00388      香港交易所  1781625600             2            0.0
    ```

    ##### `BUY_VOL`（id=21 · interval · HK / SG / MY · 返回列 `buy_vol`） 买量

    单位：股

    ```python
    req.add_interval_filter(WarrantField.BUY_VOL, min_val=1)
    req.add_sort(WarrantField.BUY_VOL, desc=True)
    ```

    实测返回（HK · all_count=10554、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name   buy_vol  warrant_type  current_price
    0  HK.56746  恒指汇丰八甲牛V.C  HK.800000       恒生指数  41410000             3          0.065
    1  HK.56560  恒指摩通八三牛G.C  HK.800000       恒生指数  40730000             3          0.114
    2  HK.63929  恒指摩利八十牛E.C  HK.800000       恒生指数  40380000             3          0.102
    3  HK.64852  恒指瑞银八十牛G.C  HK.800000       恒生指数  40000000             3          0.131
    4  HK.29035  泡玛星展六甲沽A.P   HK.09992       泡泡玛特  40000000             2          0.071
    ```

    ##### `SELL_VOL`（id=22 · interval · HK / SG / MY · 返回列 `sell_vol`） 卖量

    单位：股

    ```python
    req.add_interval_filter(WarrantField.SELL_VOL, min_val=1)
    req.add_sort(WarrantField.SELL_VOL, desc=True)
    ```

    实测返回（HK · all_count=11581、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  sell_vol  warrant_type  current_price
    0  HK.26774  阿里法巴六七购B.C   HK.09988     阿里巴巴-W  60130000             1          0.010
    1  HK.29035  泡玛星展六甲沽A.P   HK.09992       泡泡玛特  37900000             2          0.071
    2  HK.55588  恒指汇丰九四熊D.P  HK.800000       恒生指数  34110000             4          0.055
    3  HK.56458  恒指摩通八九牛4.C  HK.800000       恒生指数  33830000             3          0.064
    4  HK.57114  恒指法兴八九牛7.C  HK.800000       恒生指数  33370000             3          0.054
    ```

    ##### `EFFECTIVE_LEVERAGE`（id=23 · interval · HK / SG / MY · 返回列 `effective_leverage`） 有效杠杆

    SDK 直传原始值（协议字段 ×1000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.EFFECTIVE_LEVERAGE, min_val=3.0, max_val=50.0)
    req.add_sort(WarrantField.EFFECTIVE_LEVERAGE, desc=True)
    ```

    实测返回（HK · all_count=5409、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  effective_leverage  warrant_type  current_price
    0  HK.23821  建行国君六六购A.C   HK.00939       建设银行              47.082             1          0.102
    1  HK.25486  华地信证六六购B.C   HK.01109       华润置地              45.821             1          0.010
    2  HK.23727  领展信证六六购A.C   HK.00823     领展房产基金              44.375             1          0.012
    3  HK.23398  建行麦银六六购A.C   HK.00939       建设银行              42.977             1          0.017
    4  HK.23575  华地摩通六六购A.C   HK.01109       华润置地              42.093             1          0.012
    ```

    ##### `LAST_CLOSE_PRICE`（id=24 · interval · HK / SG / MY · 返回列 `last_close_price`） 昨收价

    单位：元；SDK 直传原始价（协议字段 ×1000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.LAST_CLOSE_PRICE, min_val=0.1, max_val=2.0)
    req.add_sort(WarrantField.LAST_CLOSE_PRICE, desc=False)
    ```

    实测返回（HK · all_count=7028、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  last_close_price  warrant_type  current_price
    0  HK.14210  腾讯花旗六乙沽A.P   HK.00700       腾讯控股               0.1             2          0.101
    1  HK.67749  阿里瑞银六六牛B.C   HK.09988     阿里巴巴-W               0.1             3          0.100
    2  HK.53182  平安汇丰七甲牛L.C   HK.02318       中国平安               0.1             3          0.107
    3  HK.69230  平安法兴七十牛U.C   HK.02318       中国平安               0.1             3          0.105
    4  HK.56325  恒指法兴八三牛8.C  HK.800000       恒生指数               0.1             3          0.119
    ```

    ##### `TURNOVER`（id=25 · interval · HK / SG / MY · 返回列 `turnover`） 成交额

    单位：元

    ```python
    req.add_interval_filter(WarrantField.TURNOVER, min_val=1)
    req.add_sort(WarrantField.TURNOVER, desc=True)
    ```

    实测返回（HK · all_count=6093、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name     turnover  warrant_type  current_price
    0  HK.55994  恒指摩通九三熊R.P  HK.800000       恒生指数  864568920.0             4          0.056
    1  HK.57003  恒指摩通八九牛8.C  HK.800000       恒生指数  852463370.0             3          0.038
    2  HK.57109  恒指法兴八七牛E.C  HK.800000       恒生指数  842853250.0             3          0.037
    3  HK.55641  恒指法兴八三熊P.P  HK.800000       恒生指数  777372600.0             4          0.055
    4  HK.57114  恒指法兴八九牛7.C  HK.800000       恒生指数  608277730.0             3          0.054
    ```

    ##### `SELL_PRICE`（id=26 · interval · HK / SG / MY · 返回列 `sell_price`） 卖价

    单位：元；SDK 直传原始价（协议字段 ×1000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.SELL_PRICE, min_val=0.001)
    req.add_sort(WarrantField.SELL_PRICE, desc=False)
    ```

    实测返回（HK · all_count=11581、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  sell_price  warrant_type  current_price
    0  HK.23665  S金摩通六七购A.C   HK.02840      SPDR金        0.01             1           0.01
    1  HK.25680  百度麦银六七购A.C   HK.09888    百度集团-SW        0.01             1           0.01
    2  HK.27365  中交法兴六六购A.C   HK.01800     中国交通建设        0.01             1           0.01
    3  HK.28314  铁塔信证六九购A.C   HK.00788       中国铁塔        0.01             1           0.01
    4  HK.28806  协鑫麦银六九购A.C   HK.03800       协鑫科技        0.01             1           0.01
    ```

    ##### `BUY_PRICE`（id=27 · interval · HK / SG / MY · 返回列 `buy_price`） 买价

    单位：元；SDK 直传原始价（协议字段 ×1000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.BUY_PRICE, min_val=0.001)
    req.add_sort(WarrantField.BUY_PRICE, desc=False)
    ```

    实测返回（HK · all_count=10554、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  buy_price  warrant_type  current_price
    0  HK.13598  小米摩通六乙购B.C   HK.01810     小米集团-W       0.01             1          0.010
    1  HK.14635  比迪星展六甲购A.C   HK.01211      比亚迪股份       0.01             1          0.010
    2  HK.14652  腾讯法兴六九购A.C   HK.00700       腾讯控股       0.01             1          0.011
    3  HK.16396  南科信证六乙购A.C   HK.03033     南方恒生科技       0.01             1          0.014
    4  HK.17724  泡玛汇丰六甲购A.C   HK.09992       泡泡玛特       0.01             1          0.012
    ```

    ##### `HIGH_PRICE`（id=28 · interval · HK / SG / MY · 返回列 `high_price`） 最高价

    单位：元；SDK 直传原始价；日内最高（协议字段 ×1000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.HIGH_PRICE, min_val=0.001)
    req.add_sort(WarrantField.HIGH_PRICE, desc=True)
    ```

    实测返回（HK · all_count=6075、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  high_price  warrant_type  current_price
    0  HK.11115  美光法兴六甲购A.C        N/A        N/A        6.74             1           6.74
    1  HK.24047  建板摩利六七购A.C   HK.01888      建滔积层板        6.47             1           6.47
    2  HK.25060  建滔华泰六八购B.C   HK.00148       建滔集团        5.67             1           5.65
    3  HK.16544  建板信证六十购A.C   HK.01888      建滔积层板        5.57             1           5.57
    4  HK.26175  建板汇丰六八购A.C   HK.01888      建滔积层板        5.44             1           5.44
    ```

    ##### `LOW_PRICE`（id=29 · interval · HK / SG / MY · 返回列 `low_price`） 最低价

    单位：元；SDK 直传原始价；日内最低（协议字段 ×1000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.LOW_PRICE, min_val=0.001)
    req.add_sort(WarrantField.LOW_PRICE, desc=False)
    ```

    实测返回（HK · all_count=6075、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  low_price  warrant_type  current_price
    0  HK.28933  阿里麦银六七购A.C   HK.09988     阿里巴巴-W       0.01             1           0.01
    1  HK.29014  阿里法兴六六购A.C   HK.09988     阿里巴巴-W       0.01             1           0.01
    2  HK.13598  小米摩通六乙购B.C   HK.01810     小米集团-W       0.01             1           0.01
    3  HK.13662  中联麦银六九购A.C   HK.00762       中国联通       0.01             1           0.01
    4  HK.14148  腾讯汇丰六七购A.C   HK.00700       腾讯控股       0.01             1           0.01
    ```

    ##### `RATIO_ITM_OTM`（id=30 · interval · HK / SG / MY · 返回列 `ipop`） 价内/价外 %

    单位：%；SDK 直传如 15.0，可为负；返回列名为 ipop（协议字段 ×100000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.RATIO_ITM_OTM, min_val=-50.0, max_val=50.0)
    req.add_sort(WarrantField.RATIO_ITM_OTM, desc=False)
    ```

    实测返回（HK · all_count=16166、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name      ipop  warrant_type  current_price
    0  HK.21173  信达海通八七购A.C   HK.01359       中国信达 -41.74285             1          0.000
    1  HK.21158  华泥瑞信八七购A.C   HK.01313     华润建材科技 -41.68907             1          0.000
    2  HK.25100  喜相摩通六六购A.C   HK.02473      喜相逢集团 -37.67187             1          0.061
    3  HK.25841  喜相麦银六七购A.C   HK.02473      喜相逢集团 -37.64062             1          0.025
    4  HK.15946  信达瑞信七六购A.C   HK.01359       中国信达 -37.40952             1          0.000
    ```

    ##### `BREAK_EVEN_POINT`（id=31 · interval · HK / SG / MY · 返回列 `break_even_point`） 打和点 %

    单位：%；SDK 直传如 15.0（协议字段 ×100000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.BREAK_EVEN_POINT, min_val=-100.0, max_val=100.0)
    req.add_sort(WarrantField.BREAK_EVEN_POINT, desc=False)
    ```

    实测返回（HK · all_count=11618、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  break_even_point  warrant_type  current_price
    0  HK.21137  恒大中银八七购A.C        N/A        N/A               0.0             1          0.000
    1  HK.16449  恒生中银九乙购A.C        N/A        N/A               0.0             1          0.000
    2  HK.49942  道指汇丰六乙熊H.P    US..DJI      道琼斯指数               0.0             4          0.013
    3  HK.49950  道指瑞银六乙熊L.P    US..DJI      道琼斯指数               0.0             4          0.012
    4  HK.29859  东风麦银六六购A.C        N/A        N/A               0.0             1          0.720
    ```

    ##### `AMPLITUDE`（id=32 · interval · HK / SG / MY · 返回列 `amplitude`） 振幅 %

    单位：%；SDK 直传如 15.0（协议字段 ×100000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.AMPLITUDE, min_val=0.01)
    req.add_sort(WarrantField.AMPLITUDE, desc=True)
    ```

    实测返回（HK · all_count=5358、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  amplitude  warrant_type  current_price
    0  HK.23936  舜光信证六六购A.C   HK.02382     舜宇光学科技    3.80000             1          0.054
    1  HK.23432  舜光摩利六六购A.C   HK.02382     舜宇光学科技    3.27273             1          0.055
    2  HK.24022  舜光花旗六六购A.C   HK.02382     舜宇光学科技    3.00000             1          0.058
    3  HK.20335  江铜摩通六六购A.C   HK.00358     江西铜业股份    2.24390             1          0.181
    4  HK.61517  中芯法兴六甲牛H.C   HK.00981       中芯国际    2.00000             3          0.076
    ```

    ##### `SCORE_FAXING`（id=33 · interval · HK / SG / MY · 返回列 `fx_score`） 法兴评分

    SDK 直传原始评分；返回列名为 fx_score（协议字段 ×100000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.SCORE_FAXING, min_val=0.0, max_val=10.0)
    req.add_sort(WarrantField.SCORE_FAXING, desc=True)
    ```

    实测返回（HK · all_count=16170、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  fx_score  warrant_type  current_price
    0  HK.29442  中药法巴七五购A.C   HK.01177     中国生物制药   0.94860             1          0.071
    1  HK.13660  建滔法兴七一购B.C   HK.00148       建滔集团   0.94397             1          0.193
    2  HK.29636  美图摩通六甲购A.C   HK.01357       美图公司   0.93674             1          0.127
    3  HK.24961  中移摩通六九购A.C   HK.00941       中国移动   0.93553             1          0.070
    4  HK.21241  兖矿摩通六八购A.C   HK.01171       兖矿能源   0.93449             1          0.202
    ```

    ##### `LAST_TRADE_DATE`（id=34 · interval · HK / SG / MY · 返回列 `last_trade_date`） 最后交易日 (时间戳秒)

    Unix 秒级时间戳；通常比 MATURITY_DATE 早 1 个交易日

    ```python
    req.add_interval_filter(WarrantField.LAST_TRADE_DATE,
                            min_val=1900000000, max_val=2200000000)
    req.add_sort(WarrantField.LAST_TRADE_DATE, desc=False)
    ```

    实测返回（HK · all_count=1、命中 1 行、head 前 5）：

    ```
           code        name owner_code owner_name  last_trade_date  warrant_type  current_price
    0  HK.29183  建行法巴零乙购A.C   HK.00939       建设银行       1924272000             1          0.237
    ```

    ##### `STREET_VOLUME`（id=35 · interval · HK / SG / MY · 返回列 `street_vol`） 街货量

    单位：股；返回列名为 street_vol

    ```python
    req.add_interval_filter(WarrantField.STREET_VOLUME, min_val=1)
    req.add_sort(WarrantField.STREET_VOLUME, desc=True)
    ```

    实测返回（HK · all_count=11611、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  street_vol  warrant_type  current_price
    0  HK.14958  腾讯法兴六七购A.C   HK.00700       腾讯控股   400000000             1          0.010
    1  HK.14826  腾讯摩通六七购A.C   HK.00700       腾讯控股   398760000             1          0.010
    2  HK.25097  腾讯摩通六九购A.C   HK.00700       腾讯控股   319360000             1          0.012
    3  HK.13039  小米摩通六乙购A.C   HK.01810     小米集团-W   306960000             1          0.017
    4  HK.14148  腾讯汇丰六七购A.C   HK.00700       腾讯控股   300000000             1          0.010
    ```

    ##### `LOT_SIZE`（id=36 · interval · HK / SG / MY · 返回列 `lot_size`） 每手股数

    单位：股

    ```python
    req.add_interval_filter(WarrantField.LOT_SIZE, min_val=1)
    req.add_sort(WarrantField.LOT_SIZE, desc=False)
    ```

    实测返回（HK · all_count=16170、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  lot_size  warrant_type  current_price
    0  HK.22588  万科麦银六六购B.C   HK.02202       万科企业       100             1          0.010
    1  HK.24402  航赁麦银六七购A.C   HK.02588     中银航空租赁       100             1          0.019
    2  HK.24702  航赁华泰六七购A.C   HK.02588     中银航空租赁       100             1          0.010
    3  HK.27072  蔚来麦银六九沽A.P   HK.09866      蔚来-SW       100             2          0.071
    4  HK.19866  南科华泰六六购A.C   HK.03033     南方恒生科技       200             1          0.010
    ```

    ##### `ISSUE_SIZE`（id=37 · interval · HK / SG / MY · 返回列 `issue_size`） 发行量

    单位：股

    ```python
    req.add_interval_filter(WarrantField.ISSUE_SIZE, min_val=1)
    req.add_sort(WarrantField.ISSUE_SIZE, desc=True)
    ```

    实测返回（HK · all_count=16170、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  issue_size  warrant_type  current_price
    0  HK.22659  阿里韩投八乙购A.C   HK.09988     阿里巴巴-W   500000000             1          0.370
    1  HK.16737  宁德法兴七乙购A.C   HK.03750       宁德时代   500000000             1          0.880
    2  HK.13850    恒指摩通六乙沽C  HK.800000       恒生指数   500000000             2          0.000
    3  HK.22235  港交韩投八八购A.C   HK.00388      香港交易所   480000000             1          0.325
    4  HK.22254  中移韩投八八购A.C   HK.00941       中国移动   480000000             1          0.162
    ```

    ##### `IPO_PRICE`（id=38 · interval · HK / SG / MY · 返回列 `ipo_price`） 发行价

    单位：元；SDK 直传原始价（协议字段 ×1000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.IPO_PRICE, min_val=0.001)
    req.add_sort(WarrantField.IPO_PRICE, desc=False)
    ```

    实测返回（HK · all_count=0、命中 0 行）：无数据。原因：OpenD 实测多数窝轮 ipo_price 返回 0，导致 min_val=0.001 过滤后无数据

    ##### `LOWER_STRIKE_PRICE`（id=39 · interval · HK / SG / MY · 返回列 `lower_strike_price`） 下限价

    单位：元；SDK 直传原始价；仅界内证(5)有效（协议字段 ×1000 取整传输）

    ```python
    req.add_choice_filter(WarrantField.WARRANT_TYPE, [WarrantType.IW])
    req.add_interval_filter(WarrantField.LOWER_STRIKE_PRICE, min_val=0.001)
    req.add_sort(WarrantField.LOWER_STRIKE_PRICE, desc=False)
    ```

    实测返回（HK · all_count=0、命中 0 行）：无数据。原因：HK 当前无界内证（IW）上市，按窝轮类型筛选后无数据

    ##### `UPPER_STRIKE_PRICE`（id=40 · interval · HK / SG / MY · 返回列 `upper_strike_price`） 上限价

    单位：元；SDK 直传原始价；仅界内证(5)有效（协议字段 ×1000 取整传输）

    ```python
    req.add_choice_filter(WarrantField.WARRANT_TYPE, [WarrantType.IW])
    req.add_interval_filter(WarrantField.UPPER_STRIKE_PRICE, min_val=0.001)
    req.add_sort(WarrantField.UPPER_STRIKE_PRICE, desc=False)
    ```

    实测返回（HK · all_count=0、命中 0 行）：无数据。原因：HK 当前无界内证（IW）上市，按窝轮类型筛选后无数据

    ##### `IW_PRICE_STATUS`（id=41 · choice · HK / SG / MY · 返回列 `iw_price_status`） 界内/界外

    0=界外 1=界内；仅界内证(5)返回非 0 值

    ```python
    req.add_choice_filter(WarrantField.WARRANT_TYPE, [WarrantType.IW])
    ```

    实测返回（HK · all_count=0、命中 0 行）：无数据。原因：HK 当前无界内证（IW）上市，按窝轮类型筛选后无数据

    ##### `SENSITIVITY`（id=42 · interval · HK / SG / MY · 返回列 `sensitivity`） 敏感度

    SDK 直传原始值（协议字段 ×1000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.SENSITIVITY, min_val=0.001)
    req.add_sort(WarrantField.SENSITIVITY, desc=False)
    ```

    实测返回（HK · all_count=13623、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  sensitivity  warrant_type  current_price
    0  HK.19340  腾音信证六九购A.C   HK.01698    腾讯音乐-SW        0.018             1          0.010
    1  HK.28495  稀宇麦银六十购B.C   HK.00100  MINIMAX-W        0.019             1          0.013
    2  HK.51984  美团瑞银七乙熊G.P   HK.03690       美团-W        0.020             4          0.275
    3  HK.52261  美团法巴七七熊K.P   HK.03690       美团-W        0.020             4          0.280
    4  HK.52532  美团瑞银七乙熊H.P   HK.03690       美团-W        0.020             4          0.310
    ```

    ##### `CONVERSION_PRICE`（id=43 · interval · HK / SG / MY · 无对应返回列） 换股价

    未在返回 DataFrame 单独暴露；可用作筛选 / 排序条件

    ```python
    req.add_interval_filter(WarrantField.CONVERSION_PRICE, min_val=0.001)
    req.add_sort(WarrantField.CONVERSION_PRICE, desc=False)
    ```

    实测返回（HK · all_count=16170、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  warrant_type  current_price
    0  HK.64814  平安瑞银八三牛A.C   HK.02318       中国平安             3            0.0
    1  HK.15946  信达瑞信七六购A.C   HK.01359       中国信达             1            0.0
    2  HK.24719    腾讯东亚九四沽A   HK.00700       腾讯控股             2            0.0
    3  HK.26168    金软瑞银九二购B   HK.03888       金山软件             1            0.0
    4  HK.64492  恒指汇丰八五熊G.P  HK.800000       恒生指数             3            0.0
    ```

    ##### `CHANGE_RATE`（id=44 · interval · HK / SG / MY · 无对应返回列） 涨跌幅 %

    单位：%；SDK 直传如 5.0；未在返回 DataFrame 单独暴露（协议字段 ×1000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.CHANGE_RATE, min_val=-100.0, max_val=100.0)
    req.add_sort(WarrantField.CHANGE_RATE, desc=True)
    ```

    实测返回（HK · all_count=16170、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  warrant_type  current_price
    0  HK.25160  远能华泰六七购B.C   HK.01138       中远海能             1          0.136
    1  HK.23936  舜光信证六六购A.C   HK.02382     舜宇光学科技             1          0.054
    2  HK.25876  远能华泰六八购A.C   HK.01138       中远海能             1          0.093
    3  HK.23432  舜光摩利六六购A.C   HK.02382     舜宇光学科技             1          0.055
    4  HK.26285  远能华泰六九购B.C   HK.01138       中远海能             1          0.048
    ```

    ##### `CHANGE_VALUE`（id=45 · interval · HK / SG / MY · 无对应返回列） 涨跌额

    单位：元；未在返回 DataFrame 单独暴露

    ```python
    req.add_interval_filter(WarrantField.CHANGE_VALUE, min_val=-1.0, max_val=1.0)
    req.add_sort(WarrantField.CHANGE_VALUE, desc=True)
    ```

    实测返回（HK · all_count=7641、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  warrant_type  current_price
    0  HK.25336  铁塔摩利六乙购A.C   HK.00788       中国铁塔             1          0.017
    1  HK.25366  铁塔摩通六乙购A.C   HK.00788       中国铁塔             1          0.028
    2  HK.26138  铁塔中银六乙购A.C   HK.00788       中国铁塔             1          0.027
    3  HK.26447  中铁法兴六九购A.C   HK.00390       中国中铁             1          0.020
    4  HK.67330  京东摩通六乙牛A.C   HK.09618    京东集团-SW             3          0.216
    ```

    ##### `SCORE`（id=51 · interval · HK / SG / MY · 返回列 `score`） Warrant 评分

    综合评分；SDK 直传原始分（协议字段 ×100000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.SCORE, min_val=0.0, max_val=10.0)
    req.add_sort(WarrantField.SCORE, desc=True)
    ```

    实测返回（HK · all_count=16170、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  score  warrant_type  current_price
    0  HK.11048  澳港摩通六七购A.C        N/A        N/A  0.010             1          0.195
    1  HK.11056  欧港摩通六七购A.C        N/A        N/A  0.009             1          0.016
    2  HK.49582  标指摩通六九牛B.C    US..SPX    标普500指数  0.009             3          0.193
    3  HK.10087  美日摩通六六购A.C  FX.USDJPY      美元/日元  0.008             1          0.073
    4  HK.11047  澳港摩通六七沽A.P        N/A        N/A  0.008             2          0.013
    ```

    ##### `FILTER_NO_TRADE`（id=52 · choice · HK / SG / MY · 返回列 `current_price`） 过滤无成交窝轮

    开关字段：0=不过滤 1=过滤掉成交量为 0 的窝轮；不返回数据列

    ```python
    req.add_choice_filter(WarrantField.FILTER_NO_TRADE, [1])
    req.add_sort(WarrantField.VOLUME, desc=True)
    ```

    实测返回（HK · all_count=15151、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  current_price  warrant_type
    0  HK.55994  恒指摩通九三熊R.P  HK.800000       恒生指数          0.056             4
    1  HK.55641  恒指法兴八三熊P.P  HK.800000       恒生指数          0.055             4
    2  HK.57109  恒指法兴八七牛E.C  HK.800000       恒生指数          0.037             3
    3  HK.57003  恒指摩通八九牛8.C  HK.800000       恒生指数          0.038             3
    4  HK.55430  恒指瑞银八十熊B.P  HK.800000       恒生指数          0.053             4
    ```

    ##### `CURRENCY_CODE`（id=53 · choice · HK / SG / MY · 无对应返回列） 币种

    通常按市场决定（HK=HKD、SG=SGD、MY=MYR）；未在返回 DataFrame 单独暴露

    ```python
    req.add_sort(WarrantField.TURNOVER, desc=True)
    ```

    实测返回（HK · all_count=16170、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  warrant_type  current_price
    0  HK.55994  恒指摩通九三熊R.P  HK.800000       恒生指数             4          0.056
    1  HK.57003  恒指摩通八九牛8.C  HK.800000       恒生指数             3          0.038
    2  HK.57109  恒指法兴八七牛E.C  HK.800000       恒生指数             3          0.037
    3  HK.55641  恒指法兴八三熊P.P  HK.800000       恒生指数             4          0.055
    4  HK.57114  恒指法兴八九牛7.C  HK.800000       恒生指数             3          0.054
    ```

    ##### `STOCK_OWNER_PRICE`（id=54 · interval · HK / SG / MY · 返回列 `stock_owner_price`） 正股价

    单位：元；SDK 直传原始价；返回 stock_owner_price 列（协议字段 ×1000 取整传输）

    ```python
    req.add_interval_filter(WarrantField.STOCK_OWNER_PRICE, min_val=0.001)
    req.add_sort(WarrantField.STOCK_OWNER_PRICE, desc=False)
    ```

    实测返回（HK · all_count=16168、命中 5 行、head 前 5）：

    ```
           code        name owner_code owner_name  stock_owner_price  warrant_type  current_price
    0  HK.16376  碧桂法巴九十购A.C   HK.02007        碧桂园              0.209             1          0.000
    1  HK.16468  中粮麦银九甲购A.C   HK.00606       中骏商管              0.295             1          0.000
    2  HK.19876  喜相华泰六八购A.C   HK.02473      喜相逢集团              0.640             1          0.010
    3  HK.25841  喜相麦银六七购A.C   HK.02473      喜相逢集团              0.640             1          0.025
    4  HK.29782  喜相华泰六六购A.C   HK.02473      喜相逢集团              0.640             1          0.010
    ```

:::tip 接口限制
* 每 30 秒内最多请求 60 次筛选窝轮接口
:::

---

# 获取窝轮和期货列表

`get_referencestock_list(code, reference_type)`

* **介绍**

    获取证券的关联数据，如：获取正股相关窝轮、获取期货相关合约

* **参数**
    参数|类型|说明
    :-|:-|:-
    code|str|证券代码
    reference_type|[SecurityReferenceType](./quote.md#2911)|要获得的相关数据


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回证券的关联数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 证券的关联数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|证券代码
        lot_size|int|每手股数，期货表示合约乘数
        stock_type|[SecurityType](./quote.md#3325)|证券类型
        stock_name|str|证券名字
        list_time|str|上市时间  (格式：yyyy-MM-dd
港股和 A 股市场默认是北京时间，美股市场默认是美东时间)
        wrt_valid|bool|是否是窝轮  (若为 True，下面 wrt 开头的字段有效)
        wrt_type|[WrtType](./quote.md#926)|窝轮类型
        wrt_code|str|所属正股
        future_valid|bool|是否是期货  (若为 True，以下 future 开头的字段有效)
        future_main_contract|bool|是否主连合约  (期货特有字段)
        future_last_trade_time|str|最后交易时间  (期货特有字段主连，当月，下月等无该字段)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取正股相关的窝轮
ret, data = quote_ctx.get_referencestock_list('HK.00700', SecurityReferenceType.WARRANT)
if ret == RET_OK:
    print(data)
    print(data['code'][0])    # 取第一条的股票代码
    print(data['code'].values.tolist())   # 转为 list
else:
    print('error:', data)
print('******************************************')
# 港期相关合约
ret, data = quote_ctx.get_referencestock_list('HK.A50main', SecurityReferenceType.FUTURE)
if ret == RET_OK:
    print(data)
    print(data['code'][0])    # 取第一条的股票代码
    print(data['code'].values.tolist())   # 转为 list
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
        code  lot_size stock_type stock_name   list_time  wrt_valid wrt_type  wrt_code  future_valid  future_main_contract  future_last_trade_time
0     HK.24719      1000    WARRANT    腾讯东亚九四沽A  2018-07-20       True      PUT  HK.00700         False                   NaN                     NaN
..         ...       ...        ...                ...       ...        ...       ...       ...           ...                   ...                    ...
1617  HK.63402     10000    WARRANT    腾讯高盛一八牛Y  2020-11-26       True     BULL  HK.00700         False                   NaN                     NaN

[1618 rows x 11 columns]
HK.24719
['HK.24719', 'HK.27886', 'HK.28621', 'HK.14339', 'HK.27952', 'HK.18693', 'HK.20306', 'HK.53635', 'HK.47269', 'HK.27227', 
...        ...       ...        ...        ...         ...        ...      ...       ... 
'HK.63402']
******************************************
        code  lot_size stock_type         stock_name list_time  wrt_valid  wrt_type  wrt_code  future_valid  future_main_contract future_last_trade_time
0  HK.A50main      5000     FUTURE      安硕富时 A50 ETF主连(2012)                False       NaN       NaN          True                  True                       
..         ...       ...        ...                ...       ...        ...       ...       ...           ...                   ...                    ...
5  HK.A502106      5000     FUTURE      安硕富时 A50 ETF2106                False       NaN       NaN          True                 False             2021-06-29

[6 rows x 11 columns]
HK.A50main
['HK.A50main', 'HK.A502011', 'HK.A502012', 'HK.A502101', 'HK.A502103', 'HK.A502106']
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取证券关联数据接口
* 当获取正股相关窝轮时，不受上述限频限制
:::

---

# 获取期货合约资料

`get_future_info(code_list)`

* **介绍**

    获取期货合约资料

* **参数**
    参数|类型|说明
    :-|:-|:-
    code_list|list|股票代码列表  (list 中元素类型是 str)


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回期货合约资料数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 期货合约资料数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        owner|str|标的
        exchange|str|交易所
        type|str|合约类型
        size|float|合约规模
        size_unit|str|合约规模单位
        price_currency|str|报价货币
        price_unit|str|报价单位
        min_change|float|最小变动
        min_change_unit|str|最小变动的单位 (该字段已废弃)
        trade_time|str|交易时间
        time_zone|str|时区
        last_trade_time|str|最后交易时间  (主连，当月，下月等期货没有该字段)
        exchange_format_url|str|交易所规格链接 url
        origin_code|str|实际合约代码

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_future_info(["HK.MPImain", "HK.HAImain"])
if ret == RET_OK:
    print(data)
    print(data['code'][0])    # 取第一条的股票代码
    print(data['code'].values.tolist())   # 转为 list
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
    code      name       owner exchange  type     size size_unit price_currency price_unit  min_change min_change_unit                        trade_time time_zone last_trade_time                                exchange_format_url           origin_code
0  HK.MPImain   內房期货主连  恒生中国内地地产指数      港交所  股指期货     50.0    指数点×港元             港元        指数点        0.50                (09:15 - 12:00), (13:00 - 16:30)       CCT                  https://sc.hkex.com.hk/TuniS/www.hkex.com.hk/P...           HK.MPI2112
1  HK.HAImain   海通证券期货主连    HK.06837      港交所  股票期货  10000.0         股             港元      每股/港元        0.01                   (09:30 - 12:00), (13:00 - 16:00)       CCT                  https://sc.hkex.com.hk/TuniS/www.hkex.com.hk/P...           HK.HAI2112
HK.MPImain
['HK.MPImain', 'HK.HAImain']
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次获取期货合约资料接口
* 每次请求的代码列表中，期货个数上限为 200 个
:::

---

# 条件选股

`get_stock_filter(market, filter_list, plate_code=None, begin=0, num=200)`

* **介绍**

    条件选股

* **参数**
    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场标识  (不区分沪股和深股，传入沪股或者深股都会返回沪深市场的股票)
    filter_list|list|筛选条件的列表  (参考下面的表格，列表中元素类型为 SimpleFilter 或 AccumulateFilter 或 FinancialFilter)
    plate_code|str|板块代码
    begin|int|数据起始点
    num|int|请求数据个数
    * SimpleFilter 对象相关参数如下：  

        字段|类型|说明
        :-|:-|:-
        stock_field|[StockField](./quote.md#860)|简单属性
        filter_min|float|区间下限  (闭区间不传默认为 -∞)
        filter_max|float|区间上限  (闭区间不传默认为 +∞)
        is_no_filter|bool|该字段是否不需要筛选  (True：不筛选False：筛选不传默认不筛选)
        sort|[SortDir](./quote.md#5471)|排序方向  (不传默认为不排序)

    * AccumulateFilter 对象相关参数如下：

        字段|类型|说明
        :-|:-|:-
        stock_field|[StockField](./quote.md#4370)|累积属性
        filter_min|float|区间下限  (闭区间不传默认为 -∞)
        filter_max|float|区间上限  (闭区间不传默认为 +∞)
        is_no_filter|bool|该字段是否不需要筛选  (True：不筛选False：筛选不传默认不筛选)
        sort|[SortDir](./quote.md#5471)|排序方向  (不传默认为不排序)
        days|int|所筛选的数据的累计天数

    * FinancialFilter 对象相关参数如下：

        字段|类型|说明
        :-|:-|:-
        stock_field|[StockField](./quote.md#8542)|财务属性
        filter_min|float|区间下限  (闭区间不传默认为 -∞)
        filter_max|float|区间上限  (闭区间不传默认为 +∞)
        is_no_filter|bool|该字段是否不需要筛选  (True：不筛选False：筛选不传默认不筛选)
        sort|[SortDir](./quote.md#5471)|排序方向  (不传默认为不排序)
        quarter|[FinancialQuarter](./quote.md#2253)|财报累积时间

    * CustomIndicatorFilter 对象相关参数如下：

        字段|类型|说明
        :-|:-|:-
        stock_field1|[StockField](./quote.md#2057)|自定义技术指标属性
        stock_field1_para|list|自定义技术指标属性参数  (根据指标类型进行传参：1. MA：[平均移动周期] 2.EMA：[指数移动平均周期] 3.RSI：[RSI 指标周期] 4.MACD：[快速平均线值, 慢速平均线值, DIF值] 5.BOLL：[均线周期, 偏移值] 6.KDJ：[RSV 周期, K 值计算周期, D 值计算周期]) 
        relative_position|[RelativePosition](./quote.md#2453)|相对位置
        stock_field2|[StockField](./quote.md#2057)|自定义技术指标属性
        stock_field2_para|list|自定义技术指标属性参数  (根据指标类型进行传参：1. MA：[平均移动周期] 2.EMA：[指数移动平均周期] 3.RSI：[RSI 指标周期] 4.MACD：[快速平均线值, 慢速平均线值, DIF值] 5.BOLL：[均线周期, 偏移值] 6.KDJ：[RSV 周期, K 值计算周期, D 值计算周期]) 
        value|float|自定义数值  (当 stock_field2 在 [StockField](./quote.md#2057) 中选择自定义数值时，value 为必传参数) 
        ktype|[KLType](./quote.md#4119)|K线类型 KLType   (仅支持K_60M，K_DAY，K_WEEK，K_MON 四种时间周期)
        consecutive_period|int|筛选连续周期（consecutive_period）都符合条件的数据  (填写范围为[1,12]) 
        is_no_filter|bool|该字段是否不需要筛选  (True：不筛选False：筛选不传默认不筛选)
 
    * PatternFilter 对象相关参数如下：

        字段|类型|说明
        :-|:-|:-
        stock_field|[StockField](./quote.md#159)|形态技术指标属性
        ktype|[KLType](./quote.md#4119)|K线类型 KLType （仅支持K_60M，K_DAY，K_WEEK，K_MON 四种时间周期）
        consecutive_period|int|筛选连续周期（consecutive_period）都符合条件的数据  (填写范围为[1,12]) 
        is_no_filter|bool|该字段是否不需要筛选  (True：不筛选False：筛选不传默认不筛选)


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>tuple</td>
            <td>当 ret == RET_OK，返回选股数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 选股数据元组组成如下：
        字段|类型|说明
        :-|:-|:-
        last_page|bool|是否是最后一页
        all_count|int|列表总数量
        stock_list|list|选股数据  (list 中元素类型是 FilterStockData)
        
        - FilterStockData 类型的字段格式：

            字段|类型|说明
            :-|:-|:-
            stock_code|str|股票代码
            stock_name|str|股票名字
            cur_price|float|最新价
            cur_price_to_highest_52weeks_ratio|float|(现价 - 52周最高)/52周最高  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            cur_price_to_lowest_52weeks_ratio|float|(现价 - 52周最低)/52周最低  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            high_price_to_highest_52weeks_ratio|float|(今日最高 - 52周最高)/52周最高  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            low_price_to_lowest_52weeks_ratio|float|(今日最低 - 52周最低)/52周最低  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            volume_ratio|float|量比
            bid_ask_ratio|float|委比  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            lot_price|float|每手价格
            market_val|float|市值
            pe_annual|float|市盈率
            pe_ttm|float|市盈率 TTM
            pb_rate|float|市净率
            change_rate_5min|float|五分钟价格涨跌幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            change_rate_begin_year|float|年初至今价格涨跌幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            ps_ttm|float|市销率 TTM  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            pcf_ttm|float|市现率 TTM  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            total_share|float|总股数  (单位：股)
            float_share|float|流通股数  (单位：股)
            float_market_val|float|流通市值  (单位：元)
            change_rate|float|涨跌幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            amplitude|float|振幅  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            volume|float|日均成交量
            turnover|float|日均成交额
            turnover_rate|float|换手率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            net_profit|float|净利润
            net_profix_growth|float|净利润增长率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            sum_of_business|float|营业收入
            sum_of_business_growth|float|营业同比增长率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            net_profit_rate|float|净利率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            gross_profit_rate|float|毛利率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            debt_asset_rate|float|资产负债率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            return_on_equity_rate|float|净资产收益率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            roic|float|投入资本回报率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            roa_ttm|float|资产回报率 TTM  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。仅适用于年报)
            ebit_ttm|float|息税前利润 TTM  (单位：元。仅适用于年报)
            ebitda|float|税息折旧及摊销前利润  (单位：元)
            operating_margin_ttm|float|营业利润率 TTM  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。仅适用于年报)
            ebit_margin|float|EBIT 利润率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            ebitda_margin|float|EBITDA 利润率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            financial_cost_rate|float|财务成本率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            operating_profit_ttm|float|营业利润 TTM  (单位：元。仅适用于年报)
            shareholder_net_profit_ttm|float|归属于母公司的净利润  (单位：元。仅适用于年报)
            net_profit_cash_cover_ttm|float|盈利中的现金收入比例  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。仅适用于年报)
            current_ratio|float|流动比率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            quick_ratio|float|速动比率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            current_asset_ratio|float|流动资产率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            current_debt_ratio|float|流动负债率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            equity_multiplier|float|权益乘数 
            property_ratio|float|产权比率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            cash_and_cash_equivalents|float|现金和现金等价  (单位：元)
            total_asset_turnover|float|总资产周转率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            fixed_asset_turnover|float|固定资产周转率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            inventory_turnover|float|存货周转率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            operating_cash_flow_ttm|float|经营活动现金流 TTM   (单位：元。仅适用于年报)
            accounts_receivable|float|应收账款净额  (单位：元)
            ebit_growth_rate|float|EBIT 同比增长率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            operating_profit_growth_rate|float|营业利润同比增长率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            total_assets_growth_rate|float|总资产同比增长率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            profit_to_shareholders_growth_rate|float|归母净利润同比增长率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            profit_before_tax_growth_rate|float|总利润同比增长率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            eps_growth_rate|float|EPS 同比增长率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            roe_growth_rate|float|ROE 同比增长率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            roic_growth_rate|float|ROIC 同比增长率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            nocf_growth_rate|float|经营现金流同比增长率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            nocf_per_share_growth_rate|float|每股经营现金流同比增长率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            operating_revenue_cash_cover|float|经营现金收入比  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            operating_profit_to_total_profit|float|营业利润占比  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
            basic_eps|float|基本每股收益  (单位：元)
            diluted_eps|float|稀释每股收益  (单位：元)
            nocf_per_share|float|每股经营现金净流量  (单位：元)
            price|float|最新价格
            ma|float|简单均线  (根据 MA 参数返回具体的数值)
            ma5|float|5日简单均线
            ma10|float|10日简单均线
            ma20|float|20日简单均线
            ma30|float|30日简单均线
            ma60|float|60日简单均线
            ma120|float|120日简单均线
            ma250|float|250日简单均线
            rsi|float|RSI的值  (根据 RSI 参数返回具体的数值，RSI 默认参数为12)
            ema|float|指数移动均线  (根据 EMA 参数返回具体的数值) 
            ema5|float|5日指数移动均线 
            ema10|float|10日指数移动均线
            ema20|float|20日指数移动均线
            ema30|float|30日指数移动均线
            ema60|float|60日指数移动均线
            ema120|float|120日指数移动均线
            ema250|float|250日指数移动均线
            kdj_k|float|KDJ 指标的 K 值  (根据 KDJ 参数返回具体的数值，KDJ 默认参数为[9,3,3]) 
            kdj_d|float|KDJ 指标的 D 值  (根据 KDJ 参数返回具体的数值，KDJ 默认参数为[9,3,3]) 
            kdj_j|float|KDJ 指标的 J 值  (根据 KDJ 参数返回具体的数值，KDJ 默认参数为[9,3,3]) 
            macd_diff|float|MACD 指标的 DIFF 值  (根据 MACD 参数返回具体的数值，MACD 默认参数为[12,26,9]) 
            macd_dea|float|MACD 指标的 DEA 值  (根据 MACD 参数返回具体的数值，MACD 默认参数为[12,26,9]) 
            macd|float|MACD 指标的 MACD 值  (根据 MACD 参数返回具体的数值，MACD 默认参数为[12,26,9]) 
            boll_upper|float|BOLL 指标的 UPPER 值  (根据 BOLL 参数返回具体的数值，BOLL 默认参数为[20.2]) 
            boll_middler|float|BOLL 指标的 MIDDLER 值  (根据 BOLL 参数返回具体的数值，BOLL 默认参数为[20.2])
            boll_lower|float|BOLL 指标的 LOWER 值  (根据 BOLL 参数返回具体的数值，BOLL 默认参数为[20.2])


* **Example**

```python
from futu import *
import time

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
simple_filter = SimpleFilter()
simple_filter.filter_min = 2
simple_filter.filter_max = 1000
simple_filter.stock_field = StockField.CUR_PRICE
simple_filter.is_no_filter = False
# simple_filter.sort = SortDir.ASCEND

financial_filter = FinancialFilter()
financial_filter.filter_min = 0.5
financial_filter.filter_max = 50
financial_filter.stock_field = StockField.CURRENT_RATIO
financial_filter.is_no_filter = False
financial_filter.sort = SortDir.ASCEND
financial_filter.quarter = FinancialQuarter.ANNUAL

custom_filter = CustomIndicatorFilter()
custom_filter.ktype = KLType.K_DAY
custom_filter.stock_field1 = StockField.KDJ_K
custom_filter.stock_field1_para = [10,4,4]
custom_filter.stock_field2 = StockField.KDJ_K
custom_filter.stock_field2_para = [9,3,3]
custom_filter.relative_position = RelativePosition.MORE
custom_filter.is_no_filter = False

nBegin = 0
last_page = False
ret_list = list()
while not last_page:
    nBegin += len(ret_list)
    ret, ls = quote_ctx.get_stock_filter(market=Market.HK, filter_list=[simple_filter, financial_filter, custom_filter], begin=nBegin)  # 对香港市场的股票做简单、财务和指标筛选
    if ret == RET_OK:
        last_page, all_count, ret_list = ls
        print('all count = ', all_count)
        for item in ret_list:
            print(item.stock_code)  # 取股票代码
            print(item.stock_name)  # 取股票名称
            print(item[simple_filter])   # 取 simple_filter 对应的变量值
            print(item[financial_filter])   # 取 financial_filter 对应的变量值
            print(item[custom_filter])  # 获取 custom_filter 的数值
    else:
        print('error: ', ls)
    time.sleep(3)  # 加入时间间隔，避免触发限频

quote_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
39 39 [ stock_code:HK.08103  stock_name:HMVOD视频  cur_price:2.69  current_ratio(annual):4.413 ,  stock_code:HK.00376  stock_name:云锋金融  cur_price:2.96  current_ratio(annual):12.585 ,  stock_code:HK.09995  stock_name:荣昌生物-B  cur_price:92.65  current_ratio(annual):16.054 ,  stock_code:HK.80737  stock_name:湾区发展-R  cur_price:2.8  current_ratio(annual):17.249 ,  stock_code:HK.00737  stock_name:湾区发展  cur_price:3.25  current_ratio(annual):17.249 ,  stock_code:HK.03939  stock_name:万国国际矿业  cur_price:2.22  current_ratio(annual):17.323 ,  stock_code:HK.01055  stock_name:中国南方航空股份  cur_price:5.17  current_ratio(annual):17.529 ,  stock_code:HK.02638  stock_name:港灯-SS  cur_price:7.68  current_ratio(annual):21.255 ,  stock_code:HK.00670  stock_name:中国东方航空股份  cur_price:3.53  current_ratio(annual):25.194 ,  stock_code:HK.01952  stock_name:云顶新耀-B  cur_price:69.5  current_ratio(annual):26.029 ,  stock_code:HK.00089  stock_name:大生地产  cur_price:4.22  current_ratio(annual):26.914 ,  stock_code:HK.00728  stock_name:中国电信  cur_price:2.81  current_ratio(annual):27.651 ,  stock_code:HK.01372  stock_name:比速科技  cur_price:5.1  current_ratio(annual):28.303 ,  stock_code:HK.00753  stock_name:中国国航  cur_price:6.38  current_ratio(annual):31.828 ,  stock_code:HK.01997  stock_name:九龙仓置业  cur_price:43.75  current_ratio(annual):33.239 ,  stock_code:HK.02158  stock_name:医渡科技  cur_price:39.0  current_ratio(annual):34.046 ,  stock_code:HK.02588  stock_name:中银航空租赁  cur_price:77.0  current_ratio(annual):34.531 ,  stock_code:HK.01330  stock_name:绿色动力环保  cur_price:3.36  current_ratio(annual):35.028 ,  stock_code:HK.01525  stock_name:建桥教育  cur_price:6.28  current_ratio(annual):36.989 ,  stock_code:HK.09908  stock_name:嘉兴燃气  cur_price:10.02  current_ratio(annual):37.848 ,  stock_code:HK.06078  stock_name:海吉亚医疗  cur_price:49.8  current_ratio(annual):39.0 ,  stock_code:HK.01071  stock_name:华电国际电力股份  cur_price:2.16  current_ratio(annual):39.507 ,  stock_code:HK.00357  stock_name:美兰空港  cur_price:34.15  current_ratio(annual):39.514 ,  stock_code:HK.00762  stock_name:中国联通  cur_price:5.15  current_ratio(annual):40.74 ,  stock_code:HK.01787  stock_name:山东黄金  cur_price:15.56  current_ratio(annual):41.604 ,  stock_code:HK.00902  stock_name:华能国际电力股份  cur_price:2.66  current_ratio(annual):42.919 ,  stock_code:HK.00934  stock_name:中石化冠德  cur_price:2.96  current_ratio(annual):43.361 ,  stock_code:HK.01117  stock_name:现代牧业  cur_price:2.3  current_ratio(annual):45.037 ,  stock_code:HK.00177  stock_name:江苏宁沪高速公路  cur_price:8.78  current_ratio(annual):45.93 ,  stock_code:HK.01379  stock_name:温岭工量刃具  cur_price:5.71  current_ratio(annual):46.774 ,  stock_code:HK.01876  stock_name:百威亚太  cur_price:22.5  current_ratio(annual):46.917 ,  stock_code:HK.01907  stock_name:中国旭阳集团  cur_price:4.38  current_ratio(annual):47.129 ,  stock_code:HK.02160  stock_name:心通医疗-B  cur_price:15.54  current_ratio(annual):47.384 ,  stock_code:HK.00293  stock_name:国泰航空  cur_price:7.1  current_ratio(annual):47.983 ,  stock_code:HK.00694  stock_name:北京首都机场股份  cur_price:6.34  current_ratio(annual):47.985 ,  stock_code:HK.09922  stock_name:九毛九  cur_price:26.65  current_ratio(annual):48.278 ,  stock_code:HK.01083  stock_name:港华燃气  cur_price:3.39  current_ratio(annual):49.2 ,  stock_code:HK.00291  stock_name:华润啤酒  cur_price:58.0  current_ratio(annual):49.229 ,  stock_code:HK.00306  stock_name:冠忠巴士集团  cur_price:2.29  current_ratio(annual):49.769 ]
HK.08103
HMVOD视频
2.69
2.69
4.413
...
HK.00306
冠忠巴士集团
2.29
2.29
49.769
```

:::tip 提示
* 利用[获取子板块列表函数](../quote/get-plate-list.md) 获取子板块代码，条件选股支持的板块分别为
    1. 港股的行业板块和概念板块。
    2. 美股的行业板块
    3. 沪深的行业板块，概念板块和地域板块
* 支持的板块指数代码
    代码|说明
    :-|:-
    HK.Motherboard|港股主板
    HK.GEM|港股创业板
    HK.BK1911|H 股主板
    HK.BK1912|H 股创业板
    US.NYSE|纽交所
    US.AMEX|美交所
    US.NASDAQ|纳斯达克
    SH.3000000|上海主板
    SZ.3000001|深证主板
    SZ.3000004|深证创业板
:::

:::tip 接口限制
* 港股 BMP 权限不支持条件选股功能
* 每 30 秒内最多请求 10 次条件选股接口
* 每页返回的筛选结果最多 200 个
* 建议筛选条件不超过 250 个，否则可能会出现“业务处理超时没返回”
* 累积属性的同一筛选条件数量上限 10 个
* 如果使用“最新价”等动态数据作为排序字段，在多页获取的间隙，数据的排序有可能发生变化
* 非同类指标不支持比较，仅限于同类指标之间建立比较关系，跨不同类型的指标比较会报错。例如：MA5 和 MA10 可以建立关系。MA5和EMA10不能建立关系。
* 自定义指标属性的同一类筛选条件超出数量上限10个
* 简单属性，财务属性，形态属性不支持对同一字段重复指定筛选条件
* 条件选股暂不支持美股盘前盘后、夜盘，筛选结果均按照盘中数据返回
:::

---

# 筛选正股

`get_stock_screen(request)`

* **介绍**

    条件选股 V2。相比旧接口 [get_stock_filter](./get-stock-filter.md)，因子覆盖更广（11 类共 244+ 个因子），数值统一传原始值（OpenD 自动倍率转换），支持单字段或多字段排序、显式声明取回属性，结果按 `value_type` 分别填入 `sval` / `ival` / `aval` / `dval`。

* **参数**

    参数|类型|说明
    :-|:-|:-
    request|StockScreenRequest|条件选股请求对象，通过 builder 方式构建

    * StockScreenRequest 字段：

        字段|类型|说明
        :-|:-|:-
        page_from|int|分页起始位置  (不传默认为 0)
        page_count|int|单页最大返回数  (不传默认为 200)

    * 筛选条件 builder 方法（每次调用追加一条筛选条件，所有数值字段直接传原始值，OpenD 自动倍率转换）：

        方法|说明
        :-|:-
        add_simple_field(field, values)|市场 / 交易所 / 指数 / 自选股等枚举字段筛选  (field 取自 [SimpleField](./quote.md#1036)；values 为枚举值列表（OR 关系）。ScrMarket.MY / JP / SG 后续支持，目前结果为空)
        add_plate(plate_ids, parent_plate_id=None)|板块筛选  (plate_ids 形如 ["BK1001"])
        add_simple_property(name, lower=None, upper=None)|简单行情属性区间筛选  (name 取自 [SimpleProperty](./quote.md#3458)（最新价、市值、PE、量比等）；lower / upper 直接传原始值，如最新价 10 元传 10、市值 ≥ 100 亿传 10_000_000_000)
        add_cumulative_property(name, days=1, lower=None, upper=None)|累计行情属性  (name 取自 [CumulativeProperty](./quote.md#7431)；days 用于 N 日累计。涨跌幅类（如 PRICE_CHANGE_PCT）传值为**小数**（5% 传 0.05，非 5.0）)
        add_financial_property(name, term=None, year=None, lower=None, upper=None, ...)|财务属性  (name 取自 [FinancialProperty](./quote.md#9745)；term 取自 Term 枚举（Q1=1、年报=100、最新单季=10 等）。Term.SURPRISE_LATEST 系列（200~204）实测 HK/US 均会返回数值，但当前数据通常与 ANNUAL 相同，慎用)
        add_indicator_positional(first_indicator_name, period_type, position, second_indicator=None, ...)|技术指标位置关系  (如 MA5 上穿 MA20。指标名/周期/位置取自 [Indicator / Period / Position](./quote.md#823))
        add_indicator_pattern(name, period_type, ...)|技术指标形态（金叉、死叉、背离等）  (name 取自 [Pattern](./quote.md#823))
        add_featured_property(name, intervals=None, value_set=None, period=None, range_period=None, first_custom_param=None)|特色指标（筹码、热度、分析师评级、资金流等）
        add_broker_holdings(name, days=None, param=None, intervals=None)|经纪商持股因子  (仅港股。支持 6101 集中度 / 6103 数量 / 6106 中央结算持股占比 / 6107 中央结算持股变动；不支持 6102 持仓变动、6104 经纪商排行、6105 经纪商持仓量。6101 / 6106 / 6107 倍率 1000，按百分数传值（如 20% 传 20）；6103 无倍率。intervals 用 dict 列表，key 用 `filterMin` / `filterMax`。`days` 参数不生效)
        add_kline_shape(name, period=None, value_set=None)|K 线形态（双底、头肩底等）  (period 必传，目前仅支持日 K(11) 与 1 小时 K(21))
        add_option(name, intervals=None, param=None, period=None)|期权指标（正股 IV、HV 等）

    * 取回属性 builder 方法（声明返回哪些字段值；不声明则只返回 stock_id）：

        方法|说明
        :-|:-
        add_retrieve_basic(name)|代码 / 名称 / 行业  (name 取自 [BasicProperty](./quote.md#55)：CODE=1101、NAME=1102、INDUSTRY=1103)
        add_retrieve_simple(name)|简单行情属性  (name 取自 [SimpleProperty](./quote.md#3458))
        add_retrieve_cumulative(name, days=1, period_average=None)|累计属性  (name 取自 [CumulativeProperty](./quote.md#7431))
        add_retrieve_financial(name, term=None, year=None, ...)|财务属性  (name 取自 [FinancialProperty](./quote.md#9745))
        add_retrieve_indicator(name, period=None, indicator_params=None)|技术指标
        add_retrieve_featured(name, period=None, range_period=None, first_custom_param=None)|特色属性
        add_retrieve_broker(name, days=None, param=None)|经纪商
        add_retrieve_option(name, param=None, period=None)|期权属性
        add_retrieve_kline_shape(name, period=None)|K 线形态  (period 必传，否则不返回结果；目前仅支持日 K(11) 与 1 小时 K(21))

    * 排序 builder 方法：

        方法|说明
        :-|:-
        set_sort(direction, property_type, property_params)|单字段排序  (direction 取自 ScrSortDir：ASC=1、DESC=2、ABS_ASC=3、ABS_DESC=4。property_type 取 'basic' / 'simple' / 'cumulative' / 'financial' / 'indicator' / 'featured' / 'broker' / 'option' / 'kline_shape')
        add_sort(direction, property_type, property_params)|多字段排序  (按调用顺序生效；与 set_sort 二选一，sortList 非空时优先)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>tuple</td>
            <td>当 ret == RET_OK，返回 (last_page, all_count, items)</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 返回 tuple 字段：

        字段|类型|说明
        :-|:-|:-
        last_page|bool|是否最后一页
        all_count|int|满足条件的总条数
        items|list[dict]|当前页结果列表，元素结构为 `{'stock_id': int, 'results': [result, ...]}`

    * 单条 result 结构：

        字段|类型|说明
        :-|:-|:-
        type|str|属性类型  ('basic' / 'simple' / 'cumulative' / 'financial' / 'indicator' / 'featured' / 'broker' / 'option' / 'kline_shape')
        property|dict|对应 property 描述（含 name / days / term 等）
        value_type|int|值类型  (1=string(sval)、2=int64(ival)、3=int64数组(aval)、4=double(dval)。当 OpenD 无数据时仅下发 value_type（多为 2），sval/ival/aval/dval 均缺失，如港股 Q2/Q3/Q4 财务数据)
        sval|str|字符串值（value_type=1 时存在）
        ival|int|整型值（value_type=2 时存在）
        aval|list[int]|整型数组值（value_type=3 时存在）
        dval|float|浮点值（value_type=4 时存在）
        enum_type_name|str|当 ival 为枚举码时，对应的枚举类型名（如 'KlineShapeType'）
        enum_name|str|当 ival 为枚举码时，OpenD/SDK 解码出的枚举名（如 'DOUBLE_BOTTOMS'、'NONE'）
        end_time|int|财报结束时间戳  (仅 financial 类型，且当前 OpenD 版本暂未下发，实际返回结果中通常没有该字段)

* **Example**

```python
from futu import OpenQuoteContext, RET_OK, StockScreenRequest
from futu.quote.stock_screen_const import (
    ScrMarket, ScrSortDir, SimpleField, SimpleProperty,
    CumulativeProperty, FinancialProperty, Term,
    Indicator, Period, Position, Pattern,
    BasicProperty, KlineShapeProperty, KlineShapeType,
)

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 示例 1：港股大市值股 + MACD 金叉
req = StockScreenRequest()
req.add_simple_field(field=SimpleField.MARKET, values=[ScrMarket.HK])
req.add_simple_property(name=SimpleProperty.PRICE, lower=10.0)                   # 最新价 ≥ 10
req.add_simple_property(name=SimpleProperty.MARKET_CAP, lower=10_000_000_000.0)  # 市值 ≥ 100 亿
req.add_simple_property(name=SimpleProperty.PE_TTM, lower=10.0, upper=50.0)      # PE(TTM) 10~50
req.add_indicator_pattern(name=Pattern.MACD_GOLD_CROSS, period_type=Period.DAY)  # MACD 金叉
# 取回字段
req.add_retrieve_basic(name=BasicProperty.CODE)
req.add_retrieve_basic(name=BasicProperty.NAME)
req.add_retrieve_simple(name=SimpleProperty.PRICE)
req.add_retrieve_simple(name=SimpleProperty.MARKET_CAP)
req.add_retrieve_simple(name=SimpleProperty.PE_TTM)
# 排序
req.set_sort(direction=ScrSortDir.DESC, property_type='simple',
             property_params={'name': int(SimpleProperty.MARKET_CAP)})
req.page_count = 50

ret, data = quote_ctx.get_stock_screen(req)
if ret == RET_OK:
    last_page, all_count, items = data
    print(f"总数 {all_count}, 当前返回 {len(items)} 条")
    for it in items[:3]:
        print(it['stock_id'], it['results'])
else:
    print('error: ', data)

# 示例 2：财务因子 + 累计涨跌幅
req = StockScreenRequest()
req.add_simple_field(field=SimpleField.MARKET, values=[ScrMarket.HK])
req.add_cumulative_property(name=CumulativeProperty.PRICE_CHANGE_PCT,
                            days=5, lower=-0.05, upper=0.05)                     # 5 日涨跌幅 -5%~5%（百分数传小数）
req.add_financial_property(name=FinancialProperty.NET_PROFIT,
                           term=Term.ANNUAL, lower=0.0)                          # 年报净利润 > 0
req.add_retrieve_basic(name=BasicProperty.CODE)
req.add_retrieve_simple(name=SimpleProperty.PRICE)
req.page_count = 200
ret, data = quote_ctx.get_stock_screen(req)

# 示例 3：K 线形态（W 型底 + 头肩底）
req = StockScreenRequest()
req.add_simple_field(field=SimpleField.MARKET, values=[ScrMarket.HK])
req.add_kline_shape(name=KlineShapeProperty.SHAPE_TYPE, period=Period.DAY,
                    value_set=[KlineShapeType.DOUBLE_BOTTOMS,
                               KlineShapeType.HEAD_SHOULDERS_BOTTOM])
req.add_retrieve_basic(name=BasicProperty.CODE)
req.add_retrieve_kline_shape(name=KlineShapeProperty.SHAPE_TYPE, period=Period.DAY)
ret, data = quote_ctx.get_stock_screen(req)

quote_ctx.close()
```

* **Output**

```python
总数 1, 当前返回 1 条
54047868453564 [{'type': 'basic', 'property': {'name': 1101}, 'value_type': 1, 'sval': '00700'},
                {'type': 'basic', 'property': {'name': 1102}, 'value_type': 1, 'sval': '腾讯控股'},
                {'type': 'simple', 'property': {'name': 2201}, 'value_type': 4, 'dval': 460.0},
                {'type': 'simple', 'property': {'name': 2301}, 'value_type': 4, 'dval': 4194280264040.0},
                {'type': 'simple', 'property': {'name': 2303}, 'value_type': 4, 'dval': 15.75126}]
```

* **字段逐项示例（按类别）**

    > 以下示例均以 HK 市场为例：先 `req = StockScreenRequest()`，再 `req.add_simple_field(field=SimpleField.MARKET, values=[ScrMarket.HK])`，
    > 再叠加每段中的筛选 / 取回 / 排序条件，最后 `quote_ctx.get_stock_screen(req)` 取 `(last_page, all_count, items)`。
    > 实测的 `head` 已展开 `results` 数组里的对应 property 值（code/name 来自 BasicProperty.CODE/NAME，因子列名取自 SDK 字段名小写）。

    #### 简单行情属性 SimpleProperty

    通过 `add_simple_property(name, lower, upper)` 传入；`lower/upper` 直传原始值（元/股/百分数 5% 传 5.0）

    ##### `PRICE`（id=2201 · simple · SimpleProperty） 最新价

    单位：元；lower/upper 直传原始价，OpenD 自动倍率转换

    ```python
    req.add_simple_property(name=SimpleProperty.PRICE, lower=10.0)
    req.add_retrieve_simple(name=SimpleProperty.PRICE)
    req.set_sort(direction=ScrSortDir.DESC, property_type='simple',
                 property_params={'name': int(SimpleProperty.PRICE)})
    ```

    实测返回（HK · all_count=485、命中 5 行、head 前 5）：

    ```
          stock_id   code    name   price
    47704201761008  04336  应用材料-T  1620.0
    87836376173009  02513      智谱  1097.0
    47704201761005  04333    思科-T   750.0
    86839943761574  03750    宁德时代   672.5
    87840671141778  03986    兆易创新   653.5
    ```

    ##### `MARKET_CAP`（id=2301 · simple · SimpleProperty） 总市值

    单位：元；lower=100 亿写 10_000_000_000

    ```python
    req.add_simple_property(name=SimpleProperty.MARKET_CAP, lower=10_000_000_000.0)
    req.add_retrieve_simple(name=SimpleProperty.MARKET_CAP)
    req.set_sort(direction=ScrSortDir.DESC, property_type='simple',
                 property_params={'name': int(SimpleProperty.MARKET_CAP)})
    ```

    实测返回（HK · all_count=591、命中 5 行、head 前 5）：

    ```
          stock_id   code    name        market_cap
    54047868453564  00700    腾讯控股   4222484299075.2
    83820581829436  80700  腾讯控股-R   3641391766113.6
    86839943761574  03750    宁德时代   3111406771825.0
    47704201761005  04333    思科-T   2956075998750.0
    57754425230710  01398    工商银行  2573253176182.58
    ```

    ##### `PE_TTM`（id=2303 · simple · SimpleProperty） PE(TTM)

    正常区间筛选；可为负

    ```python
    req.add_simple_property(name=SimpleProperty.PE_TTM, lower=5.0, upper=20.0)
    req.add_retrieve_simple(name=SimpleProperty.PE_TTM)
    req.set_sort(direction=ScrSortDir.ASC, property_type='simple',
                 property_params={'name': int(SimpleProperty.PE_TTM)})
    ```

    实测返回（HK · all_count=830、命中 5 行、head 前 5）：

    ```
          stock_id   code      name  pe_ttm
    28604482191640  00280      景福集团     5.0
    67345087202619  01339  中国人民保险集团   5.037
    68629282424057  01273      香港信贷  5.0847
    76063870813891  01731    其利工业集团  5.0877
    35433480192608  00608      达利国际  5.0877
    ```

    ##### `VOLUME_RATIO`（id=2217 · simple · SimpleProperty） 量比

    今日成交量 / N 日均量；> 2 表示放量

    ```python
    req.add_simple_property(name=SimpleProperty.VOLUME_RATIO, lower=2.0)
    req.add_retrieve_simple(name=SimpleProperty.VOLUME_RATIO)
    req.set_sort(direction=ScrSortDir.DESC, property_type='simple',
                 property_params={'name': int(SimpleProperty.VOLUME_RATIO)})
    ```

    实测返回（HK · all_count=340、命中 5 行、head 前 5）：

    ```
          stock_id   code      name  volume_ratio
    50796578209975  00183      宏辉集团         600.0
    45999099741384  01224      中渝置地       404.642
              1543  01543  中盈盛达融资担保       400.714
    24142011170996  00180      开达集团       314.999
     5033701671181  00269    中国资源交通         200.0
    ```

    ##### `DIVIDEND_RATIO`（id=2305 · simple · SimpleProperty） 股息率

    单位：% ；股息率 ≥ 5% 传 5.0

    ```python
    req.add_simple_property(name=SimpleProperty.DIVIDEND_RATIO, lower=5.0)
    req.add_retrieve_simple(name=SimpleProperty.DIVIDEND_RATIO)
    req.set_sort(direction=ScrSortDir.DESC, property_type='simple',
                 property_params={'name': int(SimpleProperty.DIVIDEND_RATIO)})
    ```

    实测返回（HK · all_count=0、命中 0 行）：无数据。原因：HK 当下抽样无 ≥ 5% 股息率股票，可降低 lower 阈值

    #### 累计行情属性 CumulativeProperty

    通过 `add_cumulative_property(name, days, lower, upper)` 传入；**百分数类（涨跌幅/换手率）传小数**（5% 传 0.05）

    ##### `PRICE_CHANGE_PCT`（id=3102 · cumulative · CumulativeProperty） N 日涨跌幅 %

    **百分数传小数**：5% 传 0.05；`days` 指 N 日累计窗口

    ```python
    req.add_cumulative_property(name=CumulativeProperty.PRICE_CHANGE_PCT,
                                days=5, lower=0.05)
    req.add_retrieve_cumulative(name=CumulativeProperty.PRICE_CHANGE_PCT, days=5)
    req.set_sort(direction=ScrSortDir.DESC, property_type='cumulative',
                 property_params={'name': int(CumulativeProperty.PRICE_CHANGE_PCT), 'days': 5})
    ```

    实测返回（HK · all_count=363、命中 5 行、head 前 5）：

    ```
          stock_id   code      name  change_pct_5d
    88510686038921  02953     嬴集团股权            4.0
    77640123811704  01912       康特隆         2.7679
    47704201761005  04333      思科-T         2.2029
    88467736365964  02956  中国健康科技股权         1.6667
    47704201761008  04336    应用材料-T         1.4384
    ```

    ##### `AMPLITUDE`（id=3103 · cumulative · CumulativeProperty） N 日振幅 %

    同 PRICE_CHANGE_PCT，百分数传小数

    ```python
    req.add_cumulative_property(name=CumulativeProperty.AMPLITUDE,
                                days=20, lower=0.1)
    req.add_retrieve_cumulative(name=CumulativeProperty.AMPLITUDE, days=20)
    req.set_sort(direction=ScrSortDir.DESC, property_type='cumulative',
                 property_params={'name': int(CumulativeProperty.AMPLITUDE), 'days': 20})
    ```

    实测返回（HK · all_count=2345、命中 5 行、head 前 5）：

    ```
          stock_id   code    name  amp_20d
    47704201761008  04336  应用材料-T  43.3783
    55671366092780  02028    映美控股   9.0893
    59558311493749  00117  天利控股集团   8.0532
    42623255446398  00894    万裕科技     7.59
    88433376627363  02723    深演智能   6.3243
    ```

    ##### `AVG_VOLUME`（id=3104 · cumulative · CumulativeProperty） N 日均量

    单位：股；N 日成交量算术平均

    ```python
    req.add_cumulative_property(name=CumulativeProperty.AVG_VOLUME,
                                days=20, lower=1_000_000)
    req.add_retrieve_cumulative(name=CumulativeProperty.AVG_VOLUME, days=20)
    req.set_sort(direction=ScrSortDir.DESC, property_type='cumulative',
                 property_params={'name': int(CumulativeProperty.AVG_VOLUME), 'days': 20})
    ```

    实测返回（HK · all_count=2295、命中 5 行、head 前 5）：

    ```
          stock_id   code    name  avg_vol_20d
    84688165145005  02477    经纬天地  15586288027
    58506044508119  02007     碧桂园  11318232417
    69325067126991  02255  海昌海洋公园  10691740000
    81462644703252  00020    商汤-W   9517974535
    79671643350793  09993    金辉控股   7418314265
    ```

    ##### `TURNOVER_RATIO`（id=3106 · cumulative · CumulativeProperty） N 日累计换手率

    单位：% ；百分数传小数（5% 传 0.05）

    ```python
    req.add_cumulative_property(name=CumulativeProperty.TURNOVER_RATIO,
                                days=20, lower=0.05)
    req.add_retrieve_cumulative(name=CumulativeProperty.TURNOVER_RATIO, days=20)
    req.set_sort(direction=ScrSortDir.DESC, property_type='cumulative',
                 property_params={'name': int(CumulativeProperty.TURNOVER_RATIO), 'days': 20})
    ```

    实测返回（HK · all_count=800、命中 5 行、head 前 5）：

    ```
          stock_id   code   name  turnover_ratio_20d
    58196806861368  00568   山东墨龙              6.7527
    84688165145005  02477   经纬天地              3.8966
    88089779243675  02715    埃斯顿              3.7288
    84434762074537  02473  喜相逢集团              3.4646
    87230785784391  02631   天岳先进              3.2208
    ```

    #### 财务属性 FinancialProperty

    通过 `add_financial_property(name, term, year, lower, upper)` 传入；`term` 取自 `Term` 枚举（年报=100、Q1=1、TTM 类不需要 term）；**比率类传小数**（15% 传 0.15）

    ##### `NET_PROFIT`（id=4101 · financial · FinancialProperty） 净利润

    单位：元；term=ANNUAL(100) 年报、Q1=1、Q2/Q3/Q4 部分港股无数据

    ```python
    req.add_financial_property(name=FinancialProperty.NET_PROFIT,
                               term=Term.ANNUAL, lower=1_000_000_000.0)
    req.add_retrieve_financial(name=FinancialProperty.NET_PROFIT, term=Term.ANNUAL)
    req.set_sort(direction=ScrSortDir.DESC, property_type='financial',
                 property_params={'name': int(FinancialProperty.NET_PROFIT),
                                  'term': int(Term.ANNUAL)})
    ```

    实测返回（HK · all_count=437、命中 5 行、head 前 5）：

    ```
          stock_id   code    name      net_profit
    57754425230710  01398    工商银行  412328868600.0
    56186762167211  00939    建设银行  377880459000.0
    63586990818568  01288    农业银行  324736536300.0
    57118770073492  03988    中国银行  286850625600.0
    83820581829436  80700  腾讯控股-R  255561692100.0
    ```

    ##### `ROE`（id=4110 · financial · FinancialProperty） 净资产收益率

    单位：% ；百分数传小数（15% 传 0.15）；term=ANNUAL

    ```python
    req.add_financial_property(name=FinancialProperty.ROE,
                               term=Term.ANNUAL, lower=0.15)
    req.add_retrieve_financial(name=FinancialProperty.ROE, term=Term.ANNUAL)
    req.set_sort(direction=ScrSortDir.DESC, property_type='financial',
                 property_params={'name': int(FinancialProperty.ROE),
                                  'term': int(Term.ANNUAL)})
    ```

    实测返回（HK · all_count=322、命中 5 行、head 前 5）：

    ```
          stock_id   code    name      roe
    62487479191132  01628    禹洲集团   40.644
    69823283339309  08237    华星控股  12.6906
    52845277610549  00565  锦艺集团控股   3.0644
    86882893433405  02621    手回集团   2.7027
    64969970288874  02282   美高梅中国   2.6886
    ```

    ##### `REVENUE_GROWTH`（id=4106 · financial · FinancialProperty） 营收同比增长率

    单位：% ；百分数传小数（20% 传 0.20）；term=ANNUAL

    ```python
    req.add_financial_property(name=FinancialProperty.REVENUE_GROWTH,
                               term=Term.ANNUAL, lower=0.20)
    req.add_retrieve_financial(name=FinancialProperty.REVENUE_GROWTH, term=Term.ANNUAL)
    req.set_sort(direction=ScrSortDir.DESC, property_type='financial',
                 property_params={'name': int(FinancialProperty.REVENUE_GROWTH),
                                  'term': int(Term.ANNUAL)})
    ```

    实测返回（HK · all_count=638、命中 5 行、head 前 5）：

    ```
          stock_id   code    name  revenue_growth
    46772193854353  00913    港湾数字        106.7922
    88377542057458  07666  剂泰科技-P          73.067
    53047141075220  02324    首都创投         63.5792
    43589623088228  01124    沿海家园         26.7323
    74259984551169  03329    交银国际         20.5256
    ```

    ##### `BASIC_EPS`（id=4801 · financial · FinancialProperty） 基本每股收益

    单位：元；term=ANNUAL

    ```python
    req.add_financial_property(name=FinancialProperty.BASIC_EPS,
                               term=Term.ANNUAL, lower=1.0)
    req.add_retrieve_financial(name=FinancialProperty.BASIC_EPS, term=Term.ANNUAL)
    req.set_sort(direction=ScrSortDir.DESC, property_type='financial',
                 property_params={'name': int(FinancialProperty.BASIC_EPS),
                                  'term': int(Term.ANNUAL)})
    ```

    实测返回（HK · all_count=324、命中 5 行、head 前 5）：

    ```
          stock_id   code             name      basic_eps
    86998857554659  06883             颖通控股  123007487.548
    88261577939456  06656             思格新能        139.457
    69290707392656  06288  FAST RETAIL-DRS         74.984
    80418967660265  09961           携程集团-S         56.044
    85439784425509  06181             老铺黄金         31.388
    ```

    ##### `DIVIDENDS_TTM_RATIO`（id=4219 · financial · FinancialProperty） TTM 股息率

    单位：% ；百分数传小数；TTM 类不需要 term/year

    ```python
    req.add_financial_property(name=FinancialProperty.DIVIDENDS_TTM_RATIO, lower=0.05)
    req.add_retrieve_financial(name=FinancialProperty.DIVIDENDS_TTM_RATIO)
    req.set_sort(direction=ScrSortDir.DESC, property_type='financial',
                 property_params={'name': int(FinancialProperty.DIVIDENDS_TTM_RATIO)})
    ```

    实测返回（HK · all_count=463、命中 5 行、head 前 5）：

    ```
          stock_id   code    name  div_ttm_ratio
    50856707752105  00169  万达酒店发展         4.0526
              2136  02136    利福中国         0.6562
    77622943942788  02180    万宝盛华         0.3752
    75419625726233  08473  弥明生活百货         0.3303
    64896955845349  02789    远大中国         0.2994
    ```

    #### 技术指标位置关系 Indicator

    通过 `add_indicator_positional(first_indicator_name, period_type, position, second_indicator=None, value=None, first_indicator_params=None)` 传入；`position` 取自 `Position`（OVER=1、BELOW=2、CROSS_UP=3、CROSS_DOWN=4）

    ##### `MA5 / MA20`（id=11 · indicator · Indicator） MA5 上穿 MA20

    add_indicator_positional：first/second 都是 Indicator 枚举；位置 CROSS_UP=3、CROSS_DOWN=4、OVER=1、BELOW=2

    ```python
    req.add_indicator_positional(first_indicator_name=Indicator.MA5,
                                 period_type=Period.DAY,
                                 position=Position.CROSS_UP,
                                 second_indicator=Indicator.MA20)
    ```

    实测返回（HK · all_count=67、命中 5 行、head 前 5）：

    ```
          stock_id   code    name
    88356067214548  01236   乐动机器人
    88313117542845  02493  迈威生物-B
    88179973556902  02726    瀚天天成
    87033217287972  01828    富卫集团
    86968792779992  03288    海天味业
    ```

    ##### `RSI`（id=52 · indicator · Indicator） RSI 超买（>70）

    指标参数通过 first_indicator_params 传入，例如 RSI 周期 14；单值比较用 second_value

    ```python
    req.add_indicator_positional(first_indicator_name=Indicator.RSI,
                                 period_type=Period.DAY,
                                 position=Position.OVER, second_value=70,
                                 first_indicator_params=[14])
    ```

    实测返回（HK · all_count=97、命中 5 行、head 前 5）：

    ```
          stock_id   code     name
    88502096109937  08561  爱世纪集团股权
    88476326299379  01779   天辰生物-B
    88450556496782  02958  远见控股(旧)
    88416196762328  06872   丹诺医药-B
    88407606823814  02950  升能集团(旧)
    ```

    ##### `MACD_DIF`（id=41 · indicator · Indicator） MACD DIF 在零轴上方

    second_value 为单值阈值；position=OVER 表示 DIF > 0

    ```python
    req.add_indicator_positional(first_indicator_name=Indicator.MACD_DIF,
                                 period_type=Period.DAY,
                                 position=Position.OVER, second_value=0)
    ```

    实测返回（HK · all_count=786、命中 5 行、head 前 5）：

    ```
          stock_id   code      name
    88476326299379  01779    天辰生物-B
    88467736365964  02956  中国健康科技股权
    88450556496782  02958   远见控股(旧)
    88437671594888  02952  杭品生活科技股权
    88433376627363  02723      深演智能
    ```

    ##### `PRICE / BOLL_UPPER`（id=1 · indicator · Indicator） 股价上穿布林上轨

    PRICE(1) 与 BOLL_UPPER(61) 比较位置

    ```python
    req.add_indicator_positional(first_indicator_name=Indicator.PRICE,
                                 period_type=Period.DAY,
                                 position=Position.CROSS_UP,
                                 second_indicator=Indicator.BOLL_UPPER)
    ```

    实测返回（HK · all_count=50、命中 5 行、head 前 5）：

    ```
          stock_id   code    name
    87544318404244  09876  大洋环球控股
    85864986184208  02576  太美医疗科技
    84482006714840  02520    山西安装
    83000243002163  06963    阳光保险
    82961588291781  02245    力勤资源
    ```

    #### 技术指标形态 Pattern

    通过 `add_indicator_pattern(name, period_type)` 传入；`name` 取自 `Pattern` 枚举

    ##### `MACD_GOLD_CROSS`（id=21 · pattern · Pattern） MACD 金叉

    add_indicator_pattern：name 取自 Pattern 枚举

    ```python
    req.add_indicator_pattern(name=Pattern.MACD_GOLD_CROSS, period_type=Period.DAY)
    ```

    实测返回（HK · all_count=116、命中 5 行、head 前 5）：

    ```
          stock_id   code      name
    88502096109937  08561   爱世纪集团股权
    88416196764014  08558  麦迪森控股(旧)
    88265872906147  06051        有赞
    86998857553944  06168       周六福
    86822763895471  06831      绿茶集团
    ```

    ##### `KDJ_GOLD_CROSS`（id=11 · pattern · Pattern） KDJ 金叉

    同上，K 上穿 D

    ```python
    req.add_indicator_pattern(name=Pattern.KDJ_GOLD_CROSS, period_type=Period.DAY)
    ```

    实测返回（HK · all_count=179、命中 5 行、head 前 5）：

    ```
          stock_id   code           name
    88480621267856  02960  ALCO HOLD RTS
    88420491725703  02951        京玖康疗(旧)
    88179973556702  02526           德适-B
    87746181861167  03887  HASHKEY HLDGS
    87741886892639  02655           果下科技
    ```

    ##### `BOLL_BREAK_UPPER`（id=41 · pattern · Pattern） 股价突破布林上轨

    BOLL 形态系列 41~44

    ```python
    req.add_indicator_pattern(name=Pattern.BOLL_BREAK_UPPER, period_type=Period.DAY)
    ```

    实测返回（HK · all_count=50、命中 5 行、head 前 5）：

    ```
          stock_id   code    name
    87544318404244  09876  大洋环球控股
    85864986184208  02576  太美医疗科技
    84482006714840  02520    山西安装
    83000243002163  06963    阳光保险
    82961588291781  02245    力勤资源
    ```

    #### 特色指标 FeaturedProperty

    通过 `add_featured_property(name, intervals, value_set, period, range_period, first_custom_param)` 传入；区间用 `intervals=[(lower, upper)]`，枚举用 `value_set=[...]`

    ##### `SHORT_POSITION`（id=5110 · featured · FeaturedProperty） 空头持仓

    单位：股；不需 intervals

    ```python
    req.add_featured_property(name=FeaturedProperty.SHORT_POSITION)
    req.add_retrieve_featured(name=FeaturedProperty.SHORT_POSITION)
    req.set_sort(direction=ScrSortDir.DESC, property_type='featured',
                 property_params={'name': int(FeaturedProperty.SHORT_POSITION)})
    ```

    实测返回（HK · all_count=0、命中 0 行）：无数据。原因：该 featured 因子 HK 暂未暴露数据，需切换 US 市场查询

    ##### `ANALYST_RATING`（id=5401 · featured · FeaturedProperty） 分析师评级

    枚举值：1=强烈买入、2=买入、3=持有、4=卖出、5=强烈卖出；value_set 传枚举列表

    ```python
    req.add_featured_property(name=FeaturedProperty.ANALYST_RATING, value_set=[1, 2])
    req.add_retrieve_featured(name=FeaturedProperty.ANALYST_RATING)
    req.set_sort(direction=ScrSortDir.ASC, property_type='featured',
                 property_params={'name': int(FeaturedProperty.ANALYST_RATING)})
    ```

    实测返回（HK · all_count=0、命中 0 行）：无数据。原因：需切换至覆盖率更高的 US 市场，或放宽 value_set

    ##### `ANALYST_TARGET_PRICE`（id=5403 · featured · FeaturedProperty） 分析师目标价

    单位：元；区间用 dict 列表 `[{'lower': {'value': X, 'includes': True}}]`，上下限可省

    ```python
    req.add_featured_property(name=FeaturedProperty.ANALYST_TARGET_PRICE,
                              intervals=[{'lower': {'value': 100.0, 'includes': True}}])
    req.add_retrieve_featured(name=FeaturedProperty.ANALYST_TARGET_PRICE)
    req.set_sort(direction=ScrSortDir.DESC, property_type='featured',
                 property_params={'name': int(FeaturedProperty.ANALYST_TARGET_PRICE)})
    ```

    实测返回（HK · all_count=0、命中 0 行）：无数据。原因：需切换至覆盖率更高的 US 市场，或放宽 intervals 下限

    ##### `HIST_PERCENTILE_PE`（id=5502 · featured · FeaturedProperty） 当前 PE 历史百分位

    range_period 必传：RangePeriod 枚举 (THREE_MONTHS=1、SIX_MONTHS=2、ONE_YEAR=3、THREE_YEARS=4)

    ```python
    req.add_featured_property(name=FeaturedProperty.HIST_PERCENTILE_PE,
                              range_period=RangePeriod.THREE_YEARS,
                              intervals=[{'upper': {'value': 0.30, 'includes': True}}])
    req.add_retrieve_featured(name=FeaturedProperty.HIST_PERCENTILE_PE,
                              range_period=RangePeriod.THREE_YEARS)
    req.set_sort(direction=ScrSortDir.ASC, property_type='featured',
                 property_params={'name': int(FeaturedProperty.HIST_PERCENTILE_PE),
                                  'rangePeriod': int(RangePeriod.THREE_YEARS)})
    ```

    实测返回（HK · all_count=0、命中 0 行）：无数据。原因：HK 部分股票无历史 PE 数据，可放宽 range_period / intervals

    ##### `CASH_FLOW_MAIN_NET_IN`（id=5901 · featured · FeaturedProperty） 主力资金净流入

    单位：元；资金流入用 CashFlowPeriod 枚举 (DAY=1、WEEK=2、MONTH_P=3、QUARTER=4)

    ```python
    req.add_featured_property(name=FeaturedProperty.CASH_FLOW_MAIN_NET_IN,
                              range_period=CashFlowPeriod.DAY,
                              intervals=[{'lower': {'value': 10_000_000.0, 'includes': True}}])
    req.add_retrieve_featured(name=FeaturedProperty.CASH_FLOW_MAIN_NET_IN,
                              range_period=CashFlowPeriod.DAY)
    req.set_sort(direction=ScrSortDir.DESC, property_type='featured',
                 property_params={'name': int(FeaturedProperty.CASH_FLOW_MAIN_NET_IN),
                                  'rangePeriod': int(CashFlowPeriod.DAY)})
    ```

    实测返回（HK · all_count=0、命中 0 行）：无数据。原因：HK 实测无数据，建议改用 US 市场或更短周期

    #### 经纪商持股 BrokerProperty

    通过 `add_broker_holdings(name, days, param, intervals)` 传入；**仅港股**；`days` 参数不生效。

    - **支持因子**：6101 集中度 / 6103 数量 / 6106 中央结算持股占比 / 6107 中央结算持股变动
    - **不支持因子**：6102 持仓变动、6104 经纪商排行、6105 经纪商持仓量
    - **倍率**：6101 / 6106 / 6107 倍率 1000，按百分数传值（20% 传 20）；6103 无倍率（整数）
    - **intervals 用法**：dict 列表，key 用 `filterMin` / `filterMax`（**不是 `lower` / `upper`**），支持单端或双端区间。示例：`[{'filterMin': {'value': 20.0, 'includes': True}}]` 或 `[{'filterMin': {'value': 20.0, 'includes': True}, 'filterMax': {'value': 50.0, 'includes': False}}]`

    ##### `CONCENTRATED_DISTRIBUTION`（id=6101 · broker · BrokerProperty） 经纪商集中度

    仅港股；intervals 按 dict 列表传，单位 %（20% 传 20.0）；param=经纪商代码逗号分隔

    ```python
    req.add_broker_holdings(name=BrokerProperty.CONCENTRATED_DISTRIBUTION,
                            intervals=[{'filterMin': {'value': 20.0, 'includes': True}}])
    req.add_retrieve_broker(name=BrokerProperty.CONCENTRATED_DISTRIBUTION)
    req.set_sort(direction=ScrSortDir.DESC, property_type='broker',
                 property_params={'name': int(BrokerProperty.CONCENTRATED_DISTRIBUTION)})
    ```

    ##### `CENTRAL_HOLDINGS_RATIO`（id=6106 · broker · BrokerProperty） 中央结算系统持股占比

    仅港股；intervals 按 dict 列表传，单位 %

    ```python
    req.add_broker_holdings(name=BrokerProperty.CENTRAL_HOLDINGS_RATIO,
                            intervals=[{'filterMin': {'value': 10.0, 'includes': True}}])
    req.add_retrieve_broker(name=BrokerProperty.CENTRAL_HOLDINGS_RATIO)
    req.set_sort(direction=ScrSortDir.DESC, property_type='broker',
                 property_params={'name': int(BrokerProperty.CENTRAL_HOLDINGS_RATIO)})
    ```

    ##### `BROKER_NUM`（id=6103 · broker · BrokerProperty） 持有该股的经纪商数量

    仅港股；整数（intervals 用 dict 列表）

    ```python
    req.add_broker_holdings(name=BrokerProperty.BROKER_NUM,
                            intervals=[{'filterMin': {'value': 100, 'includes': True}}])
    req.add_retrieve_broker(name=BrokerProperty.BROKER_NUM)
    req.set_sort(direction=ScrSortDir.DESC, property_type='broker',
                 property_params={'name': int(BrokerProperty.BROKER_NUM)})
    ```

    #### K 线形态 KlineShapeProperty

    通过 `add_kline_shape(name, period, value_set)` 传入；`period` 必传，目前仅支持日 K(`Period.DAY`=11) 与 1 小时 K(`Period.HOUR_1`=5)

    ##### `SHAPE_TYPE`（id=6200 · kline_shape · KlineShapeProperty） K 线形态识别

    period 必传：日 K=11、1 小时 K=5（实测发现 SDK 文档曾标注 21，但 21 实为周 K，应传 5）；value_set 取自 KlineShapeType

    ```python
    req.add_kline_shape(name=KlineShapeProperty.SHAPE_TYPE, period=Period.DAY,
                        value_set=[KlineShapeType.DOUBLE_BOTTOMS,
                                   KlineShapeType.HEAD_SHOULDERS_BOTTOM])
    req.add_retrieve_kline_shape(name=KlineShapeProperty.SHAPE_TYPE, period=Period.DAY)
    ```

    实测返回（HK · all_count=0、命中 0 行）：无数据。原因：指定形态 + 区间无命中，可放宽 value_set

    ##### `RISE_PROB`（id=6201 · kline_shape · KlineShapeProperty） 形态后上涨概率

    单位：% ；与 SHAPE_TYPE 联合使用

    ```python
    req.add_kline_shape(name=KlineShapeProperty.SHAPE_TYPE, period=Period.DAY,
                        value_set=[KlineShapeType.DOUBLE_BOTTOMS])
    req.add_retrieve_kline_shape(name=KlineShapeProperty.RISE_PROB, period=Period.DAY)
    req.set_sort(direction=ScrSortDir.DESC, property_type='kline_shape',
                 property_params={'name': int(KlineShapeProperty.RISE_PROB),
                                  'period': int(Period.DAY)})
    ```

    实测返回（HK · all_count=0、命中 0 行）：无数据。原因：与 SHAPE_TYPE 联用；HK 抽样无命中

    #### 期权属性 OptionProperty

    通过 `add_option(name, intervals, param, period)` 传入；用于按正股 IV / HV 等期权维度筛选

    ##### `STOCK_IV`（id=1000 · option · OptionProperty） 正股期权隐含波动率

    单位：% ；intervals 用 dict 列表；period 取自 OptionHVPeriod (HV_30D/60D/90D/120D/365D)

    ```python
    req.add_option(name=OptionProperty.STOCK_IV,
                   intervals=[{'lower': {'value': 30.0, 'includes': True}}])
    req.add_retrieve_option(name=OptionProperty.STOCK_IV)
    req.set_sort(direction=ScrSortDir.DESC, property_type='option',
                 property_params={'name': int(OptionProperty.STOCK_IV)})
    ```

    实测返回（HK · all_count=0、命中 0 行）：无数据。原因：需切换至期权全集市场（US）或放低 intervals 下限

    ##### `STOCK_IV_RANK`（id=1001 · option · OptionProperty） 正股 IV Rank

    0~100；衡量当前 IV 在历史中的相对位置（intervals 用 dict 列表）

    ```python
    req.add_option(name=OptionProperty.STOCK_IV_RANK,
                   intervals=[{'lower': {'value': 50.0, 'includes': True}}])
    req.add_retrieve_option(name=OptionProperty.STOCK_IV_RANK)
    req.set_sort(direction=ScrSortDir.DESC, property_type='option',
                 property_params={'name': int(OptionProperty.STOCK_IV_RANK)})
    ```

    实测返回（HK · all_count=0、命中 0 行）：无数据。原因：需切换至期权全集市场（US）或放低 intervals 下限

    ##### `STOCK_HV`（id=1006 · option · OptionProperty） 正股历史波动率

    单位：% ；intervals 用 dict 列表；period 取自 OptionHVPeriod

    ```python
    req.add_option(name=OptionProperty.STOCK_HV,
                   intervals=[{'lower': {'value': 20.0, 'includes': True}}])
    req.add_retrieve_option(name=OptionProperty.STOCK_HV)
    req.set_sort(direction=ScrSortDir.DESC, property_type='option',
                 property_params={'name': int(OptionProperty.STOCK_HV)})
    ```

    实测返回（HK · all_count=0、命中 0 行）：无数据。原因：需切换至期权全集市场（US）或放低 intervals 下限

:::tip 接口限制
* 每 30 秒内最多请求 10 次条件选股接口
:::

---

# 获取板块内股票列表

`get_plate_stock(plate_code, sort_field=SortField.CODE, ascend=True)`

* **介绍**

    获取指定板块内的股票列表，获取股指的成分股

* **参数**
    参数|类型|说明
    :-|:-|:-
    plate_code|str|板块代码  (先利用 [获取板块列表](../quote/get-plate-list.md) 获取板块代码例如：“SH.BK0001”，“SH.BK0002”)
    sort_field|[SortField](./quote.md#2930)|排序字段
    ascend|bool|排序方向  (True：升序False：降序)


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回板块股票数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 板块股票数据
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        lot_size|int|每手股数，期货表示合约乘数
        stock_name|str|股票名称
        stock_type|[SecurityType](./quote.md#3325)|股票类型
        list_time|str|上市时间  (格式：yyyy-MM-dd
港股和 A 股市场默认是北京时间，美股市场默认是美东时间)
        stock_id|int|股票 ID
        main_contract|bool|是否主连合约  (期货特有字段)
        last_trade_time|str|最后交易时间  (期货特有字段主连，当月，下月等期货没有该字段)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_plate_stock('HK.BK1001')
if ret == RET_OK:
    print(data)
    print(data['stock_name'][0])    # 取第一条的股票名称
    print(data['stock_name'].values.tolist())   # 转为 list
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
    code  lot_size stock_name  stock_owner  stock_child_type stock_type   list_time        stock_id  main_contract last_trade_time
0   HK.00462      4000       天然乳品          NaN               NaN      STOCK  2005-06-10  55589761712590          False                
..       ...       ...        ...          ...               ...        ...         ...             ...            ...             ...
9   HK.06186      1000       中国飞鹤          NaN               NaN      STOCK  2019-11-13  78159814858794          False               

[10 rows x 10 columns]
天然乳品
['天然乳品', '现代牧业', '雅士利国际', '原生态牧业', '中国圣牧', '中地乳业', '庄园牧场', '澳优', '蒙牛乳业', '中国飞鹤']
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取板块内股票列表接口
:::

::: details  常用的板块、指数代码
代码|说明
:-|:-
HK.HSI Constituent Stocks|恒指成份股
HK.HSCEI Stock|国指成份股
HK.Motherboard|港股主板
HK.GEM|港股创业板
HK.LIST1910|所有港股
HK.LIST1911|主板 H 股
HK.LIST1912|创业板 H 股
HK.Fund|ETF（港股基金）
HK.LIST1600|热度榜（港）
HK.LIST1921|已上市新股-港股
SH.LIST3000000|上海主板
SH.LIST0901|上证 B 股
SH.LIST0902|深证 B 股
SH.LIST3000002|沪深指数
SH.LIST3000005|全部 A 股（沪深）
SH.LIST0600|热度榜（沪深）
SH.LIST0992|科创板
SH.LIST0921|已上市新股-A 股	
SZ.LIST3000001|深证主板
SZ.LIST3000003|中小板
SZ.LIST3000004|创业板（深）
US.USAALL|全部美股
:::

---

# 获取板块列表

`get_plate_list(market, plate_class)`

* **介绍**

    获取板块列表

* **参数**
    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场标识  (注意：这里不区分沪和深，输入沪或者深都会返回沪深市场的子板块)
    plate_class|[Plate](./quote.md#1362)|板块分类


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回板块列表数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 板块列表数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|板块代码
        plate_name|str|板块名字
        plate_id|str|板块 ID

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_plate_list(Market.HK, Plate.CONCEPT)
if ret == RET_OK:
    print(data)
    print(data['plate_name'][0])    # 取第一条的板块名称
    print(data['plate_name'].values.tolist())   # 转为 list
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
    code plate_name plate_id
0   HK.BK1000      做空集合股   BK1000
..        ...        ...      ...
77  HK.BK1999       殡葬概念   BK1999

[78 rows x 3 columns]
做空集合股
['做空集合股', '阿里概念股', '雄安概念股', '苹果概念', '一带一路', '5G概念', '夜店股', '粤港澳大湾区', '特斯拉概念股', '啤酒', '疑似财技股', '体育用品', '稀土概念', '人民币升值概念', '抗疫概念', '新股与次新股', '腾讯概念', '云办公', 'SaaS概念', '在线教育', '汽车经销商', '挪威政府全球养老基金持仓', '武汉本地概念股', '核电', '内地医药股', '化妆美容股', '科网股', '公用股', '石油股', '电讯设备', '电力股', '手游股', '婴儿及小童用品股', '百货业股', '收租股', '港口运输股', '电信股', '环保', '煤炭股', '汽车股', '电池', '物流', '内地物业管理股', '农业股', '黄金股', '奢侈品股', '电力设备股', '连锁快餐店', '重型机械股', '食品股', '内险股', '纸业股', '水务股', '奶制品股', '光伏太阳能股', '内房股', '内地教育股', '家电股', '风电股', '蓝筹地产股', '内银股', '航空股', '石化股', '建材水泥股', '中资券商股', '高铁基建股', '燃气股', '公路及铁路股', '钢铁金属股', '华为概念', 'OLED概念', '工业大麻', '香港本地股', '香港零售股', '区块链', '猪肉概念', '节假日概念', '殡葬概念']
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取板块列表接口
:::

---

# 获取静态数据

`get_stock_basicinfo(market, stock_type=SecurityType.STOCK, code_list=None)`

* **介绍**

    获取静态数据

* **参数**
    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场类型
    stock_type|[SecurityType](./quote.md#3325)|股票类型，但不支持传入 SecurityType.DRVT
    code_list|list|股票列表  (- 默认为 None，代表获取全市场股票的静态信息
  - 若传入股票列表，只返回指定股票的信息
  - 支持传入期权
  - list 中元素类型是 str)
    注：当 market 和 code_list 同时存在时，会忽略 market，仅对 code_list 进行查询。


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回股票静态数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 股票静态数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        lot_size|int|每手股数，期权表示每份合约股数  (指数期权无该字段)，期货表示合约乘数
        stock_type|[SecurityType](./quote.md#3325)|股票类型
        stock_child_type|[WrtType](./quote.md#926)|窝轮子类型
        stock_owner|str|窝轮所属正股的代码，或期权标的股的代码
        option_type|[OptionType](./quote.md#3713)|期权类型
        strike_time|str|期权行权日  (格式：yyyy-MM-dd
港股和 A 股市场默认是北京时间，美股市场默认是美东时间)
        strike_price|float|期权行权价
        suspension|bool|期权是否停牌  (True：停牌False：未停牌)
        listing_date|str|上市时间  (此字段停止维护，不建议使用
格式：yyyy-MM-dd)
        stock_id|int|股票 ID
        delisting|bool|是否退市
        index_option_type|str|指数期权类型
        main_contract|bool|是否主连合约
        last_trade_time|str|最后交易时间  (主连，当月，下月等期货没有该字段)
        exchange_type|[ExchType](./quote.html#6898)|所属交易所

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret, data = quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK)
if ret == RET_OK:
    print(data)
else:
    print('error:', data)
print('******************************************')
ret, data = quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK, ['HK.06998', 'HK.00700'])
if ret == RET_OK:
    print(data)
    print(data['name'][0])  # 取第一条的股票名称
    print(data['name'].values.tolist())  # 转为 list
else:
    print('error:', data)
quote_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
        code             name  lot_size stock_type stock_child_type stock_owner option_type strike_time strike_price suspension listing_date        stock_id  delisting index_option_type  main_contract last_trade_time exchange_type
0      HK.00001               长和       500      STOCK              N/A                     N/A                      N/A        N/A   2015-03-18   4440996184065      False               N/A          False                  HK_MAINBOARD  
...         ...              ...       ...        ...              ...         ...         ...         ...          ...        ...          ...             ...        ...               ...            ...             ...
2592   HK.09979     绿城管理控股      1000      STOCK              N/A                                              N/A        N/A   2020-07-10  79203491915515      False               N/A          False                  HK_MAINBOARD                

[2593 rows x 16 columns]
******************************************
        code            name  lot_size stock_type stock_child_type stock_owner option_type strike_time strike_price suspension listing_date        stock_id  delisting index_option_type  main_contract last_trade_time exchange_type
0  HK.06998     嘉和生物-B       500      STOCK              N/A                                              N/A        N/A   2020-10-07  79572859099990      False               N/A          False                  HK_MAINBOARD                
1  HK.00700     腾讯控股         100      STOCK              N/A                                              N/A        N/A   2004-06-16  54047868453564      False               N/A          False                  HK_MAINBOARD               
嘉和生物-B
['嘉和生物-B', '腾讯控股']
```

:::tip 提示
* 当传入程序无法识别的股票时（包括很久之前退市的股票和不存在的股票），此接口仍然返回股票信息，用“是否退市”字段来标识该股票不存在。统一处理为：代码正常显示，股票名显示为“未知股票”，其他字段均为默认值（整型默认是0，字符串默认是空字符串）。
* 此接口与其他的行情接口不同，其他接口遇到程序无法识别的股票时，会拒绝请求并返回错误描述“未知股票”。
* 获取期权数据（例如：希腊值、到期日、未平仓量），请使用 [获取快照](./get-market-snapshot.md)。
:::

---

# 获取 IPO 信息

`get_ipo_list(market)`

* **介绍**

    获取指定市场的 IPO 信息

* **参数**
    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场标识  (注意：这里不区分沪和深，输入沪或者深都会返回沪深市场的股票)


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回 IPO 数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * IPO 数据
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        list_time|str|上市日期，美股是预计上市日期 (格式：yyyy-MM-dd)
        list_timestamp|float|上市日期时间戳，美股是预计上市日期时间戳
        apply_code|str|申购代码（A 股适用）
        issue_size|int|发行总数（A 股适用）；发行量（美股、新加坡、马来西亚、日本适用）
        online_issue_size|int|网上发行量（A 股适用）
        apply_upper_limit|int|申购上限（A 股适用）
        apply_limit_market_value|int|顶格申购需配市值（A 股适用）
        is_estimate_ipo_price|bool|是否预估发行价（A 股适用）
        ipo_price|float|发行价  (预估值会因为募集资金、发行数量、发行费用等数据变动而变动，仅供参考。实际数据公布后会第一时间更新)（A 股适用）
        industry_pe_rate|float|行业市盈率（A 股适用）
        is_estimate_winning_ratio|bool|是否预估中签率（A 股适用）
        winning_ratio|float|中签率  (- 预估值会因为募集资金、发行数量、发行费用等数据变动而变动，仅供参考。实际数据公布后会第一时间更新
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)（A 股适用）
        issue_pe_rate|float|发行市盈率（A 股适用）
        apply_time|str|申购日期字符串 (格式：yyyy-MM-dd)（A 股适用）
        apply_timestamp|float|申购日期时间戳（A 股适用）
        winning_time|str|公布中签日期字符串 (格式：yyyy-MM-dd)（A 股、新加坡、马来西亚适用）
        winning_timestamp|float|公布中签日期时间戳（A 股、新加坡、马来西亚适用）
        is_has_won|bool|是否已经公布中签号（A 股适用）
        winning_num_data|str|中签号（A 股适用）  (格式类似：末"五"位数：12345，12346末"六"位数：123456)
        ipo_price_min|float|最低发售价（港股适用）；最低发行价（美股、新加坡、日本适用）
        ipo_price_max|float|最高发售价（港股适用）；最高发行价（美股、新加坡、日本适用）
        list_price|float|上市价（港股适用）
        lot_size|int|每手股数
        entrance_price|float|入场费（港股适用）
        is_subscribe_status|bool|是否为认购状态  (True：认购中False：待上市)
        apply_end_time|str|截止认购日期字符串 (格式：yyyy-MM-dd)（港股、新加坡、马来西亚适用）
        apply_end_timestamp|float|截止认购日期时间戳|因需处理认购手续，富途认购截止时间会早于交易所公布的日期（港股、新加坡、马来西亚适用）
        apply_start_time|str|开始认购日期字符串 (格式：yyyy-MM-dd)（新加坡、马来西亚适用）
        apply_start_timestamp|float|开始认购日期时间戳（新加坡、马来西亚适用）
        offer_price|float|发行价（马来西亚适用）

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_ipo_list(Market.HK)
if ret == RET_OK:
    print(data)
    print(data['code'][0])    # 取第一条的股票代码
    print(data['code'].values.tolist())   # 转为 list
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
    code      name   list_time  list_timestamp apply_code issue_size online_issue_size apply_upper_limit apply_limit_market_value is_estimate_ipo_price ipo_price industry_pe_rate is_estimate_winning_ratio winning_ratio issue_pe_rate apply_time apply_timestamp winning_time winning_timestamp is_has_won winning_num_data  ipo_price_min  ipo_price_max  list_price  lot_size  entrance_price  is_subscribe_status apply_end_time  apply_end_timestamp  apply_start_time  apply_start_timestamp  offer_price
0  HK.06666  恒大物业  2020-12-02    1.606838e+09        N/A        N/A               N/A               N/A                      N/A                   N/A       N/A              N/A                       N/A           N/A           N/A        N/A             N/A          N/A               N/A        N/A              N/A          8.500           9.75         0.0       500         4924.12                 True     2020-11-26         1.606352e+09               N/A                    N/A          N/A
1  HK.02110  裕勤控股  2020-12-07    1.607270e+09        N/A        N/A               N/A               N/A                      N/A                   N/A       N/A              N/A                       N/A           N/A           N/A        N/A             N/A          N/A               N/A        N/A              N/A          0.225           0.27         0.0     10000         2727.21                 True     2020-11-27         1.606439e+09               N/A                    N/A          N/A
HK.06666
['HK.06666', 'HK.02110']
```

::: tip 接口限制
* 每 30 秒内最多请求 10 次获取 IPO 信息接口
:::

---

# 获取全局市场状态

`get_global_state()`  

* **介绍**

    获取全局状态


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK 时，返回全局状态</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 全局状态字典格式如下：
        字段|类型|说明
        :-|:-|:-
        market_sz|[MarketState](./quote.md#1252)|深圳市场状态
        market_sh|[MarketState](./quote.md#1252)|上海市场状态
        market_hk|[MarketState](./quote.md#1252)|香港市场状态
        market_hkfuture|[MarketState](./quote.md#1252)|香港期货市场状态  (不同品种的交易时间存在差异，建议使用 [get_market_state](../quote/get-market-state.md) 接口获取指定品种的市场状态)
        market_usfuture|[MarketState](./quote.md#1252)|美国期货市场状态  (不同品种的交易时间存在差异，建议使用 [get_market_state](../quote/get-market-state.md) 接口获取指定品种的市场状态)
        market_us|[MarketState](./quote.md#1252)|美国市场状态  (不同品种的交易时间存在差异，建议使用 [get_market_state](../quote/get-market-state.md) 接口获取指定品种的市场状态)
        market_sgfuture|[MarketState](./quote.md#1252)|新加坡期货市场状态  (不同品种的交易时间存在差异，建议使用 [get_market_state](../quote/get-market-state.md) 接口获取指定品种的市场状态)
        market_jpfuture|[MarketState](./quote.md#1252)|日本期货市场状态
        market_sg|[MarketState](./quote.md#1252)|新加坡市场状态
        market_my|[MarketState](./quote.md#1252)|马来西亚市场状态
        market_jp|[MarketState](./quote.md#1252)|日本市场状态
        server_ver|str|OpenD 版本号
        trd_logined|bool|True：已登录交易服务器，False：未登录交易服务器
        qot_logined|bool|True：已登录行情服务器，False：未登录行情服务器
        timestamp|str|当前格林威治时间戳  (单位：秒)
        local_timestamp|float|OpenD 运行机器的当前时间戳  (单位：秒)
        program_status_type|[ProgramStatusType](../ftapi/common.md#6427)|当前状态
        program_status_desc|str|额外描述
    

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
print(quote_ctx.get_global_state())
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
(0, {'market_sz': 'MORNING', 'market_us': 'AFTER_HOURS_END', 'market_sh': 'MORNING', 'market_hk': 'MORNING', 'market_hkfuture': 'FUTURE_DAY_OPEN', 'market_usfuture': 'FUTURE_OPEN', 'market_sgfuture': 'FUTURE_DAY_OPEN', 'market_jpfuture': 'FUTURE_DAY_OPEN', 'server_ver': '504', 'trd_logined': True, 'timestamp': '1620962951', 'qot_logined': True, 'local_timestamp': 1620962951.047128, 'program_status_type': 'READY', 'program_status_desc': ''})
```

---

# 获取交易日历

`request_trading_days(market=None, start=None, end=None, code=None)`

* **介绍**

    请求指定市场 / 指定标的的交易日历。  
    注意：该交易日是通过自然日剔除周末和节假日得到，未剔除临时休市数据。  

* **参数**
    参数|类型|说明
    :-|:-|:-
    market|[TradeDateMarket](./quote.md#940)|市场类型
    start|str|起始日期  (格式：yyyy-MM-dd
例如：“2018-01-01”)
    end|str|结束日期  (格式：yyyy-MM-dd
例如：“2018-01-01”)
    code| str | 股票代码
    注：当 market 和 code 同时存在时，会忽略 market，仅对 code 进行查询。

    * start 和 end 的组合如下
        Start 类型|End 类型|说明
        :-|:-|:-
        str|str|start 和 end 分别为指定的日期
        None|str|start 为 end 往前 365 天
        str|None|end 为 start 往后 365 天
        None|None|start 为往前 365 天，end 当前日期


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>list</td>
            <td>当 ret == RET_OK 时，返回交易日数据。list 中元素类型为 dict</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 交易日数据格式如下：
        字段|类型|说明
        :-|:-|:-
        time|str|时间 (格式：yyyy-MM-dd)
        trade_date_type|[TradeDateType](./quote.md#6676)|交易日类型

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.request_trading_days(market=TradeDateMarket.HK, start='2020-04-01', end='2020-04-10')
if ret == RET_OK:
    print('HK market calendar:', data)
else:
    print('error:', data)
print('******************************************')
ret, data = quote_ctx.request_trading_days(start='2020-04-01', end='2020-04-10', code='HK.00700')
if ret == RET_OK:
    print('HK.00700 calendar:', data)
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
HK market calendar: [{'time': '2020-04-01', 'trade_date_type': 'WHOLE'}, {'time': '2020-04-02', 'trade_date_type': 'WHOLE'}, {'time': '2020-04-03', 'trade_date_type': 'WHOLE'}, {'time': '2020-04-06', 'trade_date_type': 'WHOLE'}, {'time': '2020-04-07', 'trade_date_type': 'WHOLE'}, {'time': '2020-04-08', 'trade_date_type': 'WHOLE'}, {'time': '2020-04-09', 'trade_date_type': 'WHOLE'}]
******************************************
HK.00700 calendar: [{'time': '2020-04-01', 'trade_date_type': 'WHOLE'}, {'time': '2020-04-02', 'trade_date_type': 'WHOLE'}, {'time': '2020-04-03', 'trade_date_type': 'WHOLE'}, {'time': '2020-04-06', 'trade_date_type': 'WHOLE'}, {'time': '2020-04-07', 'trade_date_type': 'WHOLE'}, {'time': '2020-04-08', 'trade_date_type': 'WHOLE'}, {'time': '2020-04-09', 'trade_date_type': 'WHOLE'}]
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次获取交易日接口。
* 历史交易日历提供过去 10 年的数据，未来交易日历提供到今年 12 月 31 日 (举例：今天的日期是 2021 年 7 月 6 日，我们仅提供 2011-07-06 到 2021-12-31 期间的交易日历)。
:::

---

﻿# 搜索行情标的

`get_search_quote(keyword, max_count=10)`

* **介绍**

    按关键词搜索行情标的，返回匹配的标的列表。

* **参数**

    参数|类型|说明
    :-|:-|:-
    keyword|str|搜索词
    max_count|int|本次请求的最大返回条数  (默认10条，最大100条)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回搜索行情列表</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * DataFrame 字段说明：

        字段|类型|说明
        :-|:-|:-
        market|[Market](./quote.md#427)|市场类型
        code|str|股票代码
        name|str|股票名称
        sec_type|[SecurityType](./quote.md#3325)|股票类型
        is_watched|bool|是否已在自选

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret, data = quote_ctx.get_search_quote('aapl',10)
if ret == RET_OK:
    print(data)
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
  market         code                        name sec_type  is_watched
0     US      US.AAPL                          苹果    STOCK        True
1     US      US.AAPB  2倍做多AAPL ETF-GraniteShares      ETF       False
2     US  US.LIST2139                        虚拟现实    PLATE       False
3     US  US.LIST2432                       流媒体概念    PLATE       False
4     US  US.LIST2437                        苹果概念    PLATE       False
5     JP      JP.2788         Apple International    STOCK       False
6     US      US.AAPI     APPLE ISPORTS GROUP INC    STOCK       False
7     SH    SH.603020                        爱普股份    STOCK       False
8     US      US.APLY      AAPL期权收益策略ETF-YieldMax      ETF       False
9     US      US.APRU      APPLE RUSH COMPANY INC    STOCK       False
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次搜索行情标的接口。
:::

---

﻿# 搜索资讯

`get_search_news(keyword, max_count=10, news_sub_type=NewsSubType.ALL)`

* **介绍**

    按关键词搜索资讯，返回匹配的新闻、公告、评级等资讯列表。

* **参数**

    参数|类型|说明
    :-|:-|:-
    keyword|str|搜索词
    max_count|int|本次请求的最大返回条数  (默认10条，最大100条)
    news_sub_type|[NewsSubType](./quote.md#320)|资讯子类型  (默认 NewsSubType.ALL)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回搜索资讯列表</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * DataFrame 字段说明：

        字段|类型|说明
        :-|:-|:-
        title|str|标题
        news_sub_type|[NewsSubType](./quote.md#320)|资讯子类型
        source|str|来源
        publish_time|str|发布时间
        view_count|int|浏览量
        related_securities|list|关联标的列表
        url|str|详情页链接

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret, data = quote_ctx.get_search_news('space', 10, news_sub_type=NewsSubType.ALL)
if ret == RET_OK:
    print(data)
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
                                               title news_sub_type       source publish_time  view_count related_securities                                                url
0                         Space：2026年12月期 第一财季业绩说明材料          NEWS        日本交易所         5/13         329                 []           https://news.futunn.com/notice/307288728
1               Space：2026年12月期 第一财季业绩简报[日本会计准则]（合并）          NEWS        日本交易所         5/13         277                 []           https://news.futunn.com/notice/307288725
2           SPACE CO., LTD. 第一季度盈利表现强劲，但全年利润和股息预期下调。          NEWS     TipRanks         5/13         201                 []  https://news.futunn.com/post/73007255?futusour...
3               New Street Research 开始覆盖太空经济和基础设施领域。          NEWS  PR Newswire         5/14        6035                 []  https://news.futunn.com/post/73047684?futusour...
4                                        Space：临时报告书          NEWS        日本金融厅         3/27         257                 []           https://news.futunn.com/notice/306761904
5                    Gemini Space Station | 8-K：重大事件        NOTICE      美股SEC公告         6/16         278          [US.GEMI]  https://news.futunn.com/notice/307532371?futus...
6  Extra Space Storage | 4：持股变动声明-高管 McNeal Gwyn ...        NOTICE      美股SEC公告         6/13         348           [US.EXR]  https://news.futunn.com/notice/307521769?futus...
7        Space Exploration Technologies Corp：承保或代理协议        NOTICE        SEDAR         6/12         400                 []  https://news.futunn.com/notice/307519369?futus...
8  Space Exploration Technologies Corp：补充长期形式的预备招...        NOTICE        SEDAR         6/12         231                 []  https://news.futunn.com/notice/307519371?futus...
9  Space Exploration Technologies Corp：补充长期形式的预备招...        NOTICE        SEDAR         6/12         210                 []  https://news.futunn.com/notice/307519370?futus...
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次搜索资讯接口。
:::

---

# 获取财报日历

`get_earnings_calendar(market, sort_type=None, begin_date=None, end_date=None, filter_list=None)`

* **介绍**

    获取财报日历，返回指定市场在指定日期范围内即将或已经发布财报的股票列表，包含财报日期、EPS/营收/EBIT 的实际值与预测值、期权隐含波动率等信息。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场类型（必填）
    sort_type|[EarningsCalendarSortType](./quote-market.md#1099)|排序类型（默认 Hot）
    begin_date|str|开始日期，格式 "yyyy-MM-dd"，不传默认今天（仅拉取当天）
    end_date|str|结束日期，格式 "yyyy-MM-dd"，不传则仅拉取 beginDate 当天；与 beginDate 间隔不超过 7 天
    filter_list|list[`EarningsCalendarFilter`]|筛选条件列表（多条件为 AND 关系）

* **输入限制**

    - **`filter_list` 筛选条件（`EarningsCalendarFilter`）：**

      通过 `EarningsCalendarFilter` 构造筛选条件，支持两种筛选方式：

      | 构造参数 | 说明 |
      |----------|------|
      | `indicator_type` | 筛选因子类型（`EarningsCalendarIndicatorType`，必填） |
      | `value_list` | 确切值列表（用于发布类型、指标类型、股票列表类型等枚举型筛选） |
      | `interval_min` / `interval_max` | 范围筛选的最小/最大值 |
      | `min_inclusive` / `max_inclusive` | 范围边界是否包含（默认 True） |

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'US.AAPL'`）
        name|str|股票名称
        earnings_date|str|财报日期（"yyyy-MM-dd"）
        earnings_timestamp|float|财报发布时间戳（Unix 秒）
        pub_type|str|发布类型（BEFORE=盘前 / AFTER=盘后 / REGULAR=盘中）
        period_text|str|财年周期（如 `'2025Q1'`）
        eps_actual|float|EPS 实际值（已发布时有值）
        eps_predict|float|EPS 预测值
        revenue_actual|float|总收入实际值（已发布时有值）
        revenue_predict|float|总收入预测值
        ebit_actual|float|息税前利润实际值（已发布时有值）
        ebit_predict|float|息税前利润预测值
        option_volume|int|期权成交量（仅港美股）
        iv|float|隐含波动率（%）（仅港美股）
        iv_rank|float|IV 等级（%）（仅港美股）
        iv_percentile|float|IV 百分位数（%）（仅港美股）
        market_cap|float|实时市值
        price|float|最新价

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_earnings_calendar(market=Market.US)
if ret == RET_OK:
    print(data.head(2))
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
security  name earnings_date  earnings_timestamp pub_type period_text eps_actual eps_predict revenue_actual revenue_predict ebit_actual   ebit_predict  option_volume       iv  iv_rank  iv_percentile    market_cap    price
0    US.MU  美光科技    2026-06-24        1.782331e+09    AFTER      2026Q3        N/A     20.8654            N/A   35251836320.0         N/A  26879423830.0         633420  113.795   97.754         98.015  1.186117e+12  1051.77
1  US.PAYX    沛齐    2026-06-24        1.782308e+09   BEFORE      2026Q4        N/A      1.2167            N/A    1606293190.0         N/A    661853410.0           6603   42.209   85.862         93.650  3.510892e+10    97.99
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取宏观指标列表

`get_macro_indicator_list(region)`

* **介绍**

    获取宏观指标列表，返回指定国家/地区的宏观经济指标分类及指标信息，包含指标 ID 和名称，用于后续查询历史数据。

* **参数**

    参数|类型|说明
    :-|:-|:-
    region|[MacroRegion](./quote-market.md#888)|国家/地区（必填）

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        category_name|str|分类名称（如"全部"/"就业"/"通胀"/"利率"）
        indicator_id|int|宏观指标 ID（用于查询历史数据）
        name|str|指标名称

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_macro_indicator_list(region=MacroRegion.US)
if ret == RET_OK:
    print(data.head(2))
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
category_name  indicator_id              name
0            物价    1003000003  美国生产者物价指数(PPI)同比
1            物价    1003000001         美国核心CPI同比
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取宏观指标历史数据

`get_macro_indicator_history(indicator_id, time=None, max_count=None)`

* **介绍**

    获取宏观指标历史数据，返回指定宏观指标的历史数据点列表，包含数据日期、公布日期、公布值、预测值、前值等信息，按时间降序排列。

* **参数**

    参数|类型|说明
    :-|:-|:-
    indicator_id|int|宏观指标 ID（来自 `get_macro_indicator_list` 返回）（必填）
    time|str|时间节点，格式 "yyyy-MM-dd"，从该时间往前拉取；不传默认当前时间
    max_count|int|拉取条数，默认 100，上限 1000

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        data_time|str|数据日期（"yyyy-MM-dd"）
        release_time|str|公布日期（"yyyy-MM-dd HH:mm:ss"）
        value|float|公布值（已还原为原始值）
        predict_value|float|预测值（已还原）
        previous_value|float|前值（已还原）
        unit_type|str|单位类型（PERCENT=百分比 / VALUE=数值 / INDEX=指数）

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 先获取指标ID
ret, indicators = quote_ctx.get_macro_indicator_list(region=MacroRegion.US)
if ret == RET_OK:
    indicator_id = indicators.iloc[0]['indicator_id']

    # 查询历史数据
    ret, data = quote_ctx.get_macro_indicator_history(indicator_id=indicator_id, max_count=2)
    if ret == RET_OK:
        print(data)
    else:
        print('error:', data)

quote_ctx.close()
```

* **Output**

```
data_time         release_time   value predict_value  previous_value unit_type
0  2026-05-01  2026-06-11 20:34:01  0.0642           N/A          0.0566   PERCENT
1  2026-04-01  2026-05-13 20:31:01  0.0566           N/A          0.0427   PERCENT
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取FedWatch目标利率概率

`get_fed_watch_target_rate()`

* **介绍**

    获取 CME FedWatch 工具的联邦基金目标利率概率预测数据。返回各次 FOMC 会议对应的目标利率区间及市场隐含概率分布，数据来源于 CME 联邦基金期货定价。

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        meeting_date|str|FOMC 会议日期（"yyyy-MM-dd"）
        target_range|str|目标利率区间，如 "4.25% ~ 4.50%"
        probability|float|市场预期概率(%)，如 92.13 表示 92.13%

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_fed_watch_target_rate()
if ret == RET_OK:
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
meeting_date target_range  probability
0   2026-07-29   3.50-3.75%         62.6
1   2026-07-29   3.75-4.00%         37.4
2   2026-09-16   3.50-3.75%         29.8
3   2026-09-16   3.75-4.00%         50.6
4   2026-09-16   4.00-4.25%         19.6
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取FedWatch点阵图

`get_fed_watch_dot_plot()`

* **介绍**

    获取 CME 利率点阵图数据。返回美联储各 FOMC 委员对未来各年份联邦基金利率预期的投票分布，包含每个利率水平的投票人数、中位数利率以及当前联邦基金利率。

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        year|int|预测年份，如 2025、2026、2027
        rate|float|预期利率(%)，如 4.125 表示 4.125%
        vote_count|int|在该利率水平投票的委员人数
        is_median|bool|是否为该年份的中位数利率
        median_rate|float|该年份中位数利率(%)
        current_rate|float|当前联邦基金利率(%)

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_fed_watch_dot_plot()
if ret == RET_OK:
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
year   rate  vote_count  is_median  median_rate  current_rate
0  2026  3.375           1      False        3.875          3.63
1  2026  3.625           8      False        3.875          3.63
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取盈利超预期排名

`get_earnings_beat_rank(market, beat_type, count=None, term=None, filter_list=None, sort_field=None)`

* **介绍**

    获取盈利超预期排名，返回指定市场中财报实际值超出预期值的股票排行列表，包含超预期比率、财报后首日涨幅、同比增长率等维度数据。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场类型（支持 HK/US/SG/JP）（必填）
    beat_type|[BeatType](./quote-market.md#80)|超预期类型（必填）
    count|int|返回数量 [1, 300]，默认 30
    term|[BeatTerm](./quote-market.md#5314)|财报周期，默认 ALL
    filter_list|list[`EarningsBeatRankFilter`]|筛选条件列表（多条件为 AND 关系）
    sort_field|[EarningsBeatSortField](./quote-market.md#6386)|排序字段（固定降序），默认按市值

* **输入限制**

    - **`filter_list` 筛选条件（`EarningsBeatRankFilter`）：**

      通过 `EarningsBeatRankFilter` 构造筛选条件，仅支持范围筛选：

      | 构造参数 | 说明 |
      |----------|------|
      | `indicator_type` | 筛选因子类型（`EarningsBeatIndicatorType`，必填） |
      | `interval_min` | 范围最小值（闭区间） |
      | `interval_max` | 范围最大值（闭区间） |

      不传 `filter_list` 时使用默认筛选：超预期比率 > 0，发布时间为最近 30 天。

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回 (all_count, DataFrame) 元组</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'US.AAPL'`）
        name|str|股票名称
        industry|str|所属行业
        cur_price|float|最新价
        last_close_price|float|昨收价
        change_rate|float|今日涨跌幅（%）
        market_cap|float|市值
        pe_ttm|float|市盈率 TTM
        dividends_ttm|float|股息率 TTM（%）
        released_date|str|财报发布日期（如 `'2024-01-15'`）
        beat_ratio|float|超预期比率（%）
        actual|float|实际值
        estimate|float|预测值
        yoy|float|去年同期
        yoy_growth|float|同比增长率（%）
        earning_day_chg|float|财报后首日涨幅（%）
        term|str|财报周期（如 `'2024/Q1'`）
        detail_post_period|str|发布时段（BEFORE=盘前 / AFTER=盘后 / REGULAR=当天 / INTRADAY_TRADING=盘中）

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_earnings_beat_rank(market=Market.US, beat_type=BeatType.EPS, count=2)
if ret == RET_OK:
    all_count, df = data
    print(f'总数据量: {all_count}')
    print(df)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 1276
  security name industry  cur_price  last_close_price  change_rate    market_cap    pe_ttm  dividends_ttm released_date  beat_ratio  actual  estimate   yoy  yoy_growth  earning_day_chg     term detail_post_period
0  US.NVDA  英伟达      半导体     200.04            208.65       -4.126  4.840968e+12  30.63399          0.019    2026-05-20      37.253  2.3900    1.7413  0.76     214.473           -1.772  2027/Q1              AFTER
1  US.AAPL   苹果   消费电子产品     294.30            297.01       -0.912  4.322489e+12  35.62953          0.353    2026-04-30       3.373  2.0099    1.9444  1.65      21.818            3.239  2026/Q2              AFTER
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取股息排行

`get_dividend_rank(market, rank_type, count=None, filter_list=None, sort_field=None)`

* **介绍**

    获取股息排行，返回指定市场中高股息率或股息持续增长的股票排行列表，包含股息率、派息频率、连续增长年数等维度数据。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场类型（支持 HK/US/MY/SG/JP）（必填）
    rank_type|[DividendRankType](./quote-market.md#933)|排行类型（必填）
    count|int|返回数量 [1, 300]，默认 10
    filter_list|list[`DividendRankFilter`]|筛选条件列表（多条件为 AND 关系，支持范围型和枚举型）
    sort_field|[DividendRankSortField](./quote-market.md#113)|排序字段（固定降序），默认由 rankType 决定

* **输入限制**

    - **`filter_list` 筛选条件（`DividendRankFilter`）：**

      通过 `DividendRankFilter` 构造筛选条件，支持**范围型**和**枚举型**两种筛选：

      | 构造参数 | 说明 |
      |----------|------|
      | `indicator_type` | 筛选因子类型（`DividendRankIndicatorType`，必填） |
      | `value_list` | 枚举值列表（用于枚举型筛选，如派息频率） |
      | `interval_min` | 范围最小值（闭区间，用于范围型筛选） |
      | `interval_max` | 范围最大值（闭区间，用于范围型筛选） |

      > 注意：`value_list` 和 `interval_min/interval_max` 至少提供一种。

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'HK.00005'`）
        name|str|股票名称
        industry|str|所属行业
        cur_price|float|最新价
        change_rate|float|今日涨跌幅（%）
        change_amount|float|今日涨跌额
        market_cap|float|市值
        dividend_yield_ttm|float|股息率 TTM（%）
        avg_dividend_yield_5y|float|5年平均股息率（%）
        distribution_frequency|str|派息频率（ANNUAL/SEMI_ANNUAL/QUARTERLY/MONTHLY），不支持HK市场
        dividend_grow_year|int|股息连续增长年数
        dividends_ttm|float|股息 TTM（金额）
        payout_ratio_lfy|float|股息支付率 LFY（%）
        next_payable_date|str|下次派息日（如 `'2025-09-15'`）

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_dividend_rank(market=Market.HK, rank_type=DividendRankType.HIGH_YIELD, count=2)
if ret == RET_OK:
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
security  name industry  cur_price  change_rate  change_amount    market_cap  dividend_yield_ttm  avg_dividend_yield_5y distribution_frequency  dividend_grow_year  dividends_ttm  payout_ratio_lfy next_payable_date
0  HK.00288  万洲国际     包装食品       8.54       -0.582          -0.05  1.095701e+11              10.655                 10.855            SEMI_ANNUAL                   2          0.910            116.44               N/A
1  HK.01919  中远海控    航运及港口      13.20       -1.123          -0.15  2.021314e+11               8.522                 38.168            SEMI_ANNUAL                   0          1.125             49.67               N/A
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取派息日历

`get_dividend_calendar(market, date, data_from=None, count=None)`

* **介绍**

    获取派息日历，返回指定市场中某一天的派息数据列表，包含除净日、股权登记日、派息日等信息。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场类型（支持 HK/US/MY/SG/JP）（必填）
    date|str|查询日期，格式 `"YYYY-MM-DD"`（必填）
    data_from|int|分页偏移量，默认 0
    count|int|返回数量，默认不限

* **输入限制**

    - **`date`**：仅支持查询单天数据，格式 `"YYYY-MM-DD"`。

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回 (all_count, DataFrame) 元组</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'HK.00005'`）
        name|str|股票名称
        statement|str|方案说明
        record_date|str|股权登记日（`"YYYY-MM-DD"`）
        ex_date|str|除净日（`"YYYY-MM-DD"`）
        dividend_payable_date|str|派息日（`"YYYY-MM-DD"`）

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_dividend_calendar(market=Market.US, date='2026-06-24', count=2)
if ret == RET_OK:
    all_count, df = data
    print(f'总数据量: {all_count}')
    print(df)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 225
  security              name      statement record_date     ex_date dividend_payable_date
0   US.STX              希捷科技    1股派息0.74USD  2026-06-24  2026-06-24            2026-07-07
1   US.VGT  资讯科技ETF-Vanguard  1股派息0.1384USD  2026-06-24  2026-06-24            2026-06-26
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取经济事件日历

`get_economic_calendar(begin_date, end_date=None, market_list=None,
                                       importance=None, count=None, next_page=None)`

* **介绍**

    获取经济事件日历，返回指定日期范围内的经济数据发布事件，包含事件标题、发布时间、国家、重要性星级、前值、预测值和实际公布值。支持按市场和重要性筛选，支持分页查询。

* **参数**

    参数|类型|说明
    :-|:-|:-
    begin_date|str|开始日期，格式 "yyyy-MM-dd"（必填）
    end_date|str|结束日期，格式 "yyyy-MM-dd"；不传则仅查 begin_date 当天
    market_list|list[Market]|市场筛选（多选，支持 HK/US/SH/SG/JP/AU/MY/CA），不传返回所有市场
    importance|[EconomicImportance](./quote-market.md#1622)|事件重要性筛选，默认 ALL（全部）
    count|int|每页数量，默认 50，最大 100
    next_page|str|翻页标记，首次不传，后续传上次返回的 next_page

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        title|str|事件标题（如"非农就业人数"）
        timestamp|float|发布时间戳（秒）
        country|str|国家名称
        star|str|重要性星级（"LOW"/"MEDIUM"/"HIGH"）
        previous|str|前值（未返回时为 "--"）
        consensus|str|预测值（未返回时为 "--"）
        actual|str|实际公布值（未返回时为 "--"）

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data, next_page, has_more = quote_ctx.get_economic_calendar(begin_date='2026-06-23', end_date='2026-06-24', count=2)
if ret == RET_OK:
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
title     timestamp country    star previous consensus actual
0   日本6月综合PMI初值  1.782175e+09      日本  MEDIUM                          
1  日本6月制造业PMI初值  1.782175e+09      日本  MEDIUM
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取盘前榜

`get_us_pre_market_rank(sort_dir=None, count=10, offset=None, filter_list=None)`

* **介绍**

    获取美股盘前榜，返回盘前交易时段涨跌幅排行，包含盘前价格、涨跌幅、成交额、成交量等数据。

* **参数**

    参数|类型|说明
    :-|:-|:-
    sort_dir|[RankSortDir](./quote-market.md#6452)|排序方向，默认降序（领涨）
    count|int|返回数量 [1, 200]，默认 10
    offset|int|起始位置，默认 0
    filter_list|list[`SimpleRankFilter`]|筛选条件列表（多条件为 AND 关系）

* **输入限制**

    - **`filter_list` 筛选条件（`SimpleRankFilter`）：**

      通过 `SimpleRankFilter` 构造筛选条件：

      | 构造参数 | 说明 |
      |----------|------|
      | `indicator_type` | 筛选因子类型（`SimpleRankIndicatorType`，必填） |
      | `interval_min` | 范围最小值（闭区间，MARKET_CAP/PE 使用） |
      | `interval_max` | 范围最大值（闭区间，MARKET_CAP/PE 使用） |
      | `price_filter` | 价格筛选枚举（`PriceFilter`，PRICE 类型必填） |

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回 (all_count, DataFrame) 元组</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'US.AAPL'`）
        name|str|股票名称
        pre_market_price|float|盘前价
        pre_market_change_ratio|float|盘前涨跌幅（%）
        pre_market_change_amount|float|盘前涨跌额
        pre_market_turnover|float|盘前成交额
        pre_market_volume|int|盘前成交量
        close_price|float|收盘价（上一交易日）
        change_ratio|float|盘中涨跌幅（%）
        change_amount|float|盘中涨跌额

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_us_pre_market_rank(count=2)
if ret == RET_OK:
    all_count, df = data
    print(f'总数据量: {all_count}')
    print(df)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 17728
  security                    name  pre_market_price  pre_market_change_ratio  pre_market_change_amount  pre_market_turnover  pre_market_volume  close_price  change_ratio  change_amount
0  US.ATLN  Atlantic International              1.18                  168.303                      0.74         1.219515e+08          136776297         1.33    202.961276          0.891
1  US.BOLD           Boundless Bio              2.40                   71.428                      1.00         6.180064e+07           25082585         2.60     85.714286          1.200
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取盘后榜

`get_us_after_hours_rank(sort_dir=None, count=10, offset=None, filter_list=None)`

* **介绍**

    获取美股盘后榜，返回盘后交易时段涨跌幅排行，包含盘后价格、涨跌幅、成交额、成交量等数据。

* **参数**

    参数|类型|说明
    :-|:-|:-
    sort_dir|[RankSortDir](./quote-market.md#6452)|排序方向，默认降序（领涨）
    count|int|返回数量 [1, 200]，默认 10
    offset|int|起始位置，默认 0
    filter_list|list[`SimpleRankFilter`]|筛选条件列表（多条件为 AND 关系）

* **输入限制**

    - **`filter_list` 筛选条件（`SimpleRankFilter`）：**

      通过 `SimpleRankFilter` 构造筛选条件：

      | 构造参数 | 说明 |
      |----------|------|
      | `indicator_type` | 筛选因子类型（`SimpleRankIndicatorType`，必填） |
      | `interval_min` | 范围最小值（闭区间，MARKET_CAP/PE 使用） |
      | `interval_max` | 范围最大值（闭区间，MARKET_CAP/PE 使用） |
      | `price_filter` | 价格筛选枚举（`PriceFilter`，PRICE 类型必填） |

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回 (all_count, DataFrame) 元组</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'US.TSLA'`）
        name|str|股票名称
        after_hours_price|float|盘后价
        after_hours_change_ratio|float|盘后涨跌幅（%）
        after_hours_change_amount|float|盘后涨跌额
        after_hours_turnover|float|盘后成交额
        after_hours_volume|int|盘后成交量
        close_price|float|收盘价（上一交易日）
        change_ratio|float|盘中涨跌幅（%）
        change_amount|float|盘中涨跌额

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_us_after_hours_rank(count=2)
if ret == RET_OK:
    all_count, df = data
    print(f'总数据量: {all_count}')
    print(df)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 17728
  security                   name  after_hours_price  after_hours_change_ratio  after_hours_change_amount  after_hours_turnover  after_hours_volume  close_price  change_ratio  change_amount
0   US.MGN                  Megan               0.33                    92.048                      0.158          2.811130e+07            90547558        0.172     30.303030           0.04
1  US.QNRX  Quoin Pharmaceuticals               4.85                    49.230                      1.600          1.498305e+07             3050404        3.250    -26.303855          -1.16
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取夜盘榜

`get_us_overnight_rank(sort_dir=None, count=10, offset=None, filter_list=None)`

* **介绍**

    获取美股夜盘榜，返回夜盘交易时段涨跌幅排行，包含夜盘价格、涨跌幅、成交额、成交量等数据。

* **参数**

    参数|类型|说明
    :-|:-|:-
    sort_dir|[RankSortDir](./quote-market.md#6452)|排序方向，默认降序（领涨）
    count|int|返回数量 [1, 200]，默认 10
    offset|int|起始位置，默认 0
    filter_list|list[`SimpleRankFilter`]|筛选条件列表（多条件为 AND 关系）

* **输入限制**

    - **`filter_list` 筛选条件（`SimpleRankFilter`）：**

      通过 `SimpleRankFilter` 构造筛选条件：

      | 构造参数 | 说明 |
      |----------|------|
      | `indicator_type` | 筛选因子类型（`SimpleRankIndicatorType`，必填） |
      | `interval_min` | 范围最小值（闭区间，MARKET_CAP/PE 使用） |
      | `interval_max` | 范围最大值（闭区间，MARKET_CAP/PE 使用） |
      | `price_filter` | 价格筛选枚举（`PriceFilter`，PRICE 类型必填） |

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回 (all_count, DataFrame) 元组</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'US.NVDA'`）
        name|str|股票名称
        overnight_price|float|夜盘价
        overnight_change_ratio|float|夜盘涨跌幅（%）
        overnight_change_amount|float|夜盘涨跌额
        overnight_turnover|float|夜盘成交额
        overnight_volume|int|夜盘成交量
        close_price|float|收盘价（上一交易日）
        change_ratio|float|盘中涨跌幅（%）
        change_amount|float|盘中涨跌额

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_us_overnight_rank(count=2)
if ret == RET_OK:
    all_count, df = data
    print(f'总数据量: {all_count}')
    print(df)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 17728
  security                   name  overnight_price  overnight_change_ratio  overnight_change_amount  overnight_turnover  overnight_volume  close_price  change_ratio  change_amount
0   US.MGN                  Megan           0.3128                  81.543             1.405000e+08         1681274.123           5102016        0.172     30.303030           0.04
1  US.QNRX  Quoin Pharmaceuticals           5.2900                  62.769             2.040000e+09         1164463.400            223649        3.250    -26.303855          -1.16
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取领涨领跌榜

`get_top_movers_rank(market, sort_dir=None, count=10, offset=None, filter_list=None)`

* **介绍**

    获取领涨/领跌榜（盘中），返回盘中交易时段涨跌幅排行，支持港股和美股，包含最新价、涨跌幅、成交额、换手率、市盈率等数据。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场类型（HK/US）（必填）
    sort_dir|[RankSortDir](./quote-market.md#6452)|排序方向，默认降序（领涨）
    count|int|返回数量 [1, 200]，默认 10
    offset|int|起始位置，默认 0
    filter_list|list[`SimpleRankFilter`]|筛选条件列表（多条件为 AND 关系）

* **输入限制**

    - **`filter_list` 筛选条件（`SimpleRankFilter`）：**

      | 构造参数 | 说明 |
      |----------|------|
      | `indicator_type` | 筛选因子类型（`SimpleRankIndicatorType`，必填） |
      | `interval_min` | 范围最小值（闭区间，MARKET_CAP/PE 使用） |
      | `interval_max` | 范围最大值（闭区间，MARKET_CAP/PE 使用） |
      | `price_filter` | 价格筛选枚举（`PriceFilter`，PRICE 类型必填） |

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回 (all_count, DataFrame) 元组</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'HK.00700'`）
        name|str|股票名称
        cur_price|float|最新价
        change_ratio|float|涨跌幅（%）
        change_amount|float|涨跌额
        turnover|float|成交额
        volume|int|成交量
        turnover_ratio|float|换手率（%）
        pe_ttm|float|市盈率 TTM
        amplitude|float|振幅（%）
        market_cap|float|市值
        volume_ratio|float|量比

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_top_movers_rank(market=Market.US, count=2)
if ret == RET_OK:
    all_count, df = data
    print(f'总数据量: {all_count}')
    print(df)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 1794
   security        name  cur_price  change_ratio  change_amount      turnover   volume  turnover_ratio  pe_ttm  amplitude    market_cap  volume_ratio
0    US.QNT  Quantinuum      77.46     13.461257           9.19  4.257190e+08  5582936          175.45  -8.523     225.28  2.020045e+10         1.540
1  US.NJDCY   日本电产(ADR)       3.90      9.859155           0.35  4.051129e+04     9816            0.00  24.074     225.35  1.788243e+10         0.426
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取热议榜

`get_hot_list(market, sort_field=None, sort_dir=None, count=10, offset=None, filter_list=None)`

* **介绍**

    获取热议榜，返回指定市场中热度排行的股票列表，支持按交易热度、搜索热度、资讯热度、综合热度排序，并可按市值筛选。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场类型（HK/US）（必填）
    sort_field|[HotListSortField](./quote-market.md#5324)|排序字段，默认综合热度
    sort_dir|[RankSortDir](./quote-market.md#6452)|排序方向，默认降序
    count|int|返回数量 [1, 200]，默认 10
    offset|int|起始位置，默认 0
    filter_list|list[`HotListFilter`]|筛选条件列表（市值）

* **输入限制**

    - **`filter_list` 筛选条件（`HotListFilter`）：**

      | 构造参数 | 说明 |
      |----------|------|
      | `indicator_type` | 筛选因子类型（`HotListIndicatorType`，必填） |
      | `interval_min` | 范围最小值（闭区间） |
      | `interval_max` | 范围最大值（闭区间） |

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回 (all_count, DataFrame) 元组</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'US.TSLA'`）
        name|str|股票名称
        trade_heat|float|交易热度
        trade_heat_change|float|交易热度变化
        search_heat|float|搜索热度
        search_heat_change|float|搜索热度变化
        news_heat|float|资讯热度
        news_heat_change|float|资讯热度变化
        average_heat|float|综合热度
        average_heat_change|float|综合热度变化
        news_type|str|新闻类型（"Community"=社区讨论, "News"=资讯）
        news_title|str|新闻/讨论标题
        news_url|str|资讯 URL（news_type="News" 时有效）

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_hot_list(market=Market.US, count=2)
if ret == RET_OK:
    all_count, df = data
    print(f'总数据量: {all_count}')
    print(df)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 6342
  security    name  trade_heat  trade_heat_change  search_heat  search_heat_change  news_heat  news_heat_change  average_heat  average_heat_change news_type                                         news_title                                           news_url
0  US.SPCX  SpaceX   9999995.0                0.0    9999972.0                 0.0  9999998.0               0.0     9999988.0                  0.0      News  SpaceX收涨1%，终结三连跌！首发债券获约3.6...  https://news.futunn.com/post/55589925?lang=...
1    US.MU    美光科技   5578115.0                0.0    7923445.0                 0.0  1835896.0              -2.0     5112485.0                  0.0       N/A                                              N/A                                              N/A
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取卖空异动榜

`get_short_selling_rank(market=None, sort_field=None, sort_dir=None, count=10, offset=None, plate_list=None)`

* **介绍**

    获取卖空异动榜，返回美股/港股卖空数据排行，支持14种排序维度和行业板块筛选，包含卖空数量、比例、空头持仓、回补天数等数据。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场类型（HK/US），默认 US
    sort_field|[ShortSellingSortField](./quote-market.md#6834)|排序字段，默认卖空变化量
    sort_dir|[RankSortDir](./quote-market.md#6452)|排序方向，默认降序
    count|int|返回数量 [1, 35]，默认 10
    offset|int|起始位置，默认 0
    plate_list|list[str]|行业板块代码列表（如 `['US.BK2024']`），空=全部

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回 (all_count, DataFrame) 元组</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'US.GME'`）
        name|str|股票名称
        close_price|float|收盘价
        change_ratio|float|涨跌幅（%）
        change_ratio_5d|float|5日涨跌幅（%）
        change_ratio_10d|float|10日涨跌幅（%）
        volume|int|成交量
        short_number|int|卖空数量
        short_number_change|int|卖空变化量
        short_ratio|float|卖空比例（%）
        short_ratio_change|float|卖空变化比例（%）
        short_position_volume|int|空头持仓数量
        short_position_ratio|float|空头持仓比例（%）
        days_to_cover|float|回补天数
        week_avg_short_number|int|近一周日均卖空
        week_avg_short_ratio|float|近一周日均卖空比例（%）
        month_avg_short_number|int|近一月日均卖空
        month_avg_short_ratio|float|近一月日均卖空比例（%）

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_short_selling_rank(count=2)
if ret == RET_OK:
    all_count, df = data
    print(f'总数据量: {all_count}')
    print(df)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 0
  security           name  close_price  change_ratio  change_ratio_5d  change_ratio_10d     volume  short_number  short_number_change  short_ratio  short_ratio_change  short_position_volume  short_position_ratio  days_to_cover  week_avg_short_number  week_avg_short_ratio  month_avg_short_number  month_avg_short_ratio
0  US.SKYQ     Sky Quarry       1.9000         62.39            45.03              4.39  221413731      20302431             20226903         9.16            26780.66                 327119                  6.82            1.0                4111613                  9.19                 1136188                   8.26
1  US.TNON  Tenon Medical       0.6215         77.57             0.72              2.89  271138156      15289764             15273389         5.63            93272.60                 149174                  1.28            2.9                3063337                  5.01                  772705                   5.04
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取区间涨跌幅

`get_period_change_rank(market, period_type=None, sort_dir=None, count=10, offset=None, filter_list=None)`

* **介绍**

    获取区间涨跌幅排行，返回指定市场中按不同时间周期（5分钟至250日/年初至今）的涨跌幅排行，支持丰富的筛选条件（市值、价格、PE、PB、换手率、量比、振幅等）。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场类型（HK/US）（必填）
    period_type|[RankPeriodType](./quote-market.md#5709)|排序周期，默认 5 分钟
    sort_dir|[RankSortDir](./quote-market.md#6452)|排序方向，默认降序
    count|int|返回数量 [1, 200]，默认 10
    offset|int|起始位置，默认 0
    filter_list|list[`PeriodChangeRankFilter`]|筛选条件列表（多条件为 AND 关系）

* **输入限制**

    - **`filter_list` 筛选条件（`PeriodChangeRankFilter`）：**

      | 构造参数 | 说明 |
      |----------|------|
      | `indicator_type` | 筛选因子类型（`PeriodChangeIndicatorType`，必填） |
      | `interval_min` | 范围最小值（闭区间） |
      | `interval_max` | 范围最大值（闭区间） |

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回 (all_count, DataFrame) 元组</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'US.AAPL'`）
        name|str|股票名称
        cur_price|float|最新价
        change_ratio|float|今日涨跌幅（%）
        turnover|float|成交额
        volume|int|成交量
        market_cap|float|市值
        change_rate_5min|float|5分钟涨跌幅（%）
        change_rate_5d|float|5日涨跌幅（%）
        change_rate_10d|float|10日涨跌幅（%）
        change_rate_20d|float|20日涨跌幅（%）
        change_rate_60d|float|60日涨跌幅（%）
        change_rate_120d|float|120日涨跌幅（%）
        change_rate_250d|float|250日涨跌幅（%）
        change_rate_ytd|float|年初至今涨跌幅（%）
        pe_ttm|float|市盈率 TTM
        pb|float|市净率
        turnover_ratio|float|换手率（%）
        volume_ratio|float|量比
        amplitude|float|振幅（%）

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_period_change_rank(market=Market.US, count=2)
if ret == RET_OK:
    all_count, df = data
    print(f'总数据量: {all_count}')
    print(df)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 6429
  security                           name  cur_price  change_ratio  turnover  volume   market_cap  change_rate_5min  change_rate_5d  change_rate_10d  change_rate_20d  change_rate_60d  change_rate_120d  change_rate_250d  change_rate_ytd   pe_ttm       pb  turnover_ratio  volume_ratio  amplitude
0   US.JYD                         佳裕达物流       0.93        11.537  271197.0  311313   7717977.00             9.540           32.80           30.875           20.779          -68.150           -80.128           -90.610          -81.374 -0.40558  0.49892           5.220         0.732      20.94
1  US.RAIN  Rain Enhancement Technologies       2.23        19.892  112286.0   56451  18261097.59             9.313           -2.62            1.826           -6.302          -21.754           -71.914           -22.299          -61.815 -1.79838 -1.27283           2.812         0.816      27.15
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取破净高股息国央企

`get_high_dividend_soe_rank(sort_field=None, sort_dir=None, count=10, offset=None, filter_list=None)`

* **介绍**

    获取破净高股息国央企排行（港股），返回满足特估国企概念板块、PB<=1、股息率TTM>=5%、PE>=0 默认条件的港股排行数据。用户可通过筛选条件覆盖默认阈值。

* **参数**

    参数|类型|说明
    :-|:-|:-
    sort_field|[HighDividendSOESortField](./quote-market.md#8458)|排序字段，默认市值
    sort_dir|[RankSortDir](./quote-market.md#6452)|排序方向，默认降序
    count|int|返回数量 [1, 200]，默认 10
    offset|int|起始位置，默认 0
    filter_list|list[`HighDividendSOERankFilter`]|筛选条件列表（可覆盖默认条件）

* **输入限制**

    - **`filter_list` 筛选条件（`HighDividendSOERankFilter`）：**

      | 构造参数 | 说明 |
      |----------|------|
      | `indicator_type` | 筛选因子类型（`HighDividendSOEIndicatorType`，必填） |
      | `interval_min` | 范围最小值（闭区间） |
      | `interval_max` | 范围最大值（闭区间） |

    - **服务端默认固定条件：**
      - 概念板块 = 特估国企
      - 市净率 PB <= 1
      - 股息率 TTM >= 5%
      - 市盈率 PE >= 0

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回 (all_count, DataFrame) 元组</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'HK.00857'`）
        name|str|股票名称
        industry|str|所属行业
        cur_price|float|最新价
        change_ratio|float|涨跌幅（%）
        turnover|float|成交额
        volume|int|成交量
        market_cap|float|市值
        pe_ttm|float|市盈率 TTM
        pb|float|市净率
        dividend_yield_ttm|float|股息率 TTM（%）
        turnover_ratio|float|换手率（%）
        change_rate_5d|float|5日涨幅（%）
        change_rate_10d|float|10日涨幅（%）
        change_rate_20d|float|20日涨幅（%）
        change_rate_60d|float|60日涨幅（%）
        change_rate_120d|float|120日涨幅（%）
        change_rate_250d|float|250日涨幅（%）

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_high_dividend_soe_rank(count=2)
if ret == RET_OK:
    all_count, df = data
    print(f'总数据量: {all_count}')
    print(df)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 98
   security    name industry  cur_price  change_ratio     turnover    volume    market_cap   pe_ttm       pb  dividend_yield_ttm  turnover_ratio  change_rate_5d  change_rate_10d  change_rate_20d  change_rate_60d  change_rate_120d  change_rate_250d
0  HK.01398    工商银行       银行        6.9        -0.862  325569646.0  46871758  2.459203e+12  5.84745  0.55072               5.072           0.054          -3.894           -0.288            1.917            9.411            16.416            24.292
1  HK.00857  中国石油股份    油气生产商        8.9        -0.447  154397506.0  17228406  1.628887e+12  9.09090  0.88539               5.932           0.081          -6.342          -10.216          -16.217          -14.691            14.209            36.468
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取机构列表

`get_institution_list(market, sort_field=None, sort_dir=None, count=None, page=None, name_part=None)`

* **介绍**

    获取机构列表，返回指定市场中按持仓市值/增减仓/持仓股数等维度排行的机构列表，支持模糊搜索和游标翻页。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场类型（HK/US）（必填）
    sort_field|[InstitutionListSortField](./quote-market.md#534)|排序字段，默认持仓市值
    sort_dir|[RankSortDir](./quote-market.md#6452)|排序方向，默认降序
    count|int|返回数量 [1, 200]，默认 20
    page|str|翻页游标，首次不传，续页传上次返回的 next_page
    name_part|str|机构名模糊搜索

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        institution_id|int|机构 ID
        institution_name|str|机构名称
        position_value|float|持仓市值
        position_value_change|float|持仓市值变化
        position_count|int|持仓股票数
        position_count_change|int|持仓股票数变化
        disclosure_date|str|披露日期（yyyy-MM-dd）
        currency|str|币种

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data, next_page, all_count = quote_ctx.get_institution_list(market=Market.US, count=2)
if ret == RET_OK:
    print(f'总数据量: {all_count}')
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 17030
   institution_id                  institution_name  position_value  position_value_change  position_count  position_count_change disclosure_date currency
0          403413                               贝莱德    6.959193e+12           3.432083e+10            4443                     56      2026-06-19      USD
1      1951572549  Vanguard Capital Management, LLC    4.881261e+12           4.492246e+12            4289                   3859      2026-06-10      USD
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取机构概况

`get_institution_profile(market, institution_id)`

* **介绍**

    获取机构概况，返回指定机构的持仓市值、持仓变动统计、Top10 持股占比等画像数据。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场类型（HK/US）（必填）
    institution_id|int|机构 ID（从 get_institution_list 获取）（必填）

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回字典数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        institution_name|str|机构名称
        description|str|机构简介
        position_value|float|持仓市值
        last_position_value|float|上期持仓市值
        position_value_change_pct|float|市值变化比例（%）
        total_holding_count|int|总持仓数
        holding_change_count|int|持仓变动数
        new_count|int|建仓标的数
        sold_out_count|int|清仓标的数
        increase_count|int|增持标的数
        decrease_count|int|减持标的数
        top10_pct|float|Top10 持股占比（%）
        top10_pct_change|float|Top10 占比变动（%）
        disclosure_date|str|披露日期（yyyy-MM-dd）
        currency|str|币种

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 先获取机构ID
ret, data, _, _ = quote_ctx.get_institution_list(market=Market.US, count=1)
if ret == RET_OK and len(data) > 0:
    inst_id = data.iloc[0]['institution_id']

    # 查询机构概况
    ret, profile = quote_ctx.get_institution_profile(market=Market.US, institution_id=inst_id)
    if ret == RET_OK:
        for k, v in profile.items():
            print(f"{k}: {v}")
    else:
        print('error:', profile)

quote_ctx.close()
```

* **Output**

```
institution_name: 贝莱德
description: 贝莱德集团是美国规模最大的资产管理集团之一，提供种类繁多的证券、固定收益、现金管理等投资产品。
position_value: 6959192681765.731
last_position_value: 6093992885377.756
position_value_change_pct: 14.1975
total_holding_count: 4443
holding_change_count: 12
new_count: 87
sold_out_count: 31
increase_count: 2364
decrease_count: 1682
top10_pct: 24.3287
top10_pct_change: 0.4142
disclosure_date: 2026-06-19
currency: USD
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取机构持仓行业分布

`get_institution_distribution(market, institution_id)`

* **介绍**

    获取机构持仓行业分布，返回指定机构的持仓按行业分类的市值和占比数据。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场类型（HK/US）（必填）
    institution_id|int|机构 ID（从 get_institution_list 获取）（必填）

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        industry_id|int|行业 ID
        industry_name|str|行业名称
        position_value|float|持仓市值
        portfolio_pct|float|行业占比（%）

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 先获取机构ID
ret, data, _, _ = quote_ctx.get_institution_list(market=Market.US, count=1)
if ret == RET_OK and len(data) > 0:
    inst_id = data.iloc[0]['institution_id']

    # 查询行业分布
    ret, data = quote_ctx.get_institution_distribution(market=Market.US, institution_id=inst_id)
    if ret == RET_OK:
        print(data)
    else:
        print('error:', data)

quote_ctx.close()
```

* **Output**

```
industry_id industry_name        position_value  portfolio_pct
0           6            电子  1319006433351.533936        19.8494
1          26           计算机   992844462205.649048        14.9411
2          12          医药生物   633746255374.343994         9.5371
3          27        互联网与传媒   484195469416.382996         7.2865
4          19          非银金融   481223610387.026001         7.2418
5         N/A            其他                   N/A        41.1441
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取机构持仓变动

`get_institution_holding_change(market, institution_id, change_type=None, sort_field=None, sort_dir=None, count=None, page=None)`

* **介绍**

    获取机构持仓变动，返回指定机构按变动类型（建仓/清仓/增仓/减仓）筛选的持仓变动记录，支持排序和游标翻页。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场类型（HK/US）（必填）
    institution_id|int|机构 ID（必填）
    change_type|[InstitutionHoldingChangeType](./quote-market.md#9203)|变动类型，默认建仓
    sort_field|[InstitutionHoldingChangeSortField](./quote-market.md#5831)|排序字段，默认变动比例
    sort_dir|[RankSortDir](./quote-market.md#6452)|排序方向，默认降序
    count|int|返回数量 [1, 200]，默认 20
    page|str|翻页游标

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'US.AAPL'`）
        name|str|股票名称
        portfolio_pct|float|持股比例（%）
        change_shares|int|变动股数
        change_pct|float|变动比例（%）
        holding_date|int|持仓时间（时间戳）
        source|str|披露来源

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 先获取机构ID
ret, data, _, _ = quote_ctx.get_institution_list(market=Market.US, count=1)
if ret == RET_OK and len(data) > 0:
    inst_id = data.iloc[0]['institution_id']

    # 查询持仓变动
    ret, data, next_page, all_count = quote_ctx.get_institution_holding_change(
        market=Market.US, institution_id=inst_id, count=2)
    if ret == RET_OK:
        print(f'总数据量: {all_count}')
        print(data)
    else:
        print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 87
  security                name  portfolio_pct  change_shares  change_pct holding_date source
0   US.YSS  York Space Systems        14.6594       19012439     14.6594   2026-03-30    13F
1  US.VSNT       Versant Media        12.2661       17356403     12.2661   2026-03-30    13F
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取机构持股列表

`get_institution_holding_list(market, institution_id, change_type=None, sort_field=None, sort_dir=None, count=None, page=None, keyword=None)`

* **介绍**

    获取机构持股列表，返回指定机构的全部持股明细（包含市值、持股比例、变动等），支持按变动类型筛选、多维度排序和关键词搜索。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场类型（HK/US）（必填）
    institution_id|int|机构 ID（必填）
    change_type|[InstitutionHoldingChangeType](./quote-market.md#9203)|按变动类型筛选（不传=全部）
    sort_field|[InstitutionHoldingListSortField](./quote-market.md#684)|排序字段，默认持仓市值
    sort_dir|[RankSortDir](./quote-market.md#6452)|排序方向，默认降序
    count|int|返回数量 [1, 200]，默认 20
    page|str|翻页游标
    keyword|str|搜索关键词（股票名/代码）

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'US.AAPL'`）
        name|str|股票名称
        industry_name|str|所属行业
        holding_value|float|持股市值
        holding_pct|float|持股比例—占股票总市值（%）
        last_holding_pct|float|上期持股比例（%）
        change_shares|int|变动股数
        portfolio_pct|float|占机构总仓位比例（%）
        change_pct|float|变动比例（%）
        holding_date|int|持仓时间（时间戳）
        source|str|披露来源
        currency|str|币种

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 先获取机构ID
ret, data, _, _ = quote_ctx.get_institution_list(market=Market.US, count=1)
if ret == RET_OK and len(data) > 0:
    inst_id = data.iloc[0]['institution_id']

    # 查询持股列表
    ret, data, next_page, all_count = quote_ctx.get_institution_holding_list(
        market=Market.US, institution_id=inst_id, count=2)
    if ret == RET_OK:
        print(f'总数据量: {all_count}')
        print(data)
    else:
        print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 4430
  security name industry_name  holding_value  holding_pct  last_holding_pct  change_shares  portfolio_pct  change_pct holding_date source currency
0  US.NVDA  英伟达            电子   3.887350e+11       7.9295            7.8996      -19284971         4.9289     -0.0796   2026-03-30    13F      USD
1  US.AAPL   苹果           计算机   3.398298e+11       7.7520            7.7624      -10565359         4.3088     -0.0719   2026-03-30    13F      USD
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取ARK基金持仓

`get_ark_fund_holding(holding_type=None, cycle_type=None, sort_field=None, sort_dir=None, count=None, page=None)`

* **介绍**

    获取 ARK 基金持仓，返回 ARK 旗下 ETF 的持仓数据，支持按持仓/增持/减持/建仓/清仓类型查看，支持不同时间周期和多维度排序。

* **参数**

    参数|类型|说明
    :-|:-|:-
    holding_type|[ArkHoldingType](./quote-market.md#7626)|持仓类型，默认持仓
    cycle_type|[ArkCycleType](./quote-market.md#7532)|周期类型，默认近 1 天（holdingType=持仓时忽略）
    sort_field|[ArkFundHoldingSortField](./quote-market.md#5135)|排序字段，默认持仓数量
    sort_dir|[RankSortDir](./quote-market.md#6452)|排序方向，默认降序
    count|int|返回数量 [1, 200]，默认 20
    page|str|翻页游标

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'US.TSLA'`，部分标的可能为 N/A）
        name|str|名称
        shares|int|持仓数量
        shares_change|int|持仓数量变动
        market_value|float|持仓市值（美元）
        weight|float|持仓占比（%）
        weight_change|float|持仓占比变动（%）

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data, next_page, all_count = quote_ctx.get_ark_fund_holding(count=2)
if ret == RET_OK:
    print(f'总数据量: {all_count}')
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 2
  security                       name    shares  shares_change  market_value  weight  weight_change
0      N/A                        N/A  62494591       15631862  6.249459e+07    0.45           0.12
1  US.RXRX  Recursion Pharmaceuticals  31671298         -71280  1.007147e+08    0.73           0.01
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取ARK个股交易动态

`get_ark_stock_dynamic(security)`

* **介绍**

    获取 ARK 个股交易动态，返回指定股票在 ARK 基金中的最新交易动态信息（连续同向交易、近期交易、最近一笔等）。

* **参数**

    参数|类型|说明
    :-|:-|:-
    security|str|股票代码（如 `'US.TSLA'`）（必填）

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回字典数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        dynamic_type|str|动态类型（见下方枚举）
        transaction_count|int|交易次数
        net_shares|int|净交易股数
        last_transaction_time|str|最近交易时间（yyyy-MM-dd）
        "CONSECUTIVE_SAME_DIRECTION"|连续同向交易|
        "RECENT_TRANSACTION"|近期交易|
        "LAST_TRANSACTION"|最近一笔|
        "NO_DYNAMIC"|无动态|

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_ark_stock_dynamic(security='US.TSLA')
if ret == RET_OK:
    for k, v in data.items():
        print(f"{k}: {v}")
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
dynamic_type: CONSECUTIVE_SAME_DIRECTION
transaction_count: 2
net_shares: 76041
last_transaction_time: 2026-06-22
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取ARK主动交易聚合

`get_ark_active_transaction(holding_type=None, cycle_type=None, sort_field=None, sort_dir=None, count=None, page=None)`

* **介绍**

    获取 ARK 主动交易聚合，返回 ARK 基金的主动交易记录（含变动金额、变动股数），支持按持仓变动类型、周期选择和排序。

* **参数**

    参数|类型|说明
    :-|:-|:-
    holding_type|[ArkActiveTransactionHoldingType](./quote-market.md#1569)|持仓变动类型，默认增持
    cycle_type|[ArkCycleType](./quote-market.md#7532)|周期类型，默认近 1 天
    sort_field|[ArkActiveTransactionSortField](./quote-market.md#4910)|排序字段，默认变动金额
    sort_dir|[RankSortDir](./quote-market.md#6452)|排序方向，默认降序
    count|int|返回数量 [1, 200]，默认 50
    page|str|翻页游标

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'US.TSLA'`，部分标的可能为 N/A）
        name|str|名称
        change_amount|float|变动金额（美元）
        change_shares|int|变动数量（股）

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data, next_page, all_count = quote_ctx.get_ark_active_transaction(count=2)
if ret == RET_OK:
    print(f'总数据量: {all_count}')
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 2
  security      name  change_amount  change_shares
0  US.AMZN       亚马逊      9631518.0          41141
1  US.PLTR  Palantir      9482340.0          81254
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取评级变动

`get_rating_change(market, change_type=None, count=None, page=None)`

* **介绍**

    获取评级变动，返回美股的股票评级变动记录（上调/下调/首次评级），包含机构名称、目标价变动等信息，支持翻页。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场类型（仅 US）（必填）
    change_type|[RatingChangeType](./quote-market.md#863)|评级变动类型，默认上调
    count|int|返回数量 [1, 20]，默认 10
    page|str|翻页游标

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'US.TSLA'`）
        name|str|股票名称
        rating|str|当前评级（"BUY"/"HOLD"/"SELL"）
        last_rating|str|上次评级（"BUY"/"HOLD"/"SELL"）
        target_price|float|当前目标价
        last_target_price|float|上次目标价
        change_type|str|评级变动类型（"UPGRADE"/"DOWNGRADE"/"NEW_RATING"）
        institution_name|str|机构名称
        recommendation_date|str|推荐日期（yyyy-MM-dd）
        last_recommendation_date|str|上次推荐日期（yyyy-MM-dd）
        "SELL"|卖出|
        "HOLD"|持有|
        "BUY"|买入|

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data, next_page, all_count = quote_ctx.get_rating_change(market=Market.US, count=2)
if ret == RET_OK:
    print(f'总数据量: {all_count}')
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 5904
  security  name rating last_rating  target_price  last_target_price change_type institution_name recommendation_date last_recommendation_date
0    US.MU  美光科技    BUY         BUY        1500.0              950.0     UPGRADE             美银证券          2026-06-23               2026-05-13
1  US.INTC   英特尔    BUY         BUY         160.0              135.0     UPGRADE             美银证券          2026-06-23               2026-06-11
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取产业链列表

`get_industrial_chain_list(market, keyword=None, count=None, page=None)`

* **介绍**

    获取产业链列表，返回指定市场的产业链信息（含产业链类型、市值、成分股数量等），支持关键字搜索和游标翻页。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场类型（必填）
    keyword|str|搜索关键字
    count|int|返回数量 [1, 50]，默认 20
    page|str|翻页游标

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        chain_id|int|产业链 ID
        chain_type|str|产业链类型（"CHAIN"/"PARALLEL"/"UP_MID_DOWN"）
        name|str|产业链名称
        detail|str|详情描述
        market_cap|float|市值
        stocks_num|int|成分股数量
        relation_security_list|list|相关股票代码列表
        "CHAIN"|串联型|
        "PARALLEL"|并列型|
        "UP_MID_DOWN"|上中下游型|

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data, next_page, all_count = quote_ctx.get_industrial_chain_list(market=Market.US, count=2)
if ret == RET_OK:
    print(f'总数据量: {all_count}')
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 70
   chain_id   chain_type  name                                             detail    market_cap  stocks_num relation_security_list
0   9610020  UP_MID_DOWN    AI  AIGC（Artificial Intelligence Generated Content...  4.801784e+13         329     [US.NVDA, US.AAPL]
1   9610085  UP_MID_DOWN  商业航天                                                     2.590359e+12         155        [US.GE, US.RTX]
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取产业链详情

`get_industrial_chain_detail(chain_id)`

* **介绍**

    获取产业链详情，返回指定产业链的完整结构信息，包含层级节点列表和相关资讯链接。

* **参数**

    参数|类型|说明
    :-|:-|:-
    chain_id|int|产业链 ID（从 `get_industrial_chain_list` 获取）（必填）

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回字典数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        chain_id|int|产业链 ID
        chain_type|str|产业链类型（"CHAIN"/"PARALLEL"/"UP_MID_DOWN"）
        name|str|产业链名称
        node_list|list[dict]|节点列表（按层级分组）
        information_list|list[dict]|资讯链接列表
        node_id|int|节点 ID
        parent_node_id|int|父节点 ID（根节点为 0）
        layer|int|节点层级（从 1 开始）
        name|str|节点名称
        plate_id|int|关联产业板块 ID（无关联为 N/A）
        title|str|资讯标题
        url|str|资讯链接

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_industrial_chain_detail(chain_id=9610020)
if ret == RET_OK:
    print(f"chain_id: {data['chain_id']}")
    print(f"chain_type: {data['chain_type']}")
    print(f"name: {data['name']}")
    print(f"node_list (前2项):")
    for node in data['node_list'][:2]:
        print(f"  {node}")
    print(f"information_list: {data['information_list']}")
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
chain_id: 9610020
chain_type: UP_MID_DOWN
name: AI
node_list (前2项):
  {'node_id': 1, 'parent_node_id': 'N/A', 'layer': 1, 'name': '基础建设层', 'plate_id': 'N/A'}
  {'node_id': 4, 'parent_node_id': 'N/A', 'layer': 1, 'name': '算法层', 'plate_id': 'N/A'}
information_list: []
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取板块关联产业链

`get_industrial_chain_by_plate(plate_id)`

* **介绍**

    获取板块关联产业链，返回指定产业板块所关联的产业链列表信息（含类型、市值、成分股数量）。

* **参数**

    参数|类型|说明
    :-|:-|:-
    plate_id|int|产业板块 ID（从 `get_industrial_chain_detail` 的 node_list 中获取）（必填）

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>list</td>
            <td>当 ret == RET_OK，返回列表数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        chain_id|int|产业链 ID
        chain_type|str|产业链类型（"CHAIN"/"PARALLEL"/"UP_MID_DOWN"）
        name|str|产业链名称
        market_cap|float|市值
        stocks_num|int|成分股数量
        "CHAIN"|串联型|
        "PARALLEL"|并列型|
        "UP_MID_DOWN"|上中下游型|

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_industrial_chain_by_plate(plate_id=10010508)
if ret == RET_OK:
    for chain in data:
        print(chain)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
{'chain_id': 9610020, 'chain_type': 'UP_MID_DOWN', 'name': 'AI', 'market_cap': 26949823045632.0, 'stocks_num': 329}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取产业板块信息

`get_industrial_plate_info(plate_id)`

* **介绍**

    获取产业板块信息，返回指定产业板块的简介信息。

* **参数**

    参数|类型|说明
    :-|:-|:-
    plate_id|int|产业板块 ID（从 `get_industrial_chain_detail` 的 node_list 中获取）（必填）

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回字典数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        plate_id|int|产业板块 ID
        summary|str|板块简介

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_industrial_plate_info(plate_id=10010508)
if ret == RET_OK:
    for k, v in data.items():
        print(f"{k}: {v}")
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
plate_id: 10010508
summary: N/A
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取产业板块成分股

`get_industrial_plate_stock(chain_id=None, plate_id=None, market_list=None,
                                            sort_field=None, ascend=None, count=None, page=None)`

* **介绍**

    获取产业板块成分股，返回指定产业板块包含的股票列表，支持市场筛选、排序和分页。

* **参数**

    参数|类型|说明
    :-|:-|:-
    chain_id|int|产业链 ID（与 plate_id 二选一，plate_id 优先）
    plate_id|int|产业板块 ID（优先使用）
    market_list|list[`Market`]|市场筛选（支持 HK/US/CN/JP/SG/MY），不传默认全部
    sort_field|[PlateStockSortField](./quote-market.md#1698)|排序字段，默认市值
    ascend|bool|升序 True / 降序 False，默认 False（降序）
    count|int|每页数量 [1, 200]，默认 50
    page|str|翻页游标

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        security|str|股票代码（如 `'US.AAPL'`）
        name|str|股票名称

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data, next_page, all_count = quote_ctx.get_industrial_plate_stock(plate_id=10010508, count=2)
if ret == RET_OK:
    print(f'总数据量: {all_count}')
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
总数据量: 111
  security name
0  US.NVDA  英伟达
1  US.AAPL   苹果
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取热力图数据

`get_heat_map_data(market, sort_field=None, ascend=None, count=None, page=None, plate_type=None)`

* **介绍**

    获取热力图数据，返回指定市场的板块热力图信息（含涨跌幅、市值、成交额、涨跌家数、领涨股等），支持多维度排序和游标翻页。

* **参数**

    参数|类型|说明
    :-|:-|:-
    market|[Market](./quote.md#427)|市场类型（必填）
    sort_field|[HeatMapSortField](./quote-market.md#6872)|排序字段，默认涨跌幅
    ascend|bool|True=升序，False=降序，默认降序
    count|int|返回数量 [1, 200]，默认 30
    page|str|翻页游标
    plate_type|[HeatMapPlateType](./quote-market.md#3872)|板块类型，默认行业板块

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        plate|str|板块代码（如 `'HK.BK1001'`）
        plate_name|str|板块名称
        cur_price|float|最新价
        change_rate|float|涨跌幅（%）
        turnover|float|成交额
        volume|int|成交量
        market_val|float|市值
        pe_avg|float|平均市盈率
        rise_count|int|涨家数
        fall_count|int|跌家数
        equal_count|int|持平数
        leader_stock|str|领涨股代码
        description|str|板块描述

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data, next_page, all_count = quote_ctx.get_heat_map_data(market=Market.US, count=2)
if ret == RET_OK:
    print(f'板块总数: {all_count}')
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
板块总数: 145
         plate plate_name    cur_price  change_rate      turnover     volume    market_val  pe_avg  rise_count  fall_count  equal_count leader_stock description
0  US.LIST2496  人力资源与就业服务  1229.174414     4.717340  7.345543e+08  437599614  1.502404e+10  -6.112          15           3            2      US.ATLN         N/A
1  US.LIST2473         糖果  1696.630748     3.295289  1.178965e+09   14299774  1.176028e+11  49.691           4           1            0      US.RMCF         N/A
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取涨跌分布

`get_rise_fall_distribution(security=None, market=None)`

* **介绍**

    获取涨跌分布，返回指定板块或市场的涨跌家数分布区间，可用于了解市场整体涨跌格局。

* **参数**

    参数|类型|说明
    :-|:-|:-
    security|str|板块代码（优先使用，如 `'HK.BK1001'`）
    market|[Market](./quote.md#427)|市场类型（`security` 未传时使用）

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回字典数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 数据格式如下：
        字段|类型|说明
        :-|:-|:-
        plate|str|板块代码
        range_list|list[dict]|涨跌分布区间列表
        type|str|分布类型（字符串，见下表）
        left_border|int|左边界值
        right_border|int|右边界值
        stock_count|int|区间股票数
        "RISE_LIMIT"|涨停（A 股）|
        "POSITIVE_INFINITY"|(7%, +∞)|
        "NORMAL_RANGE"|正常区间|
        "NEGATIVE_INFINITY"|(-∞, -7%)|
        "FALL_LIMIT"|跌停（A 股）|

* **Example**

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_rise_fall_distribution(market=Market.US)
if ret == RET_OK:
    print(data)
else:
    print('error:', data)

quote_ctx.close()
```

* **Output**

```
{'plate': 'US.USAALL', 'range_list': [{'type': 'NEGATIVE_INFINITY', 'left_border': 0, 'right_border': -7, 'stock_count': 817}, {'type': 'NORMAL_RANGE', 'left_border': -7, 'right_border': -5, 'stock_count': 581}, {'type': 'NORMAL_RANGE', 'left_border': 0, 'right_border': 3, 'stock_count': 4168}, {'type': 'NORMAL_RANGE', 'left_border': 0, 'right_border': 0, 'stock_count': 4310}, {'type': 'POSITIVE_INFINITY', 'left_border': 7, 'right_border': 0, 'stock_count': 416}]}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 市场定义

## ARK主动交易持仓变动类型

> **ArkActiveTransactionHoldingType**

* `INCREASE`

  增持（默认）

* `DECREASE`

  减持

* `NEW`

  建仓

* `SOLD_OUT`

  清仓

## ARK主动交易排序字段

> **ArkActiveTransactionSortField**

* `CHANGE_AMOUNT`

  变动金额（默认）

* `CHANGE_SHARES`

  变动股数

## ARK周期类型

> **ArkCycleType**

* `ONE_DAY`

  近 1 天（默认）

* `FIVE_DAY`

  近 5 天

* `TEN_DAY`

  近 10 天

* `THIRTY_DAY`

  近 30 天

* `SIXTY_DAY`

  近 60 天

## ARK基金持仓排序字段

> **ArkFundHoldingSortField**

* `SHARES`

  持仓数量（默认）

* `WEIGHT_CHANGE`

  占比变动

* `SHARES_CHANGE`

  持仓变动

* `MARKET_VALUE`

  市值

* `WEIGHT`

  ETF 占比

## ARK持仓类型

> **ArkHoldingType**

* `POSITION`

  持仓（默认）

* `INCREASE`

  增持

* `DECREASE`

  减持

* `NEW`

  建仓

* `SOLD_OUT`

  清仓

## 财报超预期时间范围

> **BeatTerm**

* `LATEST`

  最近一期（默认）

* `LATEST_QUARTER`

  最近一期季报

* `LATEST_HALF`

  最近一期半年报

* `LATEST_ANNUAL`

  最近一期年报

* `ALL`

  全部（时间一样季报优先，时间不同最近一期）

## 财报超预期类型

> **BeatType**

* `EPS`

  每股收益

* `REVENUE`

  营收

* `EBIT`

  息税前利润

## 派息频率类型

> **DistributionFrequency**

* `ANNUAL`

  年派

* `SEMI_ANNUAL`

  半年派

* `QUARTERLY`

  季派

* `MONTHLY`

  月派

## 股息排行排序字段

> **DividendRankSortField**

* `DIVIDEND_YIELD_TTM`

  股息率 TTM

* `AVG_DIVIDEND_YIELD_5Y`

  5年平均股息率

* `DISTRIBUTION_FREQUENCY`

  派息频率

* `DIVIDEND_GROW_YEAR`

  股息连续增长年数

* `DIVIDENDS_TTM`

  股息 TTM

* `PAYOUT_RATIO_LFY`

  股息支付率 LFY

* `PRICE`

  价格

* `MARKET_CAP`

  市值

* `CHANGE_RATE`

  今日涨跌幅

* `CHANGE_AMOUNT`

  今日涨跌额

## 股息排行类型

> **DividendRankType**

* `HIGH_YIELD`

  高股息率

* `DIVIDEND_GROWTH`

  股息保持增长

## 财报超预期排序字段

> **EarningsBeatSortField**

* `BEAT_RATIO`

  超预期比率

* `EARNING_DAY_CHG`

  财报后首日涨幅

* `RELEASED_DATE`

  发布时间

* `ACTUAL`

  实际值

* `ESTIMATE`

  预测值

* `YOY`

  去年同期

* `YOY_GROWTH`

  同比增长率

* `PE_TTM`

  市盈率 TTM

* `DIVIDENDS_TTM`

  股息率 TTM

* `PRICE`

  价格

* `CHANGE_RATE`

  今日涨跌幅

## 财报指标类型

> **EarningsCalendarEstimateType**

* `EPS`

  每股收益（EPS GAAP）

* `REVENUE`

  总收入

* `EBIT`

  息税前利润

## 财报发布时段类型

> **EarningsCalendarPubType**

* `REGULAR`

  盘中（未识别出时段）

* `BEFORE`

  盘前

* `AFTER`

  盘后

## 财报日历排序类型

> **EarningsCalendarSortType**

* `HOT`

  热门（默认）

* `MARKET_CAP`

  历史市值

* `OPTION_VOLUME`

  期权成交量（仅港美股）

* `IV`

  隐含波动率（仅港美股）

* `IV_RANK`

  IV 等级（仅港美股）

* `IV_PERCENTILE`

  IV 百分位数（仅港美股）

* `RT_MARKET_CAP`

  实时市值

## 财报日历股票列表类型

> **EarningsCalendarStockListType**

* `WATCHLIST`

  自选股

* `POSITION`

  持仓

* `SPECIAL`

  特别关注

## 经济数据重要性

> **EconomicImportance**

* `ALL`

  全部（默认）

* `LOW`

  一星（低）

* `MEDIUM`

  二星（中）

* `HIGH`

  三星（高）

## 热力图板块类型

> **HeatMapPlateType**

* `INDUSTRY`

  行业板块（默认）

* `CONCEPT`

  概念板块

* `THEME`

  主题板块

## 热力图排序字段

> **HeatMapSortField**

* `CHANGE_RATE`

  涨跌幅（默认）

* `MARKET_VAL`

  市值

* `TURNOVER`

  成交额

* `HOT`

  热度

## 高息国企排序字段

> **HighDividendSOESortField**

* `MARKET_CAP`

  市值（默认）

* `DIVIDEND_YIELD_TTM`

  股息率 TTM

* `PB`

  市净率

* `PE_TTM`

  市盈率 TTM

* `PRICE`

  最新价

* `CHANGE_RATIO`

  今日涨跌幅

## 热门排行排序字段

> **HotListSortField**

* `TRADE_HEAT`

  交易热度

* `SEARCH_HEAT`

  搜索热度

* `NEWS_HEAT`

  资讯热度

* `AVERAGE_HEAT`

  综合热度（默认）

## 机构持仓变动排序字段

> **InstitutionHoldingChangeSortField**

* `CHANGE_PCT`

  变动比例（默认）

* `CHANGE_SHARES`

  变动股数

* `HOLDING_DATE`

  持仓时间

## 机构持仓变动类型

> **InstitutionHoldingChangeType**

* `NEW`

  建仓（默认）

* `SOLD_OUT`

  清仓

* `INCREASE`

  增仓

* `DECREASE`

  减仓

## 机构持仓列表排序字段

> **InstitutionHoldingListSortField**

* `HOLDING_VALUE`

  持仓市值（默认）

* `HOLDING_PCT`

  持股比例（占股票总市值）

* `LAST_HOLDING_PCT`

  上期持股比例

* `CHANGE_SHARES`

  变动股数

* `CHANGE_PCT`

  变动比例

* `PORTFOLIO_PCT`

  占机构总仓位比例

* `INDUSTRY`

  行业

* `HOLDING_DATE`

  持仓时间

## 机构列表排序字段

> **InstitutionListSortField**

* `POSITION_VALUE`

  持仓市值（默认）

* `POSITION_VALUE_CHANGE`

  增减仓

* `POSITION_COUNT`

  持仓股数

* `POSITION_COUNT_CHANGE`

  持仓股数变化

## 宏观数据单位类型

> **MacroDataUnitType**

* `PERCENT`

  百分比(%)

* `VALUE`

  数值

* `INDEX`

  指数

## 宏观经济地区

> **MacroRegion**

* `HK`

  香港

* `US`

  美国

* `JP`

  日本

* `SG`

  新加坡

* `AU`

  澳大利亚

* `CA`

  加拿大

* `MY`

  马来西亚

* `CN`

  中国(沪深)

## 产业链板块股票排序字段

> **PlateStockSortField**

* `CODE`

  代码

* `CHANGE_RATE`

  涨跌幅

* `TURNOVER`

  成交额

* `VOLUME`

  成交量

* `MARKET_VAL`

  市值（默认）

## 价格筛选类型

> **PriceFilter**

* `ALL`

  所有（默认）

* `LESS_THAN_1`

  小于 1

* `BETWEEN_1_AND_10`

  1~10 之间

* `BETWEEN_10_AND_100`

  10~100 之间

* `GREATER_THAN_100`

  大于 100

* `NEAR_52_WEEK_HIGH`

  接近 52 周最高

* `NEAR_52_WEEK_LOW`

  接近 52 周最低

## 排行榜周期类型

> **RankPeriodType**

* `FIVE_MIN`

  5分钟（默认）

* `ONE_DAY`

  1日

* `FIVE_DAY`

  5日

* `TWENTY_DAY`

  20日

* `SIXTY_DAY`

  60日

* `ONE_TWENTY_DAY`

  120日

* `TWO_FIFTY_DAY`

  250日

* `YTD`

  年初至今

## 排行榜排序方向

> **RankSortDir**

* `DESCENDING`

  降序（默认）

* `ASCENDING`

  升序

## 评级变动类型

> **RatingChangeType**

* `UPGRADE`

  评级上调（默认）

* `DOWNGRADE`

  评级下调

* `NEW_RATING`

  首次评级

## 做空排行排序字段

> **ShortSellingSortField**

* `SHORT_NUMBER_CHANGE`

  卖空变化量（默认）

* `SHORT_RATIO_CHANGE`

  卖空变化比例

* `SHORT_NUMBER`

  卖空数量

* `SHORT_RATIO`

  卖空比例

* `VOLUME`

  成交量

* `POSITION_VOLUME`

  空头持仓数量

* `POSITION_RATIO`

  空头持仓比例

* `DAYS_TO_COVER`

  回补天数

* `WEEK_AVG_VOLUME`

  近一周日均成交量

* `WEEK_AVG_SHORT_NUMBER`

  近一周日均卖空数量

* `WEEK_AVG_SHORT_RATIO`

  近一周日均卖空比例

* `MONTH_AVG_VOLUME`

  近一月日均成交量

* `MONTH_AVG_SHORT_NUMBER`

  近一月日均卖空数量

* `MONTH_AVG_SHORT_RATIO`

  近一月日均卖空比例

---

# 获取指标列表

`get_indicator_list(search_key='', lang_type=IndicatorLangType.NONE, search_mode=IndicatorSearchMode.PARTIAL)`

* **介绍**

    获取指标列表（可按关键词、语言类型、匹配方式过滤）。同名指标在 MyLang 和 Python 两种实现均存在时合并为同一条目返回。

* **参数**  

    参数|类型|说明
    :-|:-|:-
    search_key|str|搜索关键词  (留空则返回全部)
    lang_type|[IndicatorLangType](./quote.md#6132)|指标脚本语言类型  (默认不按语言过滤)
    search_mode|[IndicatorSearchMode](./quote.md#3105)|匹配方式  (默认部分匹配)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>list</td>
            <td>当 ret == RET_OK，返回指标条目列表</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 指标条目字段说明：

        字段|类型|说明
        :-|:-|:-
        my_lang|dict|麦语言版本指标信息（若不存在则为 None）
        python|dict|Python 版本指标信息（若不存在则为 None）

    * 单一语言指标信息字段说明：

        字段|类型|说明
        :-|:-|:-
        short_name|str|指标短名，同语言内唯一
        full_name|str|指标全名
        inputs|list|输入参数列表
        outputs|list|输出参数列表
        script|str|仅 search_mode = Exact 且 search_key 非空时返回脚本源码

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret, data = quote_ctx.get_indicator_list(search_key='MA', lang_type=IndicatorLangType.MYLANG, search_mode=IndicatorSearchMode.PARTIAL)
if ret == RET_OK:
    print(data)
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取指标列表接口。
:::
</content>
</invoke>

---

# 异步发起指标计算

`request_indicator_calc_async(short_name, lang_type, code, kl_type, klines, num=None, input_params=None)`

* **介绍**

    异步发起指标计算。接口先返回 `calc_id`，实际计算结果由 [`push-indicator-calc`](./push-indicator-calc.md) 推送，通过 `calc_id` 配对。需先注册 `IndicatorCalcHandlerBase` 子类接收推送。

* **参数**

    参数|类型|说明
    :-|:-|:-
    short_name|str|指标短名
    lang_type|[IndicatorLangType](./quote.md#6132)|脚本语言类型
    code|str|股票代码，如 `HK.00700`
    kl_type|[KLType](./quote.md#4119)|K 线类型
    klines|pd.DataFrame 或 list[dict]|K 线数据，可由 `request_history_kline` / `get_cur_kline` 返回
    num|int 或 None|最多取前 N 条 K 线参与计算  (None 表示使用全部 K 线)
    input_params|list[dict] 或 None|入参覆盖列表  (可空，留空使用云配置默认值；每项为 `{"index": int, "value": str}`)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467">RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>str</td>
            <td>当 ret == RET_OK，返回 calc_id（计算任务 ID，与推送结果配对）</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

* **Example**

```python
from futu import *
import time

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

class IndicatorCalcHandler(IndicatorCalcHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, content = super(IndicatorCalcHandler, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print('error:', content)
            return ret_code, content
        print('calc result:', content)
        return RET_OK, content

quote_ctx.set_handler(IndicatorCalcHandler())

ret, kl_data, _ = quote_ctx.request_history_kline('HK.00700', start='2024-01-01', end='2024-03-01', ktype=KLType.K_DAY)
if ret == RET_OK:
    ret, calc_id = quote_ctx.request_indicator_calc_async(
        'MA', IndicatorLangType.MYLANG, 'HK.00700', KLType.K_DAY, kl_data)
    if ret == RET_OK:
        print('calc_id:', calc_id)
    else:
        print('error:', calc_id)

time.sleep(5)
quote_ctx.close()
```

:::tip 接口限制
* 每 30 秒内最多发起 10 次指标计算请求。
* 实际计算结果通过 [Qot_PushIndicatorCalc](./push-indicator-calc.md)(3261) 异步推送，需提前注册推送回调。
:::
</content>
</invoke>

---

# 指标异步计算结果推送

`class IndicatorCalcHandlerBase(RspHandlerBase)`

* **介绍**

    指标异步计算结果推送回调基类。当 [`request_indicator_calc_async`](./request-indicator-calc.md) 发起的计算任务完成后，服务端会通过该回调主动推送结果。用户继承 `IndicatorCalcHandlerBase` 并重写 `on_recv_rsp` 方法接收推送，通过 `calc_id` 与发起的请求配对。

* **参数**

    on_recv_rsp 回调返回 (ret_code, content)，content 为 dict：

    参数|类型|说明
    :-|:-|:-
    calc_id|str|计算任务 ID，与 `request_indicator_calc_async` 返回的 calc_id 对应
    outputs|list|输出线元数据，每项含 index、name
    output_rows|list|计算结果，按时间顺序，每项含 time 与 values（与 outputs 一一对应）

* **Example**

```python
from futu import *

class IndicatorCalcHandler(IndicatorCalcHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, content = super(IndicatorCalcHandler, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print('IndicatorCalc error:', content)
            return RET_ERROR, content
        print('收到指标计算结果推送:')
        print('  calc_id:', content['calc_id'])
        print('  outputs:', content['outputs'])
        print('  rows:', len(content['output_rows']))
        return RET_OK, content

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
quote_ctx.set_handler(IndicatorCalcHandler())

# 通过 request_indicator_calc_async 发起计算后，结果会异步推送至上述 handler
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
quote_ctx.close()
```

:::tip 说明
* 本接口仅作为推送通道，无对应的主动请求，结果由 [Qot_RequestIndicatorCalc](./request-indicator-calc.md)(3260) 触发。
:::
</content>
</invoke>

---

# 获取历史 K 线额度使用明细

`get_history_kl_quota(get_detail=False)`

* **介绍**

    获取历史 K 线额度使用明细

* **参数**
    参数|类型|说明
    :-|:-|:-
    get_detail|bool|是否返回拉取历史 K 线的详细纪录  (True：返回False：不返回)


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>tuple</td>
            <td>当 ret == RET_OK，返回历史 K 线额度数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 历史 K 线额度数据格式如下：
        字段|类型|说明
        :-|:-|:-
        used_quota|int|已用额度  (即当前周期内已经下载过多少只股票)
        remain_quota|int|剩余额度
        detail_list|list|拉取历史 K 线的详细纪录，含股票代码和拉取时间  (list 中元素类型是 dict)

        - detail_list 数据列格式如下
            字段|类型|说明
            :-|:-|:-
            code|str|股票代码
            name|str|股票名称
            request_time|str|最后一次拉取的时间字符串  (格式：yyyy-MM-dd HH:mm:ss)

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_history_kl_quota(get_detail=True)  # 设置 true 代表需要返回详细的拉取历史 K 线的记录
if ret == RET_OK:
    print(data)
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
(2, 98, {'code': 'HK.00123', 'name': '越秀地产', 'request_time': '2023-06-20 19:59:00'}, {'code': 'HK.00700', 'name': '腾讯控股', 'request_time': '2023-07-19 17:48:16'}])
```


:::tip 接口限制
* 我们会根据您账户的资产和交易的情况，下发历史 K 线额度。因此，7 天内您只能获取有限只股票的历史 K 线数据。具体规则参见 [订阅额度 & 历史 K 线额度](../intro/authority.md#1314)。
* 您当日消耗的历史 K 线额度，会在 7 天后自动释放。
:::

---

# 设置到价提醒

`set_price_reminder(code, op, key=None, reminder_type=None, reminder_freq=None, value=None, note=None, reminder_session_list=NONE)`

* **介绍**

    新增、删除、修改、启用、禁用指定股票的到价提醒

* **参数**
    参数|类型|说明
    :-|:-|:-
    code|str|股票代码
    op|[SetPriceReminderOp](./quote.md#433)|操作类型
    key|int|标识，新增和删除全部的情况不需要填
    reminder_type|[PriceReminderType](./quote.md#5160)|到价提醒的类型，删除、启用、禁用的情况下会忽略该入参
    reminder_freq|[PriceReminderFreq](./quote.md#1059)|到价提醒的频率，删除、启用、禁用的情况下会忽略该入参
    value|float|提醒值，删除、启用、禁用的情况下会忽略该入参  (精确到小数点后 3 位，超出部分会被舍弃)
    note|str|用户设置的备注，仅支持 20 个以内的中文字符，删除、启用、禁用的情况下会忽略该入参
    reminder_session_list|list|美股到价提醒的时段列表，删除、启用、禁用的情况下会忽略该入参  (- list中元素类型是[PriceReminderMarketStatus](./quote.md#482)
  - 美股默认到价提醒时段：盘中+盘前盘后)


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">key</td>
            <td>int</td>
            <td>当 ret == RET_OK 时，返回操作的到价提醒 key</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>


* **Example**

```python
from futu import *
import time
class PriceReminderTest(PriceReminderHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, content = super(PriceReminderTest,self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("PriceReminderTest: error, msg: %s" % content)
            return RET_ERROR, content
        print("PriceReminderTest ", content) # PriceReminderTest 自己的处理逻辑
        return RET_OK, content
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
handler = PriceReminderTest()
quote_ctx.set_handler(handler)
ret, data = quote_ctx.get_market_snapshot(['US.AAPL'])
if ret == RET_OK:
    bid_price = data['bid_price'][0]  # 获取实时买一价
    ask_price = data['ask_price'][0]  # 获取实时卖一价
    # 设置当AAPL全时段卖一价低于（ask_price-1）时提醒
    ret_ask, ask_data = quote_ctx.set_price_reminder(code='US.AAPL', op=SetPriceReminderOp.ADD, key=None, reminder_type=PriceReminderType.ASK_PRICE_DOWN, reminder_freq=PriceReminderFreq.ALWAYS, value=(ask_price-1), note='123', reminder_session_list=[PriceReminderMarketStatus.US_PRE, PriceReminderMarketStatus.OPEN, PriceReminderMarketStatus.US_AFTER, PriceReminderMarketStatus.US_OVERNIGHT])
    if ret_ask == RET_OK:
        print('卖一价低于（ask_price-1）时提醒设置成功：', ask_data)
    else:
        print('error:', ask_data)
    # 设置当AAPL全时段买一价高于（bid_price+1）时提醒
    ret_bid, bid_data = quote_ctx.set_price_reminder(code='US.AAPL', op=SetPriceReminderOp.ADD, key=None, reminder_type=PriceReminderType.BID_PRICE_UP, reminder_freq=PriceReminderFreq.ALWAYS, value=(bid_price+1), note='456', reminder_session_list=[PriceReminderMarketStatus.US_PRE, PriceReminderMarketStatus.OPEN, PriceReminderMarketStatus.US_AFTER, PriceReminderMarketStatus.US_OVERNIGHT])
    if ret_bid == RET_OK:
        print('买一价高于（bid_price+1）时提醒设置成功：', bid_data)
    else:
        print('error:', bid_data)
time.sleep(15)
quote_ctx.close()
```

* **Output**

```python
卖一价低于（ask_price-1）时提醒设置成功： 1744022257023211123
买一价高于（bid_price+1）时提醒设置成功： 1744022257052794489
```

:::tip 提示
* API 中成交量设置统一以股为单位。但是牛牛客户端中，A 股是以手为单位展示
* 到价提醒类型，存在最小精度，如下：

    TURNOVER_UP：成交额最小精度为 10 元（人民币元，港元，美元）。传入的数值会自动向下取整到最小精度的整数倍。如果设置【00700成交额102元提醒】，设置后会得到【00700成交额100元提醒】；如果设置【00700 成交额 8 元提醒】，设置后会得到【00700 成交额 0 元提醒】。

    VOLUME_UP：A 股成交量最小精度为 1000 股，其他市场股票成交量最小精度为 10 股。传入的数值会自动向下取整到最小精度的整数倍。

    BID_VOL_UP、ASK_VOL_UP：A 股的买一卖一量最小精度为 100 股。传入的数值会自动向下取整到最小精度的整数倍。

    其余到价提醒类型精度支持到小数点后 3 位
:::

:::tip 接口限制
* 每 30 秒内最多请求 60 次设置到价提醒接口
* 每只股票每种类型可设置的提醒上限是 10 个
:::

---

# 获取到价提醒列表

`get_price_reminder(code=None, market=None)`

* **介绍**

    获取对指定股票 / 指定市场设置的到价提醒列表

* **参数**
    参数|类型|说明
    :-|:-|:-
    code|str|股票代码
    market|[Market](./quote.md#427)|市场类型  (输入沪股市场和深股市场，都会认为是 A 股市场) 
    注：code 和 market 都存在的情况下，code 优先。


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回到价提醒数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 到价提醒数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        key|int|标识，用于修改到价提醒
        reminder_type|[PriceReminderType](./quote.md#5160)|到价提醒的类型
        reminder_freq|[PriceReminderFreq](./quote.md#1059)|到价提醒的频率
        value|float|提醒值
        enable|bool|是否启用
        note|str|备注  (仅支持 20 个以内的中文字符) 
        reminder_session_list|list|美股到价提醒时段列表  (list中元素类型是[PriceReminderMarketStatus](./quote.md#482))

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_price_reminder(code='US.AAPL')
if ret == RET_OK:
    print(data)
    print(data['key'].values.tolist())   # 转为 list
else:
    print('error:', data)
print('******************************************')
ret, data = quote_ctx.get_price_reminder(code=None, market=Market.US)
if ret == RET_OK:
    print(data)
    if data.shape[0] > 0:  # 如果到价提醒列表不为空
        print(data['code'][0])    # 取第一条的股票代码
        print(data['code'].values.tolist())   # 转为 list
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
code name                  key   reminder_type reminder_freq   value  enable note                   reminder_session_list
0  US.AAPL   苹果  1744021708234288125    BID_PRICE_UP        ALWAYS  184.37    True  456                              [US_AFTER]
1  US.AAPL   苹果  1744022257052794489    BID_PRICE_UP        ALWAYS  185.50    True  456  [OPEN, US_PRE, US_AFTER, US_OVERNIGHT]
2  US.AAPL   苹果  1744021708211891867  ASK_PRICE_DOWN        ALWAYS  182.54    True  123                              [US_AFTER]
3  US.AAPL   苹果  1744022257023211123  ASK_PRICE_DOWN        ALWAYS  183.70    True  123  [OPEN, US_PRE, US_AFTER, US_OVERNIGHT]
[1744021708234288125, 1744022257052794489, 1744021708211891867, 1744022257023211123]
******************************************
      code name                  key   reminder_type reminder_freq   value  enable note                   reminder_session_list
0  US.AAPL   苹果  1744021708234288125    BID_PRICE_UP        ALWAYS  184.37    True  456                              [US_AFTER]
1  US.AAPL   苹果  1744022257052794489    BID_PRICE_UP        ALWAYS  185.50    True  456  [OPEN, US_PRE, US_AFTER, US_OVERNIGHT]
2  US.AAPL   苹果  1744021708211891867  ASK_PRICE_DOWN        ALWAYS  182.54    True  123                              [US_AFTER]
3  US.AAPL   苹果  1744022257023211123  ASK_PRICE_DOWN        ALWAYS  183.70    True  123  [OPEN, US_PRE, US_AFTER, US_OVERNIGHT]
4  US.NVDA  英伟达  1739697581665326308      PRICE_DOWN        ALWAYS  102.00    True       [OPEN, US_PRE, US_AFTER, US_OVERNIGHT]
US.AAPL
['US.AAPL', 'US.AAPL', 'US.AAPL', 'US.AAPL', 'US.NVDA']
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取到价提醒列表接口
:::

---

# 获取自选股列表

`get_user_security(group_name)`

* **介绍**

    获取指定分组的自选股列表

* **参数**

    参数|类型|说明
    :-|:-|:-
    group_name|str|需要查询的自选股分组名称


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回自选股数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 自选股数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|名字
        lot_size|int|每手股数，期权表示每份合约股数，期货表示合约乘数
        stock_type|[SecurityType](./quote.md#3325)|股票类型
        stock_child_type|[WrtType](./quote.md#926)|窝轮子类型
        stock_owner|str|窝轮所属正股的代码，或期权标的股的代码
        option_type|[OptionType](./quote.md#3713)|期权类型
        strike_time|str|期权行权日  (格式：yyyy-MM-dd
港股和 A 股市场默认是北京时间，美股市场默认是美东时间) 
        strike_price|float|期权行权价
        suspension|bool|期权是否停牌  (True：停牌) 
        listing_date|str|上市时间  (格式：yyyy-MM-dd)
        stock_id|int|股票 ID
        delisting|bool|是否退市
        main_contract|bool|是否主连合约
        last_trade_time|str|最后交易时间  (主连，当月，下月等期货没有此字段) 

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_user_security("A")
if ret == RET_OK:
    print(data)
    if data.shape[0] > 0:  # 如果自选股列表不为空
        print(data['code'][0])    # 取第一条的股票代码
        print(data['code'].values.tolist())   # 转为 list
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
    code    name  lot_size stock_type stock_child_type stock_owner option_type strike_time strike_price suspension listing_date        stock_id  delisting  main_contract last_trade_time
0  HK.HSImain  恒指期货主连        50     FUTURE              N/A                                              N/A        N/A                     71000662      False           True                
1  HK.00700    腾讯控股       100      STOCK              N/A                                              N/A        N/A   2004-06-16  54047868453564      False          False                
HK.HSImain
['HK.HSImain', 'HK.00700']
```

:::tip 提示
系统分组的中英文对应名称如下
    
中文|英文
:-|:-|:-
全部|All
沪深|CN
港股|HK
美股|US
期权|Options
港股期权|HK options
美股期权|US options
特别关注|Starred
期货|Futures
:::

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取自选股列表接口
* 不支持持仓（Positions），基金宝（Mutual Fund），外汇（Forex）分组的查询
:::

---

# 获取自选股分组

`get_user_security_group(group_type = UserSecurityGroupType.ALL)`

* **介绍**

    获取自选股分组列表

* **参数**
    参数|类型|说明
    :-|:-|:-
    group_type|[UserSecurityGroupType](./quote.md#4977)|分组类型


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK，返回自选股分组数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 自选股分组数据格式如下：
        字段|类型|说明
        :-|:-|:-
        group_name|str|分组名
        group_type|[UserSecurityGroupType](./quote.md#4977)|分组类型

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.get_user_security_group(group_type = UserSecurityGroupType.ALL)
if ret == RET_OK:
    print(data)
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
        group_name group_type
0          期权     SYSTEM
..         ...        ...
12          C     CUSTOM

[13 rows x 2 columns]
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取自选股分组接口
:::

---

# 修改自选股列表

`modify_user_security(group_name, op, code_list)`

* **介绍**

    修改指定分组的自选股列表（系统分组不支持修改）

* **参数**
    参数|类型|说明
    :-|:-|:-
    group_name|str|需要修改的自选股分组名称
    op|[ModifyUserSecurityOp](./quote.md#3838)|操作类型
    code_list|list|股票列表  (list 中元素类型是 str) 


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">msg</td>
            <td rowspan="2">str</td>
            <td>当 ret == RET_OK，返回“success”</td>
        </tr>
        <tr>
            <td>当 ret != RET_OK，msg 返回错误描述</td>
        </tr>
    </table>


* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret, data = quote_ctx.modify_user_security("A", ModifyUserSecurityOp.ADD, ['HK.00700'])
if ret == RET_OK:
    print(data) # 返回 success
else:
    print('error:', data)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
success
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次修改自选股列表接口
* 仅支持修改自定义分组，不支持修改系统分组
* “全部”自选股列表的数量存在上限：无交易客户 500 个，有交易客户 2000 个（向其他分组增加自选股时，“全部”列表中也会同步增加）
* 如果有同名的分组，会操作排序在第一个的分组
:::

---

# 到价提醒回调

`on_recv_rsp(self, rsp_pb)`

* **介绍**

    到价提醒通知回调，异步处理已设置到价提醒的通知推送。  
    在收到实时到价提醒通知推送后会回调到该函数，您需要在派生类中覆盖 on_recv_rsp。  


* **参数**

    参数|类型|说明
    :-|:-|:-
    rsp_pb|Qot_UpdatePriceReminder_pb2.Response|派生类中不需要直接处理该参数


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>dict</td>
            <td>当 ret == RET_OK，返回到价提醒</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 到价提醒
        字段|类型|说明
        :-|:-|:-
        code|str|股票代码
        name|str|股票名称
        price|float|当前价格
        change_rate|str|当前涨跌幅
        market_status|[PriceReminderMarketStatus](./quote.md#482)|触发的时间段
        content|str|到价提醒文字内容
        note|str|备注  (仅支持 20 个以内的中文字符) 
        key|int|到价提醒标识
        reminder_type|[PriceReminderType](./quote.md#5160)|到价提醒的类型
        set_value|float|用户设置的提醒值
        cur_value|float|提醒触发时的值

* **Example**

```python
import time
from futu import *

class PriceReminderTest(PriceReminderHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, content = super(PriceReminderTest,self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("PriceReminderTest: error, msg: %s" % content)
            return RET_ERROR, content
        print("PriceReminderTest ", content) # PriceReminderTest 自己的处理逻辑
        return RET_OK, content
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
handler = PriceReminderTest()
quote_ctx.set_handler(handler)  # 设置到价提醒通知回调
time.sleep(15)  # 设置脚本接收 OpenD 的推送持续时间为15秒
quote_ctx.close()   # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅
```

* **Output**

```python
PriceReminderTest  {'code': 'US.AAPL', 'name': '苹果', 'price': 185.750, 'change_rate': 0.11, 'market_status': 'US_PRE', 'content': '买一价高于185.500', 'note': '', 'key': 1744022257052794489, 'reminder_type': 'BID_PRICE_UP', 'set_value': 185.500, 'cur_value': 185.750}
```

:::tip 提示
* 此接口提供了持续获取推送数据的功能，如需一次性获取实时数据，请参考 [获取到价提醒](./get-price-reminder.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
:::

---

# 行情定义

## 累积过滤属性

> **StockField**

* `NONE`

  未知

* `CHANGE_RATE`

  涨跌幅  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  - 例如填写 [-10.2, 20.4] 值区间) 

* `AMPLITUDE`

  振幅  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  - 例如填写 [0.5, 20.6] 值区间) 

* `VOLUME`

  日均成交量  (- 精确到小数点后 0 位，超出部分会被舍弃
  - 例如填写 [2000, 70000] 值区间) 

* `TURNOVER`

  日均成交额  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 例如填写 [1400, 890000] 值区间) 


* `TURNOVER_RATE`

  换手率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  - 例如填写 [2, 30] 值区间)

## 资产类别

> **AssetClass**

* `UNKNOW`

  未知

* `STOCK`

  股票

* `BOND`

  债券

* `COMMODITY`

  商品

* `CURRENCY_MARKET`

  货币市场

* `FUTURE`

  期货

* `SWAP`

  掉期（互换）

## 公司行动


## 暗盘状态

> **DarkStatus**

* `NONE`

  无暗盘交易

* `TRADING`

  暗盘交易中

* `END`

  暗盘交易结束

## 财务过滤属性

> **StockField**

* `NONE`

  未知

* `NET_PROFIT`

  净利润  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 例如填写 [100000000, 2500000000] 值区间) 

* `NET_PROFIX_GROWTH`

  净利润增长率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  - 例如填写 [-10, 300] 值区间) 

* `SUM_OF_BUSINESS`

  营业收入  (- 精确到小数点后 3 位，超出部分会被舍弃
  -  例如填写 [100000000, 6400000000] 值区间)

* `SUM_OF_BUSINESS_GROWTH`

  营收同比增长率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  - 例如填写 [-5, 200] 值区间) 

* `NET_PROFIT_RATE`

  净利率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  -  例如填写 [10, 113] 值区间) 

* `GROSS_PROFIT_RATE`

  毛利率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  -  例如填写 [4, 65] 值区间)  

* `DEBT_ASSET_RATE`

  资产负债率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  -  例如填写 [5, 470] 值区间) 

* `RETURN_ON_EQUITY_RATE`

  净资产收益率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  -  例如填写 [20, 230] 值区间)  

* `ROIC`

  投入资本回报率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  -  例如填写 [1.0, 10.0] 值区间) 

* `ROA_TTM`

  资产回报率 TTM  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  - 仅适用于年报
  -  例如填写 [1.0, 10.0] 值区间)

* `EBIT_TTM`

  息税前利润 TTM  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  -  例如填写 [1000000000, 1000000000] 值区间) 

* `EBITDA`

  税息折旧及摊销前利润  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 单位：元
  -  例如填写 [1000000000, 1000000000] 值区间)  

* `OPERATING_MARGIN_TTM`

  营业利润率 TTM  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  - 仅适用于年报
  - 例如填写 [1.0, 10.0] 值区间) 

* `EBIT_MARGIN`

  EBIT 利润率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  -  例如填写 [1.0, 10.0] 值区间) 

* `EBITDA_MARGIN `

  EBITDA 利润率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  -  例如填写 [1.0, 10.0] 值区间) 

* `FINANCIAL_COST_RATE`

  财务成本率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  -  例如填写 [1.0, 10.0] 值区间) 

* `OPERATING_PROFIT_TTM `

  营业利润 TTM  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 单位：元
  - 仅适用于年报
  - 例如填写 [1000000000, 1000000000] 值区间) 

* `SHAREHOLDER_NET_PROFIT_TTM`

  归属于母公司的净利润  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 单位：元
  - 仅适用于年报
  - 例如填写 [1000000000, 1000000000] 值区间) 

* `NET_PROFIT_CASH_COVER_TTM`

  盈利中的现金收入比例  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  - 仅适用于年报
  - 例如填写 [1.0, 60.0] 值区间) 

* `CURRENT_RATIO`

  流动比率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [100, 250] 值区间) 

* `QUICK_RATIO`

  速动比率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [100, 250] 值区间) 

* `CURRENT_ASSET_RATIO`

  流动资产率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [100, 250] 值区间) 

* `CURRENT_DEBT_RATIO`

  流动负债率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [100, 250] 值区间) 

* `EQUITY_MULTIPLIER`

  权益乘数  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 例如填写 [100, 180] 值区间) 

* `PROPERTY_RATIO`

  产权比率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [50, 100] 值区间)

* `CASH_AND_CASH_EQUIVALENTS`

  现金和现金等价物  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 单位：元
  - 例如填写 [1000000000, 1000000000] 值区间)

* `TOTAL_ASSET_TURNOVER`

  总资产周转率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [50, 100] 值区间)
* `FIXED_ASSET_TURNOVER`

  固定资产周转率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [50, 100] 值区间)

* `INVENTORY_TURNOVER`

  存货周转率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [50, 100] 值区间)

* `OPERATING_CASH_FLOW_TTM`

  经营活动现金流 TTM  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 单位：元
  - 仅适用于年报
  - 例如填写 [1000000000, 1000000000] 值区间) 

* `ACCOUNTS_RECEIVABLE`

  应收账款净额  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 单位：元。
  - 例如填写 [1000000000, 1000000000] 值区间) 

* `EBIT_GROWTH_RATE`

  EBIT 同比增长率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [1.0, 10.0] 值区间)

* `OPERATING_PROFIT_GROWTH_RATE`

  营业利润同比增长率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [1.0, 10.0] 值区间)

* `TOTAL_ASSETS_GROWTH_RATE`

  总资产同比增长率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [1.0, 10.0] 值区间)

* `PROFIT_TO_SHAREHOLDERS_GROWTH_RATE`

  归母净利润同比增长率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [1.0, 10.0] 值区间)

* `PROFIT_BEFORE_TAX_GROWTH_RATE`

  总利润同比增长率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [1.0, 10.0] 值区间)

* `EPS_GROWTH_RATE`

  EPS 同比增长率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [1.0, 10.0] 值区间)

* `ROE_GROWTH_RATE`

  ROE 同比增长率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [1.0, 10.0] 值区间)

* `ROIC_GROWTH_RATE`

  ROIC 同比增长率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [1.0, 10.0] 值区间)

* `NOCF_GROWTH_RATE`

  经营现金流同比增长率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [1.0, 10.0] 值区间)

* `NOCF_PER_SHARE_GROWTH_RATE`

  每股经营现金流同比增长率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [1.0, 10.0] 值区间)

* `OPERATING_REVENUE_CASH_COVER`

  经营现金收入比  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [10, 100] 值区间)

* `OPERATING_PROFIT_TO_TOTAL_PROFIT`

  营业利润占比  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。
  - 例如填写 [10, 100] 值区间)

* `BASIC_EPS`

  基本每股收益  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 单位：元
  - 例如填写 [0.1, 10] 值区间)

* `DILUTED_EPS`

  稀释每股收益  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 单位：元
  - 例如填写 [0.1, 10] 值区间)

* `NOCF_PER_SHARE`

  每股经营现金净流量  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 单位：元
  - 例如填写 [0.1, 10] 值区间)

## 财务过滤属性周期

> **FinancialQuarter**

* `NONE`

  未知

* `ANNUAL`

  年报

* `FIRST_QUARTER`

  一季报

* `INTERIM`

  中报

* `THIRD_QUARTER`

  三季报

* `MOST_RECENT_QUARTER`

  最近季报

## 自定义技术指标属性

> **StockField**

* `NONE`

  未知

* `PRICE`

  最新价格

* `MA`

  简单均线

* `MA5`

  5日简单均线（不建议使用）

* `MA10`

  10日简单均线（不建议使用）

* `MA20`

  20日简单均线（不建议使用）

* `MA30`

  30日简单均线（不建议使用）

* `MA60`

  60日简单均线（不建议使用）

* `MA120`

  120日简单均线（不建议使用）

* `MA250`

  250日简单均线（不建议使用）

* `RSI`

  RSI  (指标参数的默认值为[12])

* `EMA`

  指数移动均线

* `EMA5`

  5日指数移动均线（不建议使用）

* `EMA10`

  10日指数移动均线（不建议使用）

* `EMA20`

  20日指数移动均线（不建议使用）

* `EMA30`

  30日指数移动均线（不建议使用）

* `EMA60`

  60日指数移动均线（不建议使用）

* `EMA120`

  120日指数移动均线（不建议使用）

* `EMA250`

  250日指数移动均线（不建议使用）

* `KDJ_K`

  KDJ 指标的 K 值  (指标参数需要根据 KDJ 进行传参。不传则默认为 [9,3,3])

* `KDJ_D`

  KDJ 指标的 D 值  (指标参数需要根据 KDJ 进行传参。不传则默认为 [9,3,3])

* `KDJ_J`

  KDJ 指标的 J 值  (指标参数需要根据 KDJ 进行传参。不传则默认为 [9,3,3])

* `MACD_DIFF`

  MACD 指标的 DIFF 值  (指标参数需要根据 MACD 进行传参。不传则默认为 [12,26,9])

* `MACD_DEA`

  MACD 指标的 DEA 值  (指标参数需要根据 MACD 进行传参。不传则默认为 [12,26,9])

* `MACD`

  MACD  (指标参数需要根据 MACD 进行传参。不传则默认为 [12,26,9])

* `BOLL_UPPER`

  BOLL 指标的 UPPER 值  (指标参数需要根据 BOLL 进行传参。不传则默认为 [20,2])

* `BOLL_MIDDLER`

  BOLL 指标的 MIDDLER 值  (指标参数需要根据 BOLL 进行传参。不传则默认为 [20,2])

* `BOLL_LOWER`

  BOLL 指标的 LOWER 值  (指标参数需要根据 BOLL 进行传参。不传则默认为 [20,2])

* `VALUE`

  自定义数值（stock_field1 不支持此字段）

## 指标语言类型

> **IndicatorLangType**

* `UNKNOWN`

  不过滤

* `MYLANG`

  麦语言

* `PYTHON`

  Python

## 指标搜索模式

> **IndicatorSearchMode**

* `PARTIAL`

  部分匹配（默认）

* `EXACT`

  完全匹配，同时返回 script 字段

## 指标参数值类型

指标入参 value dict 中的 type 字段取值。

## 指标形状

type 为 SHAPE 时，value 为下列枚举名字符串。

## 指标线型

type 为 LINE 时，value 为下列枚举名字符串。

## 指标参数值

指标入参 value dict 对应 Protobuf 结构；SDK 将各类型转为 Python 值。

## 指标输入参数

[get_indicator_list](./get-indicator-list.md) 返回的 inputs 元素结构。

## 指标输出参数

指标的一条输出线元数据；[push-indicator-calc](./push-indicator-calc.md) 回调 outputs 元素结构与此一致。

## 相对位置

> **RelativePosition**

* `NONE`

  未知

* `MORE`

  大于，stock_field1 位于stock_field2 的上方

* `LESS`

  小于，stock_field1 位于stock_field2 的下方

* `CROSS_UP`

  升穿，stock_field1 从下往上穿stock_field2

* `CROSS_DOWN`

  跌穿，stock_field1 从上往下穿stock_field2

## 形态技术指标属性

> **PatternField**

* `NONE`

  未知

* `MA_ALIGNMENT_LONG`

  MA多头排列（连续两天MA5>MA10>MA20>MA30>MA60，且当日收盘价大于前一天收盘价）

* `MA_ALIGNMENT_SHORT`

  MA空头排列（连续两天MA5<MA10<MA20<MA30<MA60，且当日收盘价小于前一天收盘价）

* `EMA_ALIGNMENT_LONG`

  EMA多头排列（连续两天EMA5>EMA10>EMA20>EMA30>EMA60，且当日收盘价大于前一天收盘价）

* `EMA_ALIGNMENT_SHORT`

  EMA空头排列（连续两天EMA5<EMA10<EMA20<EMA30<EMA60，且当日收盘价小于前一天收盘价）

* `RSI_GOLD_CROSS_LOW`

  RSI低位金叉（50以下，短线RSI上穿长线RSI（前一日短线RSI小于长线RSI，当日短线RSI大于长线RSI））

* `RSI_DEATH_CROSS_HIGH`

  RSI高位死叉（50以上，短线RSI下穿长线RSI（前一日短线RSI大于长线RSI，当日短线RSI小于长线RSI））

* `RSI_TOP_DIVERGENCE`

  RSI顶背离（相邻的两个K线波峰，后面的波峰对应的CLOSE>前面的波峰对应的CLOSE，后面波峰的RSI12值<前面波峰的RSI12值）

* `RSI_BOTTOM_DIVERGENCE`

  RSI底背离（相邻的两个K线波谷，后面的波谷对应的CLOSE<前面的波谷对应的CLOSE，后面波谷的RSI12值>前面波谷的RSI12值）

* `KDJ_GOLD_CROSS_LOW`

  KDJ低位金叉（D值小于或等于30，且前一日K值小于D值，当日K值大于D值）

* `KDJ_DEATH_CROSS_HIGH`

  KDJ高位死叉（D值大于或等于70，且前一日K值大于D值，当日K值小于D值）

* `KDJ_TOP_DIVERGENCE`

  KDJ顶背离（相邻的两个K线波峰，后面的波峰对应的CLOSE>前面的波峰对应的CLOSE，后面波峰的J值<前面波峰的J值）

* `KDJ_BOTTOM_DIVERGENCE`

  KDJ底背离（相邻的两个K线波谷，后面的波谷对应的CLOSE<前面的波谷对应的CLOSE，后面波谷的J值>前面波谷的J值）

* `MACD_GOLD_CROSS_LOW`

  MACD低位金叉（DIFF上穿DEA（前一日DIFF小于DEA，当日DIFF大于DEA））

* `MACD_DEATH_CROSS_HIGH`

  MACD高位死叉（DIFF下穿DEA（前一日DIFF大于DEA，当日DIFF小于DEA））

* `MACD_TOP_DIVERGENCE`

  MACD顶背离（相邻的两个K线波峰，后面的波峰对应的CLOSE>前面的波峰对应的CLOSE，后面波峰的macd值<前面波峰的macd值）

* `MACD_BOTTOM_DIVERGENCE`

  MACD底背离（相邻的两个K线波谷，后面的波谷对应的CLOSE<前面的波谷对应的CLOSE，后面波谷的macd值>前面波谷的macd值）

* `BOLL_BREAK_UPPER`

  BOLL突破上轨（前一日股价低于上轨值，当日股价大于上轨值）

* `BOLL_BREAK_LOWER`

  BOLL突破下轨（前一日股价高于下轨值，当日股价小于下轨值）

* `BOLL_CROSS_MIDDLE_UP`

  BOLL向上破中轨（前一日股价低于中轨值，当日股价大于中轨值）

* `BOLL_CROSS_MIDDLE_DOWN`

  BOLL向下破中轨（前一日股价大于中轨值，当日股价小于中轨值）

## 自选股分组类型

> **UserSecurityGroupType**

* `NONE`

  未知

* `CUSTOM`

  自定义分组

* `SYSTEM`

  系统分组

* `ALL`

  全部分组

## 指数期权类别

> **IndexOptionType**

* `NONE`

  未知

* `NORMAL`

  普通的指数期权

* `SMALL`

  小型指数期权

## 上市时段

> **IpoPeriod**

* `NONE`

  未知

* `TODAY`

  今日上市

* `TOMORROW`

  明日上市

* `NEXTWEEK`

  未来一周上市

* `LASTWEEK`

  过去一周上市

* `LASTMONTH`

  过去一月上市

## 窝轮发行商

> **Issuer**

* `UNKNOW`

  未知

* `SG`

  法兴

* `BP`

  法巴

* `CS`

  瑞信

* `CT`

  花旗

* `EA`

  东亚

* `GS`

  高盛

* `HS`

  汇丰

* `JP`

  摩通

* `MB`

  麦银

* `SC`

  渣打

* `UB`

  瑞银

* `BI`

  中银

* `DB`

  德银

* `DC`

  大和

* `ML`

  美林

* `NM`

  野村

* `RB`

  荷合

* `RS`

  苏皇

* `BC`

  巴克莱

* `HT`

  海通

* `VT`

  瑞通

* `KC`

  比联

* `MS`

  摩利

* `GJ`

  国君

* `XZ`

  星展

* `HU`

  华泰

* `KS`

  韩投  

* `CI`

  信证

## K 线字段

> **KL_FIELD**

* `ALL`

  所有

* `DATE_TIME`
  
  时间

* `HIGH`

  最高价

* `OPEN`

  开盘价

* `LOW`

  最低价

* `CLOSE`

  收盘价

* `LAST_CLOSE`

  上一个 K 线的收盘价

* `TRADE_VOL`

  成交量

* `TRADE_VAL`

  成交额

* `TURNOVER_RATE`

  换手率

* `PE_RATIO`

  市盈率

* `CHANGE_RATE`

  涨跌幅

## K 线类型

> **KLType**

* `NONE`

  未知

* `K_1M`

  1分 K

* `K_3M`

  3分 K  (期权暂不支持该K线类型)

* `K_5M`

  5分 K

* `K_10M`

  10分 K  (期权暂不支持该K线类型)

* `K_15M`

  15分 K

* `K_30M`

  30分 K  (期权暂不支持该K线类型)

* `K_60M`

  60分 K

* `K_120M`

  120分 K（2小时） (期权暂不支持该K线类型)

* `K_180M`

  180分 K（3小时） (期权暂不支持该K线类型)

* `K_240M`

  240分 K（4小时） (期权暂不支持该K线类型)

* `K_DAY`

  日 K

* `K_WEEK`

  周 K  (期权暂不支持该K线类型)

* `K_MON`

  月 K  (期权暂不支持该K线类型)

* `K_QUARTER`

  季 K  (期权暂不支持该K线类型)

* `K_YEAR`

  年 K  (期权暂不支持该K线类型)

## 周期类型

> **PeriodType**

* `INTRADAY`

  实时

* `DAY`

  日

* `WEEK`

  周

* `MONTH`

  月


## 到价提醒市场状态

> **PriceReminderMarketStatus**

* `NONE`

  未知

* `OPEN`

  盘中

* `US_PRE`

  美股盘前

* `US_AFTER`

  美股盘后

* `US_OVERNIGHT`

  美股夜盘

## 自选股操作

> **ModifyUserSecurityOp**

* `NONE`

  未知

* `ADD`

  新增

* `DEL`

  删除自选

* `MOVE_OUT`

  移出分组

## 期权类型（按行权时间）

> **OptionAreaType**

* `NONE`

  未知

* `AMERICAN`

  美式

* `EUROPEAN`

  欧式

* `BERMUDA`

  百慕大

## 期权价内/外

> **OptionCondType**

* `ALL`

  所有

* `WITHIN`

  价内

* `OUTSIDE`

  价外

## 期权类型（按方向）

> **OptionType**

* `ALL`

  所有

* `CALL`

  看涨期权

* `PUT`

  看跌期权

## 期权策略类型

> **OptionStrategyType**

* `NONE`

  未知

* `SINGLE`

  单个期权

* `COVERED`

  股票担保

* `SPREAD`

  垂直策略

* `STRADDLE`

  跨式策略

* `STRANGLE`

  宽跨式策略

* `COLLAR`

  领式策略

* `BUTTERFLY`

  蝶式策略

* `CONDOR`

  鹰式策略

* `IRON_BUTTERFLY`

  铁蝶式策略

* `IRON_CONDOR`

  铁鹰式策略

* `CALENDAR_SPREAD`

  日历策略

* `DIAGONAL_SPREAD`

  对角策略

* `CUSTOM`

  自定义策略

## 资讯子类型

> **NewsSubType**

* `ALL`

  全部

* `NEWS`

  新闻

* `NOTICE`

  公告

* `RATING`

  评级

## 板块集合类型

> **Plate**

* `ALL`

  所有板块

* `INDUSTRY`

  行业板块

* `REGION`

  地域板块  (港美股市场的地域分类数据暂为空) 

* `CONCEPT`

  概念板块

* `OTHER`

  其他板块  (仅用于 [获取股票所属板块](../quote/get-owner-plate.md) 接口的返回，不可作为其他接口的请求参数)

## 到价提醒频率

> **PriceReminderFreq**

* `NONE`

  未知

* `ALWAYS`

  持续提醒

* `ONCE_A_DAY`

  每日一次

* `ONCE`

  仅提醒一次

## 到价提醒类型

> **PriceReminderType**

* `NONE`

  未知

* `PRICE_UP`

  价格涨到

* `PRICE_DOWN`

  价格跌到

* `CHANGE_RATE_UP`

  日涨幅超  (该字段为百分比字段，设置时填 20 表示 20%) 

* `CHANGE_RATE_DOWN`

  日跌幅超  (该字段为百分比字段，设置时填 20 表示 20%) 

* `FIVE_MIN_CHANGE_RATE_UP`

  5 分钟涨幅超  (该字段为百分比字段，设置时填 20 表示 20%) 

* `FIVE_MIN_CHANGE_RATE_DOWN`

  5 分钟跌幅超  (该字段为百分比字段，设置时填 20 表示 20%) 

* `VOLUME_UP`

  成交量超过

* `TURNOVER_UP`

  成交额超过

* `TURNOVER_RATE_UP`

  换手率超过  (该字段为百分比字段，设置时填 20 表示 20%) 

* `BID_PRICE_UP`

  买一价高于

* `ASK_PRICE_DOWN`

  卖一价低于

* `BID_VOL_UP`

  买一量高于

* `ASK_VOL_UP`

  卖一量高于

* `THREE_MIN_CHANGE_RATE_UP`

  3 分钟涨幅超  (该字段为百分比字段，设置时填 20 表示 20%) 

* `THREE_MIN_CHANGE_RATE_DOWN`

  3 分钟跌幅超  (该字段为百分比字段，设置时填 20 表示 20%)

## 窝轮价内/外

> **PriceType**

* `UNKNOW`

  未知

* `OUTSIDE`

  价外，界内证表示界外

* `WITH_IN`

  价内，界内证表示界内

## 逐笔推送类型

> **PushDataType**

* `UNKNOW`

  未知

* `REALTIME`

  实时推送的数据

* `BYDISCONN`

  与富途服务器连接断开期间，拉取补充的数据  (最多 50 个)

* `CACHE`

  非实时非连接断开补充数据

## 行情市场

> **Market**

* `NONE`

  未知市场

* `HK`

  香港市场

* `US`

  美国市场

* `SH`

  沪股市场

* `SZ`

  深股市场

* `SG`

  新加坡市场

* `JP`

  日本市场

* `AU`

  澳大利亚市场

* `CA`

  加拿大市场

* `MY`

  马来西亚市场

* `FX`

  外汇市场

* `CC`

  加密货币市场

## 市场状态

> **MarketState**

各市场状态的对应时段：[点击这里](../qa/quote.md#2090)了解更多

* `NONE`

  无交易

* `AUCTION`

  盘前竞价

* `WAITING_OPEN`

  等待开盘

* `MORNING`

  早盘

* `REST`

  午间休市

* `AFTERNOON`

  午盘 / 美股持续交易时段

* `CLOSED`

  收盘

* `PRE_MARKET_BEGIN`

  美股盘前交易时段

* `PRE_MARKET_END`

  美股盘前交易结束

* `AFTER_HOURS_BEGIN`

  美股盘后交易时段

* `AFTER_HOURS_END`

  美股盘后结束

* `OVERNIGHT`

  美股夜盘交易时段

* `NIGHT_OPEN`

  夜市交易时段

* `NIGHT_END`

  夜市收盘

* `NIGHT`

  美指期权夜市交易时段

* `TRADE_AT_LAST`

  美指期权盘尾交易时段

* `FUTURE_DAY_OPEN`

  日市交易时段

* `FUTURE_DAY_BREAK`

  日市休市

* `FUTURE_DAY_CLOSE`

  日市收盘

* `FUTURE_DAY_WAIT_OPEN`

  期货待开盘

* `HK_CAS`

  港股盘后竞价

* `FUTURE_NIGHT_WAIT`

  夜市等待开盘（已废弃）

* `FUTURE_AFTERNOON`

  期货下午开盘（已废弃）

* `FUTURE_SWITCH_DATE`

  美期待开盘

* `FUTURE_OPEN`

  美期交易时段

* `FUTURE_BREAK`

  美期中盘休息

* `FUTURE_BREAK_OVER`

  美期休息后交易时段

* `FUTURE_CLOSE`

  美期收盘

* `STIB_AFTER_HOURS_WAIT`

  旧名保留兼容。A股盘后撮合等待时段（15:00-15:05）。适用范围：上交所A股/ETF、深交所A股及存托凭证/ETF。

* `ASHARE_AFTER_HOURS_WAIT`

  A股盘后撮合等待时段（15:00-15:05）。与 `STIB_AFTER_HOURS_WAIT` 同值（27）。

* `STIB_AFTER_HOURS_BEGIN`

  旧名保留兼容。A股盘后固定价格交易开始（15:05-15:30）。

* `ASHARE_AFTER_HOURS_BEGIN`

  A股盘后固定价格交易开始（15:05-15:30）。与 `STIB_AFTER_HOURS_BEGIN` 同值（28）。

* `STIB_AFTER_HOURS_END`

  旧名保留兼容。A股盘后固定价格交易结束（15:30之后）。

* `ASHARE_AFTER_HOURS_END`

  A股盘后固定价格交易结束（15:30之后）。与 `STIB_AFTER_HOURS_END` 同值（29）。

## 美股时段

> **Session**

* `NONE`

  未知

* `RTH`

  美股盘中时段

* `ETH`

  美股盘中+盘前盘后

* `OVERNIGHT`

  美股夜盘时段 (仅用于交易接口)

* `ALL`

  美股全时段  (用于行情&交易接口)

## 行情权限

> **QotRight**

* `UNKNOW`

  未知

* `BMP`

  BMP（此权限不支持订阅）

* `LEVEL1`

  Level1

* `LEVEL2`

  Level2

* `SF`

  港股 SF 高级全盘行情

* `NO`

  无权限

## 关联数据类型

> **SecurityReferenceType**

* `UNKNOW`

  未知

* `WARRANT`

  正股相关的窝轮

* `FUTURE`

  期货主连的相关合约

## K 线复权类型

> **AuType**

* `NONE`

  不复权

* `QFQ`

  前复权

* `HFQ`

  后复权

## 股票状态

> **SecurityStatus**

* `NONE`

  未知

* `NORMAL`

  正常状态

* `LISTING`

  待上市

* `PURCHASING`

  申购中

* `SUBSCRIBING`

  认购中

* `BEFORE_DRAK_TRADE_OPENING`

  暗盘开盘前

* `DRAK_TRADING`

  暗盘交易中

* `DRAK_TRADE_END`

  暗盘已收盘

* `TO_BE_OPEN`

  待开盘

* `SUSPENDED`

  停牌

* `CALLED`

  已收回

* `EXPIRED_LAST_TRADING_DATE`

  已过最后交易日

* `EXPIRED`

  已过期

* `DELISTED`

  已退市

* `CHANGE_TO_TEMPORARY_CODE`

  公司行动中，交易关闭，转至临时代码交易

* `TEMPORARY_CODE_TRADE_END`

  临时买卖结束，交易关闭

* `CHANGED_PLATE_TRADE_END`

  已转板，旧代码交易关闭

* `CHANGED_CODE_TRADE_END`

  已换代码，旧代码交易关闭

* `RECOVERABLE_CIRCUIT_BREAKER`

  可恢复性熔断

* `UN_RECOVERABLE_CIRCUIT_BREAKER`

  不可恢复性熔断

* `AFTER_COMBINATION`

  盘后撮合

* `AFTER_TRANSATION`

  盘后交易

## 股票类型

> **SecurityType**

* `NONE`

  未知

* `BOND`

  债券

* `BWRT`

  一揽子权证

* `STOCK`

  正股

* `ETF`

  信托,基金

* `WARRANT`

  窝轮

* `IDX`

  指数

* `PLATE`

  板块

* `DRVT`

  期权

* `PLATESET`

  板块集

* `FUTURE`

  期货

* `CRYPTO`

  加密货币

## 设置到价提醒操作类型

> **SetPriceReminderOp**

* `NONE`

  未知

* `ADD`

  新增

* `DEL`

  删除

* `ENABLE`

  启用

* `DISABLE`

  禁用

* `MODIFY`

  修改

* `DEL_ALL`

  删除全部（删除指定股票下的所有到价提醒）

## 排序方向

> **SortDir**

* `NONE`

  不排序

* `ASCEND`

  升序

* `DESCEND`

  降序

## 排序字段

> **SortField**

* `NONE`

  未知

* `CODE`

  代码

* `CUR_PRICE`

  最新价

* `PRICE_CHANGE_VAL`

  涨跌额

* `CHANGE_RATE`

  涨跌幅 %

* `STATUS`

  状态

* `BID_PRICE`

  买入价

* `ASK_PRICE`

  卖出价

* `BID_VOL`

  买量

* `ASK_VOL`

  卖量

* `VOLUME`

  成交量

* `TURNOVER`

  成交额

* `AMPLITUDE`

  振幅 %

* `SCORE`

  综合评分

* `PREMIUM`

  溢价 %

* `EFFECTIVE_LEVERAGE`

  有效杠杆

* `DELTA`

  对冲值  (仅认购认沽支持该字段) 

* `IMPLIED_VOLATILITY`

  引伸波幅  (仅认购认沽支持该字段) 

* `TYPE`

  类型

* `STRIKE_PRICE`

  行权价

* `BREAK_EVEN_POINT`

  打和点

* `MATURITY_TIME`

  到期日

* `LIST_TIME`

  上市日期

* `LAST_TRADE_TIME`

  最后交易日

* `LEVERAGE`

  杠杆比率

* `IN_OUT_MONEY`

  价内/价外 %

* `RECOVERY_PRICE`

  收回价  (仅牛熊证支持该字段) 

* `CHANGE_PRICE`

  换股价

* `CHANGE`

  换股比率

* `STREET_RATE`

  街货比 %

* `STREET_VOL`

  街货量

* `WARRANT_NAME`

  窝轮名称

* `ISSUER`

  发行人

* `LOT_SIZE`

  每手

* `ISSUE_SIZE`

  发行量

* `UPPER_STRIKE_PRICE`

  上限价  (仅用于界内证) 

* `LOWER_STRIKE_PRICE`

  下限价  (仅用于界内证) 

* `INLINE_PRICE_STATUS`

  界内界外  (仅用于界内证) 

* `PRE_CUR_PRICE`

  盘前最新价

* `AFTER_CUR_PRICE`

  盘后最新价

* `PRE_PRICE_CHANGE_VAL`

  盘前涨跌额

* `AFTER_PRICE_CHANGE_VAL`

  盘后涨跌额

* `PRE_CHANGE_RATE`

  盘前涨跌幅 %

* `AFTER_CHANGE_RATE`

  盘后涨跌幅 %

* `PRE_AMPLITUDE`

  盘前振幅 %

* `AFTER_AMPLITUDE`

  盘后振幅 %

* `PRE_TURNOVER`

  盘前成交额

* `AFTER_TURNOVER`

  盘后成交额

* `LAST_SETTLE_PRICE`

  昨结

* `POSITION`

  持仓量

* `POSITION_CHANGE`

  日增仓

* `MARKET_CAP`

  市值，用于 Qot_GetValuationPlateStockList

* `VALUATION`

  估值，用于 Qot_GetValuationPlateStockList

* `FORWARD_VALUATION`

  预测估值，用于 Qot_GetValuationPlateStockList

* `HISTORICAL_PERCENTILE`

  历史分位，用于 Qot_GetValuationPlateStockList

* `HOLDER_QUANTITY`

  持股股数，用于股东协议

* `SHARE_CHANGE_NUM`

  持股变动数，用于股东协议

* `HOLDING_DATE`

  持股日期，用于股东协议

* `HOLDER_PCT_CHANGE`

  变动比例，用于股东协议

* `HOLDER_CHANGE_AMOUNT`

  变动金额，用于股东协议

* `HOLDER_PCT`

  持股比例，用于股东协议

## 排序方式

> **SortType**

* `NONE`

  未知

* `DESC`

  降序

* `ASC`

  升序

## 财报类型

> **F10Type**

* `NONE`

  未知

* `Q1`

  单季报，Q1

* `Q2`

  单季报，Q2

* `Q3`

  单季报，Q3

* `Q4`

  单季报，Q4

* `Q6`

  累计季报，Q6（Q1+Q2）

* `Q9`

  累计季报，Q9（Q1+Q2+Q3）

* `ANNUAL`

  年报

* `QUARTERLY`

  单季报组合（Q1, Q2, Q3, Q4）

* `QUARTERLY_ANNUAL`

  单季报 + 年报

* `MUL_QUARTERLY`

  累计季报（Q1, Q6, Q9, Annual）

## 财报发布时间类型

> **EarningsPubTimeType**

* `NONE`

  未知

* `PRE_MARKET`

  盘前发布

* `AFTER_MARKET`

  盘后发布

* `DURING_MARKET`

  盘中发布

## 估值类型

> **ValuationType**

* `NONE`

  未知

* `PE`

  市盈率

* `PB`

  市净率

* `PS`

  市销率

## 财务报表类型

> **FinancialStatementsType**

* `NONE`

  未知

* `INCOME`

  利润表

* `BALANCE_SHEET`

  资产负债表

* `CASH_FLOW`

  现金流量表

* `MAIN_INDEX`

  关键指标

## 主营构成维度类型

> **RevenueBreakdownType**

* `NONE`

  未知

* `PRODUCT`

  产品

* `INDUSTRY`

  行业

* `REGION`

  地区

* `BUSINESS`

  业务

## 分析师评级

> **ResearchRatingType**

* `NONE`

  未知

* `SELL`

  Sell（卖出）

* `UNDERPERFORM`

  Underperform（跑输大盘）

* `HOLD`

  Hold（持有）

* `BUY`

  Buy（买入）

* `STRONG_BUY`

  Strong Buy（强力推荐）

## 研报评级维度类型

> **ResearchRatingDimensionType**

* `NONE`

  未知

* `INSTITUTION`

  机构维度（默认）

* `ANALYST`

  分析师维度

## 晨星评级类型

> **MorningstarRatingType**

* `NONE`

  未知

* `QUANTITATIVE`

  定量评级（系统模型给出）

* `QUALITATIVE`

  定性评级（分析师人工给出）

## 估值历史区间类型

> **ValuationIntervalType**

* `NONE`

  未知

* `MONTH3`

  3个月

* `MONTH6`

  6个月

* `YEAR1`

  1年

* `YEAR2`

  2年

* `YEAR3`

  3年

* `YEAR5`

  5年

* `YEAR10`

  10年

* `YEAR20`

  20年

* `YEAR30`

  30年

* `SINCE2019`

  从2019年起

## 公司行动重组方式

> **ReformType**

* `NONE`

  未知

* `STOCK_SPLIT`

  拆股

* `STOCK_MERGE`

  合股

* `BONUS_SHARE`

  送股

* `CAPITALIZATION_OF_RESERVES`

  转增股

* `RIGHTS_ISSUE`

  配股

* `NEW_SHARE_ISSUANCE`

  增发

* `CASH_DIVIDEND`

  现金分红

* `SPECIAL_DIVIDEND`

  特别股息

* `SPINOFF`

  公司分立

## 持股变动筛选类型

> **HoldingChangesFilterType**

* `NONE`

  全部（默认）

* `INCREASE`

  增持

* `DECREASE`

  减持

* `NEW_IN`

  建仓

* `CLOSE_OUT`

  清仓

## 股东持仓明细机构类型

> **HolderDetailType**

* `DEFAULT`

  默认不过滤，按服务端默认逻辑返回

* `ALL`

  全部

* `UNCLASSIFIED`

  其他机构

* `TRADITIONAL_INVESTMENT_MANAGER`

  传统投资经理

* `HEDGE_FUND_MANAGER`

  对冲基金

* `VC_OR_PE`

  风险资本/私募股权投资

* `CORPORATE_PENSION_PLAN_SPONSOR`

  企业年金

* `FOUNDATION_FUND_SPONSOR`

  基金会基金

* `INSURANCE_COMPANY`

  保险公司

* `BANK_OR_INVESTMENT_BANK`

  银行/投资银行

* `FAMILY_OFFICES_OR_TRUST`

  家族办公室/信托

* `SOVEREIGN_WEALTH_FUND`

  主权财富基金

* `REIT`

  REIT

* `STRUCTURED_FINANCE_POOL_MANAGER`

  结构化融资经理

* `UNION_PENSION_PLAN_SPONSOR`

  联合养老金

* `GOVERNMENT_PENSION_PLAN_SPONSOR`

  政府养老金

* `ENDOWMENT_FUND_SPONSOR`

  捐赠基金

* `INDIVIDUAL_INSIDERS`

  个人

* `ISSUE_SPONSORED_ADR`

  ADS

* `CORPORATIONS_PUBLIC`

  上市公司

* `CORPORATIONS_PRIVATE`

  未公开上市公司

* `STATE_OWNED_SHARES`

  国有股

## 公司资料字段类型

> **CompanyProfileFieldType**

* `SOURCE_TEXT`

  文本

* `LINK_TYPE`

  链接

* `INDEPENDENT_TITLE`

  独立标题

## 券商净买卖方向

> **BuySellType**

* `NONE`

  未知

* `NET_BUY`

  净买入

* `NET_SELL`

  净卖出

## 期权波动率查询时间周期

> **OptionVolatilityTimePeriodType**

* `NONE`

  未知

* `WEEK`

  周

* `MONTH`

  月（默认）

* `QUARTER`

  季度

* `HALF_YEAR`

  半年

* `YEAR`

  年

## 期权隐含波动率状态

> **OptionImpvolStatusType**

* `IMPVOL_FLUCTUATING`

  期权波动率处于震荡中

* `IMPVOL_OVERVALUED`

  期权波动率处于高估

* `IMPVOL_UNDERVALUED`

  期权波动率处于低估

## 简单过滤属性

> **StockField**

* `NONE`

  未知

* `STOCK_CODE`

  股票代码，不能填区间上下限值。

* `STOCK_NAME`

  股票名称，不能填区间上下限值。

* `CUR_PRICE`

  最新价  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 例如填写 [10, 20] 值区间) 

* `CUR_PRICE_TO_HIGHEST52_WEEKS_RATIO`

  **(CP - WH52) / WH52** <br>
  **CP**：现价 <br>
  **WH52**：52 周最高 <br>
  对应 PC 端“离 52 周高点百分比”  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  - 例如填写 [-30, -10] 值区间) 

* `CUR_PRICE_TO_LOWEST52_WEEKS_RATIO`

  **(CP - WL52) / WL52** <br>
  **CP**：现价 <br>
  **WL52**：52 周最低 <br>
  对应 PC 端“离 52 周低点百分比”  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  - 例如填写 [20, 40] 值区间) 

* `HIGH_PRICE_TO_HIGHEST52_WEEKS_RATIO`

  **(TH - WH52) / WH52**<br>
  **TH**：今日最高<br>
  **WH52**：52 周最高<br>
   (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  - 例如填写 [-3, -1] 值区间) 

* `LOW_PRICE_TO_LOWEST52_WEEKS_RATIO`

  **(TL - WL52) / WL52**<br>
  **TL**：今日最低<br>
  **WL52**：52 周最低<br>
   (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  - 例如填写 [10, 70] 值区间)

* `VOLUME_RATIO`

  量比  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 例如填写 [0.5, 30] 值区间)

* `BID_ASK_RATIO`

  委比  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  - 例如填写 [-20, 80.5] 值区间)

* `LOT_PRICE`

  每手价格  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 例如填写 [40, 100] 值区间)

* `MARKET_VAL`

  市值  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 例如填写 [50000000, 3000000000] 值区间)

* `PE_ANNUAL`

  市盈率(静态)  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 例如填写 [-8, 65.3] 值区间)

* `PE_TTM`

  市盈率 TTM   (- 精确到小数点后 3 位，超出部分会被舍弃
  - 例如填写 [-10, 20.5] 值区间)

* `PB_RATE`

  市净率  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 例如填写 [0.5, 20] 值区间)

* `CHANGE_RATE_5MIN`

  五分钟价格涨跌幅  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  - 例如填写 [-5, 6.3] 值区间)

* `CHANGE_RATE_BEGIN_YEAR`

  年初至今价格涨跌幅  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  - 例如填写 [-50.1, 400.7] 值区间)

* `PS_TTM`

  市销率 TTM  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  - 例如填写 [100, 500] 值区间)

* `PCF_TTM`

  市现率 TTM   (- 精确到小数点后 3 位，超出部分会被舍弃
  - 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%
  - 例如填写 [100, 1000] 值区间)

* `TOTAL_SHARE`

  总股数  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 单位：股
  - 例如填写 [1000000000, 1000000000] 值区间)

* `FLOAT_SHARE`

  流通股数  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 单位：股
  - 例如填写 [1000000000, 1000000000] 值区间)

* `FLOAT_MARKET_VAL`

  流通市值  (- 精确到小数点后 3 位，超出部分会被舍弃
  - 单位：元
  - 例如填写 [1000000000, 1000000000] 值区间)

## 订阅类型

> **SubType**

* `NONE`

  未知

* `QUOTE`

  基础报价

* `ORDER_BOOK`

  摆盘

* `TICKER`

  逐笔

* `RT_DATA`

  分时

* `K_DAY`

  日 K

* `K_5M`

  5 分 K

* `K_15M`

  15 分 K

* `K_30M`

  30 分 K

* `K_60M`

  60 分 K

* `K_1M`

  1 分 K

* `K_WEEK`

  周 K

* `K_MON`

  月 K

* `BROKER`

  经纪队列

* `K_QURATER`

  季 K

* `K_YEAR`

  年 K

* `K_3M`

  3 分 K

* `K_10M`

  10 分 K

* `K_120M`

  120 分 K（2小时）

* `K_180M`

  180 分 K（3小时）

* `K_240M`

  240 分 K（4小时）

* `ORDER_BOOK_ODD`

  碎股摆盘

## 摆盘类型

> **OrderBookType**

* `NORMAL`

  整股盘（默认）

* `ODD`

  碎股盘

## 逐笔成交方向

> **TickerDirect**

* `NONE`

  未知

* `BUY`

  外盘  (外盘（主动买入），即以卖一价或更高的价格成交股票) 

* `SELL`

  内盘  (内盘（主动卖出），即以买一价或更低的价格成交股票) 

* `NEUTRAL`

  中性盘  (中性盘，即以买一价与卖一价之间的价格撮合成交)

## 逐笔成交类型

> **TickerType**

* `UNKNOWN`

  未知

* `AUTO_MATCH`

  自动对盘

* `LATE`

  开市前成交盘

* `NON_AUTO_MATCH`

  非自动对盘

* `INTER_AUTO_MATCH`

  同一证券商自动对盘

* `INTER_NON_AUTO_MATCH`

  同一证券商非自动对盘

* `ODD_LOT`

  碎股交易

* `AUCTION`

  竞价交易

* `BULK`

  批量交易

* `CRASH`

  现金交易

* `CROSS_MARKET`

  跨市场交易

* `BULK_SOLD`

  批量卖出

* `FREE_ON_BOARD`

  离价交易

* `RULE127_OR155`

  第 127 条交易（纽交所规则）或第 155 条交易

* `DELAY`

  延迟交易

* `MARKET_CENTER_CLOSE_PRICE`

  中央收市价

* `NEXT_DAY`

  隔日交易

* `MARKET_CENTER_OPENING`

  中央开盘价交易

* `PRIOR_REFERENCE_PRICE`

  前参考价

* `MARKET_CENTER_OPEN_PRICE`

  中央开盘价

* `SELLER`

  卖方

* `T`

  T 类交易（盘前和盘后交易）

* `EXTENDED_TRADING_HOURS`

  延长交易时段

* `CONTINGENT`

  合单交易

* `AVERAGE_PRICE`

  平均价成交

* `OTC_SOLD`

  场外售出

* `ODD_LOT_CROSS_MARKET`

  碎股跨市场交易

* `DERIVATIVELY_PRICED`

  衍生工具定价

* `REOPENINGP_RICED`

  再开盘定价

* `CLOSING_PRICED`

  收盘定价

* `COMPREHENSIVE_DELAY_PRICE`

  综合延迟价格

* `OVERSEAS`

  交易的一方不是香港交易所的成员，属于场外交易

## 交易日查询市场

> **TradeDateMarket**

* `NONE`

  未知

* `HK`

  香港市场  (- 含股票、ETFs、窝轮、牛熊、期权、非假期交易期货
  - 不含假期交易期货)

* `US`

  美国市场  (- 含股票、ETFs、期权
  - 不含期货)

* `CN`

  A 股市场

* `NT`

  深（沪）股通

* `ST`

  港股通（深、沪）

* `JP_FUTURE`

  日本期货

* `SG_FUTURE`

  新加坡期货

## 交易日类型

> **TradeDateType**

* `WHOLE`

  全天交易

* `MORNING`

  上午交易，下午休市

* `AFTERNOON`

  下午交易，上午休市

## 窝轮状态

> **WarrantStatus**

* `NONE`

  未知

* `NORMAL`

  正常状态

* `SUSPEND`

  停牌

* `STOP_TRADE`

  终止交易

* `PENDING_LISTING`

  等待上市

## 窝轮类型

> **WrtType**

* `NONE`

  未知

* `CALL`

  认购窝轮

* `PUT`

  认沽窝轮

* `BULL`

  牛证

* `BEAR`

  熊证

* `INLINE`

  界内证

## 所属交易所

> **ExchType**

* `NONE`

  未知

* `HK_MAINBOARD`

  港交所·主板 

* `HK_GEMBOARD`

  港交所·创业板

* `HK_HKEX`

  港交所

* `US_NYSE`

  纽交所

* `US_NASDAQ`

  纳斯达克

* `US_PINK`

  OTC市场

* `US_AMEX`

  美交所

* `US_OPTION`

  美国  (仅美股期权适用) 

* `US_NYMEX`

  NYMEX

* `US_COMEX `

  COMEX

* `US_CBOT`

  CBOT 

* `US_CME`

  CME

* `US_CBOE`

  CBOE 

* `CN_SH`

  上交所

* `CN_SZ`

  深交所   

* `CN_STIB`

  科创板

* `SG_SGX`

  新交所 

* `JP_OSE`

  大阪交易所 

* `CC_CRYPTO`

  加密货币交易所

## 行情公共参数头

**QotHeader**

```protobuf
message QotHeader
{
    optional int32 securityFirm = 1; //券商标识，取值见 Trd_Common.SecurityFirm
}
```

## 证券标识

**Security**

```protobuf
message Security
{
    required int32 market = 1; //QotMarket，行情市场
    required string code = 2; //代码
}
```

## K 线数据

**KLine**

```protobuf
message KLine
{
    required string time = 1; //时间戳字符串（格式：yyyy-MM-dd HH:mm:ss）
    required bool isBlank = 2; //是否是空内容的点,若为 true 则只有时间信息
    optional double highPrice = 3; //最高价
    optional double openPrice = 4; //开盘价
    optional double lowPrice = 5; //最低价
    optional double closePrice = 6; //收盘价
    optional double lastClosePrice = 7; //上一个 K 线的收盘价
    optional int64 volume = 8; //成交量
    optional double turnover = 9; //成交额
    optional double turnoverRate = 10; //换手率（该字段为百分比字段，展示为小数表示）
    optional double pe = 11; //市盈率
    optional double changeRate = 12; //涨跌幅（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    optional double timestamp = 13; //时间戳
    optional double hpVolume = 14; //高精度成交量
}
```

## 基础报价的期权特有字段

**OptionBasicQotExData**

```protobuf
message OptionBasicQotExData
{
    required double strikePrice = 1; //行权价
    required int32 contractSize = 2; //每份合约数(整型数据)
    optional double contractSizeFloat = 17; //每份合约数（浮点型数据）
    required int32 openInterest = 3; //未平仓合约数
    required double impliedVolatility = 4; //隐含波动率（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    required double premium = 5; //溢价（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    required double delta = 6; //希腊值 Delta
    required double gamma = 7; //希腊值 Gamma
    required double vega = 8; //希腊值 Vega
    required double theta = 9; //希腊值 Theta
    required double rho = 10; //希腊值 Rho
    optional int32 netOpenInterest = 11; //净未平仓合约数，仅港股期权适用
    optional int32 expiryDateDistance = 12; //距离到期日天数，负数表示已过期
    optional double contractNominalValue = 13; //合约名义金额，仅港股期权适用
    optional double ownerLotMultiplier = 14; //相等正股手数，指数期权无该字段，仅港股期权适用
    optional int32 optionAreaType = 15; //OptionAreaType，期权类型（按行权时间）
    optional double contractMultiplier = 16; //合约乘数
    optional int32 indexOptionType = 18; //IndexOptionType，指数期权类型
}    
```

## 基础报价的期货特有字段

**FutureBasicQotExData**

```protobuf
message FutureBasicQotExData
{
    required double lastSettlePrice = 1; //昨结
    required int32 position = 2; //持仓量
    required int32 positionChange = 3; //日增仓
    optional int32 expiryDateDistance = 4; //距离到期日天数
}    
```

## 基础报价

**BasicQot**

```protobuf
message BasicQot
{
    required Security security = 1; //股票
    optional string name = 24; // 股票名称
    required bool isSuspended = 2; //是否停牌
    required string listTime = 3; //上市日期字符串（此字段停止维护，不建议使用，格式：yyyy-MM-dd）
    required double priceSpread = 4; //价差
    required string updateTime = 5; //最新价的更新时间字符串（格式：yyyy-MM-dd HH:mm:ss），对其他字段不适用
    required double highPrice = 6; //最高价
    required double openPrice = 7; //开盘价
    required double lowPrice = 8; //最低价
    required double curPrice = 9; //最新价
    required double lastClosePrice = 10; //昨收价
    required int64 volume = 11; //成交量
    required double turnover = 12; //成交额
    required double turnoverRate = 13; //换手率（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    required double amplitude = 14; //振幅（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    optional int32 darkStatus = 15; //DarkStatus, 暗盘交易状态	
    optional OptionBasicQotExData optionExData = 16; //期权特有字段
    optional double listTimestamp = 17; //上市日期时间戳（此字段停止维护，不建议使用）
    optional double updateTimestamp = 18; //最新价的更新时间戳，对其他字段不适用
    optional PreAfterMarketData preMarket = 19; //盘前数据
    optional PreAfterMarketData afterMarket = 20; //盘后数据
    optional int32 secStatus = 21; //SecurityStatus, 股票状态
    optional FutureBasicQotExData futureExData = 22; //期货特有字段
    optional double hpVolume = 26; //高精度成交量
}
```

## 盘前盘后数据

**PreAfterMarketData**
 
```protobuf
//美股支持盘前盘后数据
//科创板仅支持盘后数据：成交量，成交额
message PreAfterMarketData
{
    optional double price = 1;  // 盘前或盘后## 价格
    optional double highPrice = 2;  // 盘前或盘后## 最高价
    optional double lowPrice = 3;  // 盘前或盘后## 最低价
    optional int64 volume = 4;  // 盘前或盘后## 成交量
    optional double turnover = 5;  // 盘前或盘后## 成交额
    optional double changeVal = 6;  // 盘前或盘后## 涨跌额
    optional double changeRate = 7;  // 盘前或盘后## 涨跌幅（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    optional double amplitude = 8;  // 盘前或盘后## 振幅（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
}
```

## 分时数据

**TimeShare**

```protobuf
message TimeShare
{
    required string time = 1; //时间字符串（格式：yyyy-MM-dd HH:mm:ss）
    required int32 minute = 2; //距离0点过了多少分钟
    required bool isBlank = 3; //是否是空内容的点,若为 true 则只有时间信息
    optional double price = 4; //当前价
    optional double lastClosePrice = 5; //昨收价
    optional double avgPrice = 6; //均价
    optional int64 volume = 7; //成交量
    optional double turnover = 8; //成交额
    optional double timestamp = 9; //时间戳
    optional double hpVolume = 10; //高精度成交量
}
```

## 证券基本静态信息

**SecurityStaticBasic**

```protobuf

message SecurityStaticBasic
{
    required Qot_Common.Security security = 1; //股票
    required int64 id = 2; //股票 ID
    required int32 lotSize = 3; //每手数量,期权类型表示一份合约的股数
    required int32 secType = 4; //Qot_Common.SecurityType,股票类型
    required string name = 5; //股票名字
    required string listTime = 6; //上市时间字符串（此字段停止维护，不建议使用，格式：yyyy-MM-dd）
    optional bool delisting = 7; //是否退市
    optional double listTimestamp = 8; //上市时间戳（此字段停止维护，不建议使用）
    optional int32 exchType = 9; //Qot_Common.ExchType,所属交易所
}
```

## 窝轮额外静态信息
**WarrantStaticExData**

```protobuf
message WarrantStaticExData
{
    required int32 type = 1; //Qot_Common.WarrantType,窝轮类型
    required Qot_Common.Security owner = 2; //所属正股
}    
```
## 期权额外静态信息

**OptionStaticExData**

```protobuf
message OptionStaticExData
{
    required int32 type = 1; //Qot_Common.OptionType,期权
    required Qot_Common.Security owner = 2; //标的股
    required string strikeTime = 3; //行权日（格式：yyyy-MM-dd）
    required double strikePrice = 4; //行权价
    required bool suspend = 5; //是否停牌
    required string market = 6; //发行市场名字
    optional double strikeTimestamp = 7; //行权日时间戳
    optional int32 indexOptionType = 8; //Qot_Common.IndexOptionType, 指数期权的类型，仅在指数期权有效
	optional int32 expirationCycle = 9; // ExpirationCycle，交割周期
    optional int32 optionStandardType = 10; // OptionStandardType，标准期权
    optional int32 optionSettlementMode = 11; // OptionSettlementMode，结算方式
}
```

## 期货额外静态信息

**FutureStaticExData**

```protobuf
message FutureStaticExData
{
    required string lastTradeTime = 1; //最后交易日，只有非主连期货合约才有该字段
    optional double lastTradeTimestamp = 2; //最后交易日时间戳，只有非主连期货合约才有该字段
    required bool isMainContract = 3; //是否主连合约
}    
```

## 证券静态信息

**SecurityStaticInfo**

```protobuf
message SecurityStaticInfo
{
    required SecurityStaticBasic basic = 1; //证券基本静态信息
    optional WarrantStaticExData warrantExData = 2; //窝轮额外静态信息
    optional OptionStaticExData optionExData = 3; //期权额外静态信息
    optional FutureStaticExData futureExData = 4; //期货额外静态信息
}
```

## 买卖经纪

**Broker**

```protobuf
message Broker
{
    required int64 id = 1; //经纪 ID
    required string name = 2; //经纪名称
    required int32 pos = 3; //经纪档位
    
    //以下为港股 SF 行情特有字段
    optional int64 orderID = 4; //交易所订单 ID，与交易接口返回的订单 ID 并不一样
    optional int64 volume = 5; //订单股数
}
```

## 逐笔成交

**Ticker**

```protobuf
message Ticker
{
    required string time = 1; //时间字符串（格式：yyyy-MM-dd HH:mm:ss）
    required int64 sequence = 2; // 唯一标识
    required int32 dir = 3; //TickerDirection, 买卖方向
    required double price = 4; //价格
    required int64 volume = 5; //成交量
    required double turnover = 6; //成交额
    optional double recvTime = 7; //收到推送数据的本地时间戳，用于定位延迟
    optional int32 type = 8; //TickerType, 逐笔类型
    optional int32 typeSign = 9; //逐笔类型符号
    optional int32 pushDataType = 10; //用于区分推送情况，仅推送时有该字段
    optional double timestamp = 11; //时间戳
    optional double hpVolume = 12; //高精度成交量
}	
```
## 买卖档明细

**OrderBookDetail**

```protobuf
message OrderBookDetail
{
    required int64 orderID = 1; //交易所订单 ID，与交易接口返回的订单 ID 并不一样
    required int64 volume = 2; //订单股数
}
```

## 买卖档

**OrderBook**

```protobuf
message OrderBook
{
    required double price = 1; //委托价格
    required int64 volume = 2; //委托数量
    required int32 orederCount = 3; //委托订单个数
    repeated OrderBookDetail detailList = 4; //订单信息，港股 SF，美股深度摆盘特有
    optional double hpVolume = 5; //高精度委托数量
}
```

## 持股变动

**ShareHoldingChange**

```protobuf
message ShareHoldingChange
{
    required string holderName = 1; //持有者名称（机构名称 或 基金名称 或 高管姓名）
    required double holdingQty = 2; //当前持股数量
    required double holdingRatio = 3; //当前持股百分比（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    required double changeQty = 4; //较上一次变动数量
    required double changeRatio = 5; //较上一次变动百分比（该字段为百分比字段，默认不展示 %，如20实际对应20%。是相对于自身的比例，而不是总的。如总股本1万股，持有100股，持股百分比是1%，卖掉50股，变动比例是50%，而不是0.5%）
    required string time = 6; //发布时间（格式：yyyy-MM-dd HH:mm:ss）
    optional double timestamp = 7; //时间戳
}
```

## 单个订阅类型信息

**SubInfo**

```protobuf
message SubInfo
{
    required int32 subType = 1;  //Qot_Common.SubType,订阅类型
    repeated Qot_Common.Security securityList = 2; 	//订阅该类型行情的证券
}	
```

## 单条连接订阅信息

**ConnSubInfo**

```protobuf
message ConnSubInfo
{
    repeated SubInfo subInfoList = 1; //该连接订阅信息
    required int32 usedQuota = 2; //该连接已经使用的订阅额度
    required bool isOwnConnData = 3; //用于区分是否是自己连接的数据
    optional int32 securityFirm = 4; //券商标识，取值见 Trd_Common.SecurityFirm
}
```

## 板块信息

**PlateInfo**

```protobuf
message PlateInfo
{
    required Qot_Common.Security plate = 1; //板块
    required string name = 2; //板块名字
    optional int32 plateType = 3; //PlateSetType 板块类型, 仅3207（获取股票所属板块）协议返回该字段
}
```

## 复权信息

**Rehab**

```protobuf
message Rehab
{
    required string time = 1; //时间字符串（格式：yyyy-MM-dd）
    required int64 companyActFlag = 2; //公司行动(CompanyAct)组合标志位,指定某些字段值是否有效
    required double fwdFactorA = 3; //前复权因子 A
    required double fwdFactorB = 4; //前复权因子 B
    required double bwdFactorA = 5; //后复权因子 A
    required double bwdFactorB = 6; //后复权因子 B
    optional int32 splitBase = 7; //拆股(例如，1拆5，Base 为1，Ert 为5)
    optional int32 splitErt = 8;	
    optional int32 joinBase = 9; //合股(例如，50合1，Base 为50，Ert 为1)
    optional int32 joinErt = 10;	
    optional int32 bonusBase = 11; //送股(例如，10送3, Base 为10,Ert 为3)
    optional int32 bonusErt = 12;	
    optional int32 transferBase = 13; //转赠股(例如，10转3, Base 为10,Ert 为3)
    optional int32 transferErt = 14;	
    optional int32 allotBase = 15; //配股(例如，10送2, 配股价为6.3元, Base 为10, Ert 为2, Price 为6.3)
    optional int32 allotErt = 16;	
    optional double allotPrice = 17;	
    optional int32 addBase = 18; //增发股(例如，10送2, 增发股价为6.3元, Base 为10, Ert 为2, Price 为6.3)
    optional int32 addErt = 19;	
    optional double addPrice = 20;	
    optional double dividend = 21; //现金分红(例如，每10股派现0.5元,则该字段值为0.05)
    optional double spDividend = 22; //特别股息(例如，每10股派特别股息0.5元,则该字段值为0.05)
    optional double timestamp = 23; //时间戳
}
```

> - 公司行动组合标志位参见 [CompanyAct](./quote.html#1239)

## 组合腿信息

**ComboLeg**

```protobuf
message ComboLeg
{
    required Qot_Common.Security security = 1; //股票/期权
    optional int32 side = 2; //方向，取值见 Trd_Common.TrdSide
    optional double qtyRatio = 3; //数量比例
    optional uint64 positionID = 4; //持仓ID，仅 moomoo JP 平仓时填写；须为 showOptionStrategyView=True 时期权策略视图持仓中的 positionID。
}
```

## 交割周期
>**ExpirationCycle**

* `NONE`

  未知

* `WEEK`

  周期权

* `MONTH`

  月期权
  
* `END_OF_MONTH`

  月末期权
  
* `QUARTERLY`

  季期权
  
* `WEEKMON`

  周期权-周一
  
* `WEEKTUE`

  周期权-周二
  
* `WEEKWED`

  周期权-周三
  
* `WEEKTHU`

  周期权-周四
  
* `WEEKFRI`

  周期权-周五


## 期权标准类型
>**OptionStandardType**

* `NONE`

  未知

* `STANDARD`

  标准期权

* `NON_STANDARD`

  非标准期权


## 期权结算方式
>**OptionSettlementMode**

* `NONE`

  未知

* `AM`

  亚式期权

* `PM`

  路径依赖型

## 股票持有者（已废弃）

> **StockHolder**

* `NONE`

  未知

* `INSTITUTE`

  机构

* `FUND`

  基金

* `EXECUTIVE`

  高管

## 筛选 V2 - SimpleField

> 用于 [get_stock_screen](./get-stock-screen.md) 的 `add_simple_field(field, values)` 方法。所有数值字段直接传原始值，OpenD 自动完成倍率转换。

field|含义|values 取值
:-|:-|:-
1|MARKET 市场|ScrMarket：HK=1、US=2、CN=3、SG=4、CA=5、AU=6、JA=7、MY=8
2|EXCHANGE 交易所/上市地|参考 [QotMarket](#427)
3|INDEX_ID 指数 ID|指数成分股 ID
4|USE_WATCHLIST 使用自选股|0=否，1=是
5|HAS_ADR 是否有关联 ADR|0/1
6|HAS_OPTION 是否有期权|0/1
7|HAS_WARRANT 是否有窝轮|0/1
8|HAS_FUTURE 是否有期货|0/1
9|HAS_AH_STOCK 是否有 AH 股|0/1
10|IS_ISLAMIC 回教股|0/1
11|NORTH_BOUND_ID 北向板块|沪/深股通 ID
12|MM_EXCLUSIVE_ID Moomoo 独家板块|板块 ID

> 完整枚举见 SDK 中 `stock_screen_const.py` 的 `SimpleField` / `ScrMarket` 类。

## 筛选 V2 - SimpleProperty

> 用于 `add_simple_property(name, lower, upper)` 与 `add_retrieve_simple(name)`。常用因子如下，所有数值传原始值。

name|含义
:-|:-
2101|LONG_MARGIN_ALLOWED 是否允许融资 (0/1)
2103|SHORT_MARGIN_ALLOWED 是否允许融券 (0/1)
2201|PRICE 最新价
2202|OPEN_PRICE 今开价
2203|LAST_CLOSE 昨收价
2204|HIGH 今高
2205|LOW 今低
2217|VOLUME_RATIO 量比
2218|BID_ASK_RATIO 委比
2301|MARKET_CAP 市值
2302|PE_ANNUAL 静态 PE
2303|PE_TTM TTM 市盈率
2304|PB 市净率
2305|DIVIDEND_RATIO 股息率
2306|LISTED_DATE 上市时间（时间戳）
2307|LISTED_DAYS 上市天数

> 完整枚举见 `SimpleProperty` 类（含融资融券、盘前盘后、夜盘、高精度报价等共 60+ 项）。

## 筛选 V2 - CumulativeProperty

> 用于 `add_cumulative_property(name, days, lower, upper)` 与 `add_retrieve_cumulative(name, days)`。需配合 `days` 参数。

name|含义
:-|:-
3101|PRICE_CHANGE 价格涨跌额
3102|PRICE_CHANGE_PCT 价格涨跌幅 (%)
3103|AMPLITUDE 价格振幅 (%)
3104|AVG_VOLUME 平均成交量
3105|AVG_TURNOVER 平均成交额
3106|TURNOVER_RATIO 换手率 (%)
3107|HIGH_TO_N_DAY_HIGH (今高-N日最高)/N日最高
3108|LOW_TO_N_DAY_LOW (今低-N日最低)/N日最低
3109|PRICE_CHANGE_HP 高精度涨跌额

## 筛选 V2 - FinancialProperty

> 用于 `add_financial_property(name, term, year, lower, upper)` 与 `add_retrieve_financial(name, term, year)`。需配合 `term`（报告期）。

* **常用因子（完整枚举见 `FinancialProperty` 类，含盈利能力 / 偿债 / 运营 / 成长 / 现金流 / 财务超预期等共 100+ 项）**

    name|含义
    :-|:-
    4101|NET_PROFIT 净利润
    4102|NET_PROFIT_GROWTH 净利润增长率
    4105|REVENUE 营业额
    4106|REVENUE_GROWTH 营业额增长率
    4107|NET_PROFIT_RATIO 净利率
    4108|GROSS_PROFIT_RATIO 毛利率
    4109|DEBT_TO_ASSETS 资产负债率
    4110|ROE 净资产收益率
    4202|ROIC 投入资本回报率
    4801|BASIC_EPS 基本每股收益
    4901|TOTAL_SHARE 总股数
    4903|FLOAT_MARKET_CAP 流通市值
    4904|PS_TTM 市销率 TTM
    4905|PCF_TTM 市现率 TTM

* **Term 报告期**（`Term` 枚举）

    term|含义
    :-|:-
    1 / 2 / 3 / 4|Q1 / Q2 / Q3 / Q4 单季报
    6|Q6 中报（累积）
    9|Q9 三季报（累积）
    10|LATEST 最新单季
    100|ANNUAL 年报 FY
    200~204|SURPRISE_LATEST 系列（财报预测）

## 筛选 V2 - Indicator / Pattern / Period / Position

> 用于 `add_indicator_positional` / `add_indicator_pattern` / `add_retrieve_indicator`。

* **`Indicator` 技术指标**（`add_indicator_positional` 的 `first_indicator_name` / `second_indicator`）

    name|含义
    :-|:-
    1|PRICE 最新价
    11~17|MA5 / MA10 / MA20 / MA30 / MA60 / MA120 / MA250
    18|MA 动态简单均线（需设 indicator_params）
    21~27|EMA5 / EMA10 / EMA20 / EMA30 / EMA60 / EMA120 / EMA250
    28|EMA 动态指数均线
    31~33|KDJ_K / KDJ_D / KDJ_J（KDJ(9,3,3)）
    41~43|MACD_DIF / MACD_DEA / MACD_MACD（MACD(12,26,9)）
    51|RSI_12
    52|RSI 动态
    61~63|BOLL_UPPER / BOLL_MIDDLE / BOLL_LOWER（BOLL(20,2)）
    71|RVOL 动态相对成交量

* **`Pattern` 形态**（`add_indicator_pattern` 的 `name`）

    name|含义
    :-|:-
    1 / 2|MA 多头 / 空头排列
    3 / 4|EMA 多头 / 空头排列
    11 / 12|KDJ 低位金叉 / 高位死叉
    13 / 14|KDJ 顶背离 / 底背离
    21 / 22|MACD 低位金叉 / 高位死叉
    23 / 24|MACD 顶背离 / 底背离
    31 / 32|RSI 低位金叉 / 高位死叉
    33 / 34|RSI 顶背离 / 底背离

* **`Period` 周期**

    period|含义
    :-|:-
    1 / 2 / 3 / 4|1 / 3 / 5 / 15 分钟
    5|HOUR_1 1 小时
    6|MINUTE_30 30 分钟
    11 / 21 / 31|DAY 日 / WEEK 周 / MONTH 月

* **`Position` 位置关系**

    position|含义
    :-|:-
    1|OVER first 位于 second 上方
    2|BELOW first 位于 second 下方
    3|CROSS_UP first 上穿 second
    4|CROSS_DOWN first 下穿 second

* **`ScrSortDir` 排序方向**（`set_sort` / `add_sort` 的 `direction`）

    direction|含义
    :-|:-
    1|ASC 升序
    2|DESC 降序
    3|ABS_ASC 绝对值升序
    4|ABS_DESC 绝对值降序

## 筛选 V2 - BasicProperty / 取回字段

> 用于 `add_retrieve_basic(name)` 等取回方法。`add_retrieve_simple` / `add_retrieve_cumulative` / `add_retrieve_financial` 等其余取回字段共用上文 SimpleProperty / CumulativeProperty / FinancialProperty 等 ID。

* **`BasicProperty` 基础属性**

    name|含义|备注
    :-|:-|:-
    1101|CODE 股票代码|sval
    1102|NAME 股票名称|sval
    1103|INDUSTRY 所属行业|sval

> 单条返回结果按 `value_type` 字段分别填入 `sval(1)` / `ival(2)` / `aval(3)` / `dval(4)`。`enum_name` 在 ival 为枚举码时由 SDK 解码（如 K 线形态返回 `'DOUBLE_BOTTOMS'`）。

## 期权筛选 - OptUnderlyingIndicator

> 用于 [get_option_screen](./get-option-screen.md) 的 `add_underlying_filter(indicator_type, ...)` 与 `add_underlying_retrieve(indicator_type)`。

indicator_type|含义|备注
:-|:-|:-
101|STOCK_LIST 指定标的范围|values 直接传入证券代码字符串列表，如 ["US.AAPL", "HK.00700"]
103|PLATE 指定板块|**后台暂不支持，传入会报错**
106|INDEX_LIST 指定指数类型|
201|VOLUME 总成交量|
202|OPEN_INTEREST 总持仓量|
203|IV 标的隐含波动率|
204|HV 标的历史波动率|
205|IV_RANK|
206|IV_PERCENTILE|
207 / 208|IV_CHANGE / IV_CHANGE_RATIO|
209 / 210|IV_HV_RATIO / IV_HV_SPREAD|
401|MARKET_CAP 标的市值|
402|STOCK_PRICE 标的最新价|
403|CHANGE_RATIO 涨跌幅|

## 期权筛选 - OptIndicator

> 用于 `add_option_filter(indicator_type, ...)` 与 `add_option_retrieve(indicator_type)`。

indicator_type|含义|备注
:-|:-|:-
1001|STRIKE_PRICE 行权价|
1002|LEFT_DAY 距到期日天数|
1003|OPTION_TYPE 期权类型|1=CALL，2=PUT
1004|EXERCISE_TYPE 行权方式|1=美式，2=欧式
1005|EXPIRATION_TYPE 到期类型|1=周，2=月，3=季
1007|STRIKE_DATE_TIMESTAMP 到期日时间戳（秒）|
2001|IN_THE_MONEY|0=价外，1=价内
2002~2005|PRICE / MID_PRICE / BID_PRICE / ASK_PRICE|
2006~2009|BID_ASK_SPREAD / BID_VOLUME / ASK_VOLUME / BID_ASK_VOLUME_RATIO|
2010|CHANGE_RATIO 涨跌幅|
2011 / 2012|VOLUME / TURNOVER|
2013 / 2014|OPEN_INTEREST / OPEN_INTEREST_MARKET_CAP|
2018|VOL_OI_RATIO|
2021|PREMIUM 权利金|**仅 sort/retrieve，filter 不支持**
3001 / 3002 / 3003|IMPLIED_VOLATILITY / HISTORY_VOLATILITY / IV_HV_RATIO|
3004~3008|DELTA / GAMMA / VEGA / THETA / RHO|
3009 / 3010|LEVERAGE_RATIO / EFFECTIVE_GEARING|
3011 / 3012|BUY_TO_BEP / SELL_TO_BEP|
3013 / 3014|BUY_PROFIT_PROBABILITY / SELL_PROFIT_PROBABILITY|
3015~3018|INTRINSIC_VALUE_PER / TIME_VALUE_PER / ITM_DEGREE / OTM_DEGREE|
3019 / 3020|ITM_PROBABILITY / OTM_PROBABILITY|

## 窝轮筛选 V2 - WarrantField

> 用于 [get_warrant_screen](./get-warrant-screen.md) 的 `add_interval_filter(field_id, ...)` / `add_choice_filter(field_id, choices)` / `add_sort(field_id, desc)`。所有数值字段直接传原始值。

field_id|含义|筛选方式
:-|:-|:-
1|CODE 证券代码|choice（文本）
2|NAME 股票名称|choice（文本）
4|ISSUER_ID 发行商 ID|choice
5|STOCK_OWNER 正股 ID|choice（可传 "HK.00700"）
6|WARRANT_TYPE 窝轮类型|choice：1=认购，2=认沽，3=牛证，4=熊证，5=界内证
7|CONVERSION_RATIO 换股比率|interval
8|CURRENT_PRICE 当前价|interval
9|STREET_RATIO 街货占比|interval
10|VOLUME 成交量|interval
11|MATURITY_DATE 到期日（时间戳秒）|interval
12|STRIKE_PRICE 行使价|interval
13|PREMIUM 溢价|interval（可为负）
14|RECOVERY_PRICE 收回价|interval
15|IMPLIED_VOLATILITY 引伸波幅|interval
16|LEVERAGE_RATIO 杠杆比率|interval
17|PRICE_RECOVERY_RATIO 正股距收回价 %|interval
18|DELTA 对冲值|interval
19|STATUS 轮证状态|choice：0=正常，1=终止，2=待上市
20|IPO_TIME 上市时间（时间戳秒）|interval
21 / 22|BUY_VOL / SELL_VOL 买/卖量|interval
23|EFFECTIVE_LEVERAGE 有效杠杆|interval
24|LAST_CLOSE_PRICE 昨收价|interval
25|TURNOVER 成交额|interval
26 / 27|SELL_PRICE / BUY_PRICE|interval
28 / 29|HIGH_PRICE / LOW_PRICE|interval
30|RATIO_ITM_OTM 价内/价外|interval（可为负）
31|BREAK_EVEN_POINT 打和点|interval
32|AMPLITUDE 振幅|interval
33|SCORE_FAXING 法兴评分|interval
34|LAST_TRADE_DATE 最后交易日（时间戳秒）|interval
35|STREET_VOLUME 街货量|interval
36|LOT_SIZE 每手股数|interval
37|ISSUE_SIZE 发行量|interval
38|IPO_PRICE 发行价|interval
39 / 40|LOWER_STRIKE_PRICE / UPPER_STRIKE_PRICE|interval（界内证）
41|IW_PRICE_STATUS 界内/界外|choice
42|SENSITIVITY 敏感度|interval
43|CONVERSION_PRICE 换股价|interval
44 / 45|CHANGE_RATE / CHANGE_VALUE 涨跌幅/额|interval
51|SCORE 综合评分|interval
52|FILTER_NO_TRADE 过滤无成交窝轮|choice：0=否，1=是
53|CURRENCY_CODE 币种|choice
54|STOCK_OWNER_PRICE 正股价格|interval

## 窝轮筛选 V2 - WarrantMarket / WarrantType / WarrantStatus

> `WarrantScreenRequest(warrant_market=...)` 与 `add_choice_filter` 常用枚举。

* **`WarrantMarket` 市场**

    market|含义
    :-|:-
    1|HK 港股
    4|SG 新加坡
    15|MY 马来西亚

* **`WarrantType` 窝轮类型**（field_id=6 的 choice 取值）

    value|含义
    :-|:-
    1|CALL 认购
    2|PUT 认沽
    3|BULL 牛证
    4|BEAR 熊证
    5|INLINE 界内证

* **`WarrantStatus` 窝轮状态**（field_id=19 的 choice 取值）

    value|含义
    :-|:-
    0|NORMAL 正常
    1|SUSPEND 终止交易
    2|PRE_IPO 待上市


## 期权市场类型

> **OptionMarket**

* `UNKNOWN`

  未知

* `US_SECURITY`

  美股股票期权

* `US_INDEX`

  美股指数期权

* `HK_SECURITY`

  港股股票期权

* `HK_INDEX`

  港股指数期权

## 期权统计数据类型

> **OptionStatisticDataType**

* `UNKNOWN`

  未知

* `VOLUME`

  成交量

* `OPEN_INTEREST`

  持仓量

## 历史波动率时间范围

> **OptionHVTimeRange**

* `UNKNOWN`

  未知

* `THIRTY_DAY`

  30 日

* `SIXTY_DAY`

  60 日

* `NINETY_DAY`

  90 日

* `ONE_TWENTY_DAY`

  120 日

* `THREE_SIXTY_FIVE_DAY`

  365 日

## 期权合约排行类型

> **OptionRankType**

* `UNKNOWN`

  未知

* `VOLUME`

  成交量排行

* `TURNOVER`

  成交额排行

* `OI`

  持仓量排行

* `OI_INCREMENT`

  增仓量(日)排行

* `OI_DECREMENT`

  减仓量(日)排行

* `OI_MARKET_CAP`

  持仓额排行

* `OI_MARKET_CAP_INCREMENT`

  增仓额(日)排行

* `OI_MARKET_CAP_DECREMENT`

  减仓额(日)排行

* `CHANGE_RATE`

  涨跌幅排行

* `IV`

  隐含波动率排行

## 末日期权标的排序

> **ZeroDteSortType**

* `UNKNOWN`

  未知

* `VOLUME`

  期权成交量

* `IV`

  隐含波动率

* `CHANGE_RATE`

  涨跌幅

* `OPEN_INTEREST`

  持仓量

* `MARKET_CAP`

  市值

## 末日期权标的筛选因子

> **ZeroDteIndicatorType**

* `UNKNOWN`

  未知

* `OWNER_LIST`

  自选股列表

* `HAS_EARNINGS_THIS_WEEK`

  本周是否有财报(0=不限,1=有,2=无)

* `VOLUME`

  期权总成交量

* `OPEN_INTEREST`

  期权总持仓量

* `IV`

  隐含波动率(%)

* `HV`

  历史波动率(%)

* `IV_RANK`

  IV 等级(%)

* `IV_PERCENTILE`

  IV 百分位数(%)

* `PRICE`

  最新价

* `CHANGE_RATE`

  涨跌幅(%)

## 末日期权合约排序

> **ZeroDteContractSortType**

* `UNKNOWN`

  未知

* `VOLUME`

  成交量

* `OPEN_INTEREST`

  持仓量

* `IV`

  隐含波动率

* `DELTA`

  Delta

## 末日期权合约筛选因子

> **ZeroDteContractIndicatorType**

* `UNKNOWN`

  未知

* `OPTION_TYPE`

  期权方向(1=Call, 2=Put)

* `VOLUME`

  成交量

* `OPEN_INTEREST`

  未平仓数

* `IV`

  隐含波动率(%)

* `DELTA`

  Delta

* `GAMMA`

  Gamma

* `THETA`

  Theta

* `VEGA`

  Vega

* `RHO`

  Rho

* `PRICE`

  最新价

* `CHANGE_RATE`

  涨跌幅(%)

* `BREAK_EVEN_POINT`

  盈亏平衡点

* `TO_BEP`

  到盈亏平衡点(%)

* `BUY_PROFIT_PROBABILITY`

  买入盈利概率(%)

* `SELL_PROFIT_PROBABILITY`

  卖出盈利概率(%)

## 财报排序

> **EarningsSortType**

* `UNKNOWN`

  未知

* `EARNINGS_DATE`

  财报日期(默认)

* `VOLUME`

  期权成交量

* `IV`

  隐含波动率

* `MARKET_CAP`

  市值

* `CHANGE_RATIO`

  涨跌幅

* `PRICE`

  最新价

* `IV_RANK`

  IV 等级

* `IV_PERCENTILE`

  IV 百分位数

* `HV`

  历史波动率

* `OPEN_INTEREST`

  持仓量

* `LAST_REPORT_IV_CRUSH`

  上次 IV Crush

* `HISTORY_REPORT_IV_CRUSH`

  历史 IV Crush

* `LAST_REPORT_CHG_RATIO`

  上次财报日涨跌幅

* `HISTORY_REPORT_CHG_RATIO`

  历史财报日涨跌幅

* `ESTIMATE_EPS_YOY`

  预测 EPS 同比

* `ESTIMATE_REVENUE_YOY`

  预测营收同比

* `EXPECTED_MOVE_RATIO`

  预测波动

## 标的品类

> **StockCategory**

* `ALL`

  全部

* `EQUITY`

  股票

* `ETF`

  ETF

## 财报发布类型

> **EarningsPubType**

* `UNKNOWN`

  未知

* `BEFORE`

  盘前

* `AFTER`

  盘后

## 财报机会筛选因子

> **EarningsIndicatorType**

* `UNKNOWN`

  未知

* `OWNER_LIST`

  自选股列表

* `INDEX_COMPONENT`

  所属指数

* `PLATE`

  所属行业/板块

* `MARKET_CAP`

  市值

* `EXPIRATION_TYPE`

  到期类型

* `IV`

  隐含波动率(%)

* `LAST_REPORT_IV_CRUSH`

  上次 IV Crush(%)

* `HISTORY_REPORT_IV_CRUSH`

  历史 IV Crush(%)

* `IV_RANK`

  IV 等级(%)

* `IV_PERCENTILE`

  IV 百分位数(%)

* `VOLUME`

  期权成交量

* `OPEN_INTEREST`

  期权持仓量

* `PRICE`

  最新价

* `CHANGE_RATIO`

  涨跌幅(%)

* `EXPECTED_MOVE_RATIO`

  预测波动(%)

* `LAST_REPORT_CHG_RATIO`

  上次财报日涨跌幅(%)

* `HISTORY_REPORT_CHG_RATIO`

  历史财报日涨跌幅(%)

* `ESTIMATE_REVENUE_YOY`

  预测营收同比(%)

* `ESTIMATE_EPS_YOY`

  预测 EPS 同比(%)

* `EARNINGS_DAY_RANGE`

  距财报日天数

## 卖方策略类型

> **SellerType**

* `UNKNOWN`

  未知

* `COVERED_CALL`

  股票担保看涨期权 (Covered Call)

* `CASH_SECURED_PUT`

  现金担保看跌期权 (Cash Secured Put)

## 卖方专区排序

> **SellerSortType**

* `UNKNOWN`

  未知

* `ANNUALIZED_RETURN`

  年化收益率(默认)

* `INTERVAL_RETURN`

  区间收益率

* `ITM_PROBABILITY`

  行权概率

* `PREMIUM`

  权利金

## 卖方专区筛选因子

> **SellerIndicatorType**

* `UNKNOWN`

  未知

* `OWNER_LIST`

  自选股列表

* `STOCK_CATEGORY`

  标的品类

* `VOLUME`

  期权总成交量

* `OPEN_INTEREST`

  期权总持仓量

* `IV`

  标的 IV(%)

* `HV`

  标的 HV(%)

* `IV_RANK`

  IV 等级(%)

* `IV_PERCENTILE`

  IV 百分位数(%)

* `MARKET_CAP`

  标的市值

* `PRICE`

  标的最新价

* `CHANGE_RATE`

  标的涨跌幅(%)

* `PLATE`

  板块

* `EXPIRATION_TYPE`

  到期类型

* `LEFT_DAYS`

  距到期日(天)

* `OPTION_TYPE`

  期权方向(1=Call, 2=Put)

* `OPTION_EXPIRATION_TYPE`

  期权到期类型

* `STRIKE_DATE_TIMESTAMP`

  到期日时间戳(秒)

* `PREMIUM`

  权利金

* `ANNUALIZED_RETURN`

  年化收益率(%)

* `INTERVAL_RETURN`

  区间收益率(%)

* `OTM_DEGREE`

  价外程度(%)

* `OTM_PROBABILITY`

  价外概率(%)

* `OPTION_IV`

  期权隐含波动率(%)

* `BID_PRICE`

  期权买价

* `ASK_PRICE`

  期权卖价

* `OPTION_VOLUME`

  期权成交量

* `OPTION_OPEN_INTEREST`

  期权持仓量

## 标的排行排序

> **UnderlyingRankSortType**

* `UNKNOWN`

  未知

* `VOLUME`

  总成交量

* `VOLUME_RATIO`

  Put/Call 成交量比值

* `OPEN_INTEREST`

  总持仓量

* `OPEN_INTEREST_RATIO`

  Put/Call 持仓量比值

* `PRICE`

  最新价

* `PRICE_CHANGE`

  涨跌幅

* `IV`

  IV

* `IV_CHANGE`

  IV 变化率

* `HV`

  HV

* `HV_CHANGE`

  HV 变化率

* `IV_RANK`

  IV Rank

* `IV_PERCENTILE`

  IV Percentile

* `MARKET_CAP`

  市值

## 标的排行筛选因子

> **UnderlyingRankIndicatorType**

* `UNKNOWN`

  未知

* `OWNER_LIST`

  指定标的列表

* `STOCK_CATEGORY`

  标的品类

* `VOLUME`

  总成交量

* `OPEN_INTEREST`

  总持仓量

* `IV`

  IV(%)

* `HV`

  HV(%)

* `IV_RANK`

  IV Rank(%)

* `IV_PERCENTILE`

  IV Percentile(%)

* `IV_CHANGE`

  IV 变化率(%)

* `HV_CHANGE`

  HV 变化率(%)

* `VOLUME_RATIO`

  成交量 P/C 比值(%)

* `OI_RATIO`

  持仓量 P/C 比值(%)

* `MARKET_CAP`

  市值

* `PRICE`

  最新价

* `CHANGE_RATE`

  涨跌幅(%)

## 期权合约排行筛选因子

> **OptionRankIndicatorType**

* `UNKNOWN`

  未知

* `STOCK_CATEGORY`

  品类

* `MARKET_CAP`

  市值

* `OWNER_LIST`

  股票范围

* `UNDERLYING_IV`

  正股 IV(%)

* `UNDERLYING_HV`

  正股 HV(%)

* `IV_RANK`

  IV 等级(%)

* `IV_PERCENTILE`

  IV 百分位数(%)

* `IV`

  隐含波动率(%)

* `OPTION_TYPE`

  方向(Call/Put)

* `LEFT_DAYS`

  距到期日

* `IN_THE_MONEY`

  价内/价外(0=价外, 1=价内)

* `VOLUME`

  成交量

* `OPEN_INTEREST`

  持仓量

* `DELTA`

  Delta

* `GAMMA`

  Gamma

* `THETA`

  Theta

* `VEGA`

  Vega

* `RHO`

  Rho

## 到期类型

> **ExpirationType**

* `UNKNOWN`

  未知

* `MONTHLY`

  月期权

* `WEEKLY`

  周期权

* `END_OF_MONTH`

  月末期权

* `QUARTERLY`

  季度期权

## 指数成分类型

> **IndexComponentType**

* `UNKNOWN`

  未知

* `DJI`

  道琼斯指数

* `IXIC`

  纳斯达克指数

* `NDX`

  纳斯达克 100 指数

* `SPX`

  标普 500 指数

## 期权异动成交方向

> **EventTickerType**

* `UNKNOWN`

  未知

* `BUY`

  主动买入

* `SELL`

  主动卖出

* `NEUTRAL`

  中性盘

## 期权异动订单类型

> **AlertOrderType**

* `NORMAL`

  普通订单

* `SWEEP`

  扫单

* `CROSS`

  对敲单

* `FLOOR`

  场内单

## 策略类型

> **TickerStrategy**

* `UNKNOWN`

  未知

* `SINGLE_LEG`

  单腿交易

* `MULTI_LEG`

  多腿策略交易

## 市场情绪

> **MarketSentiment**

* `UNKNOWN`

  未知

* `BEARISH`

  看空

* `BULLISH`

  看多

* `NEUTRAL`

  中性

## 公司行动类型

> **CorporateActionType**

* `NONE`

  无/未知

* `SPLIT`

  拆股

* `JOIN`

  合股

* `BONUS_STOCK`

  送股

* `INTO_SHARES`

  转增股

* `ALLOT`

  配股

* `ADD`

  增发股

* `DIVIDEND`

  普通派息

* `SPECIAL_DIVIDEND`

  特别派息

* `SPIN_OFF`

  公司分立

## 价内价外类型

> **InTheMoneyType**

* `UNKNOWN`

  未知

* `IN`

  价内 (ITM)

* `OUT`

  价外 (OTM)

## 异动筛选因子类型

> **EventIndicatorType**

* `OWNER_LIST`

  指定标的列表（security_list）

* `INDUSTRY_PLATE`

  行业板块列表（security_list）

* `CONCEPT_PLATE`

  概念板块列表（security_list）

* `CORPORATE_ACTION`

  公司行动类型（value_list, CorporateActionType）

* `MARKET_CAP`

  标的市值（范围）

* `OPTION_TYPE`

  CALL(1)/PUT(2)（value_list）

* `MONEY_TYPE`

  价内(1)/价外(2)（value_list）

* `STRIKE_PRICE`

  行权价（范围）

* `EXPIRY_DAYS`

  距到期天数（范围）

* `OTM`

  价外比率(%)（范围）

* `TICKER_TYPE`

  成交方向（value_list, EventTickerType）

* `VOLUME`

  成交量（范围）

* `TURNOVER`

  成交额（范围）

* `PRICE`

  成交价（范围）

* `TIME`

  异动时间（范围，Unix 秒）

* `MAX_DAY_NUM`

  时间范围天数（value_list，0=当天, 1=近2天 ...）

* `ORDER_TYPE`

  订单类型（value_list, AlertOrderType）

* `STRATEGY`

  策略类型（value_list, TickerStrategy）

* `SENTIMENT`

  市场情绪（value_list, MarketSentiment）

* `TOTAL_VOLUME`

  期权总成交量（范围）

* `TOTAL_OI`

  期权总持仓量（范围）

* `VO_RATIO`

  量仓比(%)（范围）

* `IV`

  隐含波动率(%)（范围）

* `DELTA`

  Delta（范围）

* `GAMMA`

  Gamma（范围）

* `VEGA`

  Vega（范围）

* `THETA`

  Theta（范围）

* `RHO`

  Rho（范围）

## 告警操作类型

> **AlertOpType**

* `UNKNOWN`

  未知

* `ADD`

  新增

* `DELETE`

  删除

* `MODIFY`

  修改

* `ENABLE`

  启用

* `DISABLE`

  禁用

* `DELETE_ALL`

  删除全部

---

# 交易接口总览

<table>
    <tr>
        <th>模块</th>
        <th>接口名</th>
        <th>功能简介</th>
    </tr>
    <tr>
        <td rowspan="2">账户</td>
	    <td><a href="../trade/get-acc-list.html">Get Account List</a></td>
	    <td>获取交易业务账户列表</td>
    </tr>
    <tr>
	    <td><a href="../trade/unlock.html">Unlock Trading</a></td>
	    <td>解锁交易</td>
    </tr>
    <tr>
        <td rowspan="6">资产持仓</td>
	    <td><a href="../trade/get-funds.html">Get Account Financial Information</a></td>
	    <td>获取账户资金数据</td>
    </tr>
    <tr>
	    <td><a href="../trade/get-max-trd-qtys.html">Get Maximum Tradable Quantity</a></td>
	    <td>查询账户最大可买卖数量</td>
    </tr>
    <tr>
	    <td><a href="../trade/comboorder-tradinginfo-query.html">comboorder_tradinginfo_query</a></td>
	    <td>查询组合可交易信息</td>
    </tr>
    <tr>
	    <td><a href="../trade/get-position-list.html">Get Positions List</a></td>
	    <td>获取持仓列表</td>
    </tr>
    <tr>
	    <td><a href="../trade/get-margin-ratio.html">Get Margin Trading Data</a></td>
	    <td>获取融资融券数据</td>
    </tr>
    <tr>
        <td><a href="../trade/get-acc-cash-flow.html">Get Cash Flow Summary</a></td>
	    <td>查询账户资金流水 (最低版本要求：9.1.5108)</td>
    </tr>
    <tr>
        <td rowspan="8">订单</td>
	    <td><a href="../trade/place-order.html">Place Order</a></td>
	    <td>下单</td>
    </tr>
    <tr>
	    <td><a href="../trade/place-combo-order.html">place_combo_order</a></td>
	    <td>组合下单</td>
    </tr>
    <tr>
	    <td><a href="../trade/modify-order.html">Modify or Cancel Order</a></td>
	    <td>改单撤单</td>
    </tr>
    <tr>
	    <td><a href="../trade/get-order-list.html">Get Order list</a></td>
	    <td>查询未完成订单</td>
    </tr>
	<tr>
	    <td><a href="../trade/order-fee-query.html">Get Order Fees</a></td>
	    <td>查询订单费用 (最低版本要求：8.2.4218)</td>
    </tr>
    <tr>
	    <td><a href="../trade/get-history-order-list.html">Get Historical Order List</a></td>
	    <td>查询历史订单</td>
    </tr>
    <tr>
	    <td><a href="../trade/update-order.html">Order Callback</a></td>
	    <td>订单回调</td>
    </tr>
    <tr>
	    <td><a href="../trade/sub-acc-push.html">Trade Data Callback</a></td>
	    <td>订阅交易推送</td>
    </tr>
    <tr>
        <td rowspan="3">成交</td>
	    <td><a href="../trade/get-order-fill-list.html">Get Today's Executed Trades</a></td>
	    <td>查询当日成交</td>
    </tr>
    <tr>
	    <td><a href="../trade/get-history-order-fill-list.html">Get Historical Executed Trades</a></td>
	    <td>查询历史成交</td>
    </tr>
    <tr>
	    <td><a href="../trade/update-order-fill.html">Trade Execution Callback</a></td>
	    <td>成交回调</td>
    </tr>
</table>

---

# 交易对象

## 创建连接

`OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, is_encrypt=None, security_firm=SecurityFirm.NONE)`  
  
`OpenFutureTradeContext(host='127.0.0.1', port=11111, is_encrypt=None, security_firm=SecurityFirm.NONE)` 

`OpenCryptoTradeContext(host='127.0.0.1', port=11111, is_encrypt=None, security_firm=SecurityFirm.NONE)` 


* **介绍**

    根据交易品类，选择账户，并创建对应的交易对象。
    实例|账户
    :-|:-
    OpenSecTradeContext|证券账户  (股票、ETFs、窝轮牛熊、股票及指数的期权使用此账户)
    OpenFutureTradeContext|期货账户   (期货、期货期权使用此账户)
    OpenCryptoTradeContext|加密货币账户  (- 加密货币现货交易使用此账户
  - 仅支持 FUTUSECURITIES、FUTUINC、FUTUSG 三家券商
  - 不支持模拟交易)

* **参数**
    参数|类型|说明
    :-|:-|:-
    filter_trdmarket|[TrdMarket](./trade.html#719)|筛选对应交易市场权限的账户  (- 此参数仅对 OpenSecTradeContext 适用
  - 此参数仅用于筛选账户，不影响交易连接)
    host|str|OpenD 监听的 IP 地址
    port|int|OpenD 监听的 IP 端口
    is_encrypt|bool|是否启用加密  (默认 None 表示：使用 [enable_proto_encrypt](../ftapi/init.md#319) 的设置)
    security_firm|[SecurityFirm](./trade.md#572)|所属券商  (OpenCryptoTradeContext 仅支持 FUTUSECURITIES、FUTUINC、FUTUSG)

* **Example**

```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, is_encrypt=None, security_firm=SecurityFirm.NONE)
trd_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

```python
from futu import *
future_ctx = OpenFutureTradeContext(host='127.0.0.1', port=11111, security_firm=SecurityFirm.NONE)
future_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

```python
from futu import *
crypto_ctx = OpenCryptoTradeContext(host='127.0.0.1', port=11111, security_firm=SecurityFirm.NONE)
crypto_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```


## 关闭连接

`close()`  

* **介绍**

    关闭交易对象。默认情况下，Futu API 内部创建的线程会阻止进程退出，只有当所有 Context 都 close 后，进程才能正常退出。但通过 [set_all_thread_daemon](../ftapi/init.md#4570) 可以设置所有内部线程为 daemon 线程，这时即使没有调用 Context 的 close，进程也可以正常退出。

* **Example**

```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111)
trd_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽
```

---

# 获取交易业务账户列表

`get_acc_list()`

* **介绍**

    获取交易业务账户列表。  
    要调用其他交易接口前，请先获取此列表，确认要操作的交易业务账户无误。

* **参数**
    


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时，返回交易业务账户列表</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 交易业务账户列表格式如下：
        字段|类型|说明
        :-|:-|:-
        acc_id|int|交易业务账户
        trd_env|[TrdEnv](./trade.md#6374)|交易环境
        acc_type|[TrdAccType](./trade.md#3974)|账户类型
        uni_card_num|str|综合账户卡号，同移动端内的展示
        card_num|str|业务账户卡号  (综合账户下包含一个或多个业务账户（综合证券账户、综合期货账户等等），与交易品种有关)
        security_firm|[SecurityFirm](./trade.md#572)|所属券商
        sim_acc_type|[SimAccType](./trade.md#6449)|模拟账户类型  (仅模拟账户适用) 
        trdmarket_auth|list|交易市场权限  (list 中元素类型是 [TrdMarket](./trade.html#719)) 
        acc_status|[TrdAccStatus](./trade.md#121)|账户状态
        acc_role|[TrdAccRole](./trade.md#6395)|账户结构  (用于区分主子账户结构
  - MASTER: 主账户
  - NORMAL: 普通账户
  - IPO: 马来西亚 IPO 账户)
        jp_acc_type|list|日本账户类型  (list 中元素类型是[SubAccType](./trade.md#6112)，仅对日本券商生效)


* **说明**

    获取港股模拟交易账户，需要指定 filter_trdmarket 为 TrdMarket.HK，此时会返回2个模拟交易账号。其中 sim_acc_type = STOCK 为港股模拟账户，sim_acc_type = OPTION 为港股期权模拟账户，sim_acc_type = FUTURES 为港股期货模拟账户。   
    获取美股模拟交易账户，需要指定 filter_trdmarket 为 TrdMarket.US，sim_acc_type = STOCK_AND_OPTION 代表美股融资融券模拟账户，可以模拟交易股票和期权。sim_acc_type = FUTURES 为美国期货模拟账户。  

* **Example**

```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.get_acc_list()
if ret == RET_OK:
    print(data)
    print(data['acc_id'][0])  # 取第一个账号
    print(data['acc_id'].values.tolist())  # 转为 list
else:
    print('get_acc_list error: ', data)
trd_ctx.close()
```

* **Output**

```python
               acc_id   trd_env acc_type       uni_card_num           card_num    security_firm   sim_acc_type                           trdmarket_auth    acc_status    acc_role    jp_acc_type
0  281756479345015383      REAL   MARGIN   1001289516908051   1001329805025007   FUTUSECURITIES            N/A    [HK, US, HKCC, SG, HKFUND, USFUND, JP]       ACTIVE      NORMAL             []
1             8377516  SIMULATE     CASH                N/A                N/A              N/A          STOCK                                      [HK]       ACTIVE         N/A             []
2            10741586  SIMULATE   MARGIN                N/A                N/A              N/A         OPTION                                      [HK]       ACTIVE         N/A             []
3  281756455983234027      REAL   MARGIN                N/A   1001100321720699   FUTUSECURITIES            N/A                                      [HK]     DISABLED      NORMAL             []
281756479345015383
[281756479345015383, 8377516, 10741586, 281756455983234027]
```

---

# 解锁交易

`unlock_trade(password=None, password_md5=None, is_unlock=True)`

* **介绍**

    解锁或锁定交易

* **参数**
    
    参数|类型|说明
    :-|:-|:-
    password|str|交易密码  (如果 password_md5 不为空，就使用传入的 password_md5 解锁；否则使用 password 转 MD5 得到 password_md5 再解锁)
    password_md5|str|交易密码的 32 位 MD5 加密（全小写） (解锁交易必须要填密码，锁定交易忽略)
    is_unlock|bool|解锁或锁定  (True：解锁False：锁定)


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">msg</td>
            <td>NoneType</td>
            <td>当 ret == RET_OK 时，返回 None</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

        

* **Example**

```python
from futu import *
pwd_unlock = '123456'
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.unlock_trade(pwd_unlock)
if ret == RET_OK:
    print('unlock success!')
else:
    print('unlock_trade failed: ', data)
trd_ctx.close()
```

* **Output**

```python
unlock success!
```

:::tip 提示
* 真实账户调用 [下单](../trade/place-order.md) 或 [改单撤单](../trade/modify-order.md) 接口，需要先解锁交易；模拟账户无需解锁。
* 解锁或锁定交易针是对 OpenD 的操作，只要有一个连接解锁，其他连接都可以调用交易接口。
* 强烈建议，通过外网连接 OpenD 进行实盘交易的客户，使用加密通道，参见 [启用协议加密](../ftapi/init.md#319)。
* 命令行API 不支持富途令牌，如果开通了富途令牌，则会解锁失败，需要关闭令牌功能后再使用 命令行API 解锁。
:::

:::tip 接口限制
* 单用户ID 每 30 秒内最多请求 10 次解锁交易接口
:::

---

# 查询账户资金

`accinfo_query(trd_env=TrdEnv.REAL, acc_id=0, acc_index=0, refresh_cache=False, currency=Currency.HKD, asset_category=AssetCategory.NONE)`

* **介绍**

    查询交易业务账户的资产净值、证券市值、现金、购买力等资金数据。

* **参数**
    参数|类型|说明
    :-|:-|:-
    trd_env|[TrdEnv](./trade.md#6374)|交易环境
    acc_id|int|交易业务账户 ID  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。
  - 当 acc_id 传 0 时， 以 acc_index 指定的账户为准
  - 当 acc_id 传 ID 号时（不为 0 ），以 acc_id 指定的账户为准)
    acc_index|int|交易业务账户列表中的账户序号  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。acc_index 会在新开立/注销账户时发生变动，导致您指定的账户与实际交易账户不一致。
  - acc_index 默认为 0，表示指定第 1 个交易业务账户)
    refresh_cache|bool|是否刷新缓存  (- True：立即向富途服务器重新请求数据，不使用 OpenD 的缓存，此时会受到接口限频的限制
  - False：使用 OpenD 的缓存（特殊情况导致缓存没有及时更新才需要刷新）)
    currency|[Currency](./trade.md#8019)|计价货币  (- 仅期货账户、综合证券账户适用，其它账户类型会忽略此参数
  - 返回的 DataFrame 中，除了明确指明了货币的字段，其它资金相关字段都以此参数换算)
    asset_category|[AssetCategory](./trade.md#4752)|资产类别  (仅对日本券商生效)


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时，返回资金数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 资金数据格式如下：
        字段|类型|说明
        :-|:-|:-
        power|float|最大购买力  (- 此字段是按照 50% 的融资初始保证金率计算得到的 **近似值**。但事实上，每个标的的融资初始保证金率并不相同。我们建议您使用 [查询最大可买可卖](./get-max-trd-qtys.md) 接口返回的 **最大可买** 字段，来判断实际可买入的最大数量。)
        max_power_short|float|卖空购买力  (- 此字段是按照 60% 的融券保证金率计算得到的 **近似值**。但事实上，每个标的的融券保证金率并不相同。我们建议您使用 [查询最大可买可卖](./get-max-trd-qtys.md) 接口返回的 **可卖空** 字段，来判断实际可卖空的最大数量。)
        net_cash_power|float|现金购买力 (已废弃，请使用usd_net_cash_power等字段获取分币种的现金购买力)
        total_assets|float|总资产净值 (总资产净值 = 证券资产净值 + 基金资产净值 + 债券资产净值) 
        securities_assets|float|证券资产净值 (最低 OpenD 版本要求：8.2.4218) 
        fund_assets|float|基金资产净值 (- 综合账户返回结果为总基金资产净值，暂时不支持查询港元基金资产和美元基金资产
  - 最低 OpenD 版本要求：8.2.4218)
        bond_assets|float|债券资产净值 (最低 OpenD 版本要求：8.2.4218) 
        cash|float|现金 (已废弃，请使用us_cash等字段获取分币种的现金)
        market_val|float|证券市值  (仅证券账户适用)
        long_mv|float|多头市值  
        short_mv|float|空头市值  
        pending_asset|float|在途资产  
        interest_charged_amount|float|计息金额 
        frozen_cash|float|冻结资金
        avl_withdrawal_cash|float|现金可提  (仅证券账户适用)
        max_withdrawal|float|最大可提  (仅富途证券（香港）的证券账户适用) 
        currency|[Currency](./trade.md#8019)|计价货币  (仅综合证券账户、期货账户适用)
        available_funds|float|可用资金  (仅期货账户适用)
        unrealized_pl|float|未实现盈亏  (仅期货账户适用)
        realized_pl|float|已实现盈亏  (仅期货账户适用)
        risk_level|[CltRiskLevel](./trade.md#9239)|风控状态  (仅期货账户适用。建议统一使用 exposure_level 字段获取证券、期货账户的风险状态)
        risk_status|[CltRiskStatus](./trade.md#3989)|风险状态  (- 证券账户和期货账户均适用
  - 共分 9 个等级， `LEVEL1`是最安全，`LEVEL9`是最危险)
        initial_margin|float|初始保证金 
        margin_call_margin|float|Margin Call 保证金 
        maintenance_margin|float|维持保证金 
        hk_cash|float|港元现金  (此字段表示该币种实际的值，而不是以该币种计价的值)
        hk_avl_withdrawal_cash|float|港元可提  (此字段表示该币种实际的值，而不是以该币种计价的值)
        hkd_net_cash_power|float|港元现金购买力  (- 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：8.7)
        hkd_assets|float|港股资产净值  (- 仅综合证券账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：9.0.5008)
        us_cash|float|美元现金  (此字段表示该币种实际的值，而不是以该币种计价的值)
        us_avl_withdrawal_cash|float|美元可提  (此字段表示该币种实际的值，而不是以该币种计价的值)
        usd_net_cash_power|float|美元现金购买力  (- 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：8.7)
        usd_assets|float|美股资产净值  (- 仅综合证券账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：9.0.5008)
        cn_cash|float|人民币现金  (此字段表示该币种实际的值，而不是以该币种计价的值)
        cn_avl_withdrawal_cash|float|人民币可提  (此字段表示该币种实际的值，而不是以该币种计价的值)
        cnh_net_cash_power|float|人民币现金购买力  (- 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：8.7)
        cnh_assets|float|A股资产净值  (- 仅综合证券账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：9.0.5008)
        jp_cash|float|日元现金  (- 仅期货账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低 Futu API 版本要求：5.8.2008)
        jp_avl_withdrawal_cash|float|日元可提  (- 仅期货账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低 Futu API 版本要求：5.8.2008)
        jpy_net_cash_power|float|日元现金购买力  (- 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：8.7)
        jpy_assets|float|日股资产净值  (- 仅综合证券账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：9.0.5008)
        sg_cash|float|新元现金  (- 仅期货账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值)
        sg_avl_withdrawal_cash|float|新元可提  (- 仅期货账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值)
        sgd_net_cash_power|float|新元现金购买力  (- 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：8.7)
        sgd_assets|float|新股资产净值  (- 仅综合证券账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：9.0.5008)
        au_cash|float|澳元现金  (- 仅综合证券账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低 Futu API 版本要求：5.8.2008)
        au_avl_withdrawal_cash|float|澳元可提  (- 仅综合证券账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低 Futu API 版本要求：5.8.2008)
        aud_net_cash_power|float|澳元现金购买力  (- 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：8.7)
        aud_assets|float|澳股资产净值  (- 仅综合证券账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：9.0.5008)
        ca_cash|float|加元现金  (- 仅综合证券账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：10.0.6008)
        ca_avl_withdrawal_cash|float|加元可提  (- 仅综合证券账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：10.0.6008)
        cad_net_cash_power|float|加元现金购买力  (- 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：10.0.6008)
        cad_assets|float|加元资产净值  (- 仅综合证券账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：10.0.6008)
        my_cash|float|令吉现金  (- 仅综合证券账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：10.0.6008)
        my_avl_withdrawal_cash|float|令吉可提  (- 仅综合证券账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：10.0.6008)
        myr_net_cash_power|float|令吉现金购买力  (- 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：10.0.6008)
        myr_assets|float|令吉资产净值  (- 仅综合证券账户适用
  - 此字段表示该币种实际的值，而不是以该币种计价的值
  - 最低版本要求：10.0.6008)
        is_pdt|bool|是否为 PDT 账户  (True：是 PDT 账户，False：不是 PDT 账户仅moomoo证券(美国)账户适用最低 OpenD 版本要求：5.8.2008)
        pdt_seq|string|剩余日内交易次数  (仅moomoo证券(美国)账户适用最低 OpenD 版本要求：5.8.2008)   
        beginning_dtbp|float|初始日内交易购买力  (仅被标记为 PDT 的moomoo证券(美国)账户适用最低 OpenD 版本要求：5.8.2008)
        remaining_dtbp|float|剩余日内交易购买力  (仅被标记为 PDT 的moomoo证券(美国)账户适用最低 OpenD 版本要求：5.8.2008)
        dt_call_amount|float|日内交易待缴金额  (仅被标记为 PDT 的moomoo证券(美国)账户适用最低 OpenD 版本要求：5.8.2008)
        dt_status|[DtStatus](./trade.html#1860)|日内交易限制情况  (仅被标记为 PDT 的moomoo证券(美国)账户适用最低 OpenD 版本要求：5.8.2008)
        crypto_mv|float|加密货币市值
        exposure_level|[ExposureLevel](./trade.md#7809)|持仓限额状态  (加密货币账户返回持仓限额状态证券/期货账户返回风控状态)
        exposure_limit|float|持仓限额（单位 USD）  (仅加密货币账户返回)
        used_limit|float|已用持仓限额（单位 USD）  (仅加密货币账户返回)
        remaining_limit|float|剩余持仓限额（单位 USD）  (仅加密货币账户返回)

        
* **Example**

```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.accinfo_query()
if ret == RET_OK:
    print(data)
    print(data['power'][0])  # 取第一行的购买力
    print(data['power'].values.tolist())  # 转为 list
else:
    print('accinfo_query error: ', data)
trd_ctx.close()  # 关闭当条连接
```

* **Output**

 ```python
power  max_power_short  net_cash_power  total_assets  securities_assets  fund_assets  bond_assets   cash   market_val      long_mv   short_mv  pending_asset  interest_charged_amount  frozen_cash  avl_withdrawal_cash  max_withdrawal currency available_funds unrealized_pl realized_pl risk_level risk_status  initial_margin  margin_call_margin  maintenance_margin  hk_cash  hk_avl_withdrawal_cash  hkd_net_cash_power  hkd_assets  us_cash  us_avl_withdrawal_cash  usd_net_cash_power  usd_assets  cn_cash  cn_avl_withdrawal_cash  cnh_net_cash_power  cnh_assets  jp_cash  jp_avl_withdrawal_cash  jpy_net_cash_power jpy_assets  sg_cash sg_avl_withdrawal_cash sgd_net_cash_power sgd_assets  au_cash au_avl_withdrawal_cash aud_net_cash_power aud_assets  ca_cash ca_avl_withdrawal_cash cad_net_cash_power cad_assets  my_cash my_avl_withdrawal_cash myr_net_cash_power myr_assets  is_pdt pdt_seq beginning_dtbp remaining_dtbp dt_call_amount dt_status
0  465453.903307    465453.903307             0.0   289932.0404        197028.2204     92903.82          0.0  25.18  197003.0448  211960.7568 -14957.712            0.0                      0.0    25.930845                  0.0             0.0      HKD             N/A           N/A         N/A        N/A      LEVEL3   219346.648525       288656.787955       181250.967601      0.0                     0.0          13225.7955     0.0   3.24                     0.0           9656.4365      0.0    0.0                     0.0                 0.0    0.0      0.0                     0.0                 0.0     0.0    N/A                    N/A                N/A     0.0    N/A                    N/A                N/A    0.0    N/A                    N/A                N/A    0.0    N/A                    N/A                N/A    0.0        N/A     N/A            N/A            N/A            N/A       N/A
465453.903307
[465453.903307]
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 10 次查询账户资金接口
* 调用此接口，只有在刷新缓存时，才受到限频限制
:::

---

# 查询最大可买可卖

`acctradinginfo_query(order_type, code, price, order_id=None, adjust_limit=0, trd_env=TrdEnv.REAL, acc_id=0, acc_index=0, session=Session.NONE, jp_acc_type=SubAccType.JP_GENERAL, position_id=NONE)`

* **介绍**

    查询指定交易业务账户下的最大可买卖数量，亦可查询指定交易业务账户下指定订单的最大可改成的数量。

    现金账户请求期权不适用。

* **参数**
    参数|类型|说明
    :-|:-|:-
    order_type|[OrderType](./trade.md#4181)|订单类型
    code|str|证券代码  (如果是期货交易，且 code 为期货主连代码，则会自动转为对应的实际合约代码)
    price|float|报价  (证券账户精确到小数点后 3 位，超出部分会被舍弃期货账户精确到小数点后 9 位，超出部分会被舍弃)
    order_id|str|订单号  (- 默认传 None，查询的是新下单的最大可买可卖数量
  - 如果是改单则要传订单号，此时计算最大可买可卖时，会返回此订单可改成的最大数量
  - 如果通过此参数，查询某笔订单最大可改成的数量，需要在下单之后，间隔 0.5 秒以上再调用此接口)
    adjust_limit|float|价格微调幅度  (OpenD 会对传入价格自动调整到合法价位上（期货会忽略此参数）
  - 正数代表向上调整，负数代表向下调整
  - 例如：0.015 代表向上调整且幅度不超过 1.5%；-0.01 代表向下调整且幅度不超过 1%。默认 0 表示不调整)
    trd_env|[TrdEnv](./trade.md#6374)|交易环境
    acc_id|int|交易业务账户 ID  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。
  - 当 acc_id 传 0 时， 以 acc_index 指定的账户为准
  - 当 acc_id 传 ID 号时（不为 0 ），以 acc_id 指定的账户为准)
    acc_index|int|交易业务账户列表中的账户序号  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。acc_index 会在新开立/注销账户时发生变动，导致您指定的账户与实际交易账户不一致。
  - acc_index 默认为 0，表示指定第 1 个交易业务账户)
    session|[Session](../quote/quote.md#9152)|美股交易时段  (仅对美股生效，支持传入RTH、ETH、OVERNIGHT、ALL)
    jp_acc_type|[SubAccType](./trade.md#6112)|日本账户类型  (仅日本券商适用)
    position_id|int|持仓ID  (- 适用于日本衍生品账户查询持仓可卖和平仓需买回
  - 可通过[查询持仓](./get-position-list.md)接口获取)
    


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时，返回账号列表</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 账号列表格式如下：
        字段|类型|说明
        :-|:-|:-
        max_cash_buy|float|现金可买  (-  期权的单位是“张”
  - 期货账户不适用)
        max_cash_and_margin_buy|float|最大可买  (-  期权的单位是“张”
  - 期货账户不适用)
        max_position_sell|float|持仓可卖  (期权的单位是"张")
        max_sell_short|float|可卖空  (-  期权的单位是“张”
  - 期货账户不适用)
        max_buy_back|float|平仓需买入  (- 当持有净空仓时，必须先买回空头持仓的股数，才能再继续买多
  -  期货、期权的单位是“张”)
        long_required_im|float|买 1 张合约所带来的初始保证金变动  (-  当前仅期货和期权适用。
  - 无持仓时，返回 **买入** 1 张的初始保证金占用（正数）。 
  - 有多仓时，返回 **买入** 1 张的初始保证金占用（正数）。
  - 有空仓时，返回 **买回** 1 张的初始保证金释放（负数）。)
        short_required_im|float|卖 1 张合约所带来的初始保证金变动  (-  当前仅期货和期权适用。
  - 无持仓时，返回 **卖空** 1 张的初始保证金占用（正数）。 
  - 有多仓时，返回 **卖出** 1 张的初始保证金释放（负数）。
  -  有空仓时，返回 **卖空** 1 张的初始保证金释放（正数）。)
        session|[Session](../quote/quote.md#9152)|交易订单时段（仅用于美股）

* **Example**

```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.acctradinginfo_query(order_type=OrderType.NORMAL, code='HK.00700', price=400)
if ret == RET_OK:
    print(data)
    print(data['max_cash_and_margin_buy'][0])  # 最大融资可买数量
else:
    print('acctradinginfo_query error: ', data)
trd_ctx.close()  # 关闭当条连接
```

* **Output**

```python
    max_cash_buy  max_cash_and_margin_buy  max_position_sell  max_sell_short  max_buy_back long_required_im short_required_im    session
0           0.0                   1500.0                0.0             0.0           0.0              N/A               N/A             N/A
1500.0
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 10 次查询最大可买可卖接口
:::

:::tip 提示
* 现金业务账户不支持交易衍生品，因此不支持通过现金业务账户查询期权的最大可买可卖。
* 加密货币仅支持现金账户，因此不支持查询加密货币账户的融资融券购买力。
* 期货的最大可买，需自行计算，公式：floor(最大购买力/买 1 张合约所带来的初始保证金变动)。其中，最大购买力来自[查询账户资金](./get-funds.md)，买 1 张合约所带来的初始保证金变动来自本接口。
:::

---

# 查询组合可交易信息

`comboorder_tradinginfo_query(combo_leg_list, price, qty, order_type=OrderType.NORMAL, order_id=None, trd_env=TrdEnv.REAL, acc_id=0, acc_index=0)`

* **介绍**

    查询指定组合订单在指定价格、数量下的可交易信息（如保证金、购买力等变动），亦可传入订单号查询改单场景下的可交易信息。

* **参数**

    参数|类型|说明
    :-|:-|:-
    combo_leg_list|list|组合腿列表  (- 列表元素为 ComboLeg 对象，字段说明参见 [place_combo_order](./place-combo-order.md) 中的 ComboLeg 表)
    price|float|报价  (如果是竞价、市价单，请也填入一个当前价格，服务器才好计算)
    qty|float|数量  (组合数量；每条腿的实际数量为 qty × 该腿的 qty_ratio)
    order_type|[OrderType](./trade.md#4181)|订单类型
    order_id|str|订单号  (- 默认传 None，查询的是新下单的可交易信息
  - 改单时传入服务器订单号 orderIDEx，返回该订单可改成的相关信息)
    trd_env|[TrdEnv](./trade.md#6374)|交易环境
    acc_id|int|交易业务账户 ID  (- acc_id 和 acc_index 二选一即可，推荐使用 acc_id
  - 当 acc_id 传 0 时，以 acc_index 指定的账户为准)
    acc_index|int|交易业务账户列表中的账户序号  (默认为 0，表示第 1 个交易业务账户)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时，返回可交易信息</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 可交易信息格式如下：
        字段|类型|说明
        :-|:-|:-
        nlv_change|float|综合净资产变动
        initial_margin_change|float|初始保证金变动
        maintenance_margin_change|float|维持保证金变动
        option_bp|float|期权购买力
        max_withdraw_change|float|最大可提变动
        bp_decrease|float|消耗购买力

* **Example**

```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
leg1 = ComboLeg()
leg1.code = 'US.AAPL260529C302500'
leg1.trd_side = TrdSide.BUY
leg1.qty_ratio = 1
leg2 = ComboLeg()
leg2.code = 'US.AAPL'
leg2.trd_side = TrdSide.SELL
leg2.qty_ratio = 100
combo_legs = [leg1, leg2]
ret, data = trd_ctx.comboorder_tradinginfo_query(combo_legs, price=100, qty=1, order_type=OrderType.NORMAL, trd_env=TrdEnv.SIMULATE)
if ret == RET_OK:
    print(data)
else:
    print('comboorder_tradinginfo_query error: ', data)
trd_ctx.close()
```

* **Output**

```python
   nlv_change  initial_margin_change  maintenance_margin_change  option_bp  max_withdraw_change  bp_decrease
0        ...                    ...                        ...        ...                  ...          ...
```

:::tip 接口限制
* 同一账户 ID(acc_id) 每 30 秒内最多请求 10 次查询最大可买可卖类接口。
:::

---

# 查询持仓

`position_list_query(code='', position_market=TrdMarket.NONE, pl_ratio_min=None, pl_ratio_max=None, trd_env=TrdEnv.REAL, acc_id=0, acc_index=0, refresh_cache=False, asset_category=AssetCategory.NONE, currency=Currency.USD, show_option_strategy_view=False)`

* **介绍**

    查询交易业务账户的持仓列表

* **参数**
    参数|类型|说明
    :-|:-|:-
    code|str|代码过滤  (- 只返回此代码对应的持仓数据。不传则返回所有
  - 注意：期货持仓的代码过滤，需要传入含具体月份的合约代码，无法通过主连合约代码进行过滤)
    position_market| [TrdMarket](./trade.md#719)|持仓所属市场过滤 (- 返回指定市场的持仓数据
  - 默认状态时，返回所有市场持仓数据)
    pl_ratio_min|float|当前盈亏比例下限过滤，仅返回高于此比例的持仓  (证券账户使用摊薄成本价的盈亏比例，期货账户使用平均成本价的盈亏比例例如：传入 10，则返回盈亏比例大于 +10% 的持仓)
    pl_ratio_max|float|当前盈亏比例上限过滤，低于此比例的会返回  (证券账户使用摊薄成本价的盈亏比例，期货账户使用平均成本价的盈亏比例例如：传入 10，返回盈亏比例小于 +10% 的持仓)
    trd_env|[TrdEnv](./trade.md#6374)|交易环境
    acc_id|int|交易业务账户 ID  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。
  - 当 acc_id 传 0 时， 以 acc_index 指定的账户为准
  - 当 acc_id 传 ID 号时（不为 0 ），以 acc_id 指定的账户为准)
    acc_index|int|交易业务账户列表中的账户序号  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。acc_index 会在新开立/注销账户时发生变动，导致您指定的账户与实际交易账户不一致。
  - acc_index 默认为 0，表示指定第 1 个交易业务账户)
    refresh_cache|bool|是否刷新缓存  (- True：立即向富途服务器重新请求数据，不使用 OpenD 的缓存，此时会受到接口限频的限制
  - False：使用 OpenD 的缓存（特殊情况导致缓存没有及时更新才需要刷新）)
    asset_category|[AssetCategory](./trade.md#4752)|资产类别  (仅对日本券商生效)
    currency|[Currency](./trade.md#8019)|返回持仓的货币单位  (仅加密货币账户使用)
    show_option_strategy_view|bool|是否返回期权策略视图持仓  (- True：返回期权策略维度持仓（含组合策略字段）
  - False：返回标的维度持仓（默认）)
    


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时，返回持仓列表</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 持仓列表
        字段|类型|说明
        :-|:-|:-
        position_side|[PositionSide](./trade.md#2972)|持仓方向
        code|str|股票代码
        stock_name|str|股票名称
        position_market|[TrdMarket](./trade.md#719)|持仓所属市场
        qty|float|持有数量  (期权和期货的单位是“张”)
        can_sell_qty|float|可用数量  (可用数量，是指持有的可平仓的数量。可用数量=持有数量-冻结数量期权和期货的单位是“张”。)
        currency|[Currency](./trade.md#8019)|交易货币
        nominal_price|float|市价  (精确到小数点后 3 位，超出部分四舍五入)
        cost_price|float|摊薄成本价（证券账户），平均开仓价（期货账户）  (建议使用 average_cost，diluted_cost 字段获取持仓成本价)
        cost_price_valid|bool|成本价是否有效  (True：有效False：无效)
        average_cost|float|平均成本价  (模拟证券账户不适用最低OpenD版本要求：9.2.5208)
        diluted_cost|float|摊薄成本价  (期货账户不适用最低OpenD版本要求：9.2.5208)
        market_val|float|市值  (精度：3 位小数（A 股 2 位小数，期货 0 位小数）)
        pl_ratio|float|盈亏比例（摊薄成本价模式）  (期货不适用该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        pl_ratio_valid|bool|盈亏比例是否有效  (True：有效False：无效)
        pl_ratio_avg_cost|float|盈亏比例（平均成本价模式）  (模拟证券账户不适用该字段为百分比字段，默认不展示 %，如 20 实际对应 20%最低OpenD版本要求：9.2.5208)
        pl_val|float|盈亏金额  (精度：3 位小数（A 股 2 位小数）)
        pl_val_valid|bool|盈亏金额是否有效  (True：有效False：无效)
        today_pl_val|float|今日盈亏金额  (只在真实交易环境下有效精度：3 位小数（A 股 2 位小数，期货 2 位小数）)
        today_trd_val|float|今日交易金额  (只在真实交易环境下有效精度：3 位小数（A 股 2 位小数）期货不适用)
        today_buy_qty|float|今日买入总量  (只在真实交易环境下有效精度：3 位小数（A 股 2 位小数）期货不适用)
        today_buy_val|float|今日买入总额  (只在真实交易环境下有效精度：3 位小数（A 股 2 位小数）期货不适用)
        today_sell_qty|float|今日卖出总量  (只在真实交易环境下有效精度：3 位小数（A 股 2 位小数）期货不适用)
        today_sell_val|float|今日卖出总额  (只在真实交易环境下有效精度：3 位小数（A 股 2 位小数）期货不适用)
        unrealized_pl|float|未实现盈亏  (模拟证券账户不适用综合证券账户，返回平均成本价模式下的未实现盈亏金额)
        realized_pl|float|已实现盈亏  (模拟证券账户不适用综合证券账户，返回平均成本价模式下的已实现盈亏金额)
        position_id|int|持仓ID
        combo_id|int|组合 ID  (show_option_strategy_view=True 时有效)
        strategy_type|[OptionStrategyType](../quote/quote.md#2931)|组合策略类型  (show_option_strategy_view=True 时有效)
        position_type|[PositionType](./trade.md#1492)|持仓类型  (show_option_strategy_view=True 时有效)
        acc_id|int|交易业务账户 ID
        jp_acc_type|[SubAccType](./trade.md#6112)|日本账户类型  (仅日本券商适用)

* **Example**

```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.position_list_query()
if ret == RET_OK:
    print(data)
    if data.shape[0] > 0:  # 如果持仓列表不为空
        print(data['stock_name'][0])  # 获取持仓第一个股票名称
        print(data['stock_name'].values.tolist())  # 转为 list
else:
    print('position_list_query error: ', data)
trd_ctx.close()  # 关闭当条连接
```

* **Output**

```python
       code stock_name position_market    qty  can_sell_qty  cost_price  cost_price_valid average_cost  diluted_cost  market_val  nominal_price  pl_ratio  pl_ratio_valid pl_ratio_avg_cost  pl_val  pl_val_valid today_buy_qty today_buy_val today_pl_val today_trd_val today_sell_qty today_sell_val position_side unrealized_pl realized_pl currency asset_category position_id
0  HK.01810     小米集团-W              HK  400.0         400.0      53.975              True          53.975        53.975     19820.0          49.55  -8.19824            True            -8.19824    -1770.0          True           0.0           0.0          0.0           0.0            0.0            0.0          LONG           0.0         0.0      HKD      N/A      6596101776329286054
小米集团-W
['小米集团-W']
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 10 次查询持仓接口
* 调用此接口，只有在刷新缓存时，才受到限频限制
:::

---

# 获取融资融券数据

`get_margin_ratio(code_list)`

* **介绍**

    查询股票的融资融券数据。

* **参数**
    参数|类型|说明
    :-|:-|:-
    code_list|list|股票代码列表  (每次最多可请求 100 个标的list 内元素类型为 str)
    


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时，返回融资融券数据</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 融资融券数据格式如下：
        字段|类型|说明
        :-|:-|:-
        code| str| 股票代码
        is_long_permit|bool|是否允许融资
        is_short_permit | bool | 是否允许融券
        short_pool_remain | float | 卖空池剩余  (单位：股)
        short_fee_rate | float | 融券参考利率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        alert_long_ratio | float | 融资预警比率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        alert_short_ratio | float | 融券预警比率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        im_long_ratio | float | 融资初始保证金率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        im_short_ratio | float | 融券初始保证金率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        mcm_long_ratio | float | 融资 margin call 保证金率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        mcm_short_ratio | float  | 融券 margin call 保证金率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        mm_long_ratio |float | 融资维持保证金率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)
        mm_short_ratio |float | 融券维持保证金率  (该字段为百分比字段，默认不展示 %，如 20 实际对应 20%)

* **Example**

```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.get_margin_ratio(code_list=['HK.00700','HK.09988'])  
if ret == RET_OK:
    print(data)
    print(data['is_long_permit'][0])  # 取第一条的是否允许融资
    print(data['im_short_ratio'].values.tolist())  # 转为 list
else:
    print('error:', data)
trd_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽
```

* **Output**

```python
       code  is_long_permit  is_short_permit  short_pool_remain  short_fee_rate  alert_long_ratio  alert_short_ratio  im_long_ratio  im_short_ratio  mcm_long_ratio  mcm_short_ratio  mm_long_ratio  mm_short_ratio
0  HK.00700            True             True          1826900.0            0.89              33.0               56.0           35.0            60.0            32.0             53.0           25.0            40.0
1  HK.09988            True             True          1150600.0            0.95              48.0               46.0           50.0            50.0            47.0             43.0           40.0            30.0
True
[60.0, 50.0]
```

:::tip 接口限制
* 单用户ID 每 30 秒内最多请求 10 次获取融资融券数据接口。
* 每次请求，接口参数股票代码列表，支持传入的标的数量上限是 100 个。
* 仅支持港股正股和美股正股的查询。
:::

---

# 查询账户资金流水

`get_acc_cash_flow(clearing_date='', trd_env=TrdEnv.REAL, acc_id=0, acc_index=0, cashflow_direction=CashFlowDirection.NONE, start='', end='')`

* **介绍**

    查询交易业务账户在指定日期的资金流水数据。数据覆盖出入金、调拨、货币兑换、买卖金融资产、融资融券利息等所有导致资金变动的事项。

* **参数**
    
    参数|类型|说明
    :-|:-|:-
    clearing_date|str|清算日期 (- 证券/期货账户查询资金流水的必传参数。如需查询多日，需逐日请求
  - 格式：yyyy-MM-dd，例如："2017-06-20")
    trd_env|TrdEnv|交易环境
    acc_id|int|交易业务账户 ID   (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。
  - 当 acc_id 传 0 时， 以 acc_index 指定的账户为准
  - 当 acc_id 传 ID 号时（不为 0），以 acc_id 指定的账户为准)
    acc_index|int|交易业务账户列表中的账户序号
    cashflow_direction|[CashFlowDirection](./trade.md#7573)|筛选资金流方向
    start_time|str|开始时间  (仅加密货币账户使用，格式：yyyy-MM-dd HH:mm:ss)
    end_time|str|结束时间  (仅加密货币账户使用，格式：yyyy-MM-dd HH:mm:ss)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时，返回交易业务账户资金流水列表格式</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 交易业务账户资金流水列表格式如下：
        字段|类型|说明
        :-|:-|:-
        cashflow_id|int|资金流ID
        clearing_date|str|清算日期
        settlement_date|str|交收日期
        currency|[Currency](./trade.md#3974)|币种
        cashflow_type|str|资金流类型
        cashflow_direction|[CashFlowDirection](./trade.md#7573)|资金流方向
        cashflow_amount|float|金额（正数表示流入，负数表示流出）
        cashflow_remark|str|备注
        create_time|str|创建日期  (仅加密货币账户返回，非加密货币账户此字段为空)


* **Example**

```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.get_acc_cash_flow(clearing_date='2025-02-18', trd_env=TrdEnv.REAL, acc_id=0, acc_index=0, cashflow_direction=CashFlowDirection.NONE)
if ret == RET_OK:
    print(data)
    if data.shape[0] > 0:  # 如果资金流水列表不为空
        print(data['cashflow_type'][0])  # 获取第一条流水的资金流类型
        print(data['cashflow_amount'].values.tolist())  # 转为 list
else:
    print('get_acc_cash_flow error: ', data)
trd_ctx.close()

```

* **Output**

```python
   cashflow_id     clearing_date     settlement_date     currency     cashflow_type     cashflow_direction     cashflow_amount     cashflow_remark
0  16308           2025-02-27        2025-02-28          HKD             其他                 N/A                   0.00      Opt ASS-P-JXC250227P13000-20250227
1  16357           2025-02-27        2025-03-03          HKD             其他                 OUT               -104000.00
2  16360           2025-02-27        2025-02-27          USD            基金赎回               IN                 23000.00     Fund Redemption#Taikang Kaitai US Dollar Money...
3  16384           2025-02-27        2025-02-27          HKD            基金赎回               IN                104108.96     Fund Redemption#Taikang Kaitai Hong Kong Dolla...
其他
[0.00, -104000.00, 23000.00, 104108.96]
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 20 次资金流水接口。  
* 资金流水，按照时间的"顺序"进行排列。  
* 模拟账户不支持查询资金流水。  
:::

---

# 下单

`place_order(price, qty, code, trd_side, order_type=OrderType.NORMAL, adjust_limit=0, trd_env=TrdEnv.REAL, acc_id=0, acc_index=0, remark=None, time_in_force=TimeInForce.DAY,  fill_outside_rth=False, aux_price=None, trail_type=None, trail_value=None, trail_spread=None, session=Session.NONE, jp_acc_type=SubAccType.JP_GENERAL, position_id=NONE)`

* **介绍**

    下单 
    :::tip 提示
    Python API 是同步的，但网络收发是异步的。当 place_order 对应的应答数据包与 [响应成交推送回调](../trade/update-order-fill.md) 或 [响应订单推送回调](../trade/update-order.md) 间隔很短时，就可能出现 place_order 的数据包先返回，但回调函数先被调用的情况。例如：可能先调用了 [响应订单推送回调](../trade/update-order.md)，然后 place_order 这个接口才返回。
    :::

* **参数**

    参数|类型|说明
    :-|:-|:-
    price|float|订单价格  (- 当订单是市价单或竞价单类型，仍需对 price 传参，price 可以传入任意值
  - 精度：
  - 期货：整数8位，小数9位，支持负数价格
  - 美股期权：小数2位
  - 美股：小于$1，允许小数4位；大于等于$1，允许小数2位
  - 其他：小数3位，超出部分四舍五入)
    qty|float|订单数量  (期权期货单位是"张")
    code|str|标的代码  (如果 code 为期货主连代码，则会自动转为实际对应的合约代码)
    trd_side|[TrdSide](./trade.md#5815)|交易方向
    order_type|[OrderType](./trade.md#4181)|订单类型
    adjust_limit|float|价格微调幅度  (OpenD 会对传入价格自动调整到合法价位上
  - 正数代表向上调整，负数代表向下调整
  - 例如：0.015 代表向上调整且幅度不超过 1.5%；-0.01 代表向下调整且幅度不超过 1%。默认 0 表示不调整)
    trd_env|[TrdEnv](./trade.md#6374)|交易环境
    acc_id|int|交易业务账户 ID  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。
  - 当 acc_id 传 0 时， 以 acc_index 指定的账户为准
  - 当 acc_id 传 ID 号时（不为 0 ），以 acc_id 指定的账户为准)
    acc_index|int|交易业务账户列表中的账户序号  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。acc_index 会在新开立/注销账户时发生变动，导致您指定的账户与实际交易账户不一致。
  - acc_index 默认为 0，表示指定第 1 个交易业务账户)
    remark|str|备注  (- 订单会带上此备注字段，方便您标识订单
  - 转成 utf8 后的长度上限为 64 字节)
    time_in_force|[TimeInForce](./trade.md#4241)|有效期限  (香港市场、A 股市场和环球期货的市价单，仅支持当日有效)
    fill_outside_rth|bool|是否允许盘前盘后(已弃用)  (该字段已废弃，建议使用 Session 交易时段下单用于港股盘前竞价与美股盘前盘后，且盘前盘后时段不支持市价单)
    aux_price|float|触发价格  (- 当订单是止损市价单、止损限价单、触及限价单（止盈）、触及市价单（止盈） 时，aux_price 为必传参数
  - 同price精度，超过部分四舍五入)
    trail_type|[TrailType](./trade.md#5644)|跟踪类型  (当订单是跟踪止损市价单、跟踪止损限价单时，trail_type 为必传参数)
    trail_value|float|跟踪金额/百分比  (- 当订单是跟踪止损市价单、跟踪止损限价单时，trail_value 为必传参数
  - 当跟踪类型为比例时，该字段为百分比字段，传入 20 实际对应 20%
  - 当跟踪类型为金额时，整数部分同price；小数部分美股期权固定2位，美股4位，其他同price；超过部分四舍五入
  - 当跟踪类型为比例时，精确到小数点后 2 位，整数部分同price，超过部分四舍五入)
    trail_spread|float|指定价差  (- 当订单是跟踪止损限价单时，trail_spread 为必传参数
  - 证券账户精确到小数点后 3 位，期货账户精确到小数点后 9 位，超过部分四舍五入)
    session|[Session](../quote/quote.md#9152)|美股交易时段  (仅对美股生效，支持传入RTH、ETH、OVERNIGHT、ALL)
    jp_acc_type|[SubAccType](./trade.md#6112)|日本账户类型  (仅日本券商适用)
    position_id|int|持仓ID  (- 日本券商平仓时需要填写
  - 可通过[查询持仓](./get-position-list.md)接口获取)
    expire_time|str|订单到期时间，仅在time_in_force为GTD时有效


* **返回**
    
    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时，返回订单列表</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 订单列表格式如下：
        字段|类型|说明
        :-|:-|:-
        trd_side|[TrdSide](./trade.md#5815)|交易方向
        order_type|[OrderType](./trade.md#4181)|订单类型
        order_status|[OrderStatus](./trade.md#797)|订单状态
        order_id|str|订单号
        code|str|股票代码
        stock_name|str|股票名称
        qty|float|订单数量  (期权期货单位是"张")
        price|float|订单价格  (精确到小数点后 3 位，超出部分四舍五入)
        create_time|str|创建时间  (格式：yyyy-MM-dd HH:mm:ss
期货时区指定，请参见 [FutuOpenD 配置](../quick/opend-base.md#6724))
        updated_time|str|最后更新时间  (格式：yyyy-MM-dd HH:mm:ss
期货时区指定，请参见 [FutuOpenD 配置](../quick/opend-base.md#6724))
        dealt_qty|float|成交数量  (期权期货单位是"张")
        dealt_avg_price|float|成交均价  (无精度限制)
        last_err_msg|str|最后的错误描述  (如果有错误，会返回最后一次错误的原因如果无错误，返回空字符串)
        remark|str|下单时备注的标识  (详见 [place_order](./place-order.md) 接口参数中的 remark)
        time_in_force|[TimeInForce](./trade.md#4241)|有效期限
        fill_outside_rth|bool|是否允许盘前盘后（用于港股盘前竞价与美股盘前盘后）  (True：允许False：不允许)
        session|[Session](../quote/quote.md#9152)|交易订单时段（仅用于美股）
        aux_price|float|触发价格
        trail_type|[TrailType](./trade.md#5644)|跟踪类型
        trail_value|float|跟踪金额/百分比
        trail_spread|float|指定价差
        

* **Example**

```python
from futu import *
pwd_unlock = '123456'
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.unlock_trade(pwd_unlock)  # 若使用真实账户下单，需先对账户进行解锁。此处示例为模拟账户下单，也可省略解锁。
if ret == RET_OK:
    ret, data = trd_ctx.place_order(price=510.0, qty=100, code="HK.00700", trd_side=TrdSide.BUY, trd_env=TrdEnv.SIMULATE, session=Session.NONE)
    if ret == RET_OK:
        print(data)
        print(data['order_id'][0])  # 获取下单的订单号
        print(data['order_id'].values.tolist())  # 转为 list
    else:
        print('place_order error: ', data)
else:
    print('unlock_trade failed: ', data)
trd_ctx.close()
```

* **Output**

```python

       code stock_name trd_side order_type order_status           order_id    qty  price          create_time         updated_time  dealt_qty  dealt_avg_price last_err_msg remark time_in_force fill_outside_rth session aux_price trail_type trail_value trail_spread currency
0  HK.00700       腾讯控股      BUY     NORMAL   SUBMITTING  38196006548709500  100.0  420.0  2021-11-04 11:38:19  2021-11-04 11:38:19        0.0              0.0                               DAY              N/A       N/A    N/A      N/A         N/A          N/A      HKD
38196006548709500
['38196006548709500']
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 15 次下单接口，且连续两次请求的间隔不可小于 0.02 秒。和[组合下单](place-combo-order.md)共用一个限频。
* 真实账户调用下单接口前，需要先进行 [解锁](./unlock.md)；模拟账户无需解锁。
:::

:::tip 提示
* 各订单类型对应的必传参数：[点击这里](../qa/trade.html#2984) 了解更多
* 各券商针对不同交易品种，对单笔订单股数有所限制，超出限制会导致下单失败：[点击这里](../qa/trade.html#2984) 了解更多
* 对于 **可做空标的**，暂不支持锁仓功能，故无法同时持有相同产品的多头头寸和空头头寸。
* 如果希望对 **可做空标的** 进行 **平仓** 操作，需要自行判断持仓头寸的方向，然后提交一笔反向的相同数量的订单完成平仓操作。
* 如果希望对 **可做空标的** 进行 **反手** 操作，需要两步：1. 先判断持仓头寸的方向，并提交一笔反向的相同数量的订单完成平仓操作；2. 提交一笔反向的订单，完成反向订单的提交。  
举例：A 当前持有 1 手 HK.HSI2012 期货合约的多单，如果希望反手，必须先 卖出 1 手 HK.HSI2012 完成平仓，再卖出 1 手 HK.HSI2012 完成空单的建立。  
* 美股全时段交易，仅支持限价单，订单期限可以选择当日有效或撤单前有效。选择全时段，交易者可以一次挂单参与多个时段（夜盘、盘前、盘中、盘后时段）的交易，全时段交易时间是星期日到星期四 20:00 - 次日20:00（美东时间）  
* 美股模拟交易不支持盘前盘后与夜盘
:::

---

# 组合下单

`place_combo_order(combo_leg_list, price, qty, order_type=OrderType.NORMAL, trd_env=TrdEnv.REAL, acc_id=0, acc_index=0, remark="", time_in_force=TimeInForce.DAY, expire_time=None)`

* **介绍**

    提交组合期权/组合策略订单。
    :::tip 提示
    Python API 是同步的，但网络收发是异步的。当 place_combo_order 对应的应答数据包与 [响应成交推送回调](../trade/update-order-fill.md) 或 [响应订单推送回调](../trade/update-order.md) 间隔很短时，就可能出现 place_combo_order 的数据包先返回，但回调函数先被调用的情况。
    :::

* **参数**

    参数|类型|说明
    :-|:-|:-
    combo_leg_list|list|组合腿列表  (- 列表元素为 ComboLeg 对象，每条腿描述组合中的一个标的及交易方向
  - ComboLeg 字段见下表)
    price|float|订单价格  (- 当订单是市价单或竞价单类型，仍需对 price 传参，price 可以传入任意值
  - 精度规则同 [place_order](./place-order.md) 的 price 参数)
    qty|float|订单数量  (组合下单数量；每条腿的实际数量为 qty × 该腿的 qty_ratio)
    order_type|[OrderType](./trade.md#4181)|订单类型
    trd_env|[TrdEnv](./trade.md#6374)|交易环境
    acc_id|int|交易业务账户 ID  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id
  - 当 acc_id 传 0 时，以 acc_index 指定的账户为准
  - 当 acc_id 传 ID 号时（不为 0），以 acc_id 指定的账户为准)
    acc_index|int|交易业务账户列表中的账户序号  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id
  - acc_index 默认为 0，表示指定第 1 个交易业务账户)
    remark|str|备注  (- 订单会带上此备注字段，方便您标识订单
  - 转成 utf8 后的长度上限为 64 字节)
    time_in_force|[TimeInForce](./trade.md#4241)|有效期限
    expire_time|str|订单过期时间  (time_in_force 为 GTD 时有效；格式：yyyy-MM-dd)

    * ComboLeg 对象字段：
        字段|类型|说明
        :-|:-|:-
        code|str|标的代码，格式如 US.AAPL、US.AAPL260529C302500
        trd_side|[TrdSide](./trade.md#5815)|该腿交易方向
        qty_ratio|float|数量比例  (该腿实际数量 = 订单 qty × qty_ratio)
        position_id|int|持仓 ID  (平仓时需填写。须填写 [查询持仓](./get-position-list.md) 在 show_option_strategy_view=True 时返回的期权策略视图持仓中的 position_id。)

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时，返回订单列表</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 订单列表格式如下：
        字段|类型|说明
        :-|:-|:-
        order_id|str|订单号
        code|str|组合策略代码
        strategy_type|[OptionStrategyType](../quote/quote.md#2931)|组合策略类型
        trd_side|[TrdSide](./trade.md#5815)|交易方向
        order_type|[OrderType](./trade.md#4181)|订单类型
        order_status|[OrderStatus](./trade.md#797)|订单状态
        qty|float|订单数量
        price|float|订单价格
        amount|float|订单金额
        time_in_force|[TimeInForce](./trade.md#4241)|有效期限
        expire_time|str|过期时间
        dealt_qty|float|成交数量
        dealt_avg_price|float|成交均价
        create_time|str|创建时间
        updated_time|str|最后更新时间
        last_err_msg|str|最后的错误描述
        remark|str|备注
        combo_legs|list|组合腿列表  (元素为 ComboLeg 对象)

* **Example**

```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
leg1 = ComboLeg()
leg1.code = 'US.AAPL260529C302500'
leg1.trd_side = TrdSide.BUY
leg1.qty_ratio = 1
leg2 = ComboLeg()
leg2.code = 'US.AAPL'
leg2.trd_side = TrdSide.SELL
leg2.qty_ratio = 100
combo_legs = [leg1, leg2]
ret, data = trd_ctx.place_combo_order(combo_legs, price=9.9, qty=1, order_type=OrderType.NORMAL, trd_env=TrdEnv.SIMULATE)
if ret == RET_OK:
    print(data)
    print(data['order_id'][0])
else:
    print('place_combo_order error: ', data)
trd_ctx.close()
```

* **Output**

```python
              order_id  code strategy_type trd_side order_type order_status  qty  price  ...
0  FH1C79E90941477000   ...           ...      ...     NORMAL   SUBMITTING  1.0  9.9  ...
FH1C79E90941477000
```

:::tip 接口限制
* 同一账户 ID(acc_id) 每 30 秒内最多请求 15 次下单接口，且连续两次请求的间隔不可小于 0.02 秒。和[下单](place-order.md)共用一个限频。
* 真实账户调用下单接口前，需要先进行 [解锁](./unlock.md)；模拟账户无需解锁。
:::

:::tip 提示
* combo_leg_list 中各腿标的须属于同一交易市场，系统将根据第一条腿的市场确定 trd_market。
* 各腿 qty_ratio 与 qty 共同决定每条腿的实际委托数量。
:::

---

# 改单撤单

`modify_order(modify_order_op, order_id, qty, price, adjust_limit=0, trd_env=TrdEnv.REAL, acc_id=0, acc_index=0, aux_price=None, trail_type=None, trail_value=None, trail_spread=None)`

* **介绍**

    修改订单的价格和数量、撤单、操作订单的失效和生效、删除订单等。  
	如果是 A 股通市场，将不支持改单。可撤单。删除订单是 OpenD 本地操作。

* **参数**
    参数|类型|说明
    :-|:-|:-
    modify_order_op|[ModifyOrderOp](./trade.md#2969)|改单操作类型
    order_id|str|订单号
    qty|float|订单改单后的数量  (期权和期货单位是“张”精确到小数点后 0 位，超出部分会被舍弃)
    price|float|订单改单后的价格  (证券账户精确到小数点后 3 位，超出部分会被舍弃期货账户精确到小数点后 9 位，超出部分会被舍弃)
    adjust_limit|float|价格微调幅度  (OpenD 会对传入价格自动调整到合法价位上（期货忽略此参数）
  - 正数代表向上调整，负数代表向下调整
  - 例如：0.015 代表向上调整且幅度不超过 1.5%；-0.01 代表向下调整且幅度不超过 1%。默认 0 表示不调整)
    trd_env|[TrdEnv](./trade.md#6374)|交易环境
    acc_id|int|交易业务账户 ID  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。
  - 当 acc_id 传 0 时， 以 acc_index 指定的账户为准
  - 当 acc_id 传 ID 号时（不为 0 ），以 acc_id 指定的账户为准)
    acc_index|int|交易业务账户列表中的账户序号  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。acc_index 会在新开立/注销账户时发生变动，导致您指定的账户与实际交易账户不一致。
  - acc_index 默认为 0，表示指定第 1 个交易业务账户)
    aux_price|float|触发价格  (- 当订单是止损市价单、止损限价单、触及限价单（止盈）、触及市价单（止盈） 时，aux_price 为必传参数
  - 证券账户精确到小数点后 3 位，期货账户精确到小数点后 9 位，超过部分四舍五入)
    trail_type|[TrailType](./trade.md#5644)|跟踪类型  (当订单是跟踪止损市价单、跟踪止损限价单时，trail_type 为必传参数)
    trail_value|float|跟踪金额/百分比  (- 当订单是跟踪止损市价单、跟踪止损限价单时，trail_value 为必传参数
  - 当跟踪类型为比例时，该字段为百分比字段，传入 20 实际对应 20%
  - 当跟踪类型为金额时，证券账户精确到小数点后 3 位，期货账户精确到小数点后 9 位，超过部分四舍五入
  - 当跟踪类型为比例时，精确到小数点后 2 位，超过部分四舍五入)
    trail_spread|float|指定价差  (- 当订单是跟踪止损限价单时，trail_spread 为必传参数
  - 证券账户精确到小数点后 3 位，期货账户精确到小数点后 9 位，超过部分四舍五入)


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时，返回改单信息</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 改单信息格式如下：
        字段|类型|说明
        :-|:-|:-
        trd_env|[TrdEnv](./trade.md#6374)|交易环境
        order_id|str|订单号

* **Example**

```python
from futu import *
pwd_unlock = '123456'
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.unlock_trade(pwd_unlock)  # 若使用真实账户改单/撤单，需先对账户进行解锁。此处示例为模拟账户撤单，也可省略解锁。
if ret == RET_OK:
    order_id = "8851102695472794941"
    ret, data = trd_ctx.modify_order(ModifyOrderOp.CANCEL, order_id, 0, 0)
    if ret == RET_OK:
        print(data)
        print(data['order_id'][0])  # 获取改单的订单号
        print(data['order_id'].values.tolist())  # 转为 list
    else:
        print('modify_order error: ', data)
else:
    print('unlock_trade failed: ', data)
trd_ctx.close()
```

* **Output**

```python
    trd_env             order_id
0    REAL      8851102695472794941
8851102695472794941
['8851102695472794941']
```


`cancel_all_order(trd_env=TrdEnv.REAL, acc_id=0, acc_index=0, trdmarket=TrdMarket.NONE)`

* **介绍**

    撤消全部订单。模拟交易以及 A 股通账户暂不支持全部撤单。

* **参数**
    参数|类型|说明
    :-|:-|:-
    trd_env|[TrdEnv](./trade.md#6374)|交易环境
    acc_id|int|交易业务账户 ID  (当 acc_id 传 0 时， 以 acc_index 指定的账户为准当 acc_id 传 ID 号时（不为 0 ），以 acc_id 指定的账户为准)
    acc_index|int|交易业务账户列表中的账户序号  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。acc_index 会在新开立/注销账户时发生变动，导致您指定的账户与实际交易账户不一致。
  - acc_index 默认为 0，表示指定第 1 个交易业务账户)
    trdmarket|[TrdMarket](./trade.html#719)|指定交易市场  (撤销指定账户指定市场的订单默认状态时，撤销指定账户全部市场的订单)


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td>str</td>
            <td>接口调用结果。ret == RET_OK 代表接口调用正常，ret != RET_OK 代表接口调用失败</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td rowspan="2">str</td>
            <td>当 ret == RET_OK，返回"success"</td>
        </tr>
        <tr>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * 全部撤单信息格式如下：
        字段|类型|说明
        :-|:-|:-
        trd_env|[TrdEnv](./trade.md#6374)|交易环境
        order_id|str|订单号

* **Example**

```python
from futu import *
pwd_unlock = '123456'
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.unlock_trade(pwd_unlock)  # 若使用真实账户改单/撤单，需先对账户进行解锁。此处示例为模拟账户全部撤单，也可省略解锁。
if ret == RET_OK:
    ret, data = trd_ctx.cancel_all_order()
    if ret == RET_OK:
        print(data)
    else:
        print('cancel_all_order error: ', data)
else:
    print('unlock_trade failed: ', data)
trd_ctx.close()
```

* **Output**

```python
success
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 20 次改单撤单接口，且连续两次请求的间隔不可小于 0.04 秒。  
* 真实账户调用改单撤单接口前，需要先进行 [解锁](./unlock.md)；模拟账户无需解锁。  
:::

:::tip 提示
* 若执行 **修改订单** 操作，各类订单类型对应的必传参数，可 [点击这里](../qa/trade.html#689) 了解更多。
* 如果希望执行 **改单操作** 去 **修改订单数量**，此接口入参的订单数量 **qty**，应该等于期望成交的总数量。  
举例：
一笔订单数量是 N 股，已部分成交 n 股。对于暂未成交的 (N-n) 股，如果您希望撤掉其中的 x 股，**modify_order_op** 应选择 NORMAL，**qty** 应传 (N-x)。
![order_quantity](../img/order_quantity_cn.png)
* 如果希望执行 **撤单操作**，此接口入参的 **modify_order_op** 应该选择 CANCEL。  
举例： 
一笔订单数量是 N 股，已部分成交 n 股。如果希望将未成交的 (N-n) 股全部撤掉，modify_order_op 应选择 CANCEL，此时 qty 和 price 的入参会被忽略。
:::

---

# 查询未完成订单

`order_list_query(order_id="", order_market=TrdMarket.NONE, status_filter_list=[], code='', start='', end='', trd_env=TrdEnv.REAL, acc_id=0, acc_index=0, refresh_cache=False)`

* **介绍**

    查询指定交易业务账户的未完成订单列表（包含未成交订单、24h内已成交或已撤订单）

* **参数**
    参数|类型|说明
    :-|:-|:-
    order_id|str|订单号过滤  (- 返回指定订单号的数据
  - 默认状态时，返回所有数据)
    order_market|[TrdMarket](./trade.md#719)|订单标的所属市场过滤 (- 订单标的市场过滤，会返回该市场下的标的订单
  - 默认值为NONE，会返回账户下所有市场的订单数据)
    status_filter_list|list|订单状态过滤  (- 返回指定状态的订单数据
  - 默认状态时，返回所有数据
  - list 中元素类型是 [OrderStatus](./trade.md#797))
    code|str|代码过滤  (- 返回指定代码的数据
  - 默认状态时，返回所有数据)
    start|str|开始时间  (- 严格按 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM:SS.MS 格式传
  - 期货时区指定，请参见 [OpenD 配置](../quick/opend-base.md#6724))
    end|str|结束时间  (- 严格按 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM:SS.MS 格式传
  - 期货时区指定，请参见 [OpenD 配置](../quick/opend-base.md#6724))
    trd_env|[TrdEnv](./trade.md#6374)|交易环境
    acc_id|int|交易业务账户 ID  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。
  - 当 acc_id 传 0 时， 以 acc_index 指定的账户为准
  - 当 acc_id 传 ID 号时（不为 0 ），以 acc_id 指定的账户为准)
    acc_index|int|交易业务账户列表中的账户序号  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。acc_index 会在新开立/注销账户时发生变动，导致您指定的账户与实际交易账户不一致。
  - acc_index 默认为 0，表示指定第 1 个交易业务账户)
    refresh_cache|bool|是否刷新缓存  (- True：立即向富途服务器重新请求数据，不使用 OpenD 的缓存，此时会受到接口限频的限制
  - False：使用 OpenD 的缓存（特殊情况导致缓存没有及时更新才需要刷新）)
    


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时，返回订单列表</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 订单列表格式如下：
        字段|类型|说明
        :-|:-|:-
        trd_side|[TrdSide](./trade.md#5815)|交易方向
        order_type|[OrderType](./trade.md#4181)|订单类型
        order_status|[OrderStatus](./trade.md#797)|订单状态
        order_id|str|订单号
        code|str|股票代码
        stock_name|str|股票名称
        order_market|[TrdMarket](./trade.md#719)|订单标的所属市场
        qty|float|订单数量  (期权期货单位是"张")
        price|float|订单价格  (精确到小数点后 3 位，超出部分四舍五入)
        currency|[Currency](./trade.md#8019)|交易货币
        create_time|str|创建时间  (期货时区指定，请参见 [OpenD 配置](../quick/opend-base.md#6724))
        updated_time|str|最后更新时间  (期货时区指定，请参见 [OpenD 配置](../quick/opend-base.md#6724))
        dealt_qty|float|成交数量  (期权期货单位是"张")
        dealt_avg_price|float|成交均价  (无精度限制)
        last_err_msg|str|最后的错误描述  (如果有错误，会返回最后一次错误的原因如果无错误，返回空字符串)
        remark|str|下单时备注的标识  (详见 [place_order](./place-order.md) 接口参数中的 remark)
        time_in_force|[TimeInForce](./trade.md#4241)|有效期限
        fill_outside_rth|bool|是否允许盘前盘后（用于港股盘前竞价与美股盘前盘后）  (True：允许False：不允许)
        session|[Session](../quote/quote.md#9152)|交易订单时段（仅用于美股）
        aux_price|float|触发价格
        trail_type|[TrailType](./trade.md#5644)|跟踪类型
        trail_value|float|跟踪金额/百分比
        trail_spread|float|指定价差
        jp_acc_type|[SubAccType](./trade.md#6112)|日本账户类型  (仅对日本券商生效)
        expire_time|str|订单过期时间  (time_in_force 为 GTD 时有效)
        amount|float|订单金额
        strategy_type|[OptionStrategyType](../quote/quote.md#2931)|组合策略类型
        combo_legs|list|组合腿列表  (字段说明参见 [place_combo_order](./place-combo-order.md) 中的 ComboLeg 表)

* **Example**

```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.order_list_query()
if ret == RET_OK:
    print(data)
    if data.shape[0] > 0:  # 如果订单列表不为空
        print(data['order_id'][0])  # 获取未完成订单的第一个订单号
        print(data['order_id'].values.tolist())  # 转为 list
else:
    print('order_list_query error: ', data)
trd_ctx.close()
```

* **Output**

```python
        code stock_name  order_market   trd_side           order_type   order_status             order_id    qty  price              create_time             updated_time  dealt_qty  dealt_avg_price last_err_msg      remark time_in_force fill_outside_rth session aux_price trail_type trail_value trail_spread currency jp_acc_type
0   HK.00700        HK         BUY           NORMAL  CANCELLED_ALL  6644468615272262086  100.0  520.0  2021-09-06 10:17:52.465  2021-09-07 16:10:22.806        0.0              0.0               asdfg+=@@@           GTC        N/A      N/A       560        N/A         N/A          N/A      HKD        N/A
6644468615272262086
['6644468615272262086']
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 10 次查询未完成订单接口
* 调用此接口，只有在刷新缓存时，才受到限频限制
:::

:::tip 提示
* 未完成订单，按照时间的”顺序”进行排列，即：先提交的订单在前，后提交的订单在后
:::

---

# 查询历史订单

`history_order_list_query(status_filter_list=[], code='', order_market=TrdMarket.NONE, start='', end='', trd_env=TrdEnv.REAL, acc_id=0, acc_index=0)`

* **介绍**

    查询指定交易业务账户的历史订单列表

* **参数**
    参数|类型|说明
    :-|:-|:-
    status_filter_list|list|订单状态过滤  (- 返回指定状态的订单数据
  - 默认状态时，返回所有数据
  - list 中元素类型是 [OrderStatus](./trade.md#797))
    code|str|代码过滤  (- 返回指定代码的数据
  - 默认状态时，返回所有数据)
    order_market|[TrdMarket](./trade.md#719)|订单标的所属市场过滤 (- 订单标的市场过滤，会返回该市场下的标的订单
  - 默认值为NONE，会返回账户下所有市场的订单数据)
    start|str|开始时间  (- 严格按 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM:SS.MS 格式传
  - 期货时区指定，请参见 [OpenD 配置](../quick/opend-base.md#6724))
    end|str|结束时间  (- 严格按 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM:SS.MS 格式传
  - 期货时区指定，请参见 [OpenD 配置](../quick/opend-base.md#6724))
    trd_env|[TrdEnv](./trade.md#6374)|交易环境
    acc_id|int|交易业务账户 ID  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。
  - 当 acc_id 传 0 时， 以 acc_index 指定的账户为准
  - 当 acc_id 传 ID 号时（不为 0 ），以 acc_id 指定的账户为准)
    acc_index|int|交易业务账户列表中的账户序号  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。acc_index 会在新开立/注销账户时发生变动，导致您指定的账户与实际交易账户不一致。
  - acc_index 默认为 0，表示指定第 1 个交易业务账户)

    * start 和 end 的组合如下
        Start 类型|End 类型|说明
        :-|:-|:-
        str|str|start 和 end 分别为指定的日期
        None|str|start 为 end 往前 90 天
        str|None|end 为 start 往后 90 天
        None|None|start 为往前 90 天，end 当前日期

* **返回**
    
    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时，返回订单列表</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 订单列表格式如下：
        字段|类型|说明
        :-|:-|:-
        trd_side|[TrdSide](./trade.md#5815)|交易方向
        order_type|[OrderType](./trade.md#4181)|订单类型
        order_status|[OrderStatus](./trade.md#797)|订单状态
        order_id|str|订单号
        code|str|股票代码
        stock_name|str|股票名称
        order_market|[TrdMarket](./trade.md#719)|订单标的所属市场
        qty|float|订单数量  (期权期货单位是"张")
        price|float|订单价格  (精确到小数点后 3 位，超出部分四舍五入)
        currency|[Currency](./trade.md#8019)|交易货币
        create_time|str|创建时间  (期货时区指定，请参见 [OpenD 配置](../quick/opend-base.md#6724))
        updated_time|str|最后更新时间  (期货时区指定，请参见 [OpenD 配置](../quick/opend-base.md#6724))
        dealt_qty|float|成交数量  (期权期货单位是"张")
        dealt_avg_price|float|成交均价  (无精度限制)
        last_err_msg|str|最后的错误描述  (如果有错误，会返回最后一次错误的原因如果无错误，返回空字符串)
        remark|str|下单时备注的标识  (详见 [place_order](./place-order.md) 接口参数中的 remark)
        time_in_force|[TimeInForce](./trade.md#4241)|有效期限
        fill_outside_rth|bool|是否允许盘前盘后（用于港股盘前竞价与美股盘前盘后）  (True：允许False：不允许)
        session|[Session](../quote/quote.md#9152)|交易订单时段（仅用于美股）
        aux_price|float|触发价格
        trail_type|[TrailType](./trade.md#5644)|跟踪类型
        trail_value|float|跟踪金额/百分比
        trail_spread|float|指定价差
        jp_acc_type|[SubAccType](./trade.md#6112)|日本账户类型  (仅对日本券商生效)
        expire_time|str|订单过期时间  (time_in_force 为 GTD 时有效)
        amount|float|订单金额
        strategy_type|[OptionStrategyType](../quote/quote.md#2931)|组合策略类型
        combo_legs|list|组合腿列表  (字段说明参见 [place_combo_order](./place-combo-order.md) 中的 ComboLeg 表)

* **Example**

```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUINC)
ret, data = trd_ctx.history_order_list_query()
if ret == RET_OK:
    print(data)
    if data.shape[0] > 0:  # 如果订单列表不为空
        print(data['order_id'][0])  # 获取持仓第一个订单号
        print(data['order_id'].values.tolist())  # 转为 list
else:
    print('history_order_list_query error: ', data)
trd_ctx.close()
```

* **Output**

```python
        code stock_name order_market    trd_side           order_type   order_status             order_id    qty  price              create_time             updated_time  dealt_qty  dealt_avg_price last_err_msg      remark time_in_force fill_outside_rth session aux_price trail_type trail_value trail_spread currency jp_acc_type
0   US.AAPL        US          BUY           NORMAL  CANCELLED_ALL  6644468615272262086  100.0  520.0  2021-09-06 10:17:52.465  2021-09-07 16:10:22.806        0.0              0.0               asdfg+=@@@           GTC      N/A        N/A       560        N/A         N/A          N/A      USD        N/A
6644468615272262086
['6644468615272262086']
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 10 次查询历史订单接口
:::

:::tip 提示
* 历史订单，按照时间的“倒序”进行排列，即：后提交的订单在前，先提交的订单在后
:::

---

# 响应订单推送回调

`on_recv_rsp(self, rsp_pb)`

* **介绍**

    响应订单推送，异步处理 OpenD 推送过来的订单状态信息。  
    在收到 OpenD 推送过来的订单状态信息后会回调到该函数，您需要在派生类中覆盖 on_recv_rsp。

* **参数**
    
    参数|类型|说明
    :-|:-|:-
    rsp_pb|Trd_UpdateOrder_pb2.Response|派生类中不需要直接处理该参数

* **返回**
    
    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时，返回订单列表</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 订单列表格式如下：
        字段|类型|说明
        :-|:-|:-
        trd_side|[TrdSide](./trade.md#5815)|交易方向
        order_type|[OrderType](./trade.md#4181)|订单类型
        order_status|[OrderStatus](./trade.md#797)|订单状态
        order_id|str|订单号
        code|str|股票代码
        stock_name|str|股票名称
        qty|float|订单数量  (期权期货单位是"张")
        price|float|订单价格  (精确到小数点后 3 位，超出部分四舍五入)
        currency|[Currency](./trade.md#8019)|交易货币
        create_time|str|创建时间  (期货时区指定，请参见 [OpenD 配置](../quick/opend-base.md#6724))
        updated_time|str|最后更新时间  (期货时区指定，请参见 [OpenD 配置](../quick/opend-base.md#6724))
        dealt_qty|float|成交数量  (期权期货单位是"张")
        dealt_avg_price|float|成交均价  (无精度限制)
        last_err_msg|str|最后的错误描述  (如果有错误，会返回最后一次错误的原因如果无错误，返回空字符串)
        remark|str|下单时备注的标识  (详见 [place_order](./place-order.md) 接口参数中的 remark)
        time_in_force|[TimeInForce](./trade.md#4241)|有效期限
        fill_outside_rth|bool|是否允许盘前盘后（仅用于美股）  (True：允许False：不允许)
        session|[Session](../quote/quote.md#9152)|交易订单时段（仅用于美股）
        aux_price|float|触发价格
        trail_type|[TrailType](./trade.md#5644)|跟踪类型
        trail_value|float|跟踪金额/百分比
        trail_spread|float|指定价差
        expire_time|str|订单过期时间  (time_in_force 为 GTD 时有效)
        amount|float|订单金额
        strategy_type|[OptionStrategyType](../quote/quote.md#2931)|组合策略类型
        combo_legs|list|组合腿列表  (字段说明参见 [place_combo_order](./place-combo-order.md) 中的 ComboLeg 表)

* **Example**

```python
from futu import *
from time import sleep
class TradeOrderTest(TradeOrderHandlerBase):
    """ order update push"""
    def on_recv_rsp(self, rsp_pb):
        ret, content = super(TradeOrderTest, self).on_recv_rsp(rsp_pb)
        if ret == RET_OK:
            print("* TradeOrderTest content={}\n".format(content))
        return ret, content

trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
trd_ctx.set_handler(TradeOrderTest())
print(trd_ctx.place_order(price=518.0, qty=100, code="HK.00700", trd_side=TrdSide.SELL))

sleep(15)
trd_ctx.close()
```

* **Output**

```python
* TradeOrderTest content=  trd_env      code stock_name  dealt_avg_price  dealt_qty    qty           order_id order_type  price order_status          create_time         updated_time trd_side last_err_msg trd_market remark time_in_force fill_outside_rth session aux_price trail_type trail_value trail_spread currency
0    REAL  HK.00700       腾讯控股              0.0        0.0  100.0  72625263708670783     NORMAL  518.0   SUBMITTING  2021-11-04 11:26:27  2021-11-04 11:26:27      BUY                      HK                  DAY      N/A        N/A       N/A        N/A         N/A          N/A      HKD
```

---

# 查询订单费用

`order_fee_query(order_id_list=[], acc_id=0, acc_index=0, trd_env=TrdEnv.REAL)`

* **介绍**

    查询指定订单的收费明细（最低版本要求：8.2.4218）

* **参数**
    参数|类型|说明
    :-|:-|:-
    order_id_list|list|订单号列表 (- 每次请求最多查询 400 笔订单
  - list 内元素类型为 str)
    trd_env|[TrdEnv](./trade.md#6374)|交易环境
    acc_id|int|交易业务账户 ID  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。
  - 当 acc_id 传 0 时， 以 acc_index 指定的账户为准
  - 当 acc_id 传 ID 号时（不为 0 ），以 acc_id 指定的账户为准)
    acc_index|int|交易业务账户列表中的账户序号  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。acc_index 会在新开立/注销账户时发生变动，导致您指定的账户与实际交易账户不一致。
  - acc_index 默认为 0，表示指定第 1 个交易业务账户)
    


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时，返回订单费用列表</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 订单列表格式如下：
        字段|类型|说明
        :-|:-|:-
        order_id|str|订单号
        fee_amount|float|总费用
        fee_details|list|收费明细 (- 格式：[('收费项1', 收费项1的金额), ('收费项2', 收费项2的金额), ('收费项3', 收费项3的金额)……]
  - 常见的收费项包括：佣金、平台使用费、期权监管费、期权清算费、期权交收费、交收费、证监会规费、交易活动费)

        
* **Example**

```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret1, data1 = trd_ctx.history_order_list_query(status_filter_list=[OrderStatus.FILLED_ALL])
if ret1 == RET_OK:
    if data1.shape[0] > 0:  # 如果订单列表不为空
        ret2, data2 = trd_ctx.order_fee_query(data1['order_id'].values.tolist())  # 将订单 id 转为 list，查询订单费用
        if ret2 == RET_OK:
            print(data2)
            print(data2['fee_details'][0])  # 打印第一笔订单的收费明细
        else:
            print('order_fee_query error: ', data2)
else:
    print('order_list_query error: ', data1)
trd_ctx.close()
```

* **Output**

```python
                                            order_id  fee_amount                                        fee_details
0  v3_20240314_12345678_MTc4NzA5NzY5OTA3ODAzMzMwN       10.46  [(佣金, 5.85), (平台使用费, 2.7), (期权监管费, 0.11), (期权清...
1  v3_20240318_12345678_MTM5Nzc5MDYxNDY1NDM1MDI1M        2.25  [(佣金, 0.99), (平台使用费, 1.0), (交收费, 0.15), (证监会规费...
[('佣金', 5.85), ('平台使用费', 2.7), ('期权监管费', 0.11), ('期权清算费', 0.18), ('期权交收费', 1.62)]
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 10 次查询订单费用接口。
* 仅支持查询 2018-01-01 之后的订单。
* 模拟账户不支持查询订单费用。
* 加拿大券商账户不支持查询订单费用。

:::

---

# 订阅交易推送

Python 不需要订阅交易推送

---

# 查询当日成交

`deal_list_query(code="", deal_market= TrdMarket.NONE, trd_env=TrdEnv.REAL, acc_id=0, acc_index=0, refresh_cache=False)`

* **介绍**
    
	查询指定交易业务账户的当日成交列表。  
    该接口只支持实盘交易，不支持模拟交易。

* **参数**
    参数|类型|说明
    :-|:-|:-
    code|str|代码过滤  (只返回此代码对应的成交数据不传则返回所有)
    deal_market|[TrdMarket](./trade.md#719)|成交标的所属市场过滤  (- 成交标的市场过滤，会返回该市场下的成交数据
  - 默认值为NONE，会返回账户下所有市场的成交数据)
    trd_env|[TrdEnv](./trade.md#6374)|交易环境  (仅支持 TrdEnv.REAL（真实环境），模拟环境暂不支持查询成交数据)
    acc_id|int|交易业务账户 ID  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。
  - 当 acc_id 传 0 时， 以 acc_index 指定的账户为准
  - 当 acc_id 传 ID 号时（不为 0 ），以 acc_id 指定的账户为准)
    acc_index|int|交易业务账户列表中的账户序号  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。acc_index 会在新开立/注销账户时发生变动，导致您指定的账户与实际交易账户不一致。
  - acc_index 默认为 0，表示指定第 1 个交易业务账户)
    refresh_cache|bool|是否刷新缓存  (- True：立即向富途服务器重新请求数据，不使用 OpenD 的缓存，此时会受到接口限频的限制
  - False：使用 OpenD 的缓存（特殊情况导致缓存没有及时更新才需要刷新）)
    


* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时，返回交易成交列表</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 交易成交列表格式如下：
        字段|类型|说明
        :-|:-|:-
        trd_side|[TrdSide](./trade.md#5815)|交易方向
        deal_id|str|成交号
        order_id|str|订单号
        code|str|股票代码
        stock_name|str|股票名称
        deal_market|[TrdMarket](./trade.md#719)|成交标的所属市场
        qty|float|成交数量  (期权期货单位是"张")
        price|float|成交价格  (精确到小数点后 3 位，超出部分四舍五入)
        create_time|str|创建时间  (期货时区指定，请参见 [OpenD 配置](../quick/opend-base.md#6724))
        counter_broker_id|int|对手经纪号  (仅港股有效)
        counter_broker_name|str|对手经纪名称  (仅港股有效)
        status|[DealStatus](./trade.md#8317)|成交状态
        jp_acc_type|[SubAccType](./trade.md#6112)|日本账户类型  (仅对日本券商生效)

* **Example**

```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.deal_list_query()
if ret == RET_OK:
    print(data)
    if data.shape[0] > 0:  # 如果成交列表不为空
        print(data['order_id'][0])  # 获取当日成交的第一个订单号
        print(data['order_id'].values.tolist())  # 转为 list
else:
    print('deal_list_query error: ', data)
trd_ctx.close()
```

* **Output**

```python
    code stock_name     deal_market         deal_id             order_id        qty  price    trd_side     create_time      counter_broker_id counter_broker_name status jp_acc_type
0  HK.00388      香港交易所     HK    5056208452274069375  4665291631090960915  100.0  370.0      BUY  2020-09-17 21:15:59.979           5         OK       N/A
4665291631090960915
['4665291631090960915']
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 10 次查询当日成交接口
* 调用此接口，只有在刷新缓存时，才受到限频限制
:::

:::tip 提示
* 当日成交，按照时间的“顺序”进行排列，即：先成交的记录在前，后成交的记录在后
:::

---

# 查询历史成交

`history_deal_list_query(code='', deal_market=TrdMarket.NONE, start='', end='', trd_env=TrdEnv.REAL, acc_id=0, acc_index=0)`

* **介绍**

    查询指定交易业务账户的历史成交列表。  
    该接口只支持实盘交易，不支持模拟交易。

* **参数**

    参数|类型|说明
    :-|:-|:-
    code|str|代码过滤  (只返回此代码对应的成交数据不传则返回所有)
    deal_market|[TrdMarket](./trade.md#719)|成交标的所属市场过滤  (- 成交标的市场过滤，会返回该市场下的成交数据
  - 默认值为NONE，会返回账户下所有市场的成交数据)
    start|str|开始时间  (- 严格按 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM:SS.MS 格式传
  - 期货时区指定，请参见 [OpenD 配置](../quick/opend-base.md#6724))
    end|str|结束时间  (- 严格按 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM:SS.MS 格式传
  - 期货时区指定，请参见 [OpenD 配置](../quick/opend-base.md#6724))
    trd_env|[TrdEnv](./trade.md#6374)|交易环境  (仅支持 TrdEnv.REAL（真实环境），模拟环境暂不支持查询成交数据)
    acc_id|int|交易业务账户 ID  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。
  - 当 acc_id 传 0 时， 以 acc_index 指定的账户为准
  - 当 acc_id 传 ID 号时（不为 0 ），以 acc_id 指定的账户为准)
    acc_index|int|交易业务账户列表中的账户序号  (- acc_id 和 acc_index 都可用于指定交易业务账户，二选一即可，推荐使用 acc_id。acc_index 会在新开立/注销账户时发生变动，导致您指定的账户与实际交易账户不一致。
  - acc_index 默认为 0，表示指定第 1 个交易业务账户)
    
    * start 和 end 的组合如下
        Start 类型|End 类型|说明
        :-|:-|:-
        str|str|start 和 end 分别为指定的日期
        None|str|start 为 end 往前 90 天
        str|None|end 为 start 往后 90 天
        None|None|start 为往前 90 天，end 当前日期

* **返回**
    
    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时，返回交易成交列表</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 交易成交列表格式如下：
        字段|类型|说明
        :-|:-|:-
        trd_side|[TrdSide](./trade.md#5815)|交易方向
        deal_id|str|成交号
        order_id|str|订单号
        code|str|股票代码
        stock_name|str|股票名称
        deal_market|[TrdMarket](./trade.md#719)|成交标的所属市场
        qty|float|成交数量  (期权期货单位是"张")
        price|float|成交价格  (精确到小数点后 3 位，超过部分四舍五入)
        create_time|str|创建时间  (期货时区指定，请参见 [OpenD 配置](../quick/opend-base.md#6724))
        counter_broker_id|int|对手经纪号  (仅港股有效)
        counter_broker_name|str|对手经纪名称  (仅港股有效)
        status|[DealStatus](./trade.md#8317)|成交状态
        jp_acc_type|[SubAccType](./trade.md#6112)|日本账户类型  (仅对日本券商生效)

* **Example**

```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.history_deal_list_query()
if ret == RET_OK:
    print(data)
    if data.shape[0] > 0:  # 如果成交列表不为空
        print(data['deal_id'][0])  # 获取历史成交的第一个成交号
        print(data['deal_id'].values.tolist())  # 转为 list
else:
    print('history_deal_list_query error: ', data)
trd_ctx.close()
```

* **Output**

```python
    code stock_name     deal_market         deal_id             order_id    qty  price trd_side              create_time  counter_broker_id counter_broker_name status jp_acc_type
0  HK.00388      香港交易所    HK  5056208452274069375  4665291631090960915  100.0  370.0      BUY  2020-09-17 21:15:59.979                  5                         OK        N/A
5056208452274069375
['5056208452274069375']
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 10 次查询历史成交接口
:::

:::tip 提示
* 历史成交，按照时间的“倒序”进行排列，即：后成交的记录在前，先成交的记录在后
:::

---

# 响应成交推送回调

`on_recv_rsp(self, rsp_pb)`

* **介绍**

    响应成交推送，异步处理 OpenD 推送过来的成交状态信息。  
    在收到 OpenD 推送过来的成交状态信息后会回调到该函数，您需要在派生类中覆盖 on_recv_rsp。  
    该接口只支持实盘交易，不支持模拟交易。
 
* **参数**
    
    参数|类型|说明
    :-|:-|:-
    rsp_pb|Trd_UpdateOrderFill_pb2.Response|派生类中不需要直接处理该参数

* **返回**
    
    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>pd.DataFrame</td>
            <td>当 ret == RET_OK 时，返回交易成交列表</td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK 时，返回错误描述</td>
        </tr>
    </table>

    * 交易成交列表格式如下：
        字段|类型|说明
        :-|:-|:-
        trd_side|[TrdSide](./trade.md#5815)|交易方向
        deal_id|str|成交号
        order_id|str|订单号
        code|str|股票代码
        stock_name|str|股票名称
        qty|float|成交数量  (期权期货单位是"张")
        price|float|成交价格
        create_time|str|创建时间  (期货时区指定，请参见 [FutuOpenD 配置](../quick/opend-base.md#6724))
        counter_broker_id|int|对手经纪号  (仅港股有效)
        counter_broker_name|str|对手经纪名称  (仅港股有效)
        status|[DealStatus](./trade.md#8317)|成交状态

* **Example**

```python
from futu import *
from time import sleep
class TradeDealTest(TradeDealHandlerBase):
    """ order update push"""
    def on_recv_rsp(self, rsp_pb):
        ret, content = super(TradeDealTest, self).on_recv_rsp(rsp_pb)
        if ret == RET_OK:
            print("TradeDealTest content={}".format(content))
        return ret, content

trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
trd_ctx.set_handler(TradeDealTest())
print(trd_ctx.place_order(price=595.0, qty=100, code="HK.00700", trd_side=TrdSide.BUY))

sleep(15)
trd_ctx.close()
```

* **Output**

```python
TradeDealTest content=  trd_env      code stock_name              deal_id             order_id    qty  price trd_side              create_time  counter_broker_id counter_broker_name trd_market status
0    REAL  HK.00700       腾讯控股  2511067564122483295  8561504228375901919  100.0  518.0      BUY  2021-11-04 11:29:41.595                  5                   5         HK     OK
```

---

# 交易定义

## 账户风控状态

> **CltRiskLevel**

* `NONE`

  未知

* `SAFE`

  安全

* `WARNING`

  预警

* `DANGER`

  危险

* `ABSOLUTE_SAFE`

  绝对安全

* `OPT_DANGER`

  危险  (期权相关)

:::tip 提示
* 查询期货账户的风险状态，建议使用 risk_status 字段， 返回结果详见 [CltRiskStatus](./trade.md#3989)
:::

## 货币类型

> **Currency**

* `NONE`

  未知货币

* `HKD`

  港元

* `USD`

  美元

* `CNH`

  离岸人民币

* `JPY`

  日元

* `SGD`

  新元

* `AUD`

  澳元

* `CAD`

  加拿大元

* `MYR`

  马来西亚林吉特

## 跟踪类型

**TrailType**

* `NONE`

  未知

* `RATIO`

  比例

* `AMOUNT`

  金额

## 修改订单操作

> **ModifyOrderOp**

* `NONE`

  未知操作

* `NORMAL`

  修改订单

* `CANCEL`

  撤单  (未成交订单将直接从交易所撮合队列中撤销。)

* `DISABLE`

  使失效  (- 指让订单失效，对交易所来说，DISABLE 的效果等同于 CANCEL。
  - 订单「失效」后，未成交订单将直接从交易所撮合队列中撤出，但订单信息（如价格和数量）会继续保留在富途服务器，您随时可以重新 ENABLE 它。)

* `ENABLE`

  使生效  (- 指让处于失效状态的订单重新生效。对交易所来说，ENABLE 等同于下一笔新订单。
  - 订单重新「生效」后，将按照原来的价格数量重新提交到交易所，并按照价格优先、时间优先顺序重新排队。)

* `DELETE`

  删除  (指对已撤单/下单失败的订单进行隐藏操作。)

## 成交状态

> **DealStatus**

* `OK`

  正常

* `CANCELLED`

  成交被取消

* `CHANGED`

  成交被更改

## 订单状态

> **OrderStatus**

* `NONE`

  未知状态


* `WAITING_SUBMIT`

  待提交  (富途服务器已经收到指令，正在准备提交给上游交易所)

* `SUBMITTING`

  提交中  (富途服务器已将指令发送给上游交易所，上游交易所处理中)

* `SUBMITTED`

  已提交，等待成交  (已经成功提交给上游交易所)

* `FILLED_PART`

  部分成交  (剩余部分仍未撤单。您可选择执行撤单，或者继续等待全部成交)

* `FILLED_ALL`

  全部已成交

* `CANCELLED_PART`

  部分成交，剩余部分已撤单

* `CANCELLED_ALL`

  全部已撤单，无成交

* `FAILED`

  下单失败，服务拒绝

* `DISABLED`

  已失效  (您主动执行失效操作后的订单状态，失效订单不会提交到上游交易所)

* `DELETED`

  已删除，无成交的订单才能删除  (您主动执行删除订单操作后的订单状态)

## 订单类型

:::tip 提示
* [实盘交易中，各个品类支持的订单类型](../qa/trade.md#2731)
* 模拟交易中，仅支持限价单(NORMAL)和市价单(MARKET)。
:::

> **OrderType**

* `NONE`

  未知类型

* `NORMAL`

  限价单

* `MARKET`

  市价单 

* `ABSOLUTE_LIMIT`

  绝对限价订单  (只有价格完全匹配才成交，否则下单失败
  - 举例：下一笔价格为 5 元的绝对限价买单，卖方的价格必须也是 5 元才能成交，卖方即使低于 5 元也不能成交，下单失败。卖出同理)

* `AUCTION`

  竞价市价单  (仅港股早盘竞价和收盘竞价有效)

* `AUCTION_LIMIT`

  竞价限价单 (仅早盘竞价和收盘竞价有效，参与竞价，且要求满足指定价格才会成交)

* `SPECIAL_LIMIT`

  特别限价单  (成交规则同增强限价订单，且部分成交后，交易所自动撤销订单)

* `SPECIAL_LIMIT_ALL`

  特别限价且要求全部成交订单  (全部成交，否则自动撤单)

* `STOP`

  止损市价单

* `STOP_LIMIT`

  止损限价单 

* `MARKET_IF_TOUCHED`

  触及市价单（止盈）

* `LIMIT_IF_TOUCHED`

  触及限价单（止盈） 

* `TRAILING_STOP`

  跟踪止损市价单

* `TRAILING_STOP_LIMIT`

  跟踪止损限价单 

* `TWAP_LIMIT `

  时间加权限价算法单（港股和美股）  (算法订单只支持订单查询，不支持交易。)

* `TWAP`

  时间加权市价算法单（仅美股）  (算法订单只支持订单查询，不支持交易。)

* `VWAP_LIMIT `

  成交量加权限价算法单（港股和美股）  (算法订单只支持订单查询，不支持交易。)

* `VWAP `

  成交量加权市价算法单（仅美股）  (算法订单只支持订单查询，不支持交易。)

## 持仓方向

> **PositionSide**

* `NONE`

  未知方向

* `LONG`

  多仓  (默认情况是多仓)

* `SHORT`

  空仓

## 期权组合持仓类型

> **PositionType**

* `NONE`

  未知

* `COMBINED`

  组合汇总持仓

* `LEG`

  单腿持仓

## 账户类型

> **TrdAccType**

* `NONE`

  未知类型

* `CASH`

  现金账户

* `MARGIN`

  保证金账户

* `TFSA`

  加拿大免税账户
  
* `RRSP`

  加拿大注册退休账户

* `SRRSP`

  加拿大配偶退休账户

* `DERIVATIVE`

  日本衍生品账户

## 交易环境

> **TrdEnv**

* `SIMULATE`

  模拟环境

* `REAL`

  真实环境

## 交易市场

> **TrdMarket**

* `NONE`

  未知市场

* `HK`

  香港市场

* `US`

  美国市场

* `CN`

  A 股市场  (A 股市场仅支持模拟交易，不支持实盘交易)

* `HKCC`

  香港 A 股通市场  (- A 股通市场仅支持实盘交易，不支持模拟交易
  - A 股通只能交易沪股通、深股通股票，具体以港交所 [A 股通名单](https://www.hkex.com.hk/mutual-market/stock-connect/eligible-stocks/view-all-eligible-securities?sc_lang=zh-HK) 为准)

* `FUTURES`

  期货市场

* `FUTURES_SIMULATE_US`

  美国期货模拟市场  (最低 OpenD 版本要求：7.7.3908)

* `FUTURES_SIMULATE_HK`

  香港期货模拟市场  (最低 OpenD 版本要求：7.7.3908)

* `FUTURES_SIMULATE_SG`

  新加坡期货模拟市场  (最低 OpenD 版本要求：7.7.3908)

* `FUTURES_SIMULATE_JP`

  日本期货模拟市场  (最低 OpenD 版本要求：7.7.3908)

* `HKFUND`

  香港基金市场  (最低 OpenD 版本要求：8.2.4218)

* `USFUND`

  美国基金市场  (最低 OpenD 版本要求：8.2.4218)

* `SG`

  新加坡市场  (最低 OpenD 版本要求：9.0.5008)

* `JP`

  日本市场  (最低 OpenD 版本要求：9.0.5008)

* `AU`

  澳大利亚市场  (最低 OpenD 版本要求：9.0.5008)

* `MY`

  马来西亚市场  (最低 OpenD 版本要求：9.0.5008)

* `CA`

  加拿大市场  (最低 OpenD 版本要求：9.0.5008)

* `CRYPTO`

  加密货币市场


## 账户状态

> **TrdAccStatus**

* `ACTIVE`

  生效账户

* `DISABLED`

  失效账户


## 账户结构

> **TrdAccRole**

* `NONE`

  未知

* `MASTER`

  主账户

* `NORMAL`

  普通账户

* `IPO`

  马来西亚IPO账户


## 交易证券市场


## 交易方向

> **TrdSide**

* `NONE`

  未知方向

* `BUY`

  买入

* `SELL`

  卖出

* `SELL_SHORT`

  卖空  (- 日本券商适用
  - 其他券商仅用于订单列表展示，不建议作为下单的方向)

* `BUY_BACK`

  买回  (- 日本券商适用
  - 其他券商仅用于订单列表展示，不建议作为下单的方向)

:::tip 提示
**下单** 接口的交易方向 ，建议仅使用 `买入` 和 `卖出` 两个方向作为入参。  
`卖空` 和 `买回` 仅适用于日本券商，其他券商仅用于 **查询今日订单** ，**查询历史订单** ，**响应订单推送回调** ，**查询当日成交** ，**查询历史成交** ，**响应成交推送回调** 接口的返回字段展示。
:::

## 订单有效期

> **TimeInForce**

* `DAY`

  当日有效

* `GTC`

  撤单前有效

* `IOC`

  立即成交或取消  (仅适用于加密货币市价单)

* `GTD`

  指定日期前有效

## 账户所属券商

> **SecurityFirm**

* `NONE`

  未知

* `FUTUSECURITIES`

  富途证券（香港）

* `FUTUINC`
  
  moomoo证券(美国)

* `FUTUSG`  
  moomoo证券(新加坡)

* `FUTUAU`  
  moomoo证券(澳大利亚)

* `FUTUCA`  
  moomoo证券(加拿大)

* `FUTUMY`  
  moomoo证券(马来西亚)

* `FUTUJP`  
  moomoo证券(日本)

## 模拟交易账户类型

**SimAccType**

* `NONE`

  未知

* `STOCK`

  股票模拟账户 

* `OPTION`

  期权模拟账户 

* `FUTURES`

  期货模拟账户

* `STOCK_AND_OPTION`

  美股融资融券模拟账户

## 风险状态

> **CltRiskStatus**

* `NONE`

  未知

* `LEVEL1`

  非常安全

* `LEVEL2`

  安全

* `LEVEL3`

  较安全

* `LEVEL4`

  较低风险

* `LEVEL5`

  中等风险

* `LEVEL6`

  偏高风险

* `LEVEL7`

  预警

* `LEVEL8`

  危险

* `LEVEL9`

  危险

## 持仓限额状态

> **ExposureLevel**

* `NONE`

  未知

* `NORMAL`

  正常  (剩余限额/持仓限额 > 10%，可正常买入虚拟资产)

* `NEAR_LIMIT`

  即将用尽  (10% >= 剩余限额/持仓限额 > 0%，需留意剩余限额)

* `RESTRICTED`

  受限  (剩余限额/持仓限额 = 0%，禁止买入虚拟资产)

* `SAFE`

  安全  (含贷权益值 >= 初始保证金要求，无风险)

* `MODERATE`

  适中  (剩余流动性 >= 10% * 含贷权益值，存在杠杆交易，风险较小)

* `WARNING`

  预警  (剩余流动性 < 10% * 含贷权益值，风险可能加剧)

* `MARGIN_CALL`

  危险  (含贷权益值 <= 维持保证金要求)

## 日内交易限制情况

> **DtStatus**

* `NONE`

  未知

* `Unlimited`

  无限次  (当前可以无限次日内交易，注意留意剩余日内交易购买力)

* `EM_Call`

  EM-Call  (当前状态不能新建仓位，需要补充资产净值至$25000以上，否则会被禁止新建仓位90天)

* `DT_Call`

  DT-Call  (当前状态有未补平的日内交易追缴金额（DT Call），需要在5个交易日内足额入金来补平 DT Call，否则会被禁止新建仓位，直到足额存入资金才会解禁)

## 现金流方向

> **CashFlowDirection**

* `NONE`

  未知

* `IN`

  现金流入

* `OUT`

  现金流出

## 日本子账户类型

> **SubAccType**

* `NONE`

  未知

* `JP_GENERAL`

  一般-Long

* `JP_TOKUTEI`

  特定-Long

* `JP_NISA_GENERAL`

  一般NISA

* `JP_NISA_TSUMITATE`

  累计NISA

* `JP_GENERAL_SHORT`

  一般-short

* `JP_TOKUTEI_SHORT`

  特定-short

* `JP_HONPO_GENERAL`

  本国信用交易抵押品-一般

* `JP_GAIKOKU_GENERAL`

  外国信用交易抵押品-一般

* `JP_HONPO_TOKUTEI`

  本国信用交易抵押品-特定

* `JP_GAIKOKU_TOKUTEI`

  外国信用交易抵押品-特定

* `JP_DERIVATIVE_LONG`

  衍生品子账户-Long

* `JP_DERIVATIVE_SHORT`

  衍生品子账户-Short

* `JP_HONPO_DERIVATIVE_GENERAL`

  本国衍生品证据金子账户-一般

* `JP_GAIKOKU_DERIVATIVE_GENERAL`

  外国衍生品证据金子账户-一般

* `JP_HONPO_DERIVATIVE_TOKUTEI`

  本国衍生品证据金子账户-特定

* `JP_GAIKOKU_DERIVATIVE_TOKUTEI`

  外国衍生品证据金子账户-特定

## 资产类别

> **AssetCategory**

* `NONE`

  未知

* `JP`

  本国

* `US`

  外国

## 交易品类

**TrdCategory**

```protobuf
enum TrdCategory
{
    TrdCategory_Unknown = 0; //未知品类
    TrdCategory_Security = 1; //证券
    TrdCategory_Future = 2; //期货
    TrdCategory_Crypto = 3; //加密货币
}
```

## 账户现金信息

**AccCashInfo**

```protobuf
message AccCashInfo
{
    optional int32 currency = 1;        // 货币类型，取值参考 Currency
    optional double cash = 2;           // 现金结余
    optional double availableBalance = 3;   // 现金可提金额
    optional double netCashPower = 4;		// 现金购买力
}
```

## 分市场资产信息

**AccMarketInfo**

```protobuf
message AccCashInfo
{
    optional int32 trdMarket = 1;        // 交易市场, 参见TrdMarket的枚举定义
    optional double assets = 2;          // 分市场资产信息
}
```


## 交易协议公共参数头

**TrdHeader**

```protobuf
message TrdHeader
{
  required int32 trdEnv = 1; //交易环境, 参见 TrdEnv 的枚举定义
  required uint64 accID = 2; //业务账号, 业务账号与交易环境、市场权限需要匹配，否则会返回错误
  required int32 trdMarket = 3; //交易市场, 参见 TrdMarket 的枚举定义
  optional int32 jpAccType = 4; //JP子账户类型，取值见 TrdSubAccType
}
```

## 交易业务账户

**TrdAcc**

```protobuf
message TrdAcc
{
  required int32 trdEnv = 1; //交易环境，参见 TrdEnv 的枚举定义
  required uint64 accID = 2; //业务账号
  repeated int32 trdMarketAuthList = 3; //业务账户支持的交易市场权限，即此账户能交易那些市场, 可拥有多个交易市场权限，目前仅单个，取值参见 TrdMarket 的枚举定义
  optional int32 accType = 4;   //账户类型，取值见 TrdAccType
  optional string cardNum = 5;  //卡号
  optional int32 securityFirm = 6; //所属券商，取值见SecurityFirm
  optional int32 simAccType = 7; //模拟交易账号类型，取值见SimAccType
  optional string uniCardNum = 8;  //所属综合账户卡号
  optional int32 accStatus = 9; //账号状态，取值见TrdAccStatus
  optional int32 accRole = 10; //账号分类，是不是主账号，取值见TrdAccRole
  repeated int32 jpAccType = 11; //JP子账户类型，取值见 TrdSubAccType
}
```


## 账户资金

**Funds**

```protobuf
message Funds
{
  required double power = 1; //最大购买力（此字段是按照 50% 的融资初始保证金率计算得到的 近似值。但事实上，每个标的的融资初始保证金率并不相同。我们建议您使用 查询最大可买可卖 接口返回的 最大可买 字段，来判断实际可买入的最大数量）
  required double totalAssets = 2; //资产净值
  required double cash = 3; //现金（仅单币种账户使用此字段，综合账户请使用 cashInfoList 获取分币种现金）
  required double marketVal = 4; //证券市值, 仅证券账户适用
  required double frozenCash = 5; //冻结资金
  required double debtCash = 6; //计息金额
  required double avlWithdrawalCash = 7; //现金可提（仅单币种账户使用此字段，综合账户请使用 cashInfoList 获取分币种现金可提）

  optional int32 currency = 8;            //币种，本结构体资金相关的货币类型，取值参见 Currency，期货和综合证券账户适用
  optional double availableFunds = 9;     //可用资金，期货适用
  optional double unrealizedPL = 10;      //未实现盈亏，期货适用
  optional double realizedPL = 11;        //已实现盈亏，期货适用
  optional int32 riskLevel = 12;           //风控状态，参见 CltRiskLevel, 期货适用。建议统一使用 riskStatus 字段获取证券、期货账户的风险状态
  optional double initialMargin = 13;      //初始保证金
  optional double maintenanceMargin = 14;  //维持保证金
  repeated AccCashInfo cashInfoList = 15;  //分币种的现金、现金可提和现金购买力（仅综合账户适用）
  optional double maxPowerShort = 16; //卖空购买力（此字段是按照 60% 的融券保证金率计算得到的近似值。但事实上，每个标的的融券保证金率并不相同。我们建议您使用 查询最大可买可卖 接口返回的 可卖空 字段，来判断实际可卖空的最大数量。）
  optional double netCashPower = 17;  //现金购买力（仅单币种账户使用此字段，综合账户请使用 cashInfoList 获取分币种现金购买力）
  optional double longMv = 18;        //多头市值
  optional double shortMv = 19;       //空头市值
  optional double pendingAsset = 20;  //在途资产
  optional double maxWithdrawal = 21;          //融资可提，仅证券账户适用
  optional int32 riskStatus = 22;              //风险状态，参见 CltRiskStatus，共分 9 个等级，LEVEL1是最安全，LEVEL9是最危险
  optional double marginCallMargin = 23;       //	Margin Call 保证金

  optional bool isPdt = 24;				//是否PDT账户，仅moomoo证券(美国)账户适用
  optional string pdtSeq = 25;			//剩余日内交易次数，仅被标记为 PDT 的moomoo证券(美国)账户适用
  optional double beginningDTBP = 26;		//初始日内交易购买力，仅被标记为 PDT 的moomoo证券(美国)账户适用
  optional double remainingDTBP = 27;		//剩余日内交易购买力，仅被标记为 PDT 的moomoo证券(美国)账户适用
  optional double dtCallAmount = 28;		//日内交易待缴金额，仅被标记为 PDT 的moomoo证券(美国)账户适用
  optional int32 dtStatus = 29;				//日内交易限制情况，取值见 DTStatus。仅被标记为 PDT 的moomoo证券(美国)账户适用
  
  optional double securitiesAssets = 30; // 证券资产净值
  optional double fundAssets = 31; // 基金资产净值
  optional double bondAssets = 32; // 债券资产净值

  repeated AccMarketInfo marketInfoList = 33; //分市场资产信息

  optional double cryptoMv = 34; // 加密货币市值
  optional int32 exposureLevel = 35; // 持仓限额状态，取值见 ExposureLevel
  optional double exposureLimit = 36; // 持仓限额
  optional double usedLimit = 37; // 已用持仓限额
  optional double remainingLimit = 38; // 剩余持仓限额
}
```

## 账户持仓

**Position**

```protobuf
message Position
{
    required uint64 positionID = 1;     //持仓 ID，一条持仓的唯一标识
    required int32 positionSide = 2;    //持仓方向，参见 PositionSide 的枚举定义
    required string code = 3;           //代码
    required string name = 4;           //名称
    required double qty = 5;            //持有数量，2位精度，期权单位是"张"，下同
    required double canSellQty = 6;     //可用数量，是指持有的可平仓的数量。可用数量=持有数量-冻结数量。期权和期货的单位是“张”。
    required double price = 7;          //市价，3位精度，期货为2位精度
    optional double costPrice = 8;      //摊薄成本价（证券账户），平均开仓价（期货账户）。证券无精度限制，期货为2位精度，如果没传，代表此时此值无效
    required double val = 9;            //市值，3位精度, 期货此字段值为0
    required double plVal = 10;         //盈亏金额，3位精度，期货为2位精度
    optional double plRatio = 11;       //盈亏百分比(平均成本价模式)，无精度限制，如果没传，代表此时此值无效
    optional int32 secMarket = 12;      //证券所属市场，参见 TrdSecMarket 的枚举定义
    
	//以下是此持仓今日统计
    optional double td_plVal = 21;      //今日盈亏金额，3位精度，下同, 期货为2位精度
    optional double td_trdVal = 22;     //今日交易额，期货不适用
    optional double td_buyVal = 23;     //今日买入总额，期货不适用
    optional double td_buyQty = 24;     //今日买入总量，期货不适用
    optional double td_sellVal = 25;    //今日卖出总额，期货不适用
    optional double td_sellQty = 26;    //今日卖出总量，期货不适用

    optional double unrealizedPL = 28;       //未实现盈亏（仅期货账户适用）
    optional double realizedPL = 29;         //已实现盈亏（仅期货账户适用）	
    optional int32 currency = 30;        // 货币类型，取值参考 Currency
    optional int32 trdMarket = 31;  //交易市场, 参见 TrdMarket 的枚举定义

    optional double dilutedCostPrice = 32;      //摊薄成本价，仅支持证券账户使用
    optional double averageCostPrice = 33;      //平均成本价，模拟交易证券账户不适用
    optional double averagePlRatio = 34;        //盈亏百分比(平均成本价模式)，无精度限制，如果没传，代表此时此值无效

    optional uint64 comboID = 35;       //期权策略组合 ID
    optional int32 strategyType = 36;   //期权策略类型，参见 Qot_Common.OptionStrategyType 的枚举定义
    optional int32 positionType = 37;   //期权组合持仓类型，参见 PositionType 的枚举定义
    optional uint64 accID = 38;         //交易业务账户 ID
    optional int32 jpAccType = 39;      //日本子账户类型，取值见 TrdSubAccType
}
```

## 订单

**Order**

```protobuf
message Order
{
    required int32 trdSide = 1; //交易方向, 参见 TrdSide 的枚举定义
    required int32 orderType = 2; //订单类型, 参见 OrderType 的枚举定义
    required int32 orderStatus = 3; //订单状态, 参见 OrderStatus 的枚举定义
    required uint64 orderID = 4; //订单号
    required string orderIDEx = 5; //扩展订单号(仅查问题时备用)
    required string code = 6; //代码
    required string name = 7; //名称
    required double qty = 8; //订单数量，2位精度，期权单位是"张"
    optional double price = 9; //订单价格，3位精度
    required string createTime = 10; //创建时间，严格按 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM:SS.MS 格式传
    required string updateTime = 11; //最后更新时间，严格按 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM:SS.MS 格式传
    optional double fillQty = 12; //成交数量，2位精度，期权单位是"张"
    optional double fillAvgPrice = 13; //成交均价，无精度限制
    optional string lastErrMsg = 14; //最后的错误描述，如果有错误，会有此描述最后一次错误的原因，无错误为空
    optional int32 secMarket = 15; //证券所属市场，参见 TrdSecMarket 的枚举定义
    optional double createTimestamp = 16; //创建时间戳
    optional double updateTimestamp = 17; //最后更新时间戳
    optional string remark = 18; //用户备注字符串，最大长度64字节
    optional double auxPrice = 21; //触发价格
    optional int32 trailType = 22; //跟踪类型, 参见Trd_Common.TrailType的枚举定义
    optional double trailValue = 23; //跟踪金额/百分比
    optional double trailSpread = 24; //指定价差
    optional int32 currency = 25;        // 货币类型，取值参考 Currency
    optional int32 trdMarket = 26;  //交易市场, 参见TrdMarket的枚举定义
    optional int32 session = 27; //美股订单时段, 参见Common.Session的枚举定义
    optional int32 jpAccType = 28; //JP子账户类型，取值见 TrdSubAccType
    optional string expireTime = 29;  //timeInForce为GTD时，表示订单到期时间
    optional double orderAmount = 30;  // 订单金额
    optional int32 strategyType = 31;  // 期权策略类型，参见Qot_Common.OptionStrategyType的枚举定义
    repeated Qot_Common.ComboLeg comboLegs = 32; //组合期权各腿数据
}
```

## 订单费用条目

**OrderFeeItem**

```protobuf
message OrderFeeItem
{
    optional string title = 1; //费用名字
    optional double value = 2; //费用金额
}
```

## 订单费用

**OrderFee**

```protobuf
message OrderFee
{
    required string orderIDEx = 1; //扩展订单号
    optional double feeAmount = 2; //费用总额
    repeated OrderFeeItem feeList = 3; //费用明细
}
```

## 成交

**OrderFill**

```protobuf
message OrderFill
{
	required int32 trdSide = 1; //交易方向, 参见 TrdSide 的枚举定义
    required uint64 fillID = 2; //成交号
    required string fillIDEx = 3; //扩展成交号(仅查问题时备用)
    optional uint64 orderID = 4; //订单号
    optional string orderIDEx = 5; //扩展订单号(仅查问题时备用)
    required string code = 6; //代码
    required string name = 7; //名称
    required double qty = 8; //成交数量，2位精度，期权单位是"张"
    required double price = 9; //成交价格，3位精度
    required string createTime = 10; //创建时间（成交时间），严格按 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM:SS.MS 格式传
    optional int32 counterBrokerID = 11; //对手经纪号，港股有效
    optional string counterBrokerName = 12; //对手经纪名称，港股有效
    optional int32 secMarket = 13; //证券所属市场，参见 TrdSecMarket 的枚举定义
    optional double createTimestamp = 14; //创建时间戳
    optional double updateTimestamp = 15; //最后更新时间戳
    optional int32 status = 16; //成交状态, 参见 OrderFillStatus 的枚举定义
    optional int32 trdMarket = 17;  //交易市场, 参见TrdMarket的枚举定义
    optional int32 jpAccType = 18; //JP子账户类型，取值见 TrdSubAccType
}
```

## 最大可交易数量

**MaxTrdQtys**

```protobuf
message MaxTrdQtys
{
	//因目前服务器实现的问题，卖空需要先卖掉多头持仓才能再卖空，是分开两步卖的，买回来同样是逆向两步；而看多的买是可以现金加融资一起一步买的，请注意这个差异
	required double maxCashBuy = 1;             //现金可买（期权的单位是“张”，期货账户不适用）
    optional double maxCashAndMarginBuy = 2;    //最大可买（期权的单位是“张”，期货账户不适用）
    required double maxPositionSell = 3;        //持仓可卖（期权的单位是“张”）
    optional double maxSellShort = 4;           //可卖空（期权的单位是“张”，期货账户不适用）
    optional double maxBuyBack = 5;             //平仓需买入（当持有净空仓时，必须先买回空头持仓的股数，才能再继续买多。期货、期权的单位是“张”）
    optional double longRequiredIM = 6;         //买 1 张合约所带来的初始保证金变动。仅期货和期权适用。无持仓时，返回 买入 1 张的初始保证金占用（正数）。有多仓时，返回 买入1 张的初始保证金占用（正数）。有空仓时，返回 买回 1 张的初始保证金释放（负数）。
    optional double shortRequiredIM = 7;        //卖 1 张合约所带来的初始保证金变动。仅期货和期权适用。无持仓时，返回 卖空 1 张的初始保证金占用（正数）。 有多仓时，返回卖出1 张的初始保证金占用（正数）。有空仓时，返回 卖空1 张的初始保证金释放（正数）。
}
```

## 组合可交易信息

**ComboMaxTrdQtys**

```protobuf
message ComboMaxTrdQtys
{
    optional double nlvChange = 1;    //综合净资产变动
    optional double initialMarginChange = 2;    //初始保证金变动
    optional double maintenanceMarginChange = 3;    //维持保证金变动
    optional double optionBuyPower = 4;    //期权购买力
    optional double maxWithDrawChange = 5;    //最大可提变动
    optional double buyPowerDecrease = 6;    //消耗购买力
}
```

## 组合腿

**ComboLeg**

```protobuf
message ComboLeg
{
	required Qot_Common.Security security = 1; //股票/期权
    optional int32 side = 2; //方向，取值见 Trd_Common.TrdSide
    optional double qtyRatio = 3; //数量比例
    optional uint64 positionID = 4; //持仓ID，仅 moomoo JP 平仓时使用
}
```

## 现金流水数据

**FlowSummaryInfo**

```protobuf
message FlowSummaryInfo
{
	optional string clearingDate = 1; //清算日期
	optional string settlementDate = 2; //结算日期
	optional int32 currency = 3; //币种
	optional string cashFlowType = 4; //现金流类型
	optional int32 cashFlowDirection = 5; //现金流方向 TrdCashFlowDirection
	optional double cashFlowAmount = 6; //金额
	optional string cashFlowRemark = 7; //备注
	optional uint64 cashFlowID = 8; //现金流 ID
}
```

## 过滤条件

**TrdFilterConditions**

```protobuf
message TrdFilterConditions
{
  repeated string codeList = 1; //代码过滤，只返回包含这些代码的数据，没传不过滤
  repeated uint64 idList = 2; //ID 主键过滤，只返回包含这些 ID 的数据，没传不过滤，订单是 orderID、成交是 fillID、持仓是 positionID
  optional string beginTime = 3; //开始时间，严格按 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM:SS.MS 格式传，对持仓无效，拉历史数据必须填
  optional string endTime = 4; //结束时间，严格按 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM:SS.MS 格式传，对持仓无效，拉历史数据必须填
  repeated string orderIDExList = 5; // 服务器订单ID列表，可以用来替代orderID列表，二选一
  optional int32 filterMarket = 6; //指定交易市场, 参见TrdMarket的枚举定义
}
```

---

# 基础功能


## 设置接口信息

`set_client_info(client_id, client_ver)`

* **介绍**

    设置调用接口信息, 非必调接口

* **参数**
    - client_id: client 的标识
    - client_ver: client 的版本号

* **Example**

```python
from futu import *
SysConfig.set_client_info("MyFutuAPI", 0)
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
quote_ctx.close()
```

## 设置协议格式

`set_proto_fmt(proto_fmt)`

* **介绍**

    设置通讯协议 body 格式, 目前支持 Protobuf|Json 两种格式，默认 ProtoBuf, 非必调接口

* **参数**
    - proto_fmt: 协议格式，参见[ProtoFMT](./common.md#1222)

```python
from futu import *
SysConfig.set_proto_fmt(ProtoFMT.Protobuf)
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
quote_ctx.close()
```

* **Example**

## 对所有连接设置协议加密

`enable_proto_encrypt(is_encrypt)`

* **介绍**

    对所有连接的请求和返回内容加密。如需了解协议加密流程，详见 [这里](../qa/other.md#4601)。


* **参数**
    参数|类型|说明
    :-|:-|:-
    is_encrypt|bool|是否启用加密|

* **Example**
    ```python
    from futu import *
    SysConfig.enable_proto_encrypt(is_encrypt = True)
    SysConfig.set_init_rsa_file("conn_key.txt")   # rsa 私钥文件路径
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    quote_ctx.close()
    ```


## 设置私钥路径

`set_init_rsa_file(file)`

* **介绍**

    设置 RSA 私钥文件路径。如需了解协议加密流程，详见 [这里](../qa/other.md#4601)。


* **参数**
    参数|类型|说明
    :-|:-|:-
    file|str|私钥文件路径|

* **Example**

```python
from futu import *
SysConfig.enable_proto_encrypt(is_encrypt = True)
SysConfig.set_init_rsa_file("conn_key.txt")   # rsa 私钥文件路径
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
quote_ctx.close()
```

## 设置线程模式

`set_all_thread_daemon(all_daemon)`

* **介绍**

    是否设置所有内部创建的线程为 daemon 线程。
    - 若设置为 daemon 线程：主线程退出后，则进程也退出。  
      例如：使用实时回调接口时，需要自己保证主线程存活，否则主线程退出后，进程也退出，您将不会再接收到推送数据。
    - 若设置为非 daemon 线程：主线程退出后，进程不会退出。  
      例如：在创建行情或交易对象后，若不调用 close() 关闭连接，即使主线程退出，进程不会退出。

* **参数**
    参数|类型|说明
    :-|:-|:-
    all_daemon|bool|是否设置为 daemon 线程  (- True：设置为 daemon 线程
  - False：设置为非 daemon 线程
  - 默认为 False)

* **Example**

```python
from futu import *
SysConfig.set_all_thread_daemon(True)
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
# 不调用 quote_ctx.close()，进程也会退出
```

## 设置回调

`set_handler(handler)`  

* **介绍**

    设置异步回调处理对象

* **参数**
    - handler: 回调处理对象   
        类|说明
        :-|:-
        SysNotifyHandlerBase|[OpenD 通知处理基类](./init.md#6884)
        StockQuoteHandlerBase|[报价处理基类](../quote/update-stock-quote.md)
        OrderBookHandlerBase|[摆盘处理基类](../quote/update-order-book.md)
        CurKlineHandlerBase|[实时 K 线处理基类](../quote/update-kl.md)
        TickerHandlerBase|[逐笔处理基类](../quote/update-ticker.md)
        RTDataHandlerBase|[分时数据处理基类](../quote/update-rt.md)
        BrokerHandlerBase|[经济队列处理基类](../quote/update-broker.md)
        PriceReminderHandlerBase|[到价提醒处理基类](../quote/update-price-reminder.md)
        TradeOrderHandlerBase|[订单处理基类](../trade/update-order.md)
        TradeDealHandlerBase|[成交处理基类](../trade/update-order-fill.md)


* **Example**

```python
import time
from futu import *
class OrderBookTest(OrderBookHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(OrderBookTest,self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("OrderBookTest: error, msg: %s" % data)
            return RET_ERROR, data
        print("OrderBookTest ", data) # OrderBookTest 自己的处理逻辑
        return RET_OK, data
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
handler = OrderBookTest()
quote_ctx.set_handler(handler)  # 设置实时摆盘回调
quote_ctx.subscribe(['HK.00700'], [SubType.ORDER_BOOK])  # 订阅买卖摆盘类型，OpenD 开始持续收到服务器的推送
time.sleep(15)  #  设置脚本接收 OpenD 的推送持续时间为15秒
quote_ctx.close()  # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅
```

## 获取连接 ID

`get_sync_conn_id()`  

* **介绍**

    获取连接 ID，连接初始化成功后才会有值

* **返回**
    - conn_id: 连接 ID

* **Example**

```python
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
quote_ctx.get_sync_conn_id()
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

## 事件通知回调

`SysNotifyHandlerBase`  

* **介绍**

    通知 OpenD 一些重要消息，类似连接断开等

* **协议 ID**

    1003

* **返回**

    <table>
        <tr>
            <th>参数</th>
            <th>类型</th>
            <th>说明</th>
        </tr>
        <tr>
            <td>ret</td>
            <td><a href="../ftapi/common.html#7467"> RET_CODE</a></td>
            <td>接口调用结果</td>
        </tr>
        <tr>
            <td rowspan="2">data</td>
            <td>tuple</td>
            <td>当 ret == RET_OK 时，返回 <b>事件通知数据</b> </td>
        </tr>
        <tr>
            <td>str</td>
            <td>当 ret != RET_OK，返回错误描述</td>
        </tr>
    </table>

    * **事件通知数据** 的格式如下：
        <table>
            <tr>
                <th>参数</th>
                <th>类型</th>
                <th>说明</th>
            </tr>
            <tr>
                <td>notify_type</td>
                <td>[SysNotifyType](./common.md#5896)</td>
                <td>通知类型</td>
            </tr>
            <tr>
                <td rowspan="3">sub_type</td>
                <td>[ProgramStatusType](./common.md#6427)</td>
                <td>子类型。当 notify_type == SysNotifyType.PROGRAM_STATUS 时，sub_type 返回程序状态类型</td>
            </tr>
            <tr>
                <td>[GtwEventType](./common.md#7799)</td>
                <td>子类型。当 notify_type == SysNotifyType.GTW_EVENT 时，sub_type 返回 OpenD 事件通知类型</td>
            </tr>
            <tr>
                <td>0</td>
                <td>当 notify_type != SysNotifyType.PROGRAM_STATUS 且 notify_type != SysNotifyType.GTW_EVENT 时，sub_type 返回 0</td>
            </tr>
            <tr>
                <td rowspan="2">msg</td>
                <td rowspan="2">dict</td>
                <td>事件信息。当 notify_type == SysNotifyType.CONN_STATUS 时，msg 返回 <b>连接状态事件信息</b> 字典</td>
            </tr>
            <tr>
                <td>事件信息。当 notify_type == SysNotifyType.QOT_RIGHT 时，msg 返回 <b>行情权限事件信息</b> 字典</td>
            </tr>       
        </table>
        
        * **连接状态事件信息** 字典结构如下（连接状态类型为 bool，True 表示连接正常，False 表示连接断开）:
            ```protobuf
            {
                'qot_logined': bool1, 
                'trd_logined': bool2,
            }
            ```        
        * **行情权限事件信息** 字典结构如下（点击了解 [行情权限](../quote/quote.md#2867)）:
            ```protobuf
            {
                'hk_qot_right': value1,
                'hk_option_qot_right': value2,
                'hk_future_qot_right': value3,
                'us_qot_right': value4,
                'us_option_qot_right': value5,
                'us_future_qot_right': value6,  // 已废弃
                'cn_qot_right': value7,
				'us_index_qot_right': value8,
				'us_otc_qot_right': value9,
				'sg_future_qot_right': value10,
				'jp_future_qot_right': value11,
				'us_future_qot_right_cme': value12,
				'us_future_qot_right_cbot': value13,
				'us_future_qot_right_nymex': value14,
				'us_future_qot_right_comex': value15,
				'us_future_qot_right_cboe': value16,
            }
            ```

* **Example**

```python
import time
from futu import *


class SysNotifyTest(SysNotifyHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(SysNotifyTest, self).on_recv_rsp(rsp_str)
        notify_type, sub_type, msg = data
        if ret_code != RET_OK:
            logger.debug("SysNotifyTest: error, msg: {}".format(msg))
            return RET_ERROR, data
        if notify_type == SysNotifyType.GTW_EVENT:  # OpenD 事件通知
            print("GTW_EVENT, type: {} msg: {}".format(sub_type, msg))
        elif notify_type == SysNotifyType.PROGRAM_STATUS:  # 程序状态变化通知
            print("PROGRAM_STATUS, type: {} msg: {}".format(sub_type, msg))
        elif notify_type == SysNotifyType.CONN_STATUS:  ## 连接状态变化通知
            print("CONN_STATUS, qot: {}".format(msg['qot_logined']))
            print("CONN_STATUS, trd: {}".format(msg['trd_logined']))
        elif notify_type == SysNotifyType.QOT_RIGHT:  # 行情权限变化通知
            print("QOT_RIGHT, hk: {}".format(msg['hk_qot_right']))
            print("QOT_RIGHT, hk_option: {}".format(msg['hk_option_qot_right']))
            print("QOT_RIGHT, hk_future: {}".format(msg['hk_future_qot_right']))
            print("QOT_RIGHT, us: {}".format(msg['us_qot_right']))
            print("QOT_RIGHT, us_option: {}".format(msg['us_option_qot_right']))
            print("QOT_RIGHT, cn: {}".format(msg['cn_qot_right']))
			print("QOT_RIGHT, us_index: {}".format(msg['us_index_qot_right']))
			print("QOT_RIGHT, us_otc: {}".format(msg['us_otc_qot_right']))
			print("QOT_RIGHT, sg_future: {}".format(msg['sg_future_qot_right']))
			print("QOT_RIGHT, jp_future: {}".format(msg['jp_future_qot_right']))
            print("QOT_RIGHT, us_future_cme: {}".format(msg['us_future_qot_right_cme']))
            print("QOT_RIGHT, us_future_cbot: {}".format(msg['us_future_qot_right_cbot']))
            print("QOT_RIGHT, us_future_nymex: {}".format(msg['us_future_qot_right_nymex']))
            print("QOT_RIGHT, us_future_comex: {}".format(msg['us_future_qot_right_comex']))
            print("QOT_RIGHT, us_future_cboe: {}".format(msg['us_future_qot_right_cboe']))
        return RET_OK, data


quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
handler = SysNotifyTest()
quote_ctx.set_handler(handler)  # 设置回调
time.sleep(15)  # 设置脚本接收 OpenD 的推送持续时间为15秒
quote_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽`
```

## 设置是否在控制台打印连接信息

`enable_console_log(enable)`

* **介绍**

    设置是否在控制台打印Python脚本与OpenD连接的状态信息, 非必调接口。
    非线程安全，如有必要，在程序开始处调用。

* **参数**
    参数|类型|说明
    :-|:-|:-
    enable|bool|是否在控制台打印连接状态信息  (- True：打印
  - False：不打印
  - 默认为 True)


* **Example**

```python
from futu import *
SysConfig.enable_console_log(True)
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
quote_ctx.close()
```

---

# 通用定义

## 接口调用结果

> **RET_CODE**  

* `RET_OK`

  成功

* `RET_ERROR`  

  失败

## 协议格式

> **ProtoFMT**   

* `Protobuf`  

  Google Protobuf 格式

* `Json`
  
  Json 格式

## 包加密算法


## 程序状态类型

> **ProgramStatusType**

* `NONE`  

  未知

* `LOADED`
  
  已完成必要模块加载

* `LOGING`  

  登录中

* `NEED_PIC_VERIFY_CODE`
  
  需要图形验证码

* `NEED_PHONE_VERIFY_CODE`  

  需要手机验证码

* `LOGIN_FAILED`
  
  登录失败

* `FORCE_UPDATE`  

  客户端版本过低

* `NESSARY_DATA_PREPARING`
  
  正在拉取必要信息

* `NESSARY_DATA_MISSING`  

  缺少必要信息

* `UN_AGREE_DISCLAIMER`
  
  未同意免责声明

* `READY`  

  正常可用状态

* `FORCE_LOGOUT`
  
  OpenD 登录后被强制退出登录

## 网关事件通知类型

> **GtwEventType**

* `LocalCfgLoadFailed` 

  本地配置文件加载失败

* `APISvrRunFailed`
  
  网关监听服务运行失败

* `ForceUpdate`  

  强制升级网关

* `LoginFailed`
  
  登录富途服务器失败

* `UnAgreeDisclaimer`  

  未同意免责声明，无法运行

* `LOGIN_FAILED`
  
  登录失败

* `NetCfgMissing`  

  缺少网络连接配置

* `KickedOut`
  
  登录被踢下线

* `LoginPwdChanged`
  
  登录密码变更

* `BanLogin`  

  牛牛后台不允许该账号登录

* `NeedPicVerifyCode`
  
  登录需要输入图形验证码

* `NeedPhoneVerifyCode`
  
  登录需要输入手机验证码

* `AppDataNotExist`  

  程序打包数据丢失

* `NessaryDataMissing`
  
  必要的数据没同步成功

* `TradePwdChanged`  

  交易密码变更通知

* `EnableDeviceLock`
  
  需启用设备锁


## 系统通知类型

> **SysNotifyType**

* `GTW_EVENT`  

  网关事件

* `PROGRAM_STATUS`
  
  程序状态变化

* `CONN_STATUS`  

  与后台服务的连接状态变化

* `QOT_RIGHT`
  
  行情权限变化

## 包唯一标识

**PacketID** 

```protobuf
message PacketID
{
	  required uint64 connID = 1; //当前 TCP 连接的连接 ID，一条连接的唯一标识，InitConnect 协议会返回
	  required uint32 serialNo = 2; //自增序列号
}
```

## 程序状态

**ProgramStatus**

```protobuf
message ProgramStatus
{
	  required ProgramStatusType type = 1; //当前状态
	  optional string strExtDesc = 2; // 额外描述
}
```

---

# 底层协议介绍

Futu API 是富途为主流的编程语言（Python、Java、C#、C++、JavaScript）封装的 API SDK，以方便您调用，降低策略开发难度。  
这部分主要介绍策略脚本与 OpenD 服务之间通信的底层协议，适用于非上述 5 种编程语言用户，自行对接实现底层裸协议。

:::tip 提示
* 如果您使用的编程语言在上述的 5 种主流编程语言之内，可以直接跳过这部分内容。
:::

## 协议请求流程
* 建立连接
* 初始化连接
* 请求数据或接收推送数据
* 定时发送 KeepAlive 保持连接

![proto-process](../img/proto-process.png)


## 协议设计
协议数据包括协议头以及协议体，协议头固定字段，协议体根据具体协议决定。

### 协议头

```
struct APIProtoHeader
{
    u8_t szHeaderFlag[2];
    u32_t nProtoID;
    u8_t nProtoFmtType;
    u8_t nProtoVer;
    u32_t nSerialNo;
    u32_t nBodyLen;
    u8_t arrBodySHA1[20];
    u8_t arrReserved[8];
};
```
字段|说明
:-|:-
szHeaderFlag|包头起始标志，固定为“FT”
nProtoID|协议 ID
nProtoFmtType|协议格式类型，0 为 Protobuf 格式，1 为 Json 格式
nProtoVer|协议版本，用于迭代兼容，目前填 0
nSerialNo|包序列号，用于对应请求包和回包，要求递增
nBodyLen|包体长度
arrBodySHA1|包体原始数据(解密后)的 SHA1 哈希值
arrReserved|保留 8 字节扩展

::: tip 提示
* u8_t 表示 8 位无符号整数，u32_t 表示 32 位无符号整数
* OpenD 内部处理使用 Protobuf，因此协议格式建议使用 Protobuf，减少 Json 转换开销
* nProtoFmtType 字段指定了包体的数据类型，回包会回对应类型的数据；推送协议数据类型由 OpenD 配置文件指定
* **arrBodySHA1 用于校验请求数据在网络传输前后的一致性，必须正确填入**
* **协议头的二进制流使用的是小端字节序，即一般不需要使用 ntohl 等相关函数转换数据**
:::

### 协议体
#### Protobuf 协议请求包体结构
```
message C2S
{
    required int64 req = 1;
}

message Request
{
    required C2S c2s = 1;
}
```

#### Protobuf 协议回应包体结构
```
message S2C
{
    required int64 data = 1;
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```

字段|说明
:-|:-
c2s|请求参数结构
req|请求参数，实际根据协议定义
retType|请求结果
retMsg|若请求失败，说明失败原因
errCode|若请求失败对应错误码
s2c|回应数据结构，部分协议不返回数据则无该字段
data|回应数据，实际根据协议定义

::: tip 提示
* 包体格式类型请求包由协议头 nProtoFmtType 指定，OpenD 主动推送格式在 [InitConnect](../ftapi/init.md#1515) 设置。
* 原始协议文件格式是以 Protobuf 格式定义，若需要 json 格式传输，建议使用 protobuf3 的接口直接转换成 json。
* 枚举值字段定义使用有符号整形，注释指明对应枚举，枚举一般定义于 Common.proto，Qot_Common.proto，Trd_Common.proto 文件中。
* 协议中价格、百分比等数据用浮点类型来传输，直接使用会有精度问题，需要根据精度（如协议中未指明，默认小数点后三位）做四舍五入之后再使用。
:::

## 心跳保活

```protobuf
syntax = "proto2";
package KeepAlive;
option java_package = "com.futu.openapi.pb";
option go_package = "github.com/futuopen/ftapi4go/pb/keepalive";

import "Common.proto";

message C2S
{
	required int64 time = 1; //客户端发包时的格林威治时间戳，单位秒
}

message S2C
{
	required int64 time = 1; //服务器回包时的格林威治时间戳，单位秒
}

message Request
{
	required C2S c2s = 1;
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```

* **介绍**

    心跳保活

* **协议 ID**

    1004

* **使用**

    根据[初始化链接](./init.md#1990)返回的心跳保活间隔时间，向 OpenD 发送保活协议

## 加密通信流程

* 若 OpenD 配置了加密，[InitConnect](../ftapi/init.md#1515) 初始化连接协议必须使用 [RSA](../qa/other.md#4601) 公钥加密，后续其他协议使用 InitConnect 返回的随机密钥进行 AES 加密通信。
* OpenD 的加密流程借鉴了 SSL 协议，但考虑到一般是本地部署服务和应用，简化了相关流程，OpenD 与接入 Client 共用了同一个 [RSA](../qa/other.md#4601) 私钥文件，请妥善保存和分发私钥文件。
* 可到这个 [网址](http://web.chacuo.net/netrsakeypair) 在线生成随机 [RSA](../qa/other.md#4601) 密钥对，密钥格式必须为 PCKS#1，密钥长度 512，1024 都可以，不要设置密码，将生成的私钥复制保存到文件中，然后将私钥文件路径配置到 [OpenD 配置](../opend/opend-cmd.md#8799) 约定的 **rsa_private_key** 配置项中。
*  **建议有实盘交易的用户配置加密，避免账户和交易信息泄露。**

![encrypt](../img/encrypt.png)


## RSA 加解密
* [OpenD 配置](../opend/opend-cmd.md#8799) 约定 **rsa_private_key** 为私钥文件路径
* OpenD 与接入客户端共用相同的私钥文件
* RSA 加解密仅用于 InitConnect 请求，用于安全获取其它请求协议的对称加密 Key
* OpenD 的 [RSA](../qa/other.md#4601) 密钥为 1024 位，填充方式 PKCS1，公钥加密，私钥解密，公钥可通过私钥生成
* Python API 参考实现：[RsaCrypt](https://github.com/FutunnOpen/py-futu-api/tree/master/futu/common/sys_config.py) 类的 encrypt / decrypt 接口

### 发送数据加密
* RSA 加密规则:若密钥位数是 key_size，单次加密串的最大长度为 (key_size)/8 - 11，目前位数 1024，一次加密长度可定为 100。
* 将明文数据分成一个或数个最长 100 字节的小段进行加密，拼接分段加密数据即为最终的 Body 加密数据。

### 接收数据解密
* RSA 解密同样遵循分段规则，对于 1024 位密钥，每小段待解密数据长度为 128 字节。
* 将密文数据分成一个或数个 128 字节长的小段进行解密，拼接分段解密数据即为最终的 Body 解密数据。

## AES 加解密
* 加密 key 由 InitConnect 协议返回
* 默认使用的是 AES 的 ecb 加密模式。
* Python API 参考实现: [ConnMng](https://github.com/FutunnOpen/py-futu-api/tree/master/futu/common/conn_mng.py) 类的 encrypt_conn_data / decrypt_conn_data 接口

### 发送数据加密

* AES 加密要求源数据长度必须是 16 的整数倍，故需补‘0’对齐后再加密，记录 mod_len 为源数据长度与 16 取模值。
* 因加密前有可能对源数据作修改，故需在加密后的数据尾再增加一个 16 字节的填充数据块，其最后一个字节赋值 mod_len，其余字节赋值‘0’，将加密数据和额外的填充数据块拼接作为最终要发送协议的 body 数据。

### 接收数据解密

* 协议 body 数据，先将最后一个字节取出，记为 mod_len，然后将 body 截掉尾部 16 字节填充数据块后再解密（与加密填充额外数据块逻辑对应）。
* mod_len 为 0 时，上述解密后的数据即为协议返回的 body 数据，否则需截掉尾部(16 - mod_len)长度的用于填充对齐的数据。

![aes](../img/aes.png)

---

# OpenD 相关


## Q1：OpenD 因未完成“问卷评估及协议确认”自动退出

A: 您需要进行相关问卷评估及协议确认，才可以使用 OpenD，请先 [前往完成](https://www.futunn.com/about/api-disclaimer?lang=zh-CN)。

## Q2：OpenD 因”程序自带数据不存在“退出

A: 一般因权限问题导致自带数据拷贝失败，可以尝试将程序目录下 <font color=Gray> __*Appdata.dat*__ </font> 解压后的文件拷贝到程序数据目录下。

* windows 程序数据目录:`%appdata%/com.futunn.FutuOpenD/F3CNN`
* 非 windows 程序数据目录:`~/.com.futunn.FutuOpenD/F3CNN`

## Q3：OpenD 服务启动失败

A: 请检查：
1. 是否有其他程序占用所配置的端口；
2. 是否已经有配置了相同端口的 OpenD 在运行。

## Q4：如何验证手机验证码？

A: 在 OpenD 界面上或远程到 Telnet 端口，输入命令`input_phone_verify_code -code=123456`。

::: tip 提示
* 123456 是收到的手机验证码
* -code=123456 前有空格
:::

## Q5：是否支持其他编程语言？

A: OpenD 有对外提供基于 socket 的协议，目前我们提供并维护 Python，C++，Java，C# 和 JavaScript 接口，[下载入口](https://www.futunn.com/download/OpenAPI)。

如果上述语言仍不能满足您的需求，您可以自行对接 Protobuf 协议。

## Q6：在同一设备多次验证设备锁 

A: 设备标识随机生成并存放于 

windows: %appdata%/com.futunn.FutuOpenD/F3CNN/Device.dat 文件中。
非windows: ~/.com.futunn.FutuOpenD/F3CNN/Device.dat

::: tip 提示
1. 如果文件被删除或损坏，OpenD 会重新生成新设备标识，然后验证设备锁。  
2. 另外镜像拷贝部署的用户需要注意，如果多台机器的 Device.dat 内容相同，也会导致这些机器多次验证设备锁。删除 Device.dat 文件即可解决。
:::

## Q7：OpenD 是否有提供 Docker 镜像？

A: 目前没有提供。

## Q8：一个账号可以登录多个 OpenD 吗？

A: 一个账号可以在多台机器上登录 OpenD 或者其他客户终端，最多允许 10 个 OpenD 终端同时登录。同时有“行情互踢”的限制，只能有一个 OpenD 获得最高权限行情。例如：两个终端登录同一个账号，只能有一个港股 LV2 行情，另一个是港股 BMP 行情。

## Q9：如何控制 OpenD 和其他客户端（桌面端和移动端）的行情权限？

A: 应交易所的规定，多个终端同时在线会有“行情互踢”的限制，只能有一个终端获得最高权限行情。OpenD 命令行版本的启动参数中，内置了 [auto_hold_quote_right](../opend/opend-cmd.md#8799) 参数，用于灵活配置行情权限。当该参数选项开启时，OpenD 在行情权限被抢后，会自动抢回。如果 10 秒内再次被抢，则其他终端获得最高行情权限（OpenD 不会再抢）。

## Q10：如何优先保证 OpenD 行情权限？

A: 
1. 将 OpenD 启动参数 [auto_hold_quote_right](../opend/opend-cmd.md#8799) 配置为 1；
2. 保证不要在移动端或桌面端富途牛牛上在 10 秒内连续两次抢最高权限（登录算一次，点击“重启行情”算第二次）。

![quote-right-kick](../img/quote-right-kick.png)

## Q11：如何优先保证移动端（或桌面端）的行情权限？

A: OpenD 启动参数 [auto_hold_quote_right](../opend/opend-cmd.md#8799) 设置为 0，移动端或桌面端富途牛牛在 OpenD 之后登录即可。 

## Q12：使用可视化 OpenD 记住密码登录，长时间挂机后提示连接断开，需要重新登录？

A: 使用可视化 OpenD，如果选择记住密码登录，用的是记录在本地的令牌。由于令牌有时间限制，当令牌过期后，如果出现网络波动或富途后台发布，就可能导致与后台断开连接后无法自动连接上的情况。因此，可视化 OpenD 如果希望长时间挂机，建议手动输入密码登录，由 OpenD 自动处理该情况。


## Q13：遇到产品缺陷，如何请富途的研发工程师排查日志？

A: 
1. 与客服沟通问题表现，详述：发生错误的时间、OpenD 版本号、 API 版本号、脚本语言名、接口名或协议号、含详细入参和返回的短代码或截图。

2. 客服确认是产品缺陷后，如需进一步日志排查，研发工程师会主动联系。

3. 部分问题须提供 OpenD 日志，方便定位确认问题。交易类问题需要 info 日志级别，行情类问题需要 debug 日志级别。日志级别 log_level 可以在 <font color=Gray> __*OpenD.xml*__ </font> 中 [配置](../opend/opend-cmd.md#8799) ，配置后需要重启 OpenD 方能生效，待问题复现后，将该段日志打包发给富途研发工程师。

:::tip 提示
日志路径如下：  
windows：`%appdata%/com.futunn.FutuOpenD/Log`

非 windows：`~/.com.futunn.FutuOpenD/Log`
:::

## Q14：脚本连接不上 OpenD

A: 请先尝试检查：
1. 脚本连接的端口与 OpenD 配置的端口是否一致。
2. 由于 OpenD 连接上限为 128，是否有无用连接未关闭。
3. 检查监听地址是否正确，如果脚本和 OpenD 不在同一机器，OpenD 监听地址需要设置成 0.0.0.0 。

## Q15：连接上一段时间后断开

A: 如果是自己对接协议，检查下是否有定时发送心跳维持连接。


## Q16：Linux 下通过 multiprocessing 模块以多进程方式运行 Python 脚本，连不上 OpenD？

A: Linux/Mac 环境下以默认方式创建进程后，父进程中 py-futu-api 内部创建的线程将会在子进程中消失，导致程序内部状态错误。  
可以用 spawn 方式来启动进程：

```python
import multiprocessing as mp
mp.set_start_method('spawn')
p = mp.Process(target=func)
```


## Q17：如何在一台电脑同时登录两个 OpenD?

A: 可视化 OpenD 不支持，命令行 OpenD 支持。

1. 解压从官网下载的文件，复制整个命令行 OpenD 文件夹（如 OpenD_5.2.1408_Windows）得到副本（此处以 Windows 为例，其他系统可采取相同操作）。

![file-page](../img/nnfile-page.png)

2. 分别打开两个命令行 OpenD 文件夹配置好两份 OpenD.xml 文件。

第一份配置文件参数：api_port = 11111，login_account = 登录账号1，login_pwd = 登录密码1

第二份配置文件参数：api_port = 11112，login_account = 登录账号2，login_pwd = 登录密码2

![order-page](../img/nnorder-page.png)

3. 配置完成后，分别打开两个 OpenD 程序运行。

![fod-page](../img/nnfod-page.png)

4. 调用接口时，注意接口的参数`port`（OpenD 监听端口）与 OpenD.xml 文件中的参数`api_port`为对应关系  
例如：

```python
from futu import *

# 向账号1登录的 OpenD 进行请求
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111, is_encrypt=False)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽

# 向账号2登录的 OpenD 进行请求
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11112, is_encrypt=False)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

## Q18：行情权限被其他客户端踢掉，如何通过脚本执行抢权限的运维命令？
A：
1. 在OpenD启动参数中，配置好 Telnet 地址和 Telnet 端口。
![telnet_GUI](../img/telnet_GUI.jpg)
![telnet_CMD](../img/telnet_CMD.jpg)
2. 启动 OpenD（会同时启动 Telnet）。
3. 当发现行情权限被抢之后，您可以参考如下代码示例，通过 Telnet，向 OpenD 发送 `request_highest_quote_right` 命令。
```python
from telnetlib import Telnet
with Telnet('127.0.0.1', 22222) as tn:  # Telnet 地址为：127.0.0.1，Telnet 端口为：22222
    tn.write(b'request_highest_quote_right\r\n')
    reply = b''
    while True:
        msg = tn.read_until(b'\r\n', timeout=0.5)
        reply += msg
        if msg == b'':
            break
    print(reply.decode('gb2312'))
```

<span id="update-failed-qa"></span>

## Q19：OpenD 自动升级失败

A：
通过`update`命令执行 OpenD 自动更新失败，可能的原因：
- 文件被其他进程占用：可以尝试关闭其他 OpenD 进程，或者重启系统后，再次执行 `update`
如果以上仍无法解决，可以通过[官网](https://www.futunn.com/download/OpenAPI?lang=zh-CN)自行下载更新。

## Q20：ubuntu22无法启动可视化 OpenD？
A：
在有些Linux发行版（例如Ubuntu 22.04）运行可视化OpenD时，可能会提示：`dlopen(): error loading libfuse.so.2`。
这是因为这些系统没有默认安装libfuse。通常可以手动安装来解决，例如对于Ubuntu22.04，可以在命令行运行：
```
sudo apt update
sudo apt install -y libfuse2
```
安装成功后就可以正常运行可视化OpenD了。详细信息请参考：[https://docs.appimage.org/user-guide/troubleshooting/fuse.html](https://docs.appimage.org/user-guide/troubleshooting/fuse.html)。

## Q21：Linux上如何在后台运行命令行OpenD？


A：先切到 FutuOpenD 所在目录，配置好 FutuOpenD.xml 之后，执行如下命令
```
nohup ./FutuOpenD &
```

---

# 行情相关


## Q1：订阅失败

A: 订阅接口返回错误，有以下两类常见情况：
* 订阅额度不足：

  订阅额度规则参见 [订阅额度 & 历史 K 线额度](../intro/authority.md#1314)

* 订阅权限不足：

  支持订阅的行情权限见下表
  <table>
    <tr>
      <th> 市场 </th>
      <th> 品种 </th>
      <th> 支持订阅的行情权限 </th>
    </tr>
    <tr>
      <td rowspan="3"> 香港市场 </td>
      <td > 股票 </td>
      <td > LV1, LV2, SF </td>
    </tr>
    <tr>
	    <td> 期权</td>
      <td> LV1, LV2</td>
    </tr>
    <tr>
	    <td> 期货</td>
      <td> LV1, LV2</td>
    </tr>
    <tr>
      <td rowspan="3"> 美国市场 </td>
      <td > 股票 </td>
      <td > LV1, LV2 </td>
    </tr>
    <tr>
	    <td> 期权</td>
      <td> LV1</td>
    </tr>
    <tr>
	    <td> 期货</td>
      <td> LV1, LV2</td>
    </tr>
    <tr>
      <td > A 股市场 </td>
      <td > 股票 </td>
      <td > LV1 </td>
    </tr>
    <tr>
      <td > 新加坡市场 </td>
      <td > 股票 </td>
      <td > LV1, LV2 </td>
    </tr>
    <tr>
      <td > 马来西亚市场 </td>
      <td > 股票 </td>
      <td > LV1, LV2, LV3 </td>
    </tr>
    <tr>
      <td > 日本市场 </td>
      <td > 股票 </td>
      <td > LV2, LV3 </td>
    </tr>
</table>

  获取行情权限的方式参见 [行情权限](../intro/authority.html#2867) 

  注意：若账号拥有上述权限，但仍订阅失败，可能存在被其他终端 [踢掉行情权限](./opend.html#1228) 的情况。

## Q2：反订阅失败

A: 订阅至少一分钟后才能反订阅。

## Q3：反订阅成功但没释放额度

A: 所有连接都对该行情反订阅，才会释放额度。

举例：A 连接和 B 连接都在订阅 HK.00700 的摆盘，当 A 连接反订阅后，由于 B 连接仍在调用腾讯的摆盘数据，因此 OpenD 的额度不会释放，直至所有连接都反订阅 HK.00700 的摆盘。


## Q4：订阅不足一分钟关闭脚本连接，会释放额度吗？

A: 不会。连接关闭后，订阅时长不足一分钟的标的类型，会在达到一分钟后才自动反订阅，并释放相应的订阅额度。


## Q5：请求限频的具体限制逻辑是怎样？

A: 30 秒内最多 n 次，是指第 1 次和第 n+1 次请求间隔需要大于 30 秒。

## Q6：自选股添加不上是什么原因？

A: 请先检查是否有超出上限，或者删除一部分自选。

## Q7：为什么 API 端的美股报价和牛牛客户端的报价有不同？

A: 由于美股交易分散在很多家交易所，富途提供多种美股基本报价行情。 自4 月 16 日起，Futu API **免费开放**美股实时行情权限（推广期限免）。原需单独购买行情卡才可获取的深度摆盘美股行情，现已调整为免费。Futu API 会接入两种美股报价行情：Nasdaq Basic + TotalView（Nasdaq 交易所60档），NYSE Arcabook（Arca 60档）。     
如果您发现美股当天开盘价与客户端显示不一致，这是因为 Futu API 实时上游行情会综合 Nasdaq 和 NYSE Arcabook 数据。


## Q8：API 行情卡在哪里购买？

A:  
* 港股市场
  * [港股 LV2 高级行情（仅港澳台及海外 IP）](https://qtcardfthk.futufin.com/buy?market_id=1&amp;channel=2&amp;good_type=1#/)
  * [港股期权期货 LV2高级行情（仅港澳台及海外 IP）](https://qtcardfthk.futufin.com/buy?market_id=1&amp;channel=2&amp;good_type=8#/)
  * [港股 LV2 + 期权期货 LV2 行情（仅港澳台及海外 IP）](https://qtcardfthk.futufin.com/buy?market_id=1&amp;channel=2&amp;good_type=9#/)
  * [港股高级全盘行情（SF 行情）](https://qtcardfthk.futufin.com/buy?market_id=1&amp;channel=2&amp;good_type=10#/)
  
* 美股市场 (**限时推免**)
  * [Nasdaq Basic](https://qtcardfthk.futufin.com/buy?market_id=2&amp;channel=2&amp;good_type=12#/)
  * [Nasdaq Basic+TotalView (Non-Pro)](https://qtcardfthk.futufin.com/buy?market_id=2&good_type=18&channel=2#/)
  * [Nasdaq Basic+TotalView (Pro)](https://qtcardfthk.futufin.com/buy?market_id=2&good_type=19&channel=2#/)
  * [期权 OPRA 实时行情](https://qtcardfthk.futufin.com/buy?market_id=2&good_type=16&qtcard_channel=2#/)


## Q9：为什么有时候，获取实时数据的 get 接口响应比较慢？

A: 因为获取实时数据的 get 接口需要先订阅，并依赖后台给 OpenD 的推送。如果用户刚订阅就立刻用 get 接口请求，OpenD 有可能尚未收到后台推送。为了防止这种情况的发生，get 接口内置了等待逻辑，3 秒内收到推送会立刻返回给脚本，超过 3 秒仍未收到后台推送，才会给脚本返回空数据。  
涉及的 get 接口包括：get_rt_ticker、get_rt_data、get_cur_kline、get_order_book、get_broker_queue、get_stock_quote。因此，当发现获取实时数据的 get 接口响应比较慢时，可以先检查一下是否是无成交数据的原因。


## Q10：API 美股 Nasdaq 行情卡限免，可以获取哪些数据？

A: 自 4 月 16日起，Nasdaq Basic+TotalView 行情卡和 NYSE Arcabook 行情权限，将限时推免。您可免费获取的品类涵盖 Nasdaq、NYSE、NYSE MKT 交易所上市证券（包括美股正股和 ETF，不包括美股期货和美股期权）。    
支持的数据接口包括：快照，历史 K 线，实时逐笔订阅，实时一档摆盘订阅，实时 K 线订阅，实时报价订阅，实时分时订阅，到价提醒。


## Q11：各个行情品类的摆盘支持多少档？

A: 
行情品类|LV1|LV2|LV3|SF
:-|:-|:-|:-|:-
港股（含正股、窝轮、牛熊、界内证）|/|10|/|全盘+千笔明细
港股期权期货|1|10|/|/
美股（含 ETF）|1|60档|Nasdaq 60档+Arca 60档|/
美股期权|1|/|/|/
美股期货 |/|40档|/|/
A 股|5|/|/|/
新加坡股票|1|40|/|/
马来西亚股票|3|5|10|/
日本股票|/|10|40|/

## Q12：为什么我购买激活了行情卡之后，OpenD 仍然没有行情权限？

A:   
1. 由于 Futu API 的行情权限跟 APP 的行情权限不完全一样，部分行情卡仅适用于 APP 端。请先确认您所购买的行情卡是否是 OpenD 适用的。   
我们已将 Futu API 适用的 **所有** 行情卡列在《权限与限制》一节，请点击 [这里](/intro/authority.html#2867) 查看。
2. 行情卡购买激活成功后，是立即生效的。请 **重新启动 OpenD** 后，再次查看权限状态。


## Q13：如何通过订阅接口获取实时行情？
**第一步：订阅**  

将标的的代码和数据类型传入 [订阅接口](../quote/sub.md)，完成订阅。  

订阅接口支持了实时报价、实时摆盘、实时逐笔、实时分时、实时 K 线、实时经纪队列数据的获取。订阅成功后，OpenD 会持续收到富途服务器的实时数据推送。

注意：订阅额度会根据您的总资产、交易笔数和交易量，来进行分配，具体规则参见 [订阅额度 & 历史 K 线额度](../intro/authority.md#1314)。所以，如果您的订阅额度不足，可以先检查一下是否有无用的订阅在占用额度，及时 [反订阅](../quote/sub.md) 即可释放已占用的订阅额度。

**第二步：取数据**  

如何将订阅推送的数据从 OpenD 取回脚本呢？我们提供了如下两种方式：

**方式 1：实时数据回调**  
设置相应的回调函数，来异步处理 OpenD 收到的数据推送。  

设置好回调函数后，OpenD 会将收到的实时数据，立即推给脚本的回调函数进行处理。  

如果所订阅的标的比较活跃，此时的推送数据可能数据量较大且频率较高。如果您希望适当降低 OpenD 给脚本的推送频率，建议在 [OpenD 启动参数](../opend/opend-cmd.md#8799) 中配置 API 推送频率（`qot_push_frequency`）。  

方式 1 涉及的接口包括：[实时报价回调](../quote/update-stock-quote.md)、[实时摆盘回调](../quote/update-order-book.md)、[实时 K 线回调](../quote/update-kl.md)、[实时分时回调](../quote/update-rt.md)、[实时逐笔回调](../quote/update-ticker.md)、[实时经纪队列回调](../quote/update-broker.md)。

**方式 2：获取实时数据**  
通过获取实时数据接口，可以将 OpenD 收到的最新的数据，取回脚本。这种方式更加灵活，脚本不需要处理海量的推送。只要 OpenD 在持续接收富途服务器的推送，脚本可以随用随取，不用不取。  

由于是从 OpenD 接收的推送数据中取，所以这类接口没有频率限制。  

方式 2 涉及的接口包括：[获取实时报价](../quote/get-stock-quote.md)、[获取实时摆盘](../quote/get-order-book.md)、[获取实时 K 线](../quote/get-kl.md)、[获取实时分时](../quote/get-rt.md)、[获取实时逐笔](../quote/get-ticker.md)、[获取实时经纪队列](../quote/get-broker.md)。

## Q14：各个市场状态对应什么时间段？
A: 
<table>
    <tr>
        <th>市场</th>
        <th>品类</th>
        <th>市场状态</th>
        <th>时间段（当地时间）</th>
    </tr>
    <tr>
        <td rowspan="19" width = "15%">香港市场</td>
	    <td rowspan="8" width = "15%">证券类产品（含股票、ETFs、窝轮、牛熊、界内证）</td>
	    <td> * NONE：无交易</td>
      <td> CST 08:55 - 09:00</td>
    </tr>
    <tr>
	    <td >* AUCTION：盘前竞价</td>
      <td> CST 09:00 - 09:20</td>
    </tr>
    <tr>
	    <td >* WAITING_OPEN：等待开盘</td>
      <td> CST 09:20 - 09:30</td>
    </tr>
    <tr>
	    <td>* MORNING：早盘</td>
      <td> CST 09:30 - 12:00</td>
    </tr>
    <tr>
      <td>* REST: 午间休市</td>
	    <td>CST 12:00 - 13:00</td>
    </tr>
    <tr>
	    <td>* AFTERNOON：午盘</td>
      <td>CST 13:00 - 16:00</td>
    </tr>
    <tr>
	    <td>* HK_CAS：港股盘后竞价（港股市场增加 CAS 机制对应的市场状态）</td>
      <td>CST 16:00 - 16:08</td>
    </tr>
    <tr>
	    <td>* CLOSED：收盘</td>
      <td>CST 16:08 - 08:55（T+1）</td>
    </tr>
    <tr>
	    <td rowspan="5">期权、期货（仅日市）</td>
      <td>* NONE：期权待开盘</td>
      <td> CST 08:55 - 09:30</td>
    </tr>
    <tr>
	    <td>* MORNING：早盘</td>
      <td>CST 09:30 - 12:00</td>
    </tr>
    <tr>
      <td>* REST: 午间休市</td>
	    <td>CST 12:00 - 13:00</td>
    </tr>
    <tr>
	    <td>* AFTERNOON：午盘</td>
      <td>CST 13:00 - 16:00</td>
    </tr>
    <tr>
	    <td>* CLOSED：收盘</td>
      <td>CST 16:00 - 08:55（T+1）</td>
    </tr>
    <tr>
	    <td rowspan="6">期货（日夜市）</td>
      <td>* FUTURE_DAY_WAIT_FOR_OPEN：期货待开盘</td>
      <td rowspan="6"> 不同品种交易时间不同</td>
    </tr>
    <tr>
	    <td>* NIGHT_OPEN: 夜市交易时段</td>
    </tr>
    <tr>
	    <td>* NIGHT_END：夜市收盘</td>
    </tr>
    <tr>
	    <td>* FUTURE_DAY_WAIT_FOR_OPEN：期货待开盘</td>
    </tr>
    <tr>
	    <td>* FUTURE_DAY_OPEN：日市交易时段</td>
    </tr>
    <tr>
	    <td>* FUTURE_DAY_CLOSE：日市收盘</td>
    </tr>
  <tr>
        <td rowspan="16">美国市场</td>
	    <td rowspan="5">证券类产品（含股票、ETFs）</td>
	    <td>* PRE_MARKET_BEGIN：美股盘前交易时段</td>
      <td>EST 04:00 - 09:30</td>
    </tr>
    <tr>
	    <td>* AFTERNOON：美股持续交易时段</td>
      <td>EST 09:30 - 16:00</td>
    </tr>
    <tr>
	    <td>* AFTER_HOURS_BEGIN：美股盘后交易时段</td>
      <td>EST 16:00 - 20:00</td>
    </tr>
    <tr>
	    <td>* AFTER_HOURS_END：美股盘后收盘</td>
      <td>EST 20:00 - 04:00（T+1）</td>
    </tr>
    <tr>
	    <td>* OVERNIGHT：美股夜盘交易时段</td>
      <td>EST 20:00 - 04:00（T+1）</td>
    </tr>
    <tr>
	    <td rowspan="6">期权</td>
      <td>* NONE：期权待开盘</td>
      <td rowspan="6"> 不同品种交易时间不同</td>
    </tr>
    <tr>
	    <td>* REST：美指期权午间休市</td>
    </tr>
    <tr>
	    <td>* AFTERNOON：美股持续交易时段</td>
    </tr>
    <tr>
	    <td>* TRADE_AT_LAST：美指期权盘尾交易时段</td>
    </tr>
    <tr>
	    <td>* NIGHT：美指期权夜市交易时段</td>
    </tr>
    <tr>
	    <td>* CLOSED：收盘</td>
    </tr>
    <tr>
	    <td rowspan="5">期货</td>
      <td>* FUTURE_SWITCH_DATE：美期待开盘</td>
      <td rowspan="5"> 不同品种交易时间不同</td>
    </tr>
    <tr>
	    <td>* FUTURE_OPEN：美期交易时段</td>
     </tr>
     <tr>
	    <td>* FUTURE_BREAK：美期中盘休息</td>
     </tr>
     <tr>
	    <td>* FUTRUE_BREAK_OVER：美期休息后交易时段</td>
     </tr>
     <tr>
	    <td>* FUTURE_CLOSE：美期收盘</td>
     </tr>
    <tr>
        <td rowspan="7">A股市场</td>
	    <td rowspan="7">证券类产品（含股票、ETFs）</td>
	    <td>* NONE：无交易</td>
      <td>CST 08:55 - 09:15</td>
    </tr>
    <tr>
	    <td>* Auction：盘前竞价</td>
      <td>CST 09:15 - 09:25</td>
    </tr>
    <tr>
	    <td>* WAITING_OPEN：等待开盘</td>
      <td> CST 09:25 - 09:30</td>
    </tr>
    <tr>
	    <td>* MORNING：早盘</td>
      <td>CST 09:30 - 11:30</td>
    </tr>
    <tr>
	    <td>* REST：午间休市</td>
      <td>CST 11:30 - 13:00</td>
    </tr>
    <tr>
	    <td>* AFTERNOON：午盘</td>
      <td>CST 13:00 - 15:00</td>
    </tr>
    <tr>
	    <td>* CLOSED：收盘</td>
      <td>CST 15:00 - 08:55（T+1）</td>
    </tr>
    <tr>
        <td rowspan="10">新加坡市场</td>
	    <td rowspan="5">证券类产品（含股票、ETFs、REITs、结构性窝轮、DLCs）</td>
	    <td>* WAITING_OPEN：等待开盘</td>
      <td>CST 08:30 - 09:00</td>
    </tr>
    <tr>
	    <td>* MORNING：早盘</td>
      <td>CST 09:00 - 12:00</td>
    </tr>
     <tr>
	    <td>* REST: 午间休市</td>
      <td>CST 12:00 - 13:00</td>
    </tr>
     <tr>
	    <td>* AFTERNOON：午盘</td>
      <td>CST 13:00 - 17:00</td>
    </tr>
     <tr>
	    <td>* CLOSED：收盘</td>
      <td>CST 17:16 - 08:30（T+1）</td>
    </tr>
    <tr>
        <td rowspan="5">期货</td>
        <td>* FUTURE_DAY_WAIT_FOR_OPEN：期货待开盘</td>
        <td rowspan="5">不同品种交易时间不同</td>
      </tr>
     <tr>
	    <td>* NIGHT_OPEN：夜市交易时段</td>
    </tr>
     <tr>
	    <td>* NIGHT_END：夜市收盘</td>
    </tr>
     <tr>
	    <td>* FUTURE_DAY_OPEN：日市交易时段</td>
    </tr>
     <tr>
	    <td>* FUTURE_DAY_CLOSE：日市收盘</td>
    </tr>
    <tr>
        <td rowspan="10">日本市场</td>
      <td rowspan="5">证券类产品（含股票、ETFs）</td>
	    <td>* WAITING_OPEN：等待开盘</td>
      <td>JST 07:55 - 09:00</td>
    </tr>
    <tr>
	    <td>* MORNING：早盘</td>
      <td>JST 09:00 - 11:30</td>
    </tr>
     <tr>
	    <td>* REST: 午间休市</td>
      <td>JST 11:30 - 12:30</td>
    </tr>
     <tr>
	    <td>* AFTERNOON：午盘</td>
      <td>JST 12:30 - 15:30</td>
    </tr>
     <tr>
	    <td>* CLOSED：收盘</td>
      <td>JST 15:30 - 07:50（T+1）</td>
    </tr>
    <td rowspan="5">期货</td>
	    <td>* FUTURE_DAY_WAIT_FOR_OPEN：期货待开盘</td>
      <td>JST 16:25（T-1）- 16:30（T-1）</td>
    </tr>
     <tr>
	    <td>* NIGHT_OPEN：夜市交易时段</td>
      <td>JST 16:30（T-1） - 05:30</td>
    </tr>
     <tr>
	    <td>* NIGHT_END：夜市收盘</td>
      <td>JST 05:30 - 08:45</td>
    </tr>
     <tr>
	    <td>* FUTURE_DAY_OPEN：日市交易时段</td>
      <td>JST 08:45 - 15:15</td>
    </tr>
     <tr>
	    <td>* FUTURE_DAY_CLOSE：日市收盘</td>
      <td>JST 15:15 - 16:25</td>
    </tr>
    <tr>
        <td rowspan="5">马来西亚市场</td>
      <td rowspan="5">证券类产品（含股票、ETFs、REITs、窝轮）</td>
	    <td>* AUCTION：盘前竞价</td>
      <td>CST 08:30 - 09:00</td>
    </tr>
    <tr>
	    <td>* MORNING：早盘</td>
      <td>CST 09:00 - 12:30</td>
    </tr>
     <tr>
	    <td>* REST: 午间休市</td>
      <td>CST 12:30 - 14:00</td>
    </tr>
     <tr>
	    <td>* AFTERNOON：午盘</td>
      <td>CST 14:30 - 16:45</td>
    </tr>
     <tr>
	    <td>* CLOSED：收盘</td>
      <td>CST 17：00 - 08:25（T+1）</td>
    </tr>
    <tr>
        <td rowspan="3">加密货币市场</td>
	    <td rowspan="3">加密货币</td>
	    <td>* NONE：未交易</td>
      <td rowspan="3">不同币对可交易时间不同</td>
    </tr>
     <tr>
	    <td>* MORNING：早盘</td>
    </tr>
     <tr>
	    <td>* CLOSED：收盘</td>
    </tr>
</table>
\* CST, EST, JST 分别表示中国时间，美东时间，日本时间

## Q15：接口参数股票代码的格式

A：  
* 使用不同编程语言的用户，需要的股票代码的格式不同：
   * **Python 用户**  
    标的代码 code 使用 `exchange_market.symbol`格式，`exchange_market`表示交易所市场，`symbol`表示标的代码。支持订阅的标的如下：    

<table>
    <tr>
        <th>市场</th>
        <th>标的类别</th>
        <th>exchange_market</th>
        <th>example</th>
    </tr>
    <tr>
        <td rowspan="5">香港市场</td>
        <td>证券类产品（含股票、ETFs、窝轮、牛熊、界内证）</td>
        <td>HK</td>
        <td>腾讯控股：HK.00700</td>
    </tr>
    <tr>
        <td>指数</td>
        <td>HK</td>
        <td>恒生指数：HK.800000</td>
    </tr>  
    <tr>
        <td>期货</td>
        <td>HK</td>
        <td>恒指期货2606：HK.HSI2606</td>
    </tr>
    <tr>
        <td>期权</td>
        <td>HK</td>
        <td>* 股票期权 腾讯 260330 450.00购：HK.TCH260330C450000 <br> * 指数期权 恒指 260330 24000.00购：HK.HSI260330C24000000</td>
    </tr>
    <tr>
        <td>板块  (建议使用  get_plate_list 先获取板块列表) </td>
        <td>HK</td>
        <td>AI应用股：HK.LIST24037</td>
    </tr>
    <tr>
        <td rowspan="5">美国市场</td>
        <td>证券类产品（含纽交所、美交所、纳斯达克上市的股票、ETFs）</td>
        <td>US</td>
        <td>英伟达：US.NVDA</td>
    </tr>
    <tr>
        <td>期权</td>
        <td>US</td>
        <td>* 股票期权 NVDA 260330 160.00C：US.NVDA260330C160000 <br> * 指数期权 SPXW 260330 6330.00C: US..SPXW260330C6330000</td>
    </tr>
    <tr>
        <td>期货</td>
        <td>US</td>
        <td>标普500指数期货2606：US.ES2606</td>
    </tr>
    <tr>
        <td>板块  (建议使用  get_plate_list 先获取板块列表) </td>
        <td>US</td>
        <td>半导体精选：US.LIST20077</td>
    </tr>
    <tr>
        <td>指数（暂不支持获取）</td>
        <td>US</td>
        <td>标普500指数：US..SPX</td>
    </tr>
    <tr>
        <td rowspan="3">A股市场</td>
        <td>证券类产品（含股票、ETFs）</td>
        <td>SH/SZ</td>
        <td>贵州茅台：SH.600519</td>
    </tr>
    <tr>
        <td>指数</td>
        <td>SH/SZ</td>
        <td>上证指数：SH.000001</td>
    </tr>
    <tr>
        <td>板块  (建议使用  get_plate_list 先获取板块列表) </td>
        <td>SH/SZ</td>
        <td>汽车电子概念：SH.LIST0301</td>
    </tr>
    <tr>
        <td rowspan="2">新加坡市场</td>
        <td>证券类产品（含股票、ETFs、REITs、结构性窝轮、DLCs）</td>
        <td>SG</td>
        <td>新加坡航空公司：SG.C6L</td>
    </tr>
    <tr>
        <td>期货（暂不支持获取）</td>
        <td>SG</td>
        <td>A50指数期货2606：SG.CN2606</td>
    </tr>
    <tr>
        <td rowspan="2">日本市场</td>
        <td>证券类产品（含股票、ETFs）</td>
        <td>JP</td>
        <td>任天堂：JP.7974</td>
    </tr>
    <tr>
        <td>期货（暂不支持获取）</td>
        <td>JP</td>
        <td>大阪日经指数期货2606：JP.NK2252606</td>
    </tr>
    <tr>
        <td rowspan="1">马来西亚市场</td>
        <td>证券类产品（含股票、ETFs、REITs、窝轮）</td>
        <td>MY</td>
        <td>MAYBANK：MY.1155</td>
    </tr>
    <tr>
        <td rowspan="1">加密货币市场</td>
        <td>加密货币指数及币对</td>
        <td>CC</td>
        <td>* 指数：CC.BTC <br> * 可交易币对: CC.BTCUSD</td>
    </tr>
    </table>
      

   * **非 Python 用户**   
    股票结构参见 [Security](../quote/quote.html#1377)。   
    例如：腾讯控股，参数 market 传入 QotMarket_HK_Security，参数 code 传入'00700'。

* 查询方式：  
   通过 APP 查看代码和行情市场：行情 > 自选 > 全部。  
   行情市场定义，请参考 [这里](../quote/quote.html#427)。  
    ![code](../img/code.png)    


## Q16：复权因子相关
A：  
### 概述
所谓 [复权](../quote/get-rehab.html#770) 就是对股价和成交量进行权息修复，按照股票的实际涨跌绘制股价走势图，并把成交量调整为相同的股本口径。  
公司行动（如：拆股、合股、送股、转增股、配股、增发股、分红）均可能对股价产生影响，而复权计算可对量价进行调整，剔除公司行动的影响，保持股价走势的连续性。   

### 名词解释
- 公司行动：上市公司进行一些股权、股票等影响公司股价和股东持仓变化的行为。
- 前复权：保持现有的股价不变，以当前的股价为基准，对以前的股价进行复权计算。
- 后复权：保持先前的股价不变，以过去的股价为基准，对以后的股价进行复权计算。
- 复权因子：即权息修复比例，用于计算复权后的价格及持仓数量。
- 除权除息日：即股权登记日下一个交易日。在股票的除权除息日，证券交易所都要计算出股票的除权除息价，以作为股民在除权除息日开盘的参考。其意义是股票股利分配给股东的日期。

### 复权方法
主流的复权计算方法分为两种：事件法和连乘法；而 Futu API 针对不同市场使用不同的计算方法。
- 事件复权法：通过还原除权除息的各类事件进行复权；存在两个复权因子（复权因子 A 和 复权因子 B），复权因子 B 主要调整现金分红对股价的影响，而复权因子 A 调整其他公司行动对股价的影响。
- 连乘复权法：通过复权因子连乘的方式进行复权，只保留 复权因子 A（或将 复权因子 B 置为0），复权因子 A 为 除权除息日前收盘价/该日经权息调整后的前收盘价。

::: tip 提示
*  API 对美股前复权使用连乘法，即将 复权因子 B 置为0。  
*  API 对除美股以外的标的（A股、港股、新加坡股票等）及美股后复权使用事件法。  
:::

### 计算公式
#### 单次复权
- 前复权：  
前复权价格 = 不复权价格 × 前复权因子 A + 前复权因子 B   
- 后复权：  
后复权价格 = 不复权价格 × 后复权因子 A + 后复权因子 B

#### 多次复权
- 前复权：按照时间顺序，筛选出大于计算日期的复权因子，优先使用时间较早的复权因子进行复权计算。以两次复权为例： 

  ![code](../img/forward_fomula.png)    
- 后复权：按照时间倒序，筛选出小于等于计算日期的复权因子，优先使用时间较晚的复权因子进行复权计算。以两次复权为例： 

  ![code](../img/backward_fomula.png)    

### 示例
#### 单次前复权示例
以牧原股份为例：
- 筛选复权因子如下：  

除权除息日|股票代码|方案说明|前复权因子 A |前复权因子 B 
:-|:-|:-|:-|:-
2021/06/03|SZ.002714|10转4.0股派14.61元（含税）|0.71429|-1.04357

- 不复权数据如下：  

日期|股票代码|不复权收盘价
:-|:-|:-
2021/06/02|SZ.002714|93.11
2021/06/03|SZ.002714|66.25

- 前复权数据如下：  

日期|股票代码|前复权收盘价
:-|:-|:-
2021/06/02|SZ.002714|65.4639719
2021/06/03|SZ.002714|66.25

- 前复权数据计算方法：  
牧原股份在 2021/06/03 进行拆股及现金分红行动（10转4.0股派14.61元），根据前复权计算公式对 2021/06/02 的收盘价进行调整计算，则：前复权价格（65.4639719） = 不复权价格（93.11） × 前复权因子 A（0.71429） + 前复权因子 B（-1.04357）   

  ![code](../img/forward_example.png)    

#### 多次后复权示例
接上一个例子，计算牧原股份在 2021/06/02 的后复权价格：
- 筛选复权因子如下：  

除权除息日|股票代码|方案说明|后复权因子 A |后复权因子 B 
:-|:-|:-|:-|:-|
2014/07/04|SZ.002714|10派2.34元（含税）|1|0.234
2015-06-10|SZ.002714|10转10.0股派0.61元（含税）|2|0.061
2016-07-08|SZ.002714|10转10.0股派3.53元（含税）|2|0.353
2017-07-11|SZ.002714|10转8.0股派6.9元（含税）|1.8|0.69
2018-07-03|SZ.002714|10派6.91元（含税）|1|0.691
2019-07-04|SZ.002714|10派0.5元（含税）|1|0.05
2020-06-04|SZ.002714|10转7.0股派5.5元（含税）|1.7|0.55

- 不复权数据如下：  

日期|股票代码|不复权收盘价
:-|:-|:-
2021/06/02|SZ.002714|93.11

- 后复权数据如下：  

日期|股票代码|后复权收盘价
:-|:-|:-
2021/06/02|SZ.002714|1152.7226

- 后复权数据计算方法：  
为了计算牧原股份在 2021/06/02 的后复权价格，需要将早于 2021/06/02 的复权事件进行一一复权，得到最后的后复权价格，具体计算如下：

![code](../img/backward_example.jpg)

## Q17：加密货币多券商行情相关

#### 1. 为什么加密货币行情会因券商不同而有所差异？
A：由于各券商对接的行情上游不同，同一币对在不同券商下可能存在行情数据差异。API支持根据券商切换行情数据源（OpenQuoteContext 指定 security_firm），确保您看到的行情与实际交易一致。

#### 2. 如果我没有指定券商，会展示哪个数据源的行情？
A：未指定券商时，API默认返回您的主推券商行情上游数据。

#### 3. 我有多个券商账户都支持加密货币交易，应该如何选择？
A：建议选择您实际交易账户所对应的券商来获取行情。这样可以确保所见行情与下单时的撮合价格一致，避免因行情数据源不同导致的价格偏差。

---

# 交易相关

## Q1：模拟交易相关

A:
### 概述
模拟交易是在真实的市场环境中，用虚拟资金做交易，不会对您的真实账户的资产造成影响。

#### 交易时间
模拟交易支持的时段：常规交易时段（所有市场）、美股盘中时段、美股盘前盘后时段（仅美股融资融券模拟账户支持）   
模拟交易不支持的时段：美股夜盘时段、A股竞价时段、港股竞价时段    
详情可点击 [模拟交易规则](https://support.futunn.com/topic692)


#### 支持品类
Futu API 支持模拟交易的品类请参考 [这里](../intro/intro.md#1396)。

#### 解锁
与真实交易不同，模拟交易无需对账户进行解锁，即可下单或改单撤单。


#### 订单
1. 订单类型：限价单和市价单。  
2. 改单操作类型：模拟交易不支持使生效、使失效、删除，仅支持修改订单、 撤单。  
3. 成交：模拟交易不支持成交相关操作，包括 [查询今日成交](../trade/get-order-fill-list.md#2621)、[查询历史成交](../trade/get-history-order-fill-list.md#9015)、[响应成交推送回调](../trade/update-order-fill.md#210)。
4. 有效期限：模拟交易有效期限仅支持当日有效。
5. 卖空：期权和期货支持卖空。股票仅美股支持卖空。 
6. 模拟交易账户不支持查询订单费用。
7. 模拟交易账户不支持查询现金流水。
8. 在组合期权订单场景下，支持持仓查询，暂不支持组合订单查询。

#### 操作平台
1. 移动端：我的 — 模拟交易  

![sim-page](../img/sim-page.png)

2. 桌面端：左侧模拟 tab  

![sim-page](../img/create-sim-account.png)


3. 网页端：[模拟交易界面](https://m-match.futunn.com/simulate/)

4. Futu API：在调用接口时，设置参数交易环境为模拟环境即可。详见 [如何使用 Futu API 进行模拟交易](../qa/trade.md#8728)。

::: tip 提示
* 以上四种方式只是操作平台不同，四种方式操作的模拟账户是共通的。  
:::


### 如何使用 Futu API 进行模拟交易？

#### 创建连接
先根据交易品种 [创建相应的连接](../trade/base.md#7902) 。当交易品种是股票或期权时，请使用 `OpenSecTradeContext`。当交易品种是期货时，请使用 `OpenFutureTradeContext`。

#### 获取交易业务账户列表
使用 [获取交易业务账户列表](../trade/get-acc-list.md#5754) 查看交易账户（包括模拟账户、真实账户）。以 Python 为例：返回字段交易环境 `trd_env` 为 `SIMULATE`，表示模拟账户。   
获取港股模拟交易账户，需要指定 filter_trdmarket 为 TrdMarket.HK，此时会返回2个模拟交易账号。其中 sim_acc_type = STOCK 为港股模拟账户，sim_acc_type = OPTION 为港股期权模拟账户，sim_acc_type = FUTURES 为港股期货模拟账户。   
获取美股模拟交易账户，需要指定 filter_trdmarket 为 TrdMarket.US，sim_acc_type = STOCK_AND_OPTION 代表美股融资融券模拟账户，可以模拟交易股票和期权。sim_acc_type = FUTURES 为美国期货模拟账户。    

* **Example：Stocks and Options**
```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
#trd_ctx = OpenFutureTradeContext(host='127.0.0.1', port=11111, is_encrypt=None, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.get_acc_list()
if ret == RET_OK:
    print(data)
    print(data['acc_id'][0])  # get the first account id
    print(data['acc_id'].values.tolist())  # convert to list format
else:
    print('get_acc_list error: ', data)
trd_ctx.close()
```

* **Output**
```python
               acc_id   trd_env acc_type          card_num   security_firm  \
0  281756480572583411      REAL   MARGIN  1001318721909873  FUTUSECURITIES   
1             9053218  SIMULATE     CASH               N/A             N/A   
2             9048221  SIMULATE   MARGIN               N/A             N/A   

  sim_acc_type  trdmarket_auth  
0          N/A  [HK, US, HKCC]  
1        STOCK            [HK]  
2       OPTION            [HK] 
```
::: tip 提示
* 模拟交易中，区分股票账户和期权账户，股票账户只能交易股票，期权账户只能交易期权；以 Python 为例：返回字段中模拟账户类型 `sim_acc_type` 为 `STOCK`，表示股票账户；为`OPTION`，表示期权账户。
::: 

* **Example: Futures**
```python
from futu import *
#trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
trd_ctx = OpenFutureTradeContext(host='127.0.0.1', port=11111, is_encrypt=None, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.get_acc_list()
if ret == RET_OK:
    print(data)
    print(data['acc_id'][0])  # get the first account id
    print(data['acc_id'].values.tolist())  # convert to list format
else:
    print('get_acc_list error: ', data)
trd_ctx.close()
```

* **Output**
```python
    acc_id   trd_env acc_type card_num security_firm sim_acc_type  \
0  9497808  SIMULATE   MARGIN      N/A           N/A      FUTURES   
1  9497809  SIMULATE   MARGIN      N/A           N/A      FUTURES   
2  9497810  SIMULATE   MARGIN      N/A           N/A      FUTURES   
3  9497811  SIMULATE   MARGIN      N/A           N/A      FUTURES   

          trdmarket_auth  
0  [FUTURES_SIMULATE_HK]  
1  [FUTURES_SIMULATE_US]  
2  [FUTURES_SIMULATE_SG]  
3  [FUTURES_SIMULATE_JP]  
```  

#### 下单
使用 [下单接口](../trade/place-order.md) 时，设置交易环境为模拟环境即可。以 Python 为例：`trd_env = TrdEnv.SIMULATE`。

* **Example**
```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.place_order(price=510.0, qty=100, code="HK.00700", trd_side=TrdSide.BUY, trd_env=TrdEnv.SIMULATE)
if ret == RET_OK:
    print(data)
else:
    print('place_order error: ', data)
trd_ctx.close()
```
* **Output**
```python
	code	stock_name	trd_side	order_type	order_status	order_id	qty	price	create_time	updated_time	dealt_qty	dealt_avg_price	last_err_msg	remark	time_in_force	fill_outside_rth
0	HK.00700	腾讯控股	BUY	NORMAL	SUBMITTING	4642000476506964749	100.0	510.0	2021-10-09 11:34:54	2021-10-09 11:34:54	0.0	0.0			DAY	N/A
```

#### 撤单改单
使用 [撤单接口](../trade/modify-order.md) 时，设置交易环境为模拟环境即可。以 Python 为例： `trd_env = TrdEnv.SIMULATE`。

* **Example**
```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
order_id = "4642000476506964749"
ret, data = trd_ctx.modify_order(ModifyOrderOp.CANCEL, order_id, 0, 0, trd_env=TrdEnv.SIMULATE)
if ret == RET_OK:
    print(data)
else:
    print('modify_order error: ', data)
trd_ctx.close()
```
* **Output**
```python
    trd_env             order_id
0  SIMULATE  4642000476506964749
```

#### 查询历史订单
使用 [查询历史订单接口](../trade/get-history-order-list.md) 时，设置交易环境为模拟环境即可。以 Python 为例：`trd_env = TrdEnv.SIMULATE`。

* **Example**
```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.history_order_list_query(trd_env=TrdEnv.SIMULATE)
if ret == RET_OK:
    print(data)
else:
    print('history_order_list_query error: ', data)
trd_ctx.close()
```
* **Output**
```python
	code	stock_name	trd_side	order_type	order_status	order_id	qty	price	create_time	updated_time	dealt_qty	dealt_avg_price	last_err_msg	remark	time_in_force	fill_outside_rth
0	HK.00700	腾讯控股	BUY	ABSOLUTE_LIMIT	CANCELLED_ALL	4642000476506964749	100.0	510.0	2021-10-09 11:34:54	2021-10-09 11:37:08	0.0	0.0			DAY	N/A
```

### 如何重置模拟账户？
目前 Futu API 不支持重置模拟账户，您可在移动端使用复活卡重置指定模拟账户，重置后账户资金将恢复至初始值，历史订单将会被清空。

#### 具体操作
移动端：我的 — 模拟交易 — 我的头像 — 我的道具 — 复活卡。
![sim-page](../img/sim-reset.png)


## Q2：是否支持 A 股交易？

A: 模拟交易支持 A 股交易。但真实交易仅可通过 A 股通交易部分 A 股，具体详见 [A 股通名单](https://www.hkex.com.hk/Mutual-Market/Stock-Connect/Eligible-Stocks/View-All-Eligible-Securities?sc_lang=zh-HK)。

## Q3：各市场支持的交易方向

A: 除了期货，其他股票都只支持传入 BUY 和 SELL 两个交易方向。在空仓情况下传入 SELL，产生的订单交易方向是卖空。

## Q4：真实交易中，各市场支持的订单类型

A: 
<table style="font-size:14px;">
    <tr>
        <th>市场</th>
        <th>品种</th>
        <th>限价单</th>
        <th>市价单</th>
        <th>竞价限价单</th>
        <th>竞价市价单</th>
        <th>绝对限价单</th>
        <th>特别限价单</th>
        <th>特别限价且要求<br/>全部成交订单</th>
        <th>止损市价单</th>
        <th>止损限价单</th>
        <th>触及市价单（止盈）</th>
        <th>触及限价单（止盈）</th>
        <th>跟踪止损市价单</th>
        <th>跟踪止损限价单</th>
    </tr>
    <tr>
        <td rowspan="3">香港市场</td>
        <td>证券类产品（含股票、ETFs、<br/>窝轮、牛熊、界内证）</td>
        <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td>
    </tr>
    <tr>
        <td>期权</td>
        <td>✓</td> <td>X</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>X</td> <td>✓</td> <td>X</td> <td>✓</td> <td>X</td> <td>✓</td>
    </tr>
    <tr>
        <td>期货</td>
        <td>✓</td> <td>✓</td> <td>-</td> <td>✓</td> <td>-</td> <td>-</td> <td>-</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td>
    </tr>
    <tr>
        <td rowspan="3">美国市场</td>
        <td>证券类产品（含股票、ETFs）</td>
        <td>✓</td> <td>✓</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td>
    </tr>
    <tr>
        <td>期权</td>
        <td>✓</td> <td>✓</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td>
    </tr>
    <tr>
        <td>期货</td>
        <td>✓</td> <td>✓</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td>
    </tr>
    <tr>
        <td>A 股通市场</td>
        <td>证券类产品（含股票、ETFs）</td>
        <td>✓</td> <td>X</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>X</td> <td>✓</td> <td>X</td> <td>✓</td> <td>X</td> <td>✓</td>
    </tr>
    <tr>
        <td>新加坡市场</td>
        <td>期货</td>
        <td>✓</td> <td>✓</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td>
    </tr>
    <tr>
        <td>日本市场</td>
        <td>期货</td>
        <td>✓</td> <td>✓</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td>
    </tr>
</table>


## Q5：各市场支持的订单操作

A: 
* 港股支持改单、撤单、生效、失效、删除
* 美股仅支持改单和撤单
* A 股通仅支持撤单
* 期货支持改单、撤单、删除

## Q6：OpenD 启动参数 future_trade_api_time_zone 如何使用？

A：由于期货账户支持交易的品种分布在全球多个交易所，交易所的所属时区各有不同，因此期货交易 API 的时间显示就成为了一个问题。  
OpenD 启动参数中新增了 future_trade_api_time_zone 这一参数，供全球不同地区的期货交易者灵活指定时区。默认时区为 UTC+8，如果您更习惯美东时间，只需将此参数配置为 UTC-5 即可。
::: tip  提示
+ 此参数仅会对期货交易接口类对象生效。港股交易、美股交易、A 股通交易接口类对象的时区，仍然按照交易所所在的时区进行显示。
+ 此参数会影响的接口包括：响应订单推送回调，响应成交推送回调，查询今日订单，查询历史订单，查询当日成交，查询历史成交，下单。
:::

## Q7：通过 API 下的订单，能在 APP 上面看到吗？
A：可以看到。  
通过 Futu API 成功发出下单指令后，您可以在 APP 的 **交易** 页面，查看今日订单、订单状态、成交情况等等，也可以在 **消息—订单消息** 中收到成交提醒的通知。

## Q8：哪些品类支持在非交易时段下单？
A：所有的订单，都需要在开盘期间才能够成交。  
Futu API 仅对一部分品类，支持了 **非交易时段下单** 的功能（APP 上支持更多品类的非交易时段下单功能）。具体请参考下表：

<table>
    <tr>
        <th rowspan="2">市场</th>
        <th rowspan="2">标的类型</th>
        <th rowspan="2">模拟交易</th>
        <th colspan="7">真实交易</th>
    </tr>
    <tr>
        <th>Futu HK</th>
        <th>Moomoo US</th>
        <th>Moomoo SG</th>
        <th>Moomoo AU</th>
        <th>Moomoo MY</th>
        <th>Moomoo CA</th>
        <th>Moomoo JP</th>
    </tr>
    <tr>
        <td rowspan="3">香港市场</td>
	    <td>股票、ETFs、窝轮、牛熊、界内证</td>
	    <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
   <tr>
	    <td>期权 (含指数期权，需使用期货账户交易)</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="3">美国市场</td>
	    <td>股票、ETFs</td>
	    <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
    </tr>
    <tr>
        <td>期权</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
    </tr>
   <tr>
	    <td>期货</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="2">A 股市场</td>
	    <td>A 股通股票</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
     <tr>
	    <td>非 A 股通股票</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
   <tr>
        <td rowspan="2">新加坡市场</td>
	    <td>股票、ETFs、窝轮、REITs、DLCs</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td rowspan="2">日本市场</td>
        <td>股票、ETFs、REITs</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td>期货</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td rowspan="1">澳大利亚市场</td>
        <td>股票、ETFs</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td rowspan="1">加拿大市场</td>
        <td>股票</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
</table>
::: tip 提示
- ✓：支持非交易时段下单
- X：暂不支持非交易时段下单（或暂不支持交易）
:::

## Q9：对于下单接口，各订单类型对应的必传参数以及券商对单笔订单的下单限制
A1: 各订单类型对应的必传参数

<table style="font-size:14px;">
    <tr>
        <th>参数</th>
        <th>限价单</th>
        <th>市价单</th>
        <th>竞价限价单</th>
        <th>竞价市价单</th>
        <th>绝对限价单</th>
        <th>特别限价单</th>
        <th>特别限价且要求<br/>全部成交订单</th>
        <th>止损市价单</th>
        <th>止损限价单</th>
        <th>触及市价单（止盈）</th>
        <th>触及限价单（止盈）</th>
        <th>跟踪止损市价单</th>
        <th>跟踪止损限价单</th>
    </tr>
    <tr>
        <td>price</td>
        <td>✓</td> <td></td> <td>✓</td> <td> </td> <td>✓</td> <td>✓</td> <td>✓</td>  <td></td><td>✓</td> <td></td> <td>✓</td><td> </td><td> </td>
    </tr>
    <tr>
        <td>qty</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>code</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>trd_side</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>order_type</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>trd_env</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>aux_price</td>
        <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td> </td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td> </td><td> </td>
    </tr>
    <tr>
        <td>trail_type</td>
        <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td> </td><td> </td><td> </td><td> </td><td> </td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>trail_value</td>
        <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td> </td><td> </td><td> </td><td> </td><td> </td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>trail_spread</td>
        <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td> </td><td> </td><td> </td><td> </td><td> </td> <td> </td><td>✓</td>
    </tr>
</table>

`Python 用户` 注意，[place_order](../trade/place-order.html#4080) 并未对 price 设置默认值，对于上述五类订单类型，仍需对 price 传参，price 可以传入任意值。

A2：各券商对单笔订单的股数及金额限制
<table style="font-size:14px;">
    <tr>
        <th>券商</th>
        <th>品类</th>
        <th>单笔订单股数上限</th>
        <th>单笔订单金额上限</th>
    </tr>
    <tr>
        <td rowspan="3">FUTU HK</td>
        <td>A股通</td>
        <td>1,000,000 股</td>
        <td>￥5,000,000</td>
    </tr>
    <tr>
        <td>美股</td>
        <td>500,000 股</td>
        <td>$5,000,000</td>
    </tr>
    <tr>
        <td>香港股票期货/期权</td>
        <td>3,000 手</td>
        <td>无限制</td>
    </tr>
    <tr>
        <td>moomoo US</td>
        <td>美股</td>
        <td>500,000 股</td>
        <td>$10,000,000</td>
    </tr>
    <tr>
        <td>moomoo SG</td>
        <td>美股</td>
        <td>500,000 股</td>
        <td>$5,000,000</td>
    </tr>
    <tr>
        <td>moomoo AU</td>
        <td>美股</td>
        <td>无限制</td>
        <td>无限制</td>
    </tr>
</table>


## Q10：对于改单接口，修改订单时，各订单类型对应的必传参数
A: 

<table style="font-size:14px;">
    <tr>
        <th>参数</th>
        <th>限价单</th>
        <th>市价单</th>
        <th>竞价限价单</th>
        <th>竞价市价单</th>
        <th>绝对限价单</th>
        <th>特别限价单</th>
        <th>特别限价且要求<br/>全部成交订单</th>
        <th>止损市价单</th>
        <th>止损限价单</th>
        <th>触及市价单（止盈）</th>
        <th>触及限价单（止盈）</th>
        <th>跟踪止损市价单</th>
        <th>跟踪止损限价单</th>
    </tr>
    <tr>
        <td>modify_order_op</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>order_id</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>price</td>
        <td>✓</td> <td></td> <td>✓</td> <td> </td> <td>✓</td> <td>✓</td> <td>✓</td>  <td></td><td>✓</td> <td></td> <td>✓</td><td> </td><td> </td>
    </tr>
    <tr>
        <td>qty</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>trd_env</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>aux_price</td>
        <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td> </td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td> </td><td> </td>
    </tr>
    <tr>
        <td>trail_type</td>
        <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td> </td><td> </td><td> </td><td> </td><td> </td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>trail_value</td>
        <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td> </td><td> </td><td> </td><td> </td><td> </td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>trail_spread</td>
        <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td> </td><td> </td><td> </td><td> </td><td> </td> <td> </td><td>✓</td>
    </tr>
</table>

`Python 用户` 注意，[modify_order](../trade/modify-order.html#7408) 并未对 price 设置默认值，对于上述五类订单类型，仍需对 price 传参，price 可以传入任意值。

## Q11：交易接口返回“当前证券业务账户尚未同意免责协议”？
A：  
点击下方链接完成协议确认，重启 OpenD 即可正常使用交易功能。
所属券商|协议确认
:-|:-|:-
FUTU HK|[点击这里](https://risk-disclosure.futuhk.com/index?agreementNo=HKOT0015)
Moomoo US|[点击这里](https://risk-disclosure.us.moomoo.com/index?agreementNo=USOT0027)
Moomoo SG|[点击这里](https://risk-disclosure.sg.moomoo.com/index?agreementNo=SGOT0015)
Moomoo AU|[点击这里](https://risk-disclosure.au.moomoo.com/index?agreementNo=AUOT0025)
Moomoo CA|[点击这里](https://risk-disclosure.ca.moomoo.com/index?agreementNo=CAOT0117)
Moomoo MY|[点击这里](https://risk-disclosure.my.moomoo.com/index?agreementNo=MYOT0066)
Moomoo JP|[点击这里](https://risk-disclosure.jp.moomoo.com/index?agreementNo=JPOT0140)


## Q12：典型日内交易者（PDT）相关

### 概述

客户使用moomoo证券(美国) 账户进行日内交易时，会受到美国 FINRA 的监管限制（此为美国券商受到的监管要求，与交易股票的所属市场无关。其他国家或地区的券商  (如：富途证券(香港)、moomoo证券(新加坡)) 的交易账户则不受此限制）。若用户在任意连续的5个交易日内，进行日内交易 3 次以上，则会被标记为典型日内交易者（PDT）。  
更多详情，[点击这里](https://fastsupport.fututrade.com/hans/category11014/scid11017)

### 进行日内交易的流程图
![PDT_process](../img/PDT_process.png) 

### 我愿意被标记为 PDT，且不希望程式交易被打断，如何关闭“防止被标记为 PDT”？
A：  
当您在连续的 5 个交易日内，进行第 4 次日内交易时，为了防止您被无意识地标记为 PDT，服务器会对此交易进行拦截。若您主动想被标记为 PDT，并且不希望服务器拦截，可以采取以下措施：  
在 [命令行 OpenD 中配置参数](../opend/opend-cmd.html#8799)，将启动参数 `pdt_protection` 的值修改为 0，以关闭“防止被标记为日内交易者”的功能。

![US_para](../img/US_para.png)  
注意：若您被标记 PDT，当您的账户权益小于$25000时，您将无法开仓。

### 如何关闭 DTCall 预警提醒？
A：  
您被标记为 PDT 后，需要留意账户的日内交易购买力（DTBP），日内交易超出 DTBP 时将收到日内交易保证金追缴（DTCall）。服务器会在您即将开仓下单超出剩余日内交易购买力前，阻止您的下单。若您仍然希望进行下单，并且不希望服务器拦截，可以采取以下措施：    
在 [命令行 OpenD 中配置参数](../opend/opend-cmd.html#8799)，将启动参数 `dtcall_confirmation` 的值修改为 0，以关闭“日内交易保证金追缴预警”的功能。

![US_para2](../img/US_para2.png)  
注意：若您开仓订单的市值大于您的剩余日内交易购买力，并且在今日平仓当前标的，您将会收到日内交易保证金追缴通知（Day-Trading Call），只能通过存入资金才能解除。

### 如何查看 DTBP 的值？
A：  
通过 [查询账户资金](../trade/get-funds.html#4346) 接口，可以获取日内交易相关的返回值，如：剩余日内交易次数、初始日内交易购买力、剩余日内交易购买力等。


## Q13：如何跟踪订单成交状态
A:
下单后，可使用以下接口跟踪订单成交状态：
<table>
    <tr>
      <th> 交易环境 </th>
      <th> 接口 </th>
    </tr>
    <tr>
      <td > 真实交易 </td>
      <td > [响应订单推送回调](../trade/update-order.html)，[响应成交推送回调](../trade/update-order-fill.html) </td>
    </tr>
    <tr>
	  <td> 模拟交易</td>
      <td> [响应订单推送回调](../trade/update-order.html)</td>
    </tr>
</table>

注意：对于非 python 语言用户，在使用上述两个接口之前，需要先进行 [订阅交易推送](../trade/sub-acc-push.html)

#### 响应订单推送回调 的特点：
反馈 整个订单 的信息变动。当以下 8 个字段发生变化时，会触发订单推送：  
`订单状态`，`订单价格`，`订单数量`，`成交数量`，`触发价格`，`跟踪类型`，`跟踪金额/百分比`，`指定价差`  

因此，当您进行下单、改单，撤单、使生效、使失效操作，或者订单在市场中发生了高级订单被触发、有成交变动的情况，都会触发订单推送。您只需要调用 [响应成交推送回调](../trade/update-order-fill.html)，即可监听这些信息。

#### 响应成交推送回调 的特点：
只反馈 单笔成交 的信息。当以下 1 个字段发生变化时，会触发订单推送：  
`成交状态`  

举例：假设一笔限价单订单 900 股，分成了 3 次才完全成交，每次成交分别是：200、300、400 股。  
![example](../img/example.png)


## Q14：下单接口返回“此产品最小单位为 xxx，请调整至最小单位的整数倍后再提交”？
A:  
对于不同市场的标的，交易所有着不同的最小变动单位要求。如果提交的订单价格不符合要求，订单将会被拒绝。各市场价位规则如下：  

### 价位规则
#### 香港市场

以港交所官方说明为准，点击 [这里](https://www.futufin.com/hans/support/topic605?lang=zh-cn)。


#### A 股市场
股票价位：0.01。

#### 美国市场
股票价位：
<table>
    <tr>
      <th> 合约价格 </th>
      <th> 价位 </th>
    </tr>
    <tr>
      <td > $1 以下 </td>
      <td > $0.0001 </td>
    </tr>
    <tr>
	  <td> $1 以上</td>
      <td> $0.01 </td>
    </tr>
</table>

期权价位：
<table>
    <tr>
      <th> 合约价格 </th>
      <th> 价位 </th>
    </tr>
    <tr>
      <td > $0.10 - $3.00 </td>
      <td > $0.01 或者 $0.05</td>
    </tr>
    <tr>
	  <td> $3.00 以上</td>
      <td> $0.05 或者 $0.10</td>
    </tr>
</table>

期货价位：不同合约价位规则不同。可以通过 [获取期货合约资料](../quote/get-future-info.html#7447) 接口的返回字段 `最小变动的单位` 查看。

### 怎么避免订单价格不在价位上？
* 方法一：通过 [获取实时摆盘](../quote/get-order-book.html) 接口，获取合法的交易价格。交易所摆盘上的价位一定是合法的价位。  
* 方法二：通过 [下单](../trade/place-order.html) 接口的参数 `价格微调幅度`，将传入价格自动调整到合法的交易价格上。  

   例如：假设腾讯控股当前市价为 359.600，根据价位规则，对应的最小变动价位为 0.200。  

   假设您的下单传入订单价格为 359.678，价格微调幅度为 0.0015，代表接受 OpenD 对传入价格自动向上调整到最近的合法价位，且不能超过 0.15%。此情景下，向上最近的合法价格为 359.800，价格实际需要调整的幅度为 0.034%，符合价格微调幅度的要求，因此最终提交的订单价格为 359.800。  

   若价格微调幅度设置数值小于实际需要调整的幅度，OpenD 自动调整价位失败，订单仍会返回报错“订单价格不在价位上”。


## Q15：我的购买力足够，为什么下市价单会返回“购买力不足”？
A：
### 为什么市价单会提示购买力不足  
- 出于风控考量，系统给了市价单较高的购买力系数。在所有订单参数都相同的情况下，选择市价单会比限价单占用更多的购买力。  
- 而且对于不同的品种，和不同的市场情况，风控系统会对市价单的购买力系数做动态调整。所以在下市价单时，若您通过最大购买力去计算最大可买数量，计算的结果很可能是不准确的。  
### 如何计算正确的可买数量  
不建议自己计算，您可以通过 [查询最大可买可卖](../trade/get-max-trd-qtys.html) 接口获取正确的可买数量。  
### 如何尽可能买更多  
您可以用价格为对价的限价单，替代市价单进行交易。  
其中，对价：买1价（下卖单时）或 卖1价（下买单时）  


## Q16：API模拟交易下单，支持美股融资融券模拟账户接入
A：  
API模拟交易下单，已经支持美股融资融券模拟账户接入，交易能力更全面。  
原API接口后续将陆续下线美股模拟交易服务，为保障更优质的使用体验，建议您尽快切换至新接口，畅享专业的美股模拟交易服务。


## Q17：交易接口参数使用说明
### 1. 什么是交易对象？
您的平台账号下一般会开设一个保证金综合账户，其中有多个交易子账户（正常有两个，一个综合证券账户，一个综合期货账户；根据需要还可能有综合外汇账户等其他子账户）。一些特殊用户或机构客户可能会在多个券商下开设多个综合账户。  
创建交易对象，是初步筛选子账户的过程。
- 使用 OpenSecTradeContext 创建的交易对象，调用 get_acc_list 时只会返回**证券交易账户**
- 使用 OpenFutureTradeContext 创建的交易对象，调用 get_acc_list 时只会返回**期货交易账户**  

参数 security_firm 用来筛选对应归属券商的账户，参数 filter_trdmarket  用来筛选对应交易市场权限的账户。
#### 1.1 security_firm 券商参数
Futu API 目前支持的券商有 [这些](../trade/trade.html#572)。  
创建的交易对象，在调用 get_acc_list 时，会返回 security_firm 对应券商的真实账户和所有模拟交易账户（这是因为模拟交易没有券商的概念，所以无论 security_firm 传什么，都会返回所有的模拟账户）。  
security_firm 的默认值是 FUTUSECURITIES，FUTU HK 券商账户可以不填此参数，但需要获取其他券商的账户时，需要修改券商参数。  
* **Example 1**

```python
trd_ctx = OpenSecTradeContext(security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.get_acc_list()
print(data)
```

* **Output**

```python
               acc_id   trd_env acc_type      uni_card_num          card_num   security_firm sim_acc_type                  trdmarket_auth acc_status
0  281756478396547854      REAL   MARGIN  1001200163530138  1001369091153722  FUTUSECURITIES          N/A  [HK, US, HKCC, HKFUND, USFUND]     ACTIVE
1             3450309  SIMULATE     CASH               N/A               N/A             N/A        STOCK                            [HK]     ACTIVE
2             3548731  SIMULATE   MARGIN               N/A               N/A             N/A       OPTION                            [HK]     ACTIVE
3  281756455998014447      REAL   MARGIN               N/A  1001100320482767  FUTUSECURITIES          N/A                            [HK]   DISABLED
```

* **Example 2**
```python
trd_ctx = OpenSecTradeContext(security_firm=SecurityFirm.FUTUSG)
ret, data = trd_ctx.get_acc_list()
print(data)
```
* **Output**
```python
    acc_id   trd_env acc_type uni_card_num card_num security_firm sim_acc_type trdmarket_auth acc_status
0  3450309  SIMULATE     CASH          N/A      N/A           N/A        STOCK           [HK]     ACTIVE
1  3548731  SIMULATE   MARGIN          N/A      N/A           N/A       OPTION           [HK]     ACTIVE
```


#### 1.2 filter_trdmarket 交易市场参数
Futu API 目前支持的交易市场有 [这些](../trade/trade.html#719)。

创建的交易对象，在调用 get_acc_list 时，会返回所有拥有 filter_trdmarket 市场交易权限的账户；当 filter_trdmarket 入参传 NONE 时，不过滤市场，返回所有的账户。  
filter_trdmarket 的默认参数是 HK，在综合账户体系下，这个参数用来筛选不同市场下的模拟交易账户。  
* **Example 1**

```python
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US)
ret, data = trd_ctx.get_acc_list()
print(data)
```
* **Output**
```python
               acc_id   trd_env acc_type      uni_card_num          card_num   security_firm sim_acc_type                  trdmarket_auth acc_status
0  281756478396547854      REAL   MARGIN  1001200163530138  1001369091153722  FUTUSECURITIES          N/A  [HK, US, HKCC, HKFUND, USFUND]     ACTIVE
1             3450310  SIMULATE   MARGIN               N/A               N/A             N/A        STOCK                            [US]     ACTIVE
2             3548732  SIMULATE   MARGIN               N/A               N/A             N/A       OPTION                            [US]     ACTIVE
3  281756460292981743      REAL   MARGIN               N/A  1001100520714263  FUTUSECURITIES          N/A                            [US]   DISABLED
```

* **Example 2**
```python
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.NONE)
ret, data = trd_ctx.get_acc_list()
print(data)
```
* **Output**
```python
                acc_id   trd_env acc_type      uni_card_num          card_num   security_firm sim_acc_type                  trdmarket_auth acc_status
0   281756478396547854      REAL   MARGIN  1001200163530138  1001369091153722  FUTUSECURITIES          N/A  [HK, US, HKCC, HKFUND, USFUND]     ACTIVE
1              3450309  SIMULATE     CASH               N/A               N/A             N/A        STOCK                            [HK]     ACTIVE
2              3450310  SIMULATE   MARGIN               N/A               N/A             N/A        STOCK                            [US]     ACTIVE
3              3450311  SIMULATE     CASH               N/A               N/A             N/A        STOCK                            [CN]     ACTIVE
4              3548732  SIMULATE   MARGIN               N/A               N/A             N/A       OPTION                            [US]     ACTIVE
5              3548731  SIMULATE   MARGIN               N/A               N/A             N/A       OPTION                            [HK]     ACTIVE
6   281756455998014447      REAL   MARGIN               N/A  1001100320482767  FUTUSECURITIES          N/A                            [HK]   DISABLED
7   281756460292981743      REAL   MARGIN               N/A  1001100520714263  FUTUSECURITIES          N/A                            [US]   DISABLED
8   281756468882916335      REAL   MARGIN               N/A  1001100610464507  FUTUSECURITIES          N/A                          [HKCC]   DISABLED
9   281756507537621999      REAL     CASH               N/A  1001100910390035  FUTUSECURITIES          N/A                        [HKFUND]   DISABLED
10  281756550487294959      REAL     CASH               N/A  1001101010406844  FUTUSECURITIES          N/A                        [USFUND]   DISABLED
```
::: tip 提示  
当 filter_trdmarket 入参NONE时，可以返回所有的交易账户。其中第0行是真实账户，1~5行均为模拟交易账户，6~10行是已失效的真实账户。这些失效账户都是单市场账户，现已被综合账户替代。但历史订单和历史成交还在这些已失效的账户中，可以通过这些账户来查询。  
OpenFutureTradeContext 对象中没有 filter_trdmarket 参数，只有 security_firm 参数，功能与 OpenSecTradeContext  一样。  
:::  

### 2. 交易接口参数
在使用具体的交易接口（如下单、查询订单列表）时，接口中的 `trd_env`, `acc_index` 和 `acc_id` 参数，会先筛选确认一个唯一的账户，对此账户实施对应的接口行为。
![acc-select](../img/acc-select.jpg)

::: tip 总结
1. 根据 trd_env 筛选出真实账户还是模拟账户
2. 在筛选结果中，优先选择 acc_id 指定的账户
3. 如果 acc_id 为0，则通过 acc_index选取对应账号
4. 报错场景：指定的 acc_id 不存在，或 acc_index 超出范围  
:::


### 3. 应用举例
#### 3.1 综合证券账户实盘下单
```python
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.NONE, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.unlock_trade("123123")
if ret == RET_OK:
    print("解锁成功")
    ret, data = trd_ctx.place_order(45, 200, 'HK.00700', TrdSide.BUY,
                                    order_type=OrderType.NORMAL,
                                    trd_env=TrdEnv.REAL,  # 和默认参数一样，可以不填
                                    acc_id=0)  # 和默认参数一样，可以不填
    print(data)
```

#### 3.2 综合期货账户查询实盘订单列表
```python
trd_ctx = OpenFutureTradeContext(security_firm=SecurityFirm.FUTUSECURITIES)

ret, data = trd_ctx.order_list_query(trd_env=TrdEnv.REAL,   # 和默认参数一样，可以不填
                                     acc_id=0)  # 和默认参数一样，可以不填
print(data)
```

#### 3.3 港股模拟现金账户查询账户资金
```python
# filter_trdmarket 填 TrdMarket.HK
# trd_env 填 TrdEnv.SIMULATE
# acc_index 填 0
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK)
ret, data = trd_ctx.accinfo_query(trd_env=TrdEnv.SIMULATE, acc_index=0)
print(data)
```

#### 3.4 美股模拟保证金账户下单期权
```python
# 通过 filter_trdmarket 和 trd_env 筛选完之后只剩两个账户
# 第0个是美股现金账户（交易股票）,第1个是美股保证金账户（交易期权）
# acc_index 填 1 指定美股保证金账户
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US)
ret, data = trd_ctx.place_order(10, 1, code="US.AAPL250618P550000",trd_side=TrdSide.BUY,
                                trd_env=TrdEnv.SIMULATE,
                                acc_index=1)
print(data)
```

#### 3.5 日本期货模拟账户查询最大可买卖
```python
# 将 get_acc_list 的结果打印出来，可以看到日本期货模拟账户的 acc_id 是 6271199
# 请求最大可买卖接口时传入这个 acc_id 
trd_ctx = OpenFutureTradeContext()
ret, data = trd_ctx.acctradinginfo_query(order_type=OrderType.NORMAL,
                                         price=5000,
                                         trd_env=TrdEnv.SIMULATE,
                                         acc_id=6271199,
                                         code="JP.NK225main")
print(data)
```


### 4. API 中的账户如何与 APP/桌面端对应

![card-app](../img/card-app.png)
APP 上的账户仅显示卡号后 4 位数字，我们将 [get_acc_list](../trade/get-acc-list.html) 的返回结果打印出来后，有 uni_card_num 列和 card_num 列，分别对应综合账户的卡号，和单币种账户（已废弃）的卡号。通过卡号后 4 位数就能把 API 中获取到的账号与 APP 上对应起来了。

---

# 其他

## Q1：如何编译C++ API？

A: 
futu api c++ SDK支持Windows/MacOS/Linux，每个系统提供了以下编译环境生成的库文件：
操作系统|编译工具
:-|:-
Windows |Visual Studio 2013
Centos 7|g++ 4.8.5
Ubuntu 16.04|g++ 5.4.0
MacOS | XCode 11

如果编译器版本不同，或依赖的protobuf版本不同，则可能需要自己使用源码重新编译FTAPI和protobuf，源码位置见下图目录：

```
FTAPI目录结构：
+---Bin                               存放各个系统默认编译环境编译出的依赖库
+---Include                           存放公共头文件，以及proto协议生成的.h/.cc文件
+---Sample                            示例工程
\---Src
    +---FTAPI                         FTAPI源码
    +---protobuf-all-3.5.1.tar.gz     protobuf源码
```

#### 编译步骤：
1. 重新编译protobuf：生成libprotobuf静态库
2. 从协议proto文件中生成C++文件
3. 重新编译FTAPI: 源码在Src/FTAPI，生成libFTAPI静态库

#### 步骤1： 重新编译protobuf：
- Windows：
  - 安装CMake
  - 打开VS命令行工具，cd到protobuf/cmake目录
  - 执行：cmake -G "Visual Studio 12 2019" -DCMAKE_INSTALL_PREFIX=install -Dprotobuf_BUILD_TESTS=OFF  这样会生成Visual Studio 2019的项目文件，其它版本Visual Studio请修改-G参数
  - 打开生成的Visual Studio项目文件，平台工具集设置为v120_xp，编译即可
- Linux（参考protobuf/src/README）
  - 执行 ./autogen.sh
  - 执行 CXXFLAGS="-std=gnu++11" ./configure --disable-shared
  - 执行 make
  - 将生成的libprotobuf.a放入Bin/Linux目录
- MacOS（参考protobuf/src/README）
  - 使用brew安装这些依赖库：autoconf automake libtool
  - 执行./configure CC=clang CXX="clang++ -std=gnu++11 -stdlib=libc++" --disable-shared

#### 步骤2: 重新生成proto代码
- 上面编译Protobuf后会同时生成可执行文件protoc。用protoc将Include/Proto下面的.proto文件生成对应的.h和.cc文件。例如命令以下命令会从Common.proto生成对应的Common.pb.h和Common.pb.cc
  - protoc -I="FTAPI路径/Include/Proto" --cpp_out="." FTAPI路径/Include/Proto/Common.proto
- 将生成的.h和.cc文件放到Include/Proto下面

#### 步骤3: 重新编译FTAPI
- Windows：新建Visual Studio C++静态库工程，将Src/FTAPI和Include下的源码加入工程中，平台工具集设置为v120_xp，然后编译
- Mac：新建XCode C++静态库工程，将Src/FTAPI和Include下的源码加入工程中，然后编译
- Linux：使用CMake编译FTAPI静态库，在FTAPI路径/Src目录下执行：
  - cmake -DTARGET_OS=Linux

## Q2：有没有更完整的策略样例可以参考？

A:
* Python 策略样例在 /futu/examples/ 文件夹下。您可以通过执行如下命令，找到 Python API 的安装路径：
    ```
    import futu
    print(futu.__file__)
    ```
* C# 策略样例在 /FTAPI4NET/Sample/ 文件夹下
* Java 策略样例在 /FTAPI4J/sample/ 文件夹下
* C++ 策略样例在 /FTAPI4CPP/Sample/ 文件夹下
* JavaScript 策略样例在 /FTAPI4JS/sample/ 文件夹下


## Q3：使用 python API 导入异常

A：

**场景一**：已经在 Python 环境中安装了 futu 模块，仍然提示 No module named 'futu'？  
很可能是因为当前 IDE 所使用的 interpreter 并不是你装过 futu 模块的 interpreter。也就是说，您的电脑可能装了两个以上的 Python 环境。
您可以操作如下两步：
1. 在 Python 中运行如下代码，得到当前 interpreter 的路径：
```
import sys
print(sys.executable)
```
示例图：  
 ![No module named 'futu'](../img/import-futu-error.png)

2. 在命令行中，执行 `$ D:\software\anaconda3\python.exe -m pip install futu-api`（其中前半部分的文件路径来自第 1 步打印的路径）。
这样就可以在当前的 interpreter 中也安装一份 futu 模块。

## Q4： import 成功了，仍然调用不了相关接口？ 

A：通常遇到这种情况，需要确认一下：成功导入的 futu，是不是真正的 Futu API 模块。以下几种场景也可能 import 成功。

**场景一**：存在与“futu”重名的文件

  1. 当前文件名是 futu.py
  2. 当前文件所在目录下存在另一个名为 futu.py 的文件
  3. 当前文件所在目录下存在名为 `/futu` 的文件夹    

因此，我们强烈建议您，在给文件 / 文件夹 / 工程起名的时候，不要起名叫“futu”。重名一时爽，查 bug 两行泪。

**场景二**：误装了一个名为“futu”的第三方库  

   Futu API 的正确名称为`futu-api`，而非“futu”。   

   如果您安装过名为“futu”的第三方库，请将其卸载，并 [下载 futu-api](../quick/demo.md#4688)。
   
   以 PyCharm 为例：查看第三方库的安装情况。

   ![settings](../img/settings.png)  
   ![futuku](../img/futuku.png)


## Q5：协议加密相关

A：  
### 概述
您可以使用非对称加密算法 RSA，对策略程序（Futu API）与 OpenD 之间的请求和返回内容进行加密，以保证通信安全。  
如果您的策略程序（Futu API）与 FutuOpenD 在同一台电脑上，则通常无需加密。

### 协议加密流程
您可以尝试通过以下步骤解决此问题：
1. 通过第三方 web 平台自动生成密钥文件。  
    - 具体方法：在 baidu 或 google 上搜索“RSA 在线生成”，**密钥格式**设置为 PKCS#1，**密钥长度**设置为 1024 bit，不需要设置私钥密码，点击**生成密钥对**。  
    ![ui-config](../img/create_rsa.png)  

2. 将生成的 **RSA 加密私钥** 复制粘贴至 txt 记事本，并保存至 OpenD 所在电脑的指定路径。
3. 在 OpenD 所在的电脑中，指定 **RSA 加密私钥** 的路径。  
    - 方式一：在 [可视化 OpenD](../quick/opend-base.md#4147) 启动界面右侧的“加密私钥”一栏，指定上一步骤中放置 **RSA 加密私钥** 的路径。如下图所示：  
    ![ui-config](../img/nnrsa_ui-config.png)  
    - 方式二：在 [命令行 OpenD](../opend/opend-cmd.md#8799) 启动文件 OpenD.xml 中，找到参数`rsa_private_key`，将其配置为第 2 步中 **RSA 加密私钥** 的路径。如下图所示：  
    ![ui-config](../img/nnrsa_xml.png)  
4. 将第 2 步中 txt 文件另存至策略程序（Futu API）所在电脑的指定路径， 并在策略程序中将此路径 [设置为私钥路径](../ftapi/init.md#5641)。
5. 在策略程序（Futu API）中启用协议加密。 启用协议加密的方式有两种，其中方式二的优先级更高。
    - 方式一：对单条的连接加密（通用）。在对 [行情对象](../quote/base.md#7902) 或 [交易对象](../trade/base.md#7902) 创建连接时，通过 **是否启用加密** 参数设置加密。
    - 方式二：对所有的连接加密（仅 Python）。通过`enable_proto_encrypt`接口设置加密，详见 [这里](../ftapi/init.md#319)。


:::tip 提示
* 在 OpenD 或策略程序（Futu API）中指定 **RSA 加密私钥** 路径时，需指定至 txt 文件本身。
* RSA 加密公钥无需保存，可通过私钥计算得到。
:::


## Q6：为什么我获取的 DataFrame 数据，只能展示一部分 ？

A：打印 pandas.DataFrame 数据的时候，如果行列数过多，pandas 默认会将数据折叠，导致看起来显示不全。  
因此，并不是接口返回数据真的不全。您只需要在 Python 脚本前面加上如下代码即可解决。

```
import pandas as pd
pd.options.display.max_rows=5000
pd.options.display.max_columns=5000
pd.options.display.width=1000
```

## Q7：Mac 机器使用 C++ 语言的 API，遇到 “无法打开 libFTAPIChannel.dylib” 的问题

A：在对应库目录中执行以下命令即可解决:`$ xattr -r -d com.apple.quarantine libFTAPIChannel.dylib`。


## Q8：Python 用户，为什么在 OpenD 配置文件中设置了日志级别为 no 后，log 文件夹下仍然持续产生超大容量的日志文件？

A：OpenD 配置文件中的日志级别参数，只用来控制 OpenD 产生的日志。而 Python API 默认也会产生日志，如果您不希望希望 Python API 产生日志，可以在 Python 脚本加上如下语句：

```
logger.file_level = logging.FATAL  # 用于关闭 Python API 日志
logger.console_level = logging.FATAL  # 用于关闭 Python 运行时的控制台日志
```


## Q9：对于 5.4 及以上的版本，Java API 的库名和配置方式的变更

A:
* 如果您是 Java API 5.3 及以下版本的用户，在更新版本时，请注意以下变更：

  **配置流程的变更**：

  1. 通过 [富途牛牛官网](https://www.futunn.com/download/OpenAPI)下载 Futu API。
  2. 解压下载好的 FTAPI 文件，`/FTAPI4J` 是 Java API 的目录，将目录结构中的 `/lib/futu-api-.x.y.z.jar` 添加到您的工程设置中。创建 futu-api 工程请参考 [这里](../quick/demo.html#2927)。


  **目录结构的变更**：
  1. Futu API 的 Java 版本，库名由之前的 ftapi4j.jar 变更为 `futu-api-x.y.z.jar`，其中 “x.y.z” 表示版本号。
  2. 第三方库的引用中，去掉了 /lib/jna.jar 和 /lib/jna-platform.jar 依赖，增加了 `/lib/bcprov-jdk15on-1.68.jar` 和 `/lib/bcpkix-jdk15on-1.68.jar` 依赖。
    ```
    +---ftapi4j                      futu-api 源码，如果所用 JDK 版本不兼容可以用这里的工程重新编译出 futu-api.jar
    +---lib                          存放公共库文件
    |    futu-api-x.y.z.jar          Futu API 的 Java 版本
    |    bcprov-jdk15on-1.68.jar     第三方库，用于加解密
    |    bcpkix-jdk15on-1.68.jar     第三方库，用于加解密
    |    protobuf-java-3.5.1.jar     第三方库，用于解析 protobuf 数据
    +---sample                       示例工程
    +---resources                    maven 工程默认生成的目录
    ```
* 如果您第一次接触 Futu API，我们提供了更便捷的通过 maven 仓库配置 Java API 的方式。配置流程请参考 [这里](../quick/demo.html#5757)。


## Q10：Python 用户，使用 pyinstaller 打包脚本时报错：找不到 Common_pb2 模块

A：你可以尝试通过以下步骤解决此问题：
1. 假设你需要对 main.py 进行打包。使用命令行语句，运行代码：pyinstaller main.py，不要加参数 “- F”（path 为 main.py 的所在路径）
  ```
  pyinstaller path\main.py
  ```
  打包成功后，main.py 所在目录下的 /dist 中，会生成 /main 文件夹，main.exe 就在这个文件夹中。  
  ![dist](../img/dist.png)  
2. 运行以下代码，找到 futu-api 的安装目录。  
  ```
  import futu
  print(futu.__file__)
  ```
  运行结果:  
  ```
  C:\Users\ceciliali\Anaconda3\lib\site-packages\futu\__init__.py
  ```
  ![path_futu](../img/path_futu.png)  

3. 打开上图文件夹中的 /common/pb，将所有文件全部复制到 /main 中。

4. 在 /main 中创建文件夹，命名为 futu，将上图文件夹中的 `VERSION.txt` 文件复制到 /main/futu 中。  
  ![main_futu](../img/main_futu.png) 
5. 再次尝试运行 main.exe

## Q11：接口调用结果正常，但其返回表现不符合预期？
A:
* 接口调用结果正常，表示富途已经成功收到并响应了您的请求，但接口返回表现可能与您的预期不符。  

  例如：若您在非交易时段调用 [订阅](../quote/sub.md) 接口，虽然您的请求可以被成功响应，并且接口调用结果正常，但在非交易时段下，交易所无行情数据变动，所以您将暂时无法收到行情数据推送，直至市场重新回到交易时段。  
* 接口调用结果可以通过返回字段（定义参见：[接口调用结果](../ftapi/common.md#7467)）查看，返回字段为 0 代表接口调用正常，非 0 代表接口调用失败。  
  
  对于 Python 用户，下面两种写法等价：
  ```
  if ret_code == RET_OK:
  ```
  ```
  if ret_code == 0:
  ```

## Q12：WebSocket相关
A：

### 概述

Futu API 中，WebSocket 主要用于以下两方面：
* 可视化 OpenD 中，UI 界面跟底层的命令行 OpenD 的通信使用 WebSocket 方式。
* JavaScript API 跟 OpenD 之间的通信使用 WebSocket 方式。

![WebSocket-struct](../img/WebSocket-struct.png)  
* 当 WebSocket 启动时，命令行 OpenD 会与 **FTWebSocket 中转服务** 建立 Socket 连接（TCP），这一连接会用到默认的 **监听地址** 和 **API 协议监听端口**。
* 同时，JavaScript API 会与 **FTWebSocket 中转服务** 建立 WebSocket 连接（HTTP），这一连接会用到 **WebSocket 监听地址** 和 **WebSocket 端口**。

### 使用
为保证账户安全，当 WebSocket 监听来自非本地请求时，我们强烈建议您启用 SSL 并配置 **WebSocket 鉴权密钥**。

SSL 通过在配置 **WebSocket 证书** 以及 **WebSocket 私钥** 来启用。  
命令行 OpenD 可通过配置 OpenD.xml 或配置命令行参数来设置文件路径。可视化 OpenD 点击【更多选项】下拉菜单，可以看到设置项。

![ui-more-config](../img/ui-more-config.png)

::: tip 提示
如果证书是自签的，则需要在调用 JavaScript 接口所在机器上安装该证书，或者设置不验证证书。
:::

#### 生成自签证书
自签证书生成详细资料不便在此文档展开，请自行查阅。  
在此提供较简单可用的生成步骤：
1. 安装 openssl。
2. 修改 openssl.cnf，在 alt_names 节点下加上 OpenD 所在机器 IP 地址或域名。  
例如：IP.2 = xxx.xxx.xxx.xxx, DNS.2 = www.xxx.com
3. 生成私钥以及证书（PEM）。

**证书生成参数参考如下**：  
`openssl req -x509 -newkey rsa:2048 -out futu.cer -outform PEM -keyout futu.key -days 10000 -verbose -config openssl.cnf -nodes -sha256 -subj "/CN=Futu CA" -reqexts v3_req -extensions v3_req`

::: tip 提示
* openssl.cnf 需要放到系统路径下，或在生成参数中指定绝对路径。
* 注意生成私钥需要指定不设置密码（-nodes）。
:::

附上本地自签证书以及生成证书的配置文件供测试：  
* [openssl.cnf](../file/openssl.cnf)  
* [futu.cer](../file/cer)  
* [futu.key](../file/key)

## Q13：API 的行情和交易服务分别部署在哪里？
A：  
- 行情：  

平台账号|行情服务器所在地
:-|:-|:-
牛牛号|腾讯云广州和香港
moomoo 号|腾讯云美国弗吉尼亚和新加坡

- 交易：  

所属券商|交易服务器所在地
:-|:-|:-
富途证券(香港)|香港
moomoo证券(美国)|腾讯云美国弗吉尼亚
moomoo证券(新加坡) |腾讯云新加坡
moomoo证券(澳大利亚)|腾讯云新加坡
moomoo证券(马来西亚)|阿里云马来西亚
moomoo证券(加拿大)|AWS加拿大
moomoo证券(日本)|腾讯云日本


## Q14：关于综合账户升级的过渡指引

### 1. [**综合账户升级**](https://www.futuhk.com/hans/support/topic2_1734)
综合账户支持以多种货币在同一个账户内交易不同市场品类。从单币种账户升级到综合账户，是在您原来的牛牛号下，进行账户迁移。主要包括：
- 创建新的综合账户
- 将您原来单币种业务账户里的资产，转移到综合账户里
- 关闭原来的单币种账户

### 2. **OpenD版本升级**
我们会在 2024年9月14日、15日 集中为 Futu API 客户的账户做升级，请提前检查 OpenD 和 API 版本号：  
- **7.01 及以下版本**  
  OpenD 因版本过旧，将于 2024/09/14 停止服务。届时，已登录的账户会被强制退出登录。我们建议您在 9/14 之前升级 [OpenD](../quick/opend-base.html#4147) 和 [API](../quick/demo.html#4688) 至最新版本，且不要在 9/14~9/15 期间跨周末运行策略。
- **7.02 ~ 8.2 版本**  
  OpenD 版本较旧，无法获取综合账户。我们建议您在 9/14 之前升级 [OpenD](../quick/opend-base.html#4147) 和 [API](../quick/demo.html#4688) 至最新版本，且不要在 9/14~9/15 期间跨周末运行策略。
- **8.3 及以上版本**  
  可以正常使用，我们建议您不要在 9/14~9/15 期间跨周末运行策略。  

综合账户升级时，您的资产会转移到新的综合账户，如果策略指定旧的账户，可能会运行异常。同时，在实盘交易之前，建议您进行必要的检查与测试，确保一切设置正常。

### 3. **账户升级后，Futu API有哪些表现？**
- Python API 将不再支持使用 OpenHKTradeContext,  OpenUSTradeContext, OpenHKCCTradeContext, OpenCNTradeContext 创建交易对象，请参考 [创建交易对象连接](../trade/base.html#7902) 改用 OpenSecTradeContext。  
- 非Python API用户，在使用 Trd_GetAccList 接口时，需要将 needGeneralSecAccount 参数设为 true，才能获取到综合账户的相关信息。  
- 账户新增 [账户状态](../trade/trade.html#121): 在使用 [获取交易业务账户列表](../trade/get-acc-list.html#5754) 时，返回结果新增了账户状态 。综合账户标记为 `ACTIVE` 生效账户，被停用的单币种账户标记为 `DISABLED` 失效账户。  
- [下单](../trade/place-order.html#4080)、[改单撤单](../trade/modify-order.html#7408)、[查询最大可买可卖](../trade/get-max-trd-qtys.html#2713) 等交易接口表现  
    - 支持使用 `ACTIVE` 生效账户所对应的 acc_id或acc_index 进行购买力查询与交易。
    - 不支持使用 `DISABLED` 失效账户所对应的 acc_id或acc_index 进行购买力查询与交易，若使用，将会出现报错信息。
    - Python API用户：在接口入参中，请指定 acc_id 为升级后的综合账户。
    - 非Python API用户：在 TrdHeader 中，请指定accID为升级后的综合账户。

---

# 更新日志

## 2026-06-25

### [OpenD 10.8.6808](https://www.futunn.com/download/OpenAPI)


* 支持[行情搜索](../quote/get-search-quote.md)接口，关键词智能搜索行情标的，一键定位目标资产   
* 支持[资讯搜索](../quote/get-search-news.md)接口，关键词搜资讯，新闻、公告、评级一网打尽   
* [指标列表](../quote/get-indicator-list.md)全量开放，支持麦语言、Python，技术分析触手可及  
* 期权数据全维覆盖：IV/HV、Put/Call 比、末日期权、财报期权、卖方策略，期权玩家必备，详见[行情接口](../quote/overview.md)   
* 市场基本面数据上线：机构追踪、精选宏观数据、派息/财报日历、各类榜单、产业链、FedWatch，洞察先机，详见[行情接口](../quote/overview.md)


## 2026-06-04

### [OpenD 10.7.6708](https://www.futunn.com/download/OpenAPI)


* 支持获取新加坡股票、马来西亚股票、日本股票行情数据，支持实时报价、摆盘、K线、基本面数据等多种能力，权限详见 [行情权限](../intro/authority.md#2867)   
* 支持交易新加坡股票、马来西亚股票、日本股票，订单能力全面对齐 App 端，覆盖 HK/SG/MY/JP 地区用户   
* 支持组合期权行情与交易能力，覆盖跨式、价差、蝶式等多种策略。支持[获取期权策略](../quote/get-option-strategy.md)、[期权损益分析](../quote/get-option-strategy-analysis.md)、[期权快照](../quote/get-option-quote.md) 等行情数据，通过[组合下单](../trade/place-combo-order.md) 交易组合期权，[查询组合期权购买力](../trade/comboorder-tradinginfo-query.md) 变动信息


## 2026-05-21

### [OpenD 10.6.6608](https://www.futunn.com/download/OpenAPI)


* 像在客户端一样组合筛选条件：通过 API 直接调用 [筛选正股](../quote/get-stock-screen.md#3910) 接口，从基本面、技术面、形态面 5 大维度自由组合，一行代码筛出符合策略的股票  
* 像在客户端一样查询个股基本面数据：通过 API 直接调用 [个股基本面数据](../quote/get-financials-statements.md#6376) 接口获取财务三大表、主营构成、分析师评级、晨星研报、估值（PE/PB/PS）、分红回购拆股、股东持股、内部人交易、公司概况与高管、十大经纪商、卖空数据


## 2026-05-07

### [OpenD 10.5.6508](https://www.futunn.com/download/OpenAPI)

* 新增加密货币（Crypto）行情与交易支持，覆盖 HK/US/SG 地区用户
* 新增加密货币账户资金、持仓、订单记录、资金流水查询
* K线类型 [KLType](../quote/quote.md#4119) 新增 `K_10M`(10分K)、`K_120M`(2小时K)、`K_180M`(3小时K)、`K_240M`(4小时K)
* OpenD Skills 支持加密货币功能


## 2026-04-23

### [OpenD 10.4.6408](https://www.futunn.com/download/OpenAPI)

* 交易对象连接 `OpenSecTradeContext()`, `OpenFutureTradeContext()`, `OpenCryptoTradeContext()` `security_firm` 参数默认值变更为 `NONE`，系统将自动匹配当前账户所属券商，无需手动指定
* 新增日志静默模式，支持关闭 OpenD 日志输出
* Windows 安装包文件名嵌入版本号，便于版本识别与管理
* OpenD Skills 性能优化


## 2026-04-16

### [OpenD 10.3.6308](https://www.futunn.com/download/OpenAPI)

* 美股实时行情推广期免费开放
* OpenD 支持未开户用户登录使用，附赠 100 只标的实时行情订阅额度及历史 K 线请求额度
* 历史 K 线请求额度重置周期由 30 天缩短至 7 天


## 2026-03-26

### [OpenD 10.2.6208](https://www.futunn.com/download/OpenAPI)

* API 新增美股融资融券模拟交易支持，通过设置 `TrdEnv.SIMULATE` 即可进行模拟下单，订单状态实时同步至 App 端
* OpenD Skills 性能优化


## 2026-03-20

### OpenD 10.1.6108

* 全新推出 [Futu Skills Hub](https://www.futunn.com/skillhub)，支持 OpenClaw、Claude Code、Cursor、Codex 等主流 AI Agent 接入
* 行情与交易 [Futu API Skill](https://www.futunn.com/skillhub/openapi) 覆盖 56 个 API 接口，支持香港、美国、沪深、新加坡、日本等市场，覆盖实时行情、智能交易、实时推送三大能力


## 2026-03-06

### OpenD 10.0.6018

* 修复近期已知问题


## 2025-12-17

### OpenD 9.6.5608

* 行情接口新增恒生系列指数支持，涵盖 HK.800733、HK.800734 等 82 个指数标的
* [获取交易账户列表](../trade/get-acc-list.md#5754)接口 `TrdAccRole()` 新增支持获取机构主账户，`TrdAccRole.MASTER` 表示主账户（主账户不支持交易操作）
* 修复近期已知问题


## 2025-08-14

### OpenD 9.4.5408

* 支持美股全时段订单，下单接口 [place_order()](../trade/place-order.md)传入 `Session.ALL` 即可覆盖盘前、盘中及盘后时段
* 历史日 K 数据范围扩展至近 20 年
* 美国股票 LV2 深度摆盘升级至 60 档聚合盘口数据；美国期货 LV2 升级至 40 档盘口数据
* 新增公司分立（Spin-off）行动的复权数据支持
* [获取期货合约资料](../quote/get-future-info.md)接口中 `min_change_unit`（最小变动单位）字段已废弃