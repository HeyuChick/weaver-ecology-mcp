---
name: weaver-ecology
description: Use Weaver Ecology E9 OA MCP tools for workflows, HR, departments, documents, and custom OA API calls.
---

Use the Weaver Ecology MCP when the user needs to query or operate a Weaver Ecology E9 OA system.

Before using the MCP tools, make sure Open One environment variables are configured and the local Open One server or engine has been restarted:

- `WEAVER_BASE_URL`: required. Ecology server origin, for example `http://192.168.1.100`.
- `WEAVER_APP_ID`: required. Ecology license APPID.
- `WEAVER_RSA_PRIVATE_KEY`: optional RSA private key PEM.
- `WEAVER_RSA_PUBLIC_KEY`: optional RSA public key PEM.

The Ecology server must also allow these unauthenticated endpoints in `ecology/WEB-INF/prop/weaver_session_filter.properties`:

```text
/api/ec/dev/auth/regist;/api/ec/dev/auth/applytoken;
```

The Ecology database must contain a matching license row:

```sql
INSERT INTO ECOLOGY_BIZ_EC(ID, APPID, NAME)
VALUES('123456', 'your-app-id', 'MCP service');
```

Available MCP tools include:

- `weaver_auth_register`
- `weaver_auth_get_token`
- `weaver_workflow_list`
- `weaver_workflow_create`
- `weaver_workflow_query`
- `weaver_workflow_approve`
- `weaver_hrm_user_query`
- `weaver_hrm_dept_query`
- `weaver_doc_upload`
- `weaver_api_request`
