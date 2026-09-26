"""Bulk document extraction on the cheapest model via the Message Batches API (50% off)."""

from __future__ import annotations

import base64
import csv
import io
import json
from typing import Any

from anthropic import beta_tool
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

from venture_lab.config import usage_cost_usd
from venture_lab.policy import BudgetExceeded, Policy

MAX_DOCS_PER_BATCH = 500
TEXT_SUFFIXES = {".txt", ".md", ".csv", ".json", ".html", ".eml"}


def _document_block(path: Any) -> dict[str, Any]:
    if path.suffix.lower() == ".pdf":
        data = base64.standard_b64encode(path.read_bytes()).decode()
        return {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": data}}
    return {
        "type": "text",
        "text": f'<document name="{path.name}">\n{path.read_text(encoding="utf-8", errors="replace")}\n</document>',
    }


def build_requests(files: list[Any], schema: dict[str, Any], instructions: str, model: str) -> list[Request]:
    system = [
        {
            "type": "text",
            "text": "Extract the requested fields from the document. Use null for anything the "
            "document does not state; never guess.\n\n" + instructions,
            "cache_control": {"type": "ephemeral"},
        }
    ]
    return [
        Request(
            custom_id=f"doc-{i}",
            params=MessageCreateParamsNonStreaming(
                model=model,
                max_tokens=4096,
                system=system,
                messages=[
                    {"role": "user", "content": [_document_block(f), {"type": "text", "text": "Extract the fields."}]}
                ],
                output_config={"format": {"type": "json_schema", "schema": schema}},
            ),
        )
        for i, f in enumerate(files)
    ]


def extraction_tools(
    *, experiment_id: str, ledger: Any, workspace: Any, client: Any, settings: Any, api_budget_usd: float
) -> list[Any]:
    model = settings.models.bulk
    policy = Policy(settings, ledger)

    @beta_tool
    def submit_extraction_batch(input_dir: str, schema_json: str, instructions: str, job_name: str) -> str:
        """Queue every document in a workspace folder for structured extraction on the
        bulk model via the Batch API. Results usually arrive within an hour; collect them
        with collect_extraction_batch in this or a later session.

        Args:
            input_dir: Workspace folder with .pdf/.txt/.md/.csv/.json/.html/.eml files, e.g. "samples/leases".
            schema_json: JSON Schema for one document (object, additionalProperties false,
                all properties required).
            instructions: Field definitions and edge cases for the extractor.
            job_name: Short name; results are saved under extractions/<job_name>/.
        """
        try:
            schema = json.loads(schema_json)
        except ValueError as exc:
            return f"Error: invalid schema_json ({exc})."
        folder = workspace.resolve(input_dir)
        if not folder.is_dir():
            return f"Error: {input_dir} is not a folder in the workspace."
        files = sorted(p for p in folder.iterdir() if p.suffix.lower() in TEXT_SUFFIXES | {".pdf"})
        if not files:
            return "Error: no supported documents found."
        if len(files) > MAX_DOCS_PER_BATCH:
            return f"Error: {len(files)} documents; split into jobs of at most {MAX_DOCS_PER_BATCH}."
        try:
            policy.check_budget(experiment_id, api_budget_usd)
        except BudgetExceeded as exc:
            return f"Error: {exc}"
        batch = client.messages.batches.create(requests=build_requests(files, schema, instructions, model))
        manifest = {"batch_id": batch.id, "model": model, "files": {f"doc-{i}": f.name for i, f in enumerate(files)}}
        out = workspace.resolve(f"extractions/{job_name}/manifest.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return f"Submitted batch {batch.id} with {len(files)} documents. Manifest: extractions/{job_name}/manifest.json"

    @beta_tool
    def collect_extraction_batch(job_name: str) -> str:
        """Fetch results of a submitted extraction job, write results.jsonl and results.csv
        under extractions/<job_name>/, and book the batch cost to this experiment.

        Args:
            job_name: The job_name used when submitting.
        """
        manifest_path = workspace.resolve(f"extractions/{job_name}/manifest.json")
        if not manifest_path.is_file():
            return f"Error: no job named {job_name}."
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        batch = client.messages.batches.retrieve(manifest["batch_id"])
        if batch.processing_status != "ended":
            return f"Batch still {batch.processing_status}; try again later."

        run_id = ledger.start_run(experiment_id, "batch", manifest["model"])
        rows, errors, total = [], 0, 0.0
        for result in client.messages.batches.results(manifest["batch_id"]):
            name = manifest["files"].get(result.custom_id, result.custom_id)
            if result.result.type != "succeeded":
                errors += 1
                continue
            msg = result.result.message
            cost = usage_cost_usd(manifest["model"], msg.usage, batch=True)
            ledger.add_usage(run_id, msg.usage, cost)
            total += cost
            text = next((b.text for b in msg.content if b.type == "text"), "{}")
            try:
                rows.append({"file": name, **json.loads(text)})
            except ValueError:
                errors += 1
        ledger.finish_run(run_id, "ok", f"extraction {job_name}: {len(rows)} ok, {errors} failed, ${total:.4f}")

        folder = manifest_path.parent
        (folder / "results.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
        if rows:
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=sorted({k for r in rows for k in r}))
            writer.writeheader()
            writer.writerows(
                {k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in r.items()} for r in rows
            )
            (folder / "results.csv").write_text(buf.getvalue(), encoding="utf-8")
        per_doc = total / len(rows) if rows else 0
        return f"{len(rows)} documents extracted, {errors} failed. Cost ${total:.4f} (${per_doc:.5f}/doc)."

    return [submit_extraction_batch, collect_extraction_batch]
