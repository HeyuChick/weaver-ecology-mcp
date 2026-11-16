# 本仓库变更（相对上游 fork wenzhengclaude/weaver-ecology-mcp-openone）

上游原仓库 `tanzhangjia/weaver-ecology-mcp` 已从 GitHub 删除，本仓库基于唯存 fork
（codeload tarball，tree `968089f1`）源码构建。上游代码**从未在真实泛微 E9 上跑通过**，
以下 5 项缺陷均在对真实 E9 测试环境实测中发现并修复（2026-11）：

1. **`cpk` 请求头单行化**（`src/crypto.ts: pemToSingleLine`）
   上游把多行 PEM 公钥直接放进 `cpk` 头，Node fetch 拒绝含换行的 header 值。
   泛微官方 demo 格式为不含 PEM 头尾/换行的单行 base64。

2. **`spk` 包装为 PEM**（`src/crypto.ts: ensurePem`）
   E9 `regist` 返回的系统公钥 `spk` 是单行 base64，`forge.pki.publicKeyFromPem`
   需要完整 PEM（按 64 字符折行包装）。

3. **RSA 填充改为 PKCS#1 v1.5**（`src/crypto.ts: rsaEncrypt`）
   上游注释声称 OAEP-SHA256；实测 E9 `applytoken`/`userid` 解密只接受
   `RSAES-PKCS1-V1_5`（OAEP-SHA256 / OAEP-SHA1 均返回 "secret解密失败"）。

4. **JSON body 通道**（`src/client.ts` + `src/index.ts`，`weaver_api_request` 新增
   `jsonBody` 参数）
   上游只会 `application/x-www-form-urlencoded`。E9 `/api/workflow/paService/*`
   写接口（`doCreateRequest` 等）经 `request2Entity→request2Json` 读取**整个 JSON
   body**：form 模式下 `mainData` 全部丢失、落库为 NULL。
   读接口（`getCreateWorkflowList`/`getToDoRequestList` 等）用 form 参数即可。

5. **工具描述与事实不符的警示**
   上游内置工具端点（`/api/workflow/request/create|approve|status`、
   `/api/hrm/employee/*`、`/api/file/upload`）在真实 E9 上不存在（404/空响应），
   属自拟端点。实际可用路径是 `weaver_api_request` + 官方端点。
   本仓库保留这些工具但请勿依赖（未改其内部路径，改动见上方 jsonBody 通道）。

## 实测记录（真实 E9 测试环境）

- 认证链：`regist`(cpk 单行) → `applytoken`(PKCS1v15) → 业务调用(userid 头) 全通。
- `/api/hrm/resful/getHrmUserInfoWithPage`：form 参数 `params`=JSON 字符串
  `{"curpage":1,"pagesize":N}`（数字不可加引号）+ 可选过滤
  `id/loginid/workcode/departmentid/subcompanyid1/jobtitleid/created/modified`。
  注意该接口明文返回身份证号/手机号，调用须限定过滤条件。
- `/api/workflow/paService/doCreateRequest`（JSON body）建单成功、主表字段全部落库
  （数据库比对实证）。
- 孤儿单（`workflow_currentoperator` 无行）对所有删除/收回 API 返回 NO_PERMISSION。

## 行尾约定

仓库索引统一 LF（`core.autocrlf=false` + `.gitattributes`）。上游 tarball 内
`src/*.ts` 为 CRLF，import 提交在索引中已归一为 LF，内容不变。

`patches/patch-*.py` 为逐项修复的过程脚本（CRLF 精确替换），保留作 provenance；
等价改动已直接体现在 `src/` 中。
