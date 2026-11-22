# Portfolio + Blog Content Structure

The project is being incrementally refactored from a single-page Flask portfolio into a multipage portfolio and blog. During Stage 1, the existing homepage remains in place while content storage and validation are introduced.

## Content directories

- `content/profile/`: editable profile data, localized by language.
- `content/site/`: global settings and localized site labels.
- `content/projects/<project-id>/`: project metadata and localized Markdown descriptions.
- `content/posts/<post-id>/`: blog metadata and localized Markdown articles.
- `app/static/images/`: local image and media assets.

## Content editing

Edit JSON metadata and Markdown files directly. The content loader reads JSON metadata and the Markdown body for the requested language. Missing translations are allowed; localized metadata may provide one or more supported languages. Stable IDs are used for relationships, rather than display names or slugs.

## Validation

Run content validation independently:

```bash
python scripts/validate_content.py
```

The static build also validates content before generating the `docs/` directory. Invalid content prevents the build from completing.

## Initial content model

### Profile

Profile JSON files include `name`, `full_name`, `presentation`, `education`, `skills`, `professional_objectives`, `avatar`, and `links`. Fields that have not yet been provided are kept empty rather than invented.

### Projects

Each `project.json` contains an ID, language-specific slugs/titles/descriptions, status, featured flag, technologies, tags, optional dates, optional local media, links, relationships, display order, and localized Markdown file references.

Allowed statuses: `in_progress`, `completed`, `archived`.

### Blog posts

The post model will use an ID, localized slugs/titles/descriptions, publication status, language, published/updated dates, tags, optional local cover, optional project relationship, featured flag, and Markdown body file references. Allowed statuses are `draft` and `published`. Draft filtering is implemented by the content loader; the full post model will be validated as posts are added.

## Security and media

Markdown rendering disables raw HTML. Media paths must be local repository files; external image URLs are not accepted by content validation. Markdown file paths are constrained to the corresponding content folder.
