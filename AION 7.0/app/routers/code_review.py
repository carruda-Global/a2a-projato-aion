from fastapi import APIRouter, HTTPException, Request
from src.agents._copilot_common import tem_licenca_premium
from src.agents.mai_code_reviewer import MAICodeReviewer

router = APIRouter(prefix="/api/code-review", tags=["code_review"])

CHECKOUT_URL = "https://buy.stripe.com/8x2fZj3Ik3W34Xqg0Eg7e0g"


@router.post("/review")
async def review_pr(request: Request):
    data = await request.json()
    customer_email = data.get("customer_email", "")
    if not tem_licenca_premium(customer_email):
        raise HTTPException(
            status_code=402,
            detail={
                "message": "Active subscription required for MAI Code Reviewer.",
                "checkout_url": CHECKOUT_URL,
            },
        )
    tenant_id = request.headers.get("X-Tenant-ID", "default")
    reviewer = MAICodeReviewer()
    result = await reviewer.execute({
        "action": "review",
        "repo": data.get("repo", ""),
        "pr_number": data.get("pr_number", 0),
        "diff": data.get("diff", ""),
        "tenant_id": tenant_id
    })
    return result


@router.post("/github/webhook")
async def github_webhook(request: Request):
    data = await request.json()
    tenant_id = request.headers.get("X-Tenant-ID", "default")

    if data.get("action") not in ["opened", "synchronize"]:
        return {"status": "ignored"}

    pr = data.get("pull_request", {})
    repo = data.get("repository", {}).get("full_name", "")
    pr_number = pr.get("number")

    import httpx
    async with httpx.AsyncClient() as client:
        diff_resp = await client.get(pr.get("diff_url", ""))
    diff = diff_resp.text

    reviewer = MAICodeReviewer()
    result = await reviewer.execute({
        "action": "review", "repo": repo,
        "pr_number": pr_number, "diff": diff,
        "tenant_id": tenant_id
    })

    return {"status": "reviewed", "risk_score": result["risk_score"]}
