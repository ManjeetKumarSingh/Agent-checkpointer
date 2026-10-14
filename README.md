```python
                         User Request
                              │
                              ▼
                     ┌─────────────────┐
                     │   LangGraph     │
                     │   Supervisor    │
                     └────────┬────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
          ┌──────────┐  ┌──────────┐  ┌──────────┐
          │ Research │  │   Data   │  │  Coding  │
          │  Agent   │  │  Agent   │  │  Agent   │
          └────┬─────┘  └────┬─────┘  └────┬─────┘
               │             │             │
               ▼             ▼             ▼
          Internal Tools  Internal Tools  Internal Tools
               │             │             │
               └─────────────┼─────────────┘
                             ▼
                    ┌─────────────────┐
                    │    Synthesizer  │
                    │      Agent      │
                    └────────┬────────┘
                             │
                             ▼
                           Result

```

```
Agent-checkpointer/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── graph.py
│   ├── state.py
│   ├── llm.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── research_agent.py
│   │   ├── calculation_agent.py
│   │   └── summary_agent.py
│   │
│   └── tools/
│       ├── __init__.py
│       ├── research_tools.py
│       └── calculation_tools.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```


```requirements.txt 

fastapi
uvicorn[standard]

langgraph
langchain
langchain-core

langchain-groq

langgraph-checkpoint-postgres
psycopg[binary,pool]

python-dotenv
pydantic

black

```


### For running the api endpoints :

`uvicorn app.main:app --reload`


```MultyModelRag.txt

                         USER PDF
                            │
                            ▼
                    ┌─────────────┐
                    │     S3      │
                    │  Raw Zone   │
                    └──────┬──────┘
                           │
                     EventBridge
                           │
                           ▼
                    Step Functions
                           │
                           ▼
              ┌────────────────────────┐
              │ Bedrock Data Automation │
              │     / FM Parser         │
              └───────────┬────────────┘
                          │
             ┌────────────┼─────────────┐
             ▼            ▼             ▼
           TEXT         TABLE         IMAGE
             │            │             │
             ▼            ▼             ▼
         Chunking     Structured    S3 image
             │          table          │
             │            │            │
             └────────────┼────────────┘
                          ▼
                  Embedding Layer
                          │
             ┌────────────┴────────────┐
             │                         │
        Text Embedding          Multimodal
        Titan V2                Embedding
             │                         │
             └────────────┬────────────┘
                          ▼
                OpenSearch Serverless
                  Vector Index
                          │
                          ▼
                    Hybrid Search
                 BM25 + Vector Search
                          │
                          ▼
                       Reranker
                          │
                          ▼
                     LangGraph
                          │
                          ▼
                    Amazon Nova
                     VLM / LLM
                          │
                          ▼
                      RESPONSE

```

