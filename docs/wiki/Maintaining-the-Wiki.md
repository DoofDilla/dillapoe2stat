# Maintaining the Wiki

This repository keeps the wiki content under version control in `docs/wiki/`, then mirrors the pages to the GitHub Wiki using a dedicated workflow. Follow the guidelines below to keep documentation healthy.

## Folder layout
```
docs/
  wiki/
    Home.md
    Core-Loop-Overview.md
    Module-Reference.md
    External-API-Usage.md
    Maintaining-the-Wiki.md
    _Sidebar.md
    ...
```
- Create new wiki pages here using GitHub-flavoured Markdown.
- Link between pages using the `[[Page Name]]` syntax so the same files render correctly inside the GitHub Wiki.
- Assets (images, diagrams) should live under `docs/wiki/assets/` or a similar subdirectory.

## Editing workflow
1. Edit or add Markdown files under `docs/wiki/`.
2. Commit the changes as part of your pull request.
3. When the pull request merges into `main`, the **Sync Wiki** GitHub Action will copy the folder into the repository’s wiki (`<repo>.wiki.git`).
4. The wiki remains editable directly on GitHub, but changes made there will be overwritten the next time the workflow runs. Always edit in-repo first.

## Sync automation
The workflow defined in [`.github/workflows/wiki-sync.yml`](../.github/workflows/wiki-sync.yml) performs the following steps on every push to `main` that touches `docs/wiki/`:
1. Check out the main repository.
2. Check out the corresponding `wiki` repository into a temporary directory.
3. Replace the wiki contents with the files from `docs/wiki/`.
4. Commit and push using the GitHub Actions bot identity if differences are detected.

No additional secrets are required because GitHub Actions automatically grants push access to the wiki for the default token.

## Local preview tips
- Open the Markdown files directly in VS Code or GitHub Desktop to preview formatting.
- To test navigation links locally, clone the wiki repository (`git clone <repo>.wiki.git`) and copy the files manually.
- Consider adding screenshots or diagrams by exporting them into `docs/wiki/assets/` and referencing them with relative paths.

Keeping the wiki alongside the codebase ensures documentation evolves alongside new features—remember to update the relevant pages whenever you touch the modules they describe.
