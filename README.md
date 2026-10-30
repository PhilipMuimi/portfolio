# Philip Muimi — Portfolio

A data analyst portfolio focused on data quality, healthcare datasets, research, and reporting, with software development presented as a complementary capability. It also covers professional experience, education, and personal interests. Built with semantic HTML, CSS, and vanilla JavaScript. No framework, package installation, build process, external fonts, or CDN is needed to run the site.

## Preview

From this directory:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765. To deploy, serve this directory as a static website; `index.html` is the entry point. No deployment has been performed by this update.

## Features

- Responsive layout and mobile navigation with Escape and focus handling.
- Light/dark theme with system preference support and an optional saved choice.
- Active section navigation.
- Skill category filters, text search, and accessible result announcements.
- Expandable earlier education.
- Downloadable CV and direct email, phone, WhatsApp, and profile links.
- Copy-email control where browser clipboard access is supported.
- Validated email composer that opens the visitor’s email app for review and sending.
- Local WebP images, lazy loading, reduced-motion support, keyboard focus styles, and print styles.
- Core content, links, CV, and education remain available without JavaScript.

## Content and files

| File                            | Purpose                                                                       |
| ------------------------------- | ----------------------------------------------------------------------------- |
| `index.html`                    | Content, metadata, icon symbols, links, and accessible page structure         |
| `css/style.css`                 | Design tokens, responsive layouts, themes, and print styles                   |
| `js/theme.js`                   | Applies a stored or system theme before rendering                             |
| `js/nav.js`                     | Navigation, theme control, skills filtering, clipboard, and email composition |
| `documents/Philip-Muimi-CV.pdf` | Downloadable résumé                                                           |
| `images/optimized/`             | Smaller WebP versions used by the page                                        |
| `images/`                       | Retained source photos and SVG favicon                                        |
| `qa/`                           | Generated browser screenshots and report (ignored by Git)                     |
| `scripts/browser_check.py`      | Browser regression checks via Chrome DevTools Protocol                        |

Professional experience and data skills are drawn from the supplied CV. Education dates, results, development skills, and interests also use the original portfolio. The healthcare card describes a contribution, not an independently built application. No metrics or certifications have been invented.

The contact form does not send messages itself. The visitor needs a configured email app and must send the draft there. No form data is stored or transmitted to a website server. If the app does not open, the email address remains visible and the draft stays in the form. Clipboard/theme storage failures are handled without breaking the page.

To update the CV, replace `documents/Philip-Muimi-CV.pdf`. Update employment dates, content, and contact links in `index.html` as needed. Theme colors live at the top of `css/style.css`.

## Verification

JavaScript syntax:

```sh
node --check js/theme.js
node --check js/nav.js
```

Browser checks use Python’s optional `websockets` package and a separate headless Chrome instance. With the preview running, launch Chrome with an isolated temporary profile:

```sh
google-chrome --headless --user-data-dir=/tmp/portfolio-qa-browser --remote-debugging-port=9224 about:blank
python3 scripts/browser_check.py
```

Set `PORTFOLIO_URL` or `BROWSER_DEBUG_URL` to use different local ports. The check opens the portfolio in that isolated browser, exercises the interactions, writes screenshots and `qa/browser-checks.txt`, and checks layouts from 320px to 1440px. It does not send emails or contact external profiles. Close the isolated browser afterward.

Verified in Chromium: image loading, responsive overflow, mobile navigation, theme persistence, filtering/search/empty state, education disclosure, native form validation, encoded email composition, JavaScript-free content/navigation, and absence of script or HTTP errors. Email delivery and external account ownership are outside those checks.
