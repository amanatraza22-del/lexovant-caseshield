
from flask import Flask, request, redirect, Response
import csv
import io
from datetime import datetime

app = Flask(__name__)

matter = {
    "title": "Sample Commercial Dispute",
    "client": "Fictional Demo Client",
    "status": "Under Review",
    "notes": "",
    "facts": [
        {
            "date": "2026-01-10",
            "fact": "Agreement signed",
            "source": "Agreement.pdf, page 1",
            "amount": "100000"
        },
        {
            "date": "2026-01-20",
            "fact": "Invoice issued",
            "source": "Invoice.pdf, page 1",
            "amount": "100000"
        },
        {
            "date": "2026-02-05",
            "fact": "Payment recorded",
            "source": "BankStatement.pdf, page 2",
            "amount": "75000"
        }
    ],
    "checklist": {
        "Agreement reviewed": False,
        "Dates cross-checked": False,
        "Amounts cross-checked": False,
        "Deadlines checked by lawyer": False
    }
}

def find_flags():
    flags = []
    amounts = {}

    for item in matter["facts"]:
        if not item["source"]:
            flags.append(
                ("Missing source", item["fact"],
                 "No source reference supplied")
            )

        amount = item["amount"].strip()
        if amount:
            amounts.setdefault(amount, []).append(item)

    for amount, items in amounts.items():
        if len(items) > 1:
            sources = ", ".join(
                item["source"] for item in items
            )
            flags.append((
                "Repeated amount",
                f"Amount {amount} appears in multiple entries. "
                "Check whether this is intentional.",
                sources
            ))

    return flags


def page(content):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport"
              content="width=device-width, initial-scale=1">
        <title>Lexovant CaseShield</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f2f5fa;
                color: #17243a;
                margin: 0;
            }}
            header {{
                background: #12233f;
                color: white;
                padding: 22px;
            }}
            main {{
                max-width: 950px;
                margin: auto;
                padding: 15px;
            }}
            .card {{
                background: white;
                padding: 18px;
                margin: 15px 0;
                border-radius: 12px;
                box-shadow: 0 2px 8px #00000010;
            }}
            a, button {{
                display: inline-block;
                background: #126b87;
                color: white;
                padding: 10px 14px;
                border: 0;
                border-radius: 6px;
                text-decoration: none;
                cursor: pointer;
            }}
            input, textarea, select {{
                box-sizing: border-box;
                width: 100%;
                padding: 10px;
                margin: 6px 0 12px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                overflow-wrap: anywhere;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            .flag {{
                background: #fff5df;
                border-left: 4px solid #d38b22;
                padding: 12px;
                margin: 10px 0;
            }}
            .small {{
                font-size: 12px;
                color: #606b7b;
            }}
        </style>
    </head>
    <body>
        <header>
            <h1>Lexovant CaseShield</h1>
            Litigation File Stress-Test & Evidence Traceability
        </header>
        <main>
            {content}
            <p class="small">
                Prototype only. Review flags are not legal conclusions.
                A lawyer must verify all facts and sources.
                Use fictional data only; do not enter confidential
                client information.
            </p>
        </main>
    </body>
    </html>
    """


@app.route("/")
def dashboard():
    flags = find_flags()
    completed = sum(matter["checklist"].values())
    total = len(matter["checklist"])

    content = f"""
    <div class="card">
        <h2>Case Dashboard</h2>
        <h3>{matter["title"]}</h3>
        <p>Client: {matter["client"]}</p>
        <p>Status: {matter["status"]}</p>
        <a href="/matter">Open Matter</a>
        <a href="/export.csv">Export Evidence CSV</a>
    </div>

    <div class="card">
        <h3>Review Snapshot</h3>
        <p>Evidence entries: {len(matter["facts"])}</p>
        <p>Potential review leads: {len(flags)}</p>
        <p>Checklist: {completed}/{total} completed</p>
    </div>

    <div class="card">
        <h3>What this prototype does</h3>
        <p>Organises sample facts, displays source references,
        flags repeated amounts, tracks a lawyer's checklist,
        and exports the evidence map to CSV.</p>
        <p>It does not read PDFs or use an AI model.</p>
    </div>
    """
    return page(content)


@app.route("/matter", methods=["GET", "POST"])
def matter_page():
    if request.method == "POST":
        matter["title"] = request.form.get(
            "title", matter["title"]
        )
        matter["client"] = request.form.get(
            "client", matter["client"]
        )
        matter["status"] = request.form.get(
            "status", "Under Review"
        )
        matter["notes"] = request.form.get("notes", "")

        for key in matter["checklist"]:
            matter["checklist"][key] = (
                request.form.get(key) == "on"
            )

        return redirect("/matter")

    checklist = ""
    for key, value in matter["checklist"].items():
        checked = "checked" if value else ""
        checklist += f"""
        <label>
            <input style="width:auto" type="checkbox"
                   name="{key}" {checked}>
            {key}
        </label><br>
        """

    rows = ""
    for item in matter["facts"]:
        rows += f"""
        <tr>
            <td>{item["date"]}</td>
            <td>{item["fact"]}</td>
            <td>{item["source"]}</td>
            <td>{item["amount"]}</td>
        </tr>
        """

    flags_html = ""
    for title, description, source in find_flags():
        flags_html += f"""
        <div class="flag">
            <b>{title}</b><br>
            {description}<br>
            <span class="small">Source: {source}</span>
        </div>
        """

    if not flags_html:
        flags_html = "<p>No pattern flags found.</p>"

    chronology = sorted(
        matter["facts"], key=lambda item: item["date"]
    )

    timeline = "".join(
        f'<li><b>{item["date"]}</b> — {item["fact"]} '
        f'({item["source"]})</li>'
        for item in chronology
    )

    content = f"""
    <p><a href="/">← Dashboard</a></p>

    <div class="card">
        <h2>Matter Details</h2>
        <form method="post">
            <label>Matter title</label>
            <input name="title" value="{matter["title"]}">

            <label>Client / demo label</label>
            <input name="client" value="{matter["client"]}">

            <label>Status</label>
            <select name="status">
                {''.join(
                    f'<option {"selected" if s == matter["status"] else ""}>{s}</option>'
                    for s in [
                        "New", "Documents Received",
                        "Under Review", "Advocate Review",
                        "Report Ready"
                    ]
                )}
            </select>

            <h3>Filing Readiness Checklist</h3>
            {checklist}

            <label>Lawyer Review Notes</label>
            <textarea name="notes" rows="4">{matter["notes"]}</textarea>

            <button type="submit">Save Review</button>
        </form>
    </div>

    <div class="card">
        <h2>Fact & Evidence Map</h2>
        <div style="overflow-x:auto">
            <table>
                <tr>
                    <th>Date</th><th>Fact</th>
                    <th>Source</th><th>Amount</th>
                </tr>
                {rows}
            </table>
        </div>
    </div>

    <div class="card">
        <h2>Potential Review Leads</h2>
        {flags_html}
    </div>

    <div class="card">
        <h2>Chronology</h2>
        <ol>{timeline}</ol>
    </div>
    """
    return page(content)


@app.route("/export.csv")
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Matter", "Date", "Fact",
        "Source Reference", "Amount"
    ])

    for item in matter["facts"]:
        writer.writerow([
            matter["title"], item["date"], item["fact"],
            item["source"], item["amount"]
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=caseshield_evidence_map.csv"
        }
    )


if __name__ == "__main__":
    app.run(debug=True)