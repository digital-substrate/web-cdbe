# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This application has its own version line, independent from the `dsviper`
runtime version (declared as a dependency in `requirements.txt`).

## [1.2.0] - 2026-06-17

First standalone release of Web CDBE — a Flask reference application that
builds a Commit Database Editor over a Database / CommitDatabase in pure
HTML5, with no JavaScript.

### Added
- Flask web UI to browse abstractions, keys, and attached documents over a
  Database / CommitDatabase, and to edit values in place.
- Requires dsviper >= 1.2.16.
