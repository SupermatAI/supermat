# Contributing Guide

We welcome all types of contributions to Supermat, including bug reports, feature requests, code improvements, documentation updates, and tests. Please follow the guidelines below to help us maintain a high-quality, collaborative project.

---

## Table of Contents

- [Contributing Guide](#contributing-guide)
  - [Table of Contents](#table-of-contents)
  - [1. Development Setup](#1-development-setup)
  - [2. Branch \& Commit Naming Conventions](#2-branch--commit-naming-conventions)
    - [Branch Naming](#branch-naming)
    - [Commit Messages](#commit-messages)
  - [3. Issue Reporting Guidelines](#3-issue-reporting-guidelines)
  - [4. Testing](#4-testing)
  - [5. Documentation](#5-documentation)
  - [6. Code Formatting](#6-code-formatting)
  - [7. Code of Conduct](#7-code-of-conduct)
  - [8. Final Steps](#8-final-steps)

---

## 1. Development Setup

To set up your local development environment:

1. **Clone the Repository**

   ```bash
   git clone https://github.com/SupermatAI/supermat.git
   cd supermat
   ```

2. **Install Dependencies with Poetry**  
   Ensure you have [Python Poetry](https://python-poetry.org/) installed. Then run:

   ```bash
   poetry install --with=dev,docs,frontend --all-extras
   ```

3. **Run the Application**  
   To see Supermat in action via the Gradio interface, run:

   ```bash
   python -m supermat.gradio
   ```

4. **Virtual Environment (Optional)**  
   Poetry automatically handles virtual environments. If needed, refer to Poetry’s documentation for managing virtual environments.

---

## 2. Branch & Commit Naming Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/) and semantic versioning principles for clarity and automation. This ensures that commit messages also help determine version bumps (e.g., breaking changes lead to major version increments, features to minor, fixes to patch).

### Branch Naming

Branches should be named in the following format:

```
<type>/<issue-number>-<short-description>
```

- **`<type>`:** One of the following:
  - `feat` (new feature)
  - `fix` (bug fix)
  - `docs` (documentation changes)
  - `style` (formatting, no functional changes)
  - `refactor` (code refactoring)
  - `test` (adding or updating tests)
  - `chore` (maintenance tasks)
- **`<issue-number>`:** Reference the related issue (if applicable).
- **`<short-description>`:** A brief, hyphen-separated summary.

**Examples:**

- `feat/123-add-user-auth`
- `fix/456-correct-api-endpoint`
- `docs/789-update-readme`

### Commit Messages

Commit messages should follow this structure:

```
<type>(<scope>): <description>
```

- **`<type>`:** Same as above (e.g., `feat`, `fix`).
- **`<scope>`:** (Optional) The module or area affected.
- **`<description>`:** A concise summary in the imperative mood (e.g., “add,” “fix,” “update”).

**Examples:**

- `feat(auth): add JWT-based user authentication`
- `fix(api): correct endpoint URL for data retrieval`
- `docs: update installation instructions`

For breaking changes, either append an exclamation mark after the type or include a `BREAKING CHANGE:` footer:

- `feat!: overhaul authentication system`
- Or:

  ```markdown
  feat(auth): update user authentication
  
  BREAKING CHANGE: The authentication API has changed; please update your integration accordingly.
  ```

---

## 3. Issue Reporting Guidelines

When opening a new issue, please include the following information:

- **Title:** A clear and descriptive title summarizing the problem.
- **Description:** A detailed explanation of the issue.
- **Steps to Reproduce:** Provide step-by-step instructions that allow us to reproduce the problem.
- **Expected vs. Actual Behavior:** Describe what you expected to happen and what actually occurred.
- **Environment Details:** Include OS, Python version, and any other relevant setup details.
- **Screenshots/Logs:** Attach screenshots or error logs if available.

---

## 4. Testing

We use [pytest](https://docs.pytest.org/) for running our test suite.

- **Run Tests Locally:**  

  Simply execute:

  ```bash
  pytest
  ```

- **Before Submitting a PR:**  
  Ensure that all tests pass.

---

## 5. Documentation

Our documentation is built with [MkDocs](https://www.mkdocs.org/).

- **Viewing Documentation Locally:**  
  
  Run:

  ```bash
  mkdocs serve
  ```

  This command will start a local server so you can preview the docs as you work on them.
- **Contributing Changes:**  
  Please follow the structure in the `docs/` folder and update `SUMMARY.md` if you add new pages.

---

## 6. Code Formatting

We use [black](https://black.readthedocs.io/) and [isort](https://pycqa.github.io/isort/) to enforce a consistent code style. Configuration is managed in `pyproject.toml`.

- **Format Code with Black:**  

  ```bash
  black .
  ```

- **Sort Imports with isort:**
  
  ```bash
  isort .
  ```

Please run these tools on your changes before submitting a pull request.

---

## 7. Code of Conduct

To maintain a friendly and inclusive environment, we ask all contributors to follow our Code of Conduct. We are adopting the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md) as our Code of Conduct.

- **Location:**  
  A copy of the Code of Conduct should be added to the repository as `CODE_OF_CONDUCT.md`.
- **Expectations:**  
  All contributors are expected to treat others with respect and to refrain from harassment or exclusionary behavior.
- **Reporting:**  
  If you experience or witness any violations, please report them to the project maintainers via the contact details provided in the Code of Conduct.

---

## 8. Final Steps

- **Pull Requests:**  
  - Ensure that your branch name and commit messages adhere to the guidelines above.
  - Run all tests and format your code before submission.
- **Review Process:**  
  Your pull request will undergo review and feedback. Please address any requested changes promptly.
- **Questions:**  
  If you have any questions about contributing, feel free to open an issue or join our discussions.

Thank you for contributing to Supermat and helping us build a better project!

---
