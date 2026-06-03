#!/usr/bin/env python3
"""Generate demo PDFs for the Public PDF Action Pack project."""
from pathlib import Path

from reportlab.pdfgen import canvas

demos = Path(__file__).resolve().parent.parent / "demos"
demos.mkdir(exist_ok=True)


def school_trip():
    c = canvas.Canvas(str(demos / "school-trip-letter.pdf"))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 760, "Year 4 School Trip to Warwick Castle")
    c.setFont("Helvetica", 11)
    y = 740
    for line in [
        "Dear Parents and Guardians,",
        "",
        "We are pleased to announce a school trip to Warwick Castle on Friday 20th June 2026.",
        "",
        "Cost: 18.50 per pupil, payable by Friday 6th June 2026.",
        "Please complete and return the attached consent form by the same date.",
        "",
        "Your child will need:",
        "- A packed lunch",
        "- A water bottle",
        "- Comfortable walking shoes",
        "- A waterproof coat",
        "",
        "Children should wear school uniform and bring a small backpack.",
        "",
        "The coach will depart at 8:45am and return by approximately 3:30pm.",
        "",
        "If your child requires any medication during the trip,",
        "please inform the school office by Monday 2nd June.",
        "",
        "Yours sincerely,",
        "Mrs J. Thompson, Year 4 Class Teacher",
    ]:
        c.drawString(72, y, line)
        y -= 16
    c.showPage()
    c.save()
    return "school-trip-letter.pdf"


def council_tax():
    c = canvas.Canvas(str(demos / "council-tax-reminder.pdf"))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 760, "COUNCIL TAX REMINDER NOTICE")
    c.setFont("Helvetica", 11)
    y = 740
    for line in [
        "Dear Resident,",
        "",
        "Our records show that your Council Tax account is in arrears.",
        "The outstanding balance of 847.30 must be paid in full",
        "by 30th June 2026.",
        "",
        "If payment is not received by this date we may commence",
        "recovery proceedings, which could result in additional costs",
        "of 95.00 being added to your account.",
        "",
        "If you are unable to pay the full amount, you must contact us",
        "immediately on 020 8825 7000 to discuss a payment arrangement.",
        "",
        "Do not ignore this notice - recovery action may include:",
        "- Application for a liability order at the magistrates court",
        "- Referral to enforcement agents (bailiffs)",
        "- Deduction from earnings or benefits",
        "",
        "Council Tax Reference: 50012345678",
        "Amount due: 847.30",
        "Deadline: 30th June 2026",
    ]:
        c.drawString(72, y, line)
        y -= 16
    c.showPage()
    c.save()
    return "council-tax-reminder.pdf"


def nhs_appointment():
    c = canvas.Canvas(str(demos / "nhs-appointment-letter.pdf"))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 760, "NHS Outpatient Appointment")
    c.setFont("Helvetica", 11)
    y = 740
    for line in [
        "Appointment Details:",
        "Date: Monday 15th June 2026",
        "Time: 10:30am",
        "Department: Cardiology",
        "Location: Solihull Hospital, Lode Lane, Solihull B91 2JL",
        "",
        "Please arrive 15 minutes before your appointment time.",
        "",
        "What to bring:",
        "- Your appointment letter",
        "- A list of any medications you are currently taking",
        "- Your NHS number (if known)",
        "",
        "The Cardiology department is on the first floor.",
        "Follow the blue signs from the main entrance.",
        "",
        "If you cannot attend, please call 0121 424 5000",
        "at least 48 hours before your appointment to rearrange.",
    ]:
        c.drawString(72, y, line)
        y -= 16
    c.showPage()
    c.save()
    return "nhs-appointment-letter.pdf"


def property_solicitor():
    c = canvas.Canvas(str(demos / "property-solicitor-letter.pdf"))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 760, "Client Care Letter - Property Purchase")
    c.setFont("Helvetica", 11)
    y = 740
    for line in [
        "Dear Client,",
        "",
        "Re: Purchase of 5 Horrell Road, Birmingham B90 2JS",
        "",
        "Thank you for instructing Sydney Mitchell LLP to act on your behalf",
        "in connection with the purchase of the above property.",
        "",
        "PLEASE RETURN TO US THE FOLLOWING:",
        "",
        "1. Cheque / bank transfer for 650.00 on account of costs.",
        "2. One signed copy of the enclosed letter of instruction.",
        "3. Completed and signed Conveyancing Instruction form.",
        "4. Completed Joint Purchasers Information form.",
        "5. Original proof of identity and proof of address.",
        "6. Documentary evidence of source of funds (bank statements).",
        "",
        "Our estimated legal fees are 1,125.00 plus VAT.",
        "The total estimated cost including disbursements is 1,912.50.",
        "",
        "We anticipate completion on or around 14th July 2026.",
        "",
        "Yours sincerely,",
        "Sydney Mitchell LLP",
    ]:
        c.drawString(72, y, line)
        y -= 16
    c.showPage()
    c.save()
    return "property-solicitor-letter.pdf"


if __name__ == "__main__":
    results = []
    for fn in [school_trip, council_tax, nhs_appointment, property_solicitor]:
        name = fn()
        results.append(name)
        print(f"  Created {name}")
    print(f"\n{len(results)} demo PDFs in {demos}")
