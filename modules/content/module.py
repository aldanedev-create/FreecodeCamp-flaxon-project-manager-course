"""Public read-only content endpoints; never expose the authenticated CMS API to readers."""

from pathlib import Path
from flaxon.modules import FlaxonModule
from flaxon.exceptions import NotFound

content = FlaxonModule(
    "content",
    ui_dir=Path(__file__).parent / "ui",
    ui_routes={"Help.js": "/help", "Article/[slug].js": "/help/:slug"},
)


async def published_articles(request):
    cms = request.app.cms
    await cms._load_database()
    articles = cms.content_types["help_article"]
    return [
        item for item in articles.items.values() if item.get("status") == "published"
    ]


@content.get("/articles")
async def list_articles(request):
    articles = await published_articles(request)
    return {
        "data": [
            {key: item.get(key) for key in ("id", "title", "slug", "summary")}
            for item in articles
        ]
    }


@content.get("/articles/<slug>")
async def get_article(request, slug):
    for article in await published_articles(request):
        if article["slug"] == slug:
            return {
                "data": {
                    key: article.get(key)
                    for key in ("id", "title", "slug", "summary", "body")
                }
            }
    raise NotFound("Article not found.")
