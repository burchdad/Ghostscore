def generate_action_plan_pdf(profile, actions):
    """
    Generate a PDF action plan for a profile's recommended actions.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, f"Action Plan for: {profile.get('name', profile.get('id', ''))}")
    y -= 30
    c.setFont("Helvetica", 12)
    c.drawString(40, y, f"Profile ID: {profile.get('id', '')}")
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Recommended Actions:")
    y -= 20
    c.setFont("Helvetica", 11)
    if not actions:
        c.drawString(50, y, "No recommended actions at this time.")
        y -= 15
    else:
        for i, action in enumerate(actions, 1):
            desc = action.get('description') or f"{action.get('type', '').capitalize()} {action.get('account_name', '')}"
            gain = action.get('estimated_gain')
            c.drawString(50, y, f"{i}. {desc} (Est. +{gain} pts)")
            y -= 15
            if y < 60:
                c.showPage()
                y = height - 40
    c.save()
    buffer.seek(0)
    return buffer.read()
def generate_scenario_comparison_pdf(entry_a, entry_b):
    """
    Generate a PDF comparing two scenario history entries.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "Scenario Comparison Report")
    y -= 30

    for idx, entry in enumerate([entry_a, entry_b]):
        c.setFont("Helvetica-Bold", 13)
        c.drawString(40, y, f"Scenario {'A' if idx == 0 else 'B'}:")
        y -= 18
        c.setFont("Helvetica", 11)
        c.drawString(50, y, f"Date: {str(entry.created_at)}")
        y -= 15
        c.drawString(50, y, f"Original Score: {entry.original_score}")
        y -= 15
        c.drawString(50, y, f"Simulated Score: {entry.simulated_score}")
        y -= 15
        c.drawString(50, y, f"Gain: {entry.actual_gain if entry.actual_gain is not None else entry.simulated_score - entry.original_score}")
        y -= 15
        c.drawString(50, y, "Actions:")
        y -= 15
        for a in entry.actions:
            c.drawString(60, y, f"- {a.get('description', a.get('type', ''))}")
            y -= 13
            if y < 60:
                c.showPage()
                y = height - 40
        c.drawString(50, y, f"Notes: {entry.notes or ''}")
        y -= 20
        if y < 60:
            c.showPage()
            y = height - 40
    c.save()
    buffer.seek(0)
    return buffer.read()
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def generate_profile_report_pdf(profile, score_history=None, scenario_history=None):
    """
    Generate a PDF report for a credit profile, including score history and scenario history if provided.
    Returns: bytes (PDF data)
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, f"Credit Profile Report: {profile.get('name', profile.get('id', ''))}")
    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(40, y, f"Profile ID: {profile.get('id', '')}")
    y -= 20
    if 'user_id' in profile:
        c.drawString(40, y, f"User ID: {profile['user_id']}")
        y -= 20

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Accounts:")
    y -= 20
    c.setFont("Helvetica", 11)
    for acc in profile.get('accounts', []):
        c.drawString(50, y, f"{acc['type'].capitalize()}: {acc['name']} | Balance: ${acc['balance']:.2f} | Status: {acc['status']}")
        y -= 15
        if y < 60:
            c.showPage()
            y = height - 40
    y -= 10

    if profile.get('derogatories'):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Derogatories:")
        y -= 20
        c.setFont("Helvetica", 11)
        for der in profile['derogatories']:
            c.drawString(50, y, f"{der['type'].capitalize()} on {der['date']}: {der.get('details', '')}")
            y -= 15
            if y < 60:
                c.showPage()
                y = height - 40
        y -= 10

    if score_history:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Score History:")
        y -= 20
        c.setFont("Helvetica", 11)
        for entry in score_history:
            c.drawString(50, y, f"{entry['date']}: {entry['score']}")
            y -= 15
            if y < 60:
                c.showPage()
                y = height - 40
        y -= 10

    if scenario_history:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Scenario History:")
        y -= 20
        c.setFont("Helvetica", 11)
        for entry in scenario_history:
            c.drawString(50, y, f"{entry['created_at']}: {entry['actions']} | Simulated Score: {entry['simulated_score']}")
            y -= 15
            if y < 60:
                c.showPage()
                y = height - 40
        y -= 10

    c.save()
    buffer.seek(0)
    return buffer.read()
