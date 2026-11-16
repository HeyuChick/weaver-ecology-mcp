# -*- coding: utf-8 -*-
# Patch 3: JSON body support.
# - client.ts: rawRequest/callApi/callWhitelistApi gain jsonBody option
# - index.ts: weaver_api_request gains jsonBody param
import io

def patch(path, pairs):
    with io.open(path, 'r', encoding='utf-8', newline='') as f:
        s = f.read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old[:60], s.count(old))
        s = s.replace(old, new)
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(s)
    print('patched', path)

# ---------- client.ts ----------
patch('src/client.ts', [
    # callApi signature + json passthrough
    (
        '  async callApi<T>(\r\n'
        '    path: string,\r\n'
        '    method: "GET" | "POST" | "PUT" | "DELETE" = "POST",\r\n'
        '    params?: Record<string, unknown>,\r\n'
        '    userId?: number,\r\n'
        '  ): Promise<T> {',
        '  async callApi<T>(\r\n'
        '    path: string,\r\n'
        '    method: "GET" | "POST" | "PUT" | "DELETE" = "POST",\r\n'
        '    params?: Record<string, unknown>,\r\n'
        '    userId?: number,\r\n'
        '    jsonBody?: boolean,\r\n'
        '  ): Promise<T> {'
    ),
    (
        '    return this.rawRequest<T>(url, method, headers, params);\r\n'
        '  }\r\n'
        '\r\n'
        '  /**\r\n'
        '   * 调用白名单接口（不带 userid）',
        '    return this.rawRequest<T>(url, method, headers, params, jsonBody);\r\n'
        '  }\r\n'
        '\r\n'
        '  /**\r\n'
        '   * 调用白名单接口（不带 userid）'
    ),
    # callWhitelistApi signature + passthrough
    (
        '  async callWhitelistApi<T>(\r\n'
        '    path: string,\r\n'
        '    method: "GET" | "POST" | "PUT" | "DELETE" = "POST",\r\n'
        '    params?: Record<string, unknown>,\r\n'
        '  ): Promise<T> {',
        '  async callWhitelistApi<T>(\r\n'
        '    path: string,\r\n'
        '    method: "GET" | "POST" | "PUT" | "DELETE" = "POST",\r\n'
        '    params?: Record<string, unknown>,\r\n'
        '    jsonBody?: boolean,\r\n'
        '  ): Promise<T> {'
    ),
    (
        '    return this.rawRequest<T>(url, method, headers, params);\r\n'
        '  }\r\n'
        '\r\n'
        '  /**\r\n'
        '   * 原生 HTTP 请求',
        '    return this.rawRequest<T>(url, method, headers, params, jsonBody);\r\n'
        '  }\r\n'
        '\r\n'
        '  /**\r\n'
        '   * 原生 HTTP 请求'
    ),
    # rawRequest: signature + content-type + body encoding
    (
        '  private async rawRequest<T>(\r\n'
        '    url: string,\r\n'
        '    method: string,\r\n'
        '    headers: Record<string, string>,\r\n'
        '    body?: Record<string, unknown>,\r\n'
        '  ): Promise<T> {\r\n'
        '    const fetchOptions: RequestInit = {\r\n'
        '      method,\r\n'
        '      headers: {\r\n'
        '        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",\r\n'
        '        ...headers,\r\n'
        '      },\r\n'
        '    };\r\n'
        '\r\n'
        '    if (body && method !== "GET") {\r\n'
        '      // 泛微 API 通常使用 form-urlencoded\r\n'
        '      const params = new URLSearchParams();\r\n'
        '      for (const [key, value] of Object.entries(body)) {\r\n'
        '        params.append(key, String(value));\r\n'
        '      }\r\n'
        '      fetchOptions.body = params.toString();\r\n'
        '    }',
        '  private async rawRequest<T>(\r\n'
        '    url: string,\r\n'
        '    method: string,\r\n'
        '    headers: Record<string, string>,\r\n'
        '    body?: Record<string, unknown>,\r\n'
        '    jsonBody?: boolean,\r\n'
        '  ): Promise<T> {\r\n'
        '    const contentType = jsonBody\r\n'
        '      ? "application/json; charset=UTF-8"\r\n'
        '      : "application/x-www-form-urlencoded; charset=UTF-8";\r\n'
        '    const fetchOptions: RequestInit = {\r\n'
        '      method,\r\n'
        '      headers: {\r\n'
        '        "Content-Type": contentType,\r\n'
        '        ...headers,\r\n'
        '      },\r\n'
        '    };\r\n'
        '\r\n'
        '    if (body && method !== "GET") {\r\n'
        '      if (jsonBody) {\r\n'
        '        // 泛微 paService 等接口读取整个 JSON body（request2Json）\r\n'
        '        fetchOptions.body = JSON.stringify(body);\r\n'
        '      } else {\r\n'
        '        // 泛微 API 通常使用 form-urlencoded\r\n'
        '        const params = new URLSearchParams();\r\n'
        '        for (const [key, value] of Object.entries(body)) {\r\n'
        '          params.append(key, String(value));\r\n'
        '        }\r\n'
        '        fetchOptions.body = params.toString();\r\n'
        '      }\r\n'
        '    }'
    ),
])

# ---------- index.ts ----------
patch('src/index.ts', [
    # tool schema: add jsonBody
    (
        '      isWhitelist: {\r\n'
        '        type: "boolean",\r\n'
        '        description: "是否为白名单接口（无需userid），默认为false",\r\n'
        '      },',
        '      isWhitelist: {\r\n'
        '        type: "boolean",\r\n'
        '        description: "是否为白名单接口（无需userid），默认为false",\r\n'
        '      },\r\n'
        '      jsonBody: {\r\n'
        '        type: "boolean",\r\n'
        '        description: "以 application/json 发送整个 params 作为请求体（paService 写接口等需要），默认 false 走 form-urlencoded",\r\n'
        '      },'
    ),
    # handler: read jsonBody, pass through
    (
        '          const a = args as {\r\n'
        '            path: string;\r\n'
        '            method?: "GET" | "POST" | "PUT" | "DELETE";\r\n'
        '            userId?: number;\r\n'
        '            params?: Record<string, unknown>;\r\n'
        '            isWhitelist?: boolean;\r\n'
        '          };\r\n'
        '          const method = a.method || "POST";\r\n'
        '\r\n'
        '          let data: unknown;\r\n'
        '          if (a.isWhitelist) {\r\n'
        '            data = await client.callWhitelistApi(a.path, method, a.params);\r\n'
        '          } else if (a.userId) {\r\n'
        '            data = await client.callApi(a.path, method, a.params, a.userId);\r\n'
        '          } else {',
        '          const a = args as {\r\n'
        '            path: string;\r\n'
        '            method?: "GET" | "POST" | "PUT" | "DELETE";\r\n'
        '            userId?: number;\r\n'
        '            params?: Record<string, unknown>;\r\n'
        '            isWhitelist?: boolean;\r\n'
        '            jsonBody?: boolean;\r\n'
        '          };\r\n'
        '          const method = a.method || "POST";\r\n'
        '\r\n'
        '          let data: unknown;\r\n'
        '          if (a.isWhitelist) {\r\n'
        '            data = await client.callWhitelistApi(a.path, method, a.params, a.jsonBody);\r\n'
        '          } else if (a.userId) {\r\n'
        '            data = await client.callApi(a.path, method, a.params, a.userId, a.jsonBody);\r\n'
        '          } else {'
    ),
])
