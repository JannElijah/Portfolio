# SiteCare — Website Maintenance & GitHub Release Health Console

Automated static/production website maintenance auditor, broken-asset & SEO/OG verifier, XML sitemap generator, and GitHub Workflows health monitor.

## Features
- **HTML & Asset Scanner**: Validates `<title>`, meta description, Open Graph tags, favicon, image `alt` attributes, and local asset links (`dist/` + `public/`).
- **XML Sitemap Generator**: Outputs standards-compliant `<urlset>` sitemaps.
- **GitHub CI Inspector**: Inspects `.github/workflows/*.yml`, branch state, and commit history alongside a live maintenance console.

## Run Locally
```bash
cd projects/sitecare
python -m sitecare.server
python -m pytest -v
```