'''
Manjeet, let’s build this using the same architecture we’ve been discussing for your multi-agent application with FastAPI, LangGraph, a Supervisor–Worker pattern, and a Python FastMCP server.

The key requirement is that the MCP server must know who is calling, what they are allowed to do, and which data they can access. It must not blindly trust a request just because it comes from your LangGraph agent.

1. Target architecture

React / Streamlit UI

User signs in through an identity provider

Bearer access token (JWT)

API Gateway + FastAPI

Validate user identity and establish trusted request context

LangGraph orchestration

Supervisor → specialized worker agents → MCP client

Authorization: Bearer access token

FastMCP server — security boundary

1. Authentication

Signature, issuer, audience, expiry

2. Authorization

Roles, scopes, resource ownership

Enterprise APIs / databases

Apply their own access controls as well

In production, the API Gateway may validate the incoming JWT before forwarding the request, but the MCP server still validates the credential it receives. Gateway validation alone is not enough to secure an independently reachable MCP endpoint.

2. Understand the four security concepts

Concept	Purpose	Example
Authentication	Who are you?	User ID is manjeet-123
Role-based authorization (RBAC)	Which category of actions may you perform?	manager can update a case
Scope-based authorization	Which operations has this token been granted?	cases:write
Resource-level authorization	Which particular records can you access?	Only cases assigned to your team

A role and a scope are not interchangeable. For example, a manager’s token might contain the manager role and cases:read scope, but it should not be allowed to delete cases.

For our example, we’ll use this access policy:

Role	Read cases	Update cases	Delete cases
analyst	Yes	No	No
manager	Yes	Yes	No
admin	Yes	Yes	Yes

The server will enforce both the required scope and role. It will also check record ownership or tenant boundaries where applicable.

3. Step 1 — Define how JWT authentication works

A JWT (JSON Web Token) is a signed token containing claims about the identity and permissions of the caller.

The flow is:

* The user signs in.
* Your identity provider authenticates the user.
* It issues an access token.
* The frontend sends the token to FastAPI.
* FastAPI validates the token and starts the LangGraph workflow.
* The LangGraph MCP client sends an appropriate access token to the MCP server.
* The MCP server validates the token independently.
* It checks the required role, scope and resource permissions before executing a tool.

In a real enterprise application, use an identity provider such as Microsoft Entra ID, Amazon Cognito or Okta. Since we’ve discussed custom JWT/FastAPI authentication, I’ll show the mechanics with a custom issuer for a local demonstration, then explain how to replace it with your corporate identity provider.

4. What does the JWT look like?

Here is a representative decoded payload. This is only the payload; the real token also has a header and a cryptographic signature.

{
  "sub": "manjeet-123",
  "iss": "https://auth.example.com",
  "aud": "cases-mcp-api",
  "iat": 1791970000,
  "nbf": 1791970000,
  "exp": 1791970900,
  "jti": "unique-token-id",
  "roles": ["manager"],
  "scope": "cases:read cases:write",
  "tenant_id": "tenant-001"
}

The important claims are:

* sub: the user or service identity.
* iss: the trusted token issuer.
* aud: the intended recipient, in this example the MCP API.
* iat, nbf, exp: issue, activation and expiry times.
* roles: role assignments.
* scope: permitted operations.
* tenant_id: the tenant boundary, when applicable.
* jti: unique token ID, useful for audit and revocation strategies.

A JWT is generally signed, not encrypted. Do not put passwords, secrets or unnecessary personal data inside it.

Important: The MCP server must verify the signature and claims. Decoding a JWT with a library such as Base64, without verifying its signature, proves nothing about who issued it.

5. Step 2 — Create the authorization policy

We’ll use these scope names throughout the example:

cases:read
cases:write
cases:delete

The policy should be enforced by the MCP server, not by the LLM prompt or the Supervisor agent.

ROLE_SCOPES = {
    "analyst": {
        "cases:read",
    },
    "manager": {
        "cases:read",
        "cases:write",
    },
    "admin": {
        "cases:read",
        "cases:write",
        "cases:delete",
    },
}

This is the role-to-scope policy for our example. In production, your identity provider or authorization service should be the authoritative source of permissions. The MCP server should still enforce the required permissions on every operation.

For example, if the LLM tries to invoke delete_case, it must not matter whether the LLM thinks the user is an administrator. The server must independently reject the call unless the validated identity has the required permission.

6. Step 3 — Configure JWT validation in FastMCP

Install the packages in your MCP server environment:

pip install fastmcp

For our implementation, use FastMCP’s built-in JWTVerifier. It validates the token against the issuer’s public keys, issuer and audience, rather than making you write signature-verification middleware yourself. See the official FastMCP token verification guide⁠￼.

mcp_server.py

import os
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.auth import (
    require_scopes,
    require_roles,
)
# These must match the configuration of your trusted issuer.
ISSUER = os.environ["JWT_ISSUER"]
JWKS_URI = os.environ["JWT_JWKS_URI"]
AUDIENCE = "cases-mcp-api"
# Authentication: validate incoming bearer tokens.
auth = JWTVerifier(
    jwks_uri=JWKS_URI,
    issuer=ISSUER,
    audience=AUDIENCE,
)
mcp = FastMCP(
    name="Enterprise Cases MCP",
    auth=auth,
)
# Example role claim used by our custom JWT issuer.
# Adjust this extractor if your identity provider uses
# a different claim structure.
def extract_roles(claims: dict) -> list[str]:
    roles = claims.get("roles", [])
    return roles if isinstance(roles, list) else []
# READ: analyst, manager or admin with cases:read.
@mcp.tool(
    auth=[
        require_scopes("cases:read"),
        require_roles(
            "analyst", "manager", "admin",
            extract=extract_roles,
        ),
    ]
)
def get_case(case_id: str) -> dict:
    """Retrieve a case the caller is permitted to access."""
    # Replace this sample with a repository call.
    return {
        "case_id": case_id,
        "status": "OPEN",
    }
# WRITE: manager or admin with cases:write.
@mcp.tool(
    auth=[
        require_scopes("cases:write"),
        require_roles(
            "manager", "admin",
            extract=extract_roles,
        ),
    ]
)
def update_case(case_id: str, status: str) -> dict:
    """Update a case after checking record-level access."""
    # Perform a database/API ownership and tenant check here.
    return {
        "case_id": case_id,
        "status": status,
    }
# DELETE: admin with cases:delete.
@mcp.tool(
    auth=[
        require_scopes("cases:delete"),
        require_roles("admin", extract=extract_roles),
    ]
)
def delete_case(case_id: str) -> dict:
    """Delete an authorized case."""
    # Perform a record-level check and audit before deletion.
    return {
        "case_id": case_id,
        "deleted": True,
    }
if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8001,
    )

The built-in authorization checks combine using AND logic: both the scope and the role must pass.

The returned records above are illustrative. Before connecting this to a real database, implement record-level access checks, and make deletion transactional and auditable. Pin and test your FastMCP version because APIs can change between major versions.

What happens inside the MCP server?

Suppose a manager calls update_case.

* The HTTP transport extracts the bearer token.
* JWTVerifier validates its signature using the trusted public key published through JWKS.
* It checks the issuer, audience and token validity, including expiration.
* FastMCP obtains the verified token claims and scopes.
* require_scopes("cases:write") checks the scope.
* require_roles(...) checks the role.
* If either check fails, the tool must not execute.
* If both pass, the tool executes, subject to any record-level checks.

You do not need to manually parse the raw Authorization header inside every tool. FastMCP handles transport authentication, and its authorization checks operate on the verified token context.

7. Step 4 — Configure the identity provider and signing keys

Your MCP server needs to know which issuer to trust.

Set these environment variables:

export JWT_ISSUER="https://auth.example.com"
export JWT_JWKS_URI="https://auth.example.com/.well-known/jwks.json"

These are illustrative URLs. Replace them with the real values from your identity provider.

The issuer’s JWKS endpoint publishes public signing keys. The identity provider retains the private key and uses it to sign tokens; your MCP server needs only the trusted public keys to verify them.

Signing versus verification

Identity provider

Private key → signs JWT → issues access token

MCP server

Public key from JWKS → verifies JWT signature

Do not embed the private signing key in your LangGraph code, MCP server image or frontend.

If you operate your own issuer, it must securely manage signing keys, publish the matching JWKS, issue short-lived access tokens and support key rotation. For an enterprise deployment, an established identity provider is usually preferable to building a custom login and token service.

8. Step 5 — How the JWT is passed from FastAPI to LangGraph

This is one of the most important parts of your architecture.

The frontend sends the token in the HTTP header, not in the request body.

POST /api/ask HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
Content-Type: application/json
{
  "question": "Update case C-102 to CLOSED"
}

FastAPI extracts and validates the token, then invokes LangGraph.

# api.py
import os
import jwt
from jwt import PyJWKClient
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
app = FastAPI()
bearer = HTTPBearer()
issuer = os.environ["JWT_ISSUER"]
jwks_uri = os.environ["JWT_JWKS_URI"]
jwks_client = PyJWKClient(jwks_uri)
def authenticate(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
):
    token = credentials.credentials
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=issuer,
            audience="cases-mcp-api",
            options={
                "require": ["exp", "iat", "nbf", "sub", "aud", "iss"]
            },
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid access token",
        ) from exc
    except Exception as exc:
        # In production, handle JWKS/network failures separately
        # and return a controlled service error.
        raise HTTPException(
            status_code=503,
            detail="Identity verification temporarily unavailable",
        ) from exc
    return {
        "user_id": claims["sub"],
        "roles": claims.get("roles", []),
        "scopes": claims.get("scope", "").split(),
        "tenant_id": claims.get("tenant_id"),
        # Keep raw tokens request-scoped; do not put them in graph state.
        "_access_token": token,
    }
class AskRequest(BaseModel):
    question: str
@app.post("/api/ask")
async def ask(
    request: AskRequest,
    identity: dict = Depends(authenticate),
):
    access_token = identity.pop("_access_token")
    # This function is defined in your LangGraph module.
    # Its implementation appears in the next section.
    result = await run_agent(
        question=request.question,
        identity=identity,
        access_token=access_token,
    )
    return {"answer": result}

Install the additional dependencies:

pip install fastapi uvicorn pyjwt cryptography

This example assumes an RS256 token and an issuer publishing a compatible JWKS endpoint. Your actual issuer may use a different signing algorithm or claim layout, which must be configured deliberately.

Notice the separation:

* FastAPI verifies the token and creates trusted identity context.
* LangGraph receives user identity and permissions as workflow state.
* The raw token remains a request-scoped credential, separate from the graph state.
* The MCP server validates the credential again.

For production, if the frontend’s access token is intended only for FastAPI, don’t forward it to an MCP server with a different audience. Use OAuth token exchange to obtain a token intended for the MCP resource, or obtain an appropriately scoped token from your identity provider.

9. Step 6 — Pass the token through the LangGraph MCP client

Your Supervisor agent may decide to use a case-management worker. That worker invokes MCP tools through the MCP client.

The critical point is that the token belongs to the incoming user’s request. Do not store a user’s raw JWT in a global MCP client shared by all users, or concurrent requests could accidentally use the wrong user’s credentials.

Install the client adapter:

pip install langchain-mcp-adapters langgraph

Create the MCP client for the current request, passing the bearer token through the HTTP transport.

# agent.py
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
MCP_URL = "http://mcp-server:8001/mcp"
async def run_agent(
    question: str,
    identity: dict,
    access_token: str,
):
    # Per-request headers: never use another user's token.
    client = MultiServerMCPClient(
        {
            "cases": {
                "transport": "streamable_http",
                "url": MCP_URL,
                "headers": {
                    "Authorization": f"Bearer {access_token}",
                },
            }
        }
    )
    tools = await client.get_tools()
    # Replace this with your existing Supervisor/Worker graph.
    # This minimal example demonstrates the secured MCP tool path.
    agent = create_react_agent(
        model=your_configured_chat_model,
        tools=tools,
    )
    result = await agent.ainvoke(
        {
            "messages": [
                {"role": "user", "content": question}
            ]
        },
        config={
            "configurable": {
                "thread_id": "request-specific-thread-id"
            }
        },
    )
    return result["messages"][-1].content

your_configured_chat_model represents the model already configured in your application; it is not a literal variable supplied by LangGraph. Likewise, replace the example thread ID with your actual per-conversation identifier.

The MCP adapter’s HTTP headers carry the token. The token is not a tool argument, so the LLM cannot change the bearer token by generating different tool-call parameters.

For a multi-agent graph, you can expose these secured tools to the relevant worker or workers. The MCP server remains the enforcement point regardless of which agent initiated the call.

10. Step 7 — How to issue a JWT in your custom authentication setup

If you’re using your own FastAPI authentication service rather than an enterprise identity provider, the issuer is responsible for authenticating the user and issuing a signed access token.

For a local demonstration, a minimal issuer could look like this:

# token_issuer.py
import os
import time
import uuid
import jwt
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
app = FastAPI()
PRIVATE_KEY = open(
    os.environ["JWT_PRIVATE_KEY_PATH"]
).read()
ISSUER = os.environ["JWT_ISSUER"]
AUDIENCE = "cases-mcp-api"
class TokenRequest(BaseModel):
    username: str
# DEMO ONLY: replace with actual authenticated identity
# and a server-side user/role lookup.
DEMO_USERS = {
    "analyst1": {
        "sub": "user-101",
        "roles": ["analyst"],
        "scopes": ["cases:read"],
    },
    "manager1": {
        "sub": "user-202",
        "roles": ["manager"],
        "scopes": ["cases:read", "cases:write"],
    },
}
@app.post("/demo-token")
def issue_demo_token(request: TokenRequest):
    user = DEMO_USERS.get(request.username)
    if user is None:
        raise HTTPException(status_code=401, detail="Unknown user")
    now = int(time.time())
    claims = {
        "sub": user["sub"],
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": now,
        "nbf": now,
        "exp": now + 900,  # 15 minutes
        "jti": str(uuid.uuid4()),
        "roles": user["roles"],
        "scope": " ".join(user["scopes"]),
        "tenant_id": "tenant-001",
    }
    return {
        "access_token": jwt.encode(
            claims,
            PRIVATE_KEY,
            algorithm="RS256",
            headers={"kid": os.environ["JWT_KEY_ID"]},
        ),
        "token_type": "Bearer",
        "expires_in": 900,
    }

This endpoint is deliberately a demonstration only. It accepts a username without proving the caller controls that account. Never expose it as a real login endpoint. In production, authenticate the user first, look up roles and scopes from a trusted source, and issue a short-lived token only after successful authentication. The corresponding public key must be published through JWKS with the matching key ID.

The private key should be stored in a secrets manager or protected signing service. Do not commit it to Git or include it in a Docker image.

11. Step 8 — Test the complete authorization flow

Start the MCP server with the configured issuer and JWKS URL, then start your FastAPI application.

For each test, obtain a properly signed access token from your issuer or identity provider.

Test A: Call without a token

curl -i http://localhost:8001/mcp

Expected: authentication failure. The exact response depends on the MCP transport and protocol request.

Test B: Call with a valid token

Send an actual MCP tools/call request through an MCP client configured with the token. A user with analyst and cases:read should be able to call get_case.

Test C: Try an unauthorized write

With an analyst token, attempt to call update_case.

Expected: denied because the token lacks cases:write and the required manager/admin role.

Test D: Try an unauthorized delete

With a manager token, attempt to call delete_case.

Expected: denied because the manager lacks the admin role and cases:delete scope.

Test E: Tamper with the token

Modify a signed claim or use an expired token.

Expected: authentication failure before the protected tool executes.

Also test a token with the wrong issuer, wrong audience, missing required claims, a revoked user, and a user attempting to access another tenant’s records. These cases catch issues that simple happy-path tests miss.

12. Step 9 — Deploy the application securely on AWS

For the AWS architecture we’ve discussed, the production deployment can be organized like this:

API Gateway / load balancer

HTTPS entry point; optional JWT validation at the gateway

FastAPI + LangGraph service

Runs the Supervisor, workers and MCP client

Private FastMCP service

Verifies JWTs and enforces role/scope checks; accessible only through approved network paths

Enterprise APIs / database

Enforce ownership, tenant isolation and business rules

Configure the following controls:

* Networking: Keep the MCP service private; allow ingress only from authorized application workloads.
* Secrets: Store private signing keys, client credentials and database secrets in a managed secrets service.
* TLS: Use HTTPS for external and inter-service communication where required by your deployment topology.
* IAM: Give ECS task roles or EKS workload identities only the AWS permissions their services need.
* Logging: Record the authenticated subject, tool name, authorization outcome and correlation ID. Never log raw bearer tokens.
* Revocation: Keep token lifetimes short, and use a revocation or user-status strategy where immediate access removal is required.
* Audit: For sensitive writes and deletes, record the user, resource, action and outcome.

AWS IAM roles for ECS/EKS are different from application roles such as manager and admin. An ECS task role grants infrastructure permissions; it does not automatically grant a human user permission to delete a case.

13. Step 10 — Important considerations for your multi-agent application

Scenario	Correct behavior
Supervisor calls a read-only worker	MCP checks the current caller’s read permissions
Worker attempts an unauthorized write	MCP denies the tool call
Agent generates a different user_id argument	MCP derives identity from verified claims, not that argument
User switches to another tenant	MCP and the data layer verify tenant membership and resource access
JWT expires during a long workflow	Subsequent calls must obtain a valid token; never silently bypass validation
MCP server scales horizontally	All replicas use the same trusted issuer configuration and equivalent authorization policy
One worker calls another worker	Internal identity and delegated user permissions must remain explicit and verifiable

One subtle but important distinction: if the Supervisor and workers all run inside your trusted LangGraph process, the workers generally do not need separate user JWTs just to communicate with one another. The credential is needed when crossing the MCP security boundary. If workers are independently deployed services, authenticate those service-to-service calls as well.

For sensitive operations, the safest design is to propagate a properly scoped user-delegated token to the MCP server, or use a trusted token-exchange mechanism that preserves the user’s identity and permissions. Do not trust identity fields supplied by the LLM.

14. Final implementation checklist

Production security checklist

0 of 12

Configure a trusted identity provider or secure token issuer

Register the MCP API audience and permitted scopes

Publish signing public keys through JWKS

Configure FastMCP JWTVerifier with issuer, audience and JWKS URI

Implement role checks and scope checks on each protected tool

Add tenant and record-level authorization to data access

Validate the incoming token in FastAPI

Pass the correct bearer token through the LangGraph MCP client

Keep raw tokens out of graph state, prompts and logs

Test missing, expired, tampered and insufficient-permission tokens

Deploy MCP privately with least-privilege network and IAM policies

Add audit logging, key rotation and token-revocation handling

For reference, the official FastMCP authentication documentation⁠￼ covers token validation, while its authorization guide⁠￼ documents require_scopes, require_roles and custom authorization checks.

My recommendation for your architecture: let FastAPI establish the user identity, let LangGraph orchestrate the agents, and let FastMCP independently enforce tool-level permissions. The LLM chooses tools; it never decides whether the caller is authorized to use them.


'''