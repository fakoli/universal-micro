# Contributing

Keep the first release small: Windows routing, the existing seven-key layer and the four actions. Propose further controls/platforms when there is a tested use case. Work in your own fork or a branch you control; do not patch someone else's live service to prove a contribution.

## Local checks

Python has no third-party runtime dependencies. From a clean checkout with Python/Tk, Git and Node 24:

```powershell
python -m unittest discover -v
node test_web_controller.cjs
python check_release.py
```

The unit checks use disposable files/Git repositories, a unique test mutex and stubbed global-key registration. They do not claim F13–F22, change startup, focus a harness, record speech or send a prompt. They can run with the real router active. Windows message-loop checks are skipped on other operating systems; that is not Windows runtime validation.

For client changes, follow [INTEGRATIONS.md](docs/INTEGRATIONS.md) to obtain public pinned sources and run both patched-source checks plus the Pi build and adjacent client tests. Those integration checks intentionally require the declared checkouts; no private captures or account access are needed. Node may print an experimental TypeScript-stripping warning in the Pi route check.

Hardware, voice permissions, native app shortcuts and real sign-in are covered by the separate [manual acceptance](docs/ACCEPTANCE.md). `python test_router.py --native` is optional and interactive: it creates its own temporary window and sends a chord there after F12. Run it only when you have control of the desktop; it does not target a harness.

## Changes and pull requests

Add the smallest regression check that reproduces a behavior change. Test changed and neighboring behavior. Keep source line endings LF, update the manifest for changed patch bytes, preserve upstream MIT notices and document compatibility changes. For patch updates, compare installed controller/adapter files with the maintained `web-controller.js` and `integrations/*.js` and run apply/reverse/build/acceptance checks. Do not vendor a complete browser client or machine-specific settings.

Describe the concrete problem, resulting behavior, checks actually run and any remaining gaps. For UI changes include synthetic before/after evidence and check keyboard navigation, narrow widths and accessible names. Do not post real chats, recordings, device serials/full exports, hostnames, account state, credentials, private source or deployed-model details. The [bug template](.github/ISSUE_TEMPLATE/bug_report.md) asks for sanitized reproduction details.

Use [issues](https://github.com/fakoli/universal-micro/issues) for bugs and support. This is a volunteer project with no response-time commitment. Report vulnerabilities through [SECURITY.md](SECURITY.md), never by posting sensitive details in a public issue.

Contributions are under the project's MIT license. No CLA is required. A contribution must be yours to share and must retain relevant attribution.

## Release preparation

The explicit [release file list](release-files.txt) controls publication. Update and review it when intentionally adding a public file. `python check_release.py --archive dist/universal-micro-review.zip` checks the clean committed tree, validates the archive and writes its SHA-256. Untracked/ignored operator files are excluded; this scanner is a guard, not proof that arbitrary secrets cannot exist. Review tree, history, examples and archive before release. Use a public commit identity and no personal machine paths in commit messages.
