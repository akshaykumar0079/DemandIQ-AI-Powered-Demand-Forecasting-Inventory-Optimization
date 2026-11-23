# Development guide

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
ruff check .
```

Run the API:

```bash
uvicorn demandiq.api.main:app --reload
```

Run the dashboard in another terminal:

```bash
cd frontend
npm install
npm run dev
```

Run the CSV demo:

```bash
python scripts/demo.py data/sample_sales.csv --horizon 7
```

## Pull request checklist

- Add tests for new data validation, forecasting, inventory, or API behavior.
- Preserve chronological ordering in all time-series evaluation.
- Validate user input at API boundaries and return actionable 422 errors.
- Update API and architecture docs when behavior changes.
- Run `ruff check .`, `pytest`, and `npm run build` before merging.
- Never claim a model is production-accurate without evaluation on representative, documented data.
