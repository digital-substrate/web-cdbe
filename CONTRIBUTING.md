# Contributing to Web CDBE (web-cdbe)

Thanks for your interest in contributing.

## Reporting issues

Use [GitHub Issues](https://github.com/digital-substrate/web-cdbe/issues) and pick the appropriate template (bug report or feature request).

## Submitting pull requests

1. Fork the repository and create a feature branch from `main`
2. Make your changes (see "Running locally" below)
3. Verify the server still launches and the routes you touched still work
4. Open a pull request with a clear description of what changed and why

## Running locally

Requires Python 3.14+.

```bash
pip install -r requirements.txt          # flask and deps
pip install dsviper                      # Viper Python binding (also pulled by requirements.txt)
ln -s /path/to/db.rapmc database.link    # point the server at your commit database
flask run --debug                        # launch
```

## Architecture note

This app depends on `dsviper`, the pre-built Viper Python binding (distributed on PyPI). All persistence and commit operations go through it — don't attempt to port Viper.

## License

This project is licensed under the MIT License (see [LICENSE](LICENSE)). By submitting a pull request, you agree that your contribution is provided under the same license (inbound = outbound). No CLA is required.
