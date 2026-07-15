import logging
import httpx
import re
from datetime import datetime
from .config import LinkedInConfig
from .oauth import LinkedInOAuth

logger = logging.getLogger(__name__)


class LinkedInTools:
    def __init__(self, config: LinkedInConfig, oauth: LinkedInOAuth):
        self.config = config
        self.oauth = oauth

    async def _get(self, path: str, params: dict | None = None, restli: bool = False) -> dict:
        token = await self.oauth.ensure_token()
        headers = self.oauth.restli_headers if restli else self.oauth.headers
        url = f"{self.config.api_restli if restli else self.config.api_base_url}{path}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code == 401:
                await self.oauth.refresh()
                token = await self.oauth.ensure_token()
                headers["Authorization"] = f"Bearer {token}"
                resp = await client.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code != 200:
                logger.error(f"LinkedIn API error {resp.status_code}: {resp.text[:500]}")
                return {"error": f"API error {resp.status_code}", "detail": resp.text[:500]}
            return resp.json()

    async def _post(self, path: str, data: dict, restli: bool = False) -> dict:
        token = await self.oauth.ensure_token()
        headers = self.oauth.restli_headers if restli else self.oauth.headers
        url = f"{self.config.api_restli if restli else self.config.api_base_url}{path}"
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=data, timeout=15)
            if resp.status_code == 401:
                await self.oauth.refresh()
                token = await self.oauth.ensure_token()
                headers["Authorization"] = f"Bearer {token}"
                resp = await client.post(url, headers=headers, json=data, timeout=15)
            if resp.status_code not in (200, 201):
                logger.error(f"LinkedIn API error {resp.status_code}: {resp.text[:500]}")
                return {"error": f"API error {resp.status_code}", "detail": resp.text[:500]}
            result = resp.json() if resp.text else {}
            if restli:
                restli_id = resp.headers.get("x-restli-id") or resp.headers.get("x-linkedin-id")
                if not restli_id:
                    location = resp.headers.get("location", "")
                    restli_id = location.rsplit("/", 1)[-1] if location else ""
                if restli_id:
                    result["id"] = restli_id
                else:
                    logger.warning(
                        "LinkedIn restli POST %s returned no id in x-restli-id/x-linkedin-id/location -- "
                        "raw response headers: %s", path, dict(resp.headers),
                    )
            return result if result else {"status": "created"}

    async def get_profile(self, person_id: str = "me") -> dict:
        path = f"/userinfo" if person_id == "me" else f"/userinfo?q=id&id={person_id}"
        result = await self._get(path)
        return {
            "sub": result.get("sub", ""),
            "name": result.get("name", ""),
            "given_name": result.get("given_name", ""),
            "family_name": result.get("family_name", ""),
            "email": result.get("email", ""),
            "picture": result.get("picture", ""),
            "locale": result.get("locale", ""),
        }

    async def search_people(
        self,
        keywords: str | None = None,
        company: str | None = None,
        title: str | None = None,
        location: str | None = None,
        industry: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        # LinkedIn /v2/search was deprecated in 2024. The blended search REST endpoint
        # requires Marketing Developer Platform (MDP) access. We try it first and fall
        # back to an empty list so callers degrade gracefully.
        await self.oauth.ensure_token()
        query_parts = []
        if keywords:
            query_parts.append(keywords)
        if company:
            query_parts.append(company)
        if title:
            query_parts.append(title)
        if location:
            query_parts.append(location)
        if industry:
            query_parts.append(industry)
        query = " ".join(query_parts)

        try:
            result = await self._get(
                "/rest/search/blended",
                params={
                    "q": "blended",
                    "query": query,
                    "origin": "FACETED_SEARCH",
                    "count": min(limit, 50),
                },
                restli=True,
            )
            elements = result.get("elements", [])
            people = [
                e.get("hitInfo", {}).get("com.linkedin.voyager.search.SearchProfile", e)
                for e in elements
                if "error" not in e
            ]
            return people[:limit]
        except Exception as e:
            logger.warning(f"search_people via blended search failed: {e}. "
                           "Sales Navigator API required for full people search.")
            return []

    async def search_companies(
        self,
        keywords: str,
        limit: int = 10,
    ) -> list[dict]:
        # Try the organizational entity search endpoint (MDP), then vanity name lookup.
        await self.oauth.ensure_token()

        try:
            result = await self._get(
                "/rest/organizationalEntitySearch",
                params={
                    "q": "search",
                    "query": f"(keywords:{keywords})",
                    "count": min(limit, 50),
                },
                restli=True,
            )
            elements = result.get("elements", [])
            if elements:
                return elements[:limit]
        except Exception as e:
            logger.debug(f"organizationalEntitySearch failed: {e}")

        # Fallback: vanity name exact-match lookup
        try:
            result = await self._get(
                "/v2/organizations",
                params={"q": "vanityName", "vanityName": re.sub(r"\s+", "", keywords.lower())},
            )
            org = result.get("elements", [result] if "id" in result else [])
            return org[:limit]
        except Exception as e:
            logger.warning(f"search_companies fallback also failed: {e}. "
                           "Marketing Developer Platform access may be required.")
            return []

    async def create_post(
        self,
        text: str,
        commentary: str = "",
        images_urls: list[str] | None = None,
        link_url: str | None = None,
        link_title: str | None = None,
        link_description: str | None = None,
        visibility: str = "PUBLIC",
    ) -> dict:
        profile = await self.get_profile()
        author_urn = f"urn:li:person:{profile.get('sub', '')}"
        post_data = {
            "author": author_urn,
            "commentary": commentary or text[:3000],
            "visibility": visibility,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        if link_url:
            post_data["content"] = {
                "article": {
                    "source": link_url,
                    "title": link_title or "",
                    "description": link_description or "",
                }
            }
        if text:
            text_body = text[:3000]
            post_data["commentary"] = text_body
        result = await self._post("/posts", post_data, restli=True)
        if "error" in result:
            return result
        post_id = result.get("id", "")
        logger.info(f"Post created: {post_id}")
        return {
            "status": "published",
            "post_id": post_id,
            "url": f"https://www.linkedin.com/feed/update/{post_id}",
            "created_at": datetime.now().isoformat(),
        }

    async def get_post(self, post_id: str) -> dict:
        result = await self._get(f"/posts/{post_id}", restli=True)
        return result

    async def get_post_comments(self, post_id: str, limit: int = 50) -> list[dict]:
        result = await self._get(
            f"/socialActions/{post_id}/comments",
            params={"count": min(limit, 100), "start": 0, "q": "comments"},
        )
        return result.get("elements", [])

    async def create_comment(self, post_id: str, text: str) -> dict:
        if not post_id:
            logger.warning("create_comment called with empty post_id -- skipping (link-back comment lost)")
            return {"error": "empty post_id"}
        profile = await self.get_profile()
        comment_data = {
            "actor": f"urn:li:person:{profile.get('sub', '')}",
            "object": post_id,
            "message": {"text": text[:2000]},
        }
        result = await self._post(f"/socialActions/{post_id}/comments", comment_data)
        return result

    async def get_company_profile(self, company_id: str) -> dict:
        result = await self._get(f"/companies/{company_id}")
        return result

    async def get_post_analytics(self, post_id: str) -> dict:
        result = await self._get(
            f"/rest/postAnalytics?q=statisticalData&ids=List({post_id})&fields=List(commentCount,likeCount,shareCount,impressionCount,clickCount)",
            restli=True,
        )
        return result

    async def upload_document(self, pdf_bytes: bytes, filename: str) -> dict:
        """Registers and uploads a PDF as a LinkedIn Document asset (real
        Documents API), returning the asset URN used for a carousel post."""
        profile = await self.get_profile()
        author_urn = f"urn:li:person:{profile.get('sub', '')}"
        register = await self._post(
            "/documents?action=initializeUpload",
            {"initializeUploadRequest": {"owner": author_urn}},
            restli=True,
        )
        if "error" in register:
            return register
        value = register.get("value", {})
        upload_url = value.get("uploadUrl")
        asset = value.get("document")
        if not upload_url or not asset:
            return {"error": "no upload_url/document returned", "detail": register}

        token = await self.oauth.ensure_token()
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                upload_url,
                content=pdf_bytes,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
            if resp.status_code not in (200, 201):
                logger.error(f"Document upload failed {resp.status_code}: {resp.text[:300]}")
                return {"error": f"upload failed {resp.status_code}"}
        return {"asset": asset, "filename": filename}

    async def create_carousel_post(self, text: str, document_asset: str, title: str) -> dict:
        """Publishes a native LinkedIn carousel (Document post) referencing an
        asset already uploaded via upload_document()."""
        profile = await self.get_profile()
        author_urn = f"urn:li:person:{profile.get('sub', '')}"
        post_data = {
            "author": author_urn,
            "commentary": text[:3000],
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "content": {"media": {"title": title, "id": document_asset}},
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        result = await self._post("/posts", post_data, restli=True)
        if "error" in result:
            return result
        post_id = result.get("id", "")
        return {
            "status": "published",
            "post_id": post_id,
            "url": f"https://www.linkedin.com/feed/update/{post_id}",
            "created_at": datetime.now().isoformat(),
        }

    async def get_organic_analytics(self, date_range: tuple[str, str] | None = None) -> dict:
        if date_range is None:
            date_range = ("1672531200000", "1704067199000")
        date_range_param = f"(start:{date_range[0]},end:{date_range[1]})"
        result = await self._get(
            f"/rest/organicPostAnalytics?q=analytics&dateRange={date_range_param}&fields=List(commentCount,likeCount,shareCount,impressionCount)",
            restli=True,
        )
        return result

    def get_all_tools_schema(self) -> list[dict]:
        return [
            {
                "name": "linkedin_get_profile",
                "description": "Get the authenticated user's LinkedIn profile information",
                "input_schema": {"type": "object", "properties": {"person_id": {"type": "string", "description": "Person ID (default: 'me')"}}},
            },
            {
                "name": "linkedin_search_people",
                "description": "Search for people on LinkedIn by keywords, company, title, location",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "keywords": {"type": "string"},
                        "company": {"type": "string"},
                        "title": {"type": "string"},
                        "location": {"type": "string"},
                        "industry": {"type": "string"},
                        "limit": {"type": "integer"},
                    },
                },
            },
            {
                "name": "linkedin_search_companies",
                "description": "Search for companies on LinkedIn",
                "input_schema": {"type": "object", "properties": {"keywords": {"type": "string"}, "limit": {"type": "integer"}}},
            },
            {
                "name": "linkedin_create_post",
                "description": "Create a post on LinkedIn with text, optional link and images",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Post body text"},
                        "commentary": {"type": "string"},
                        "link_url": {"type": "string"},
                        "link_title": {"type": "string"},
                        "visibility": {"type": "string", "enum": ["PUBLIC", "CONNECTIONS"]},
                    },
                    "required": ["text"],
                },
            },
            {
                "name": "linkedin_get_post",
                "description": "Get details of a LinkedIn post by ID",
                "input_schema": {"type": "object", "properties": {"post_id": {"type": "string"}}, "required": ["post_id"]},
            },
            {
                "name": "linkedin_get_post_comments",
                "description": "Get comments of a LinkedIn post",
                "input_schema": {"type": "object", "properties": {"post_id": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["post_id"]},
            },
            {
                "name": "linkedin_create_comment",
                "description": "Create a comment on a LinkedIn post",
                "input_schema": {"type": "object", "properties": {"post_id": {"type": "string"}, "text": {"type": "string"}}, "required": ["post_id", "text"]},
            },
            {
                "name": "linkedin_get_post_analytics",
                "description": "Get analytics (likes, comments, shares, impressions) for a post",
                "input_schema": {"type": "object", "properties": {"post_id": {"type": "string"}}, "required": ["post_id"]},
            },
            {
                "name": "linkedin_get_company_profile",
                "description": "Get company profile information by company ID",
                "input_schema": {"type": "object", "properties": {"company_id": {"type": "string"}}, "required": ["company_id"]},
            },
        ]
