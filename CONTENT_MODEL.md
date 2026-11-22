# Content model reference

Content files are UTF-8. Stable `id` values are used for relationships; slugs are used only in URLs and can be language-specific. Translations are optional.

## Project metadata example

```json
{
  "id": "sample-project",
  "slug": {"en": "sample-project", "pt-br": "projeto-exemplo"},
  "title": {"en": "Sample Project", "pt-br": "Projeto Exemplo"},
  "short_description": {"en": "Short summary.", "pt-br": "Resumo."},
  "status": "in_progress",
  "featured": false,
  "technologies": [],
  "tags": [],
  "start_date": null,
  "completion_date": null,
  "cover_image": null,
  "cover_alt": {"en": "Describe the image.", "pt-br": "Descreva a imagem."},
  "cover_caption": {"en": "Optional caption.", "pt-br": "Legenda opcional."},
  "media": [],
  "links": {"github": null, "demo": null},
  "related_post_ids": [],
  "order": 100,
  "content_files": {"en": "en.md", "pt-br": "pt-br.md"}
}
```

Allowed project statuses: `in_progress`, `completed`, `archived`. Dates use `YYYY-MM-DD` or `null`. Markdown translations can be omitted when unavailable; metadata maps should contain at least one localized value.

## Blog post metadata example

```json
{
  "id": "sample-post",
  "slug": {"en": "sample-post", "pt-br": "artigo-exemplo"},
  "title": {"en": "Sample Post", "pt-br": "Artigo Exemplo"},
  "description": {"en": "Short summary.", "pt-br": "Resumo."},
  "status": "draft",
  "language": "en",
  "published_at": null,
  "updated_at": null,
  "tags": [],
  "cover_image": null,
  "related_project_id": null,
  "featured": false,
  "content_files": {"en": "en.md"}
}
```

Allowed post statuses: `draft`, `published`. Published posts require a publication date. `language` identifies the primary language of the post; `content_files` lists available translations. A post can be related to one project initially.

## Profile metadata

Each language file in `content/profile/` stores the editable profile fields: `name`, `full_name`, `presentation`, `education`, `skills`, `professional_objectives`, `avatar`, and `links`. Keep unavailable personal information empty until supplied.

## Local media

Use repository-relative paths, such as `app/static/images/projects/example/cover.webp`. External media URLs are not supported by validation. Markdown image paths should remain local and be checked when the full media validation is implemented.
