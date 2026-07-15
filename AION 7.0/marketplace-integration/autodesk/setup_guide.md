# Autodesk App Store — Setup Guide

Real submission process, sourced from Autodesk's own Publisher docs
([Product Guidelines](https://apps.autodesk.com/Publisher/ProductGuidelines),
[Getting Started Guide](https://damassets.autodesk.net/content/dam/autodesk/www/pdfs/app-store-getting-started-guide.pdf),
[Publisher FAQ](https://damassets.autodesk.net/content/dam/autodesk/www/adn/pdf/frequently-asked-questions.pdf)).

## Important distinction before starting

Most listings on the Autodesk App Store are **plug-ins/add-ins that run
inside** a specific Autodesk product (Revit, AutoCAD, Civil 3D, etc.), built
against that product's SDK/API. **Engineering Copilot is not that** — it's a
standalone web app (FastAPI + browser UI). Autodesk's accepted product types
explicitly include **"standalone applications"** alongside plug-ins, content,
training material and e-books, so we list under that category rather than
building a native Revit/AutoCAD add-in (that would be a separate, much larger
project — a real Revit/AutoCAD plugin using their .NET/C++ SDKs).

## 1. Create a Publisher Account

1. Go to https://apps.autodesk.com and create a Publisher account
2. Fill in company profile: **Global Match Engenharia de Produção**, CREA-SP 5071200171
3. If selling (not just free/trial), a **PayPal account** is required for payouts —
   free/trial-only listings don't need one

## 2. Product Type

- **Type:** Standalone Application (not a Revit/AutoCAD/Civil 3D plug-in)
- **Name:** Engineering Copilot
- **Tagline:** AI Copilot for AEC document intelligence, photo analysis and compliance reporting
- **Description:** Upload project documents (specs, drawings) and site photos —
  the AI extracts equipment, tags, and applicable standards; a deterministic
  engine scores compliance (NR, ABNT, CREA, ANVISA) and generates 9 audit-ready
  documents (Memorial Descritivo, Data Book, As Built, etc.) in DOCX.
- **Category:** AEC / Productivity / Compliance
- **Compatible products:** listed as complementary to Revit, AutoCAD, Navisworks
  workflows (since it consumes exported drawings/specs from those tools), not
  as a plug-in running inside them
- **Pricing:** $249/mo (matches the Engineering & AEC Copilot entry price on
  the main site) — free 15-day trial, no card required

## 3. Required Submission Assets

- Product icon (matches `assets/logo.webp`)
- 3-5 screenshots of the actual product in use (use the `/engineering-copilot`
  page — real screenshots, not mockups)
- Short demo video is optional but improves approval odds
- Support URL: `https://global-engenharia.com/ecosystem` (or a dedicated support page)
- Support email: contato@global-engenharia.com

## 4. Review Process

- After submission, Autodesk assigns a reviewer within **24-48 hours**
- If no response after 48h, email **AppSubmissions@autodesk.com**
- After any product change post-approval, it must be **resubmitted** for re-review

## Status

Not yet submitted — needs the Publisher account created and the screenshot
assets captured from the live `/engineering-copilot` page before submission.
