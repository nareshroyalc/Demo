"""Generate the Brightline Supplies demo: 5 policy PDFs + a SQLite database.

The policy numbers below (SLA days, compensation, discount tiers, warranty months)
are the single source of truth: they are written into the PDFs AND used to
generate the database, so questions that need both docs and data have real answers.

Run:  python scripts/generate_demo_data.py
"""
from __future__ import annotations

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "data" / "docs"
DB_PATH = ROOT / "data" / "demo.db"

# ---------------------------------------------------------------- policy facts
REGION_SLA = {"North": 3, "South": 4, "East": 3, "West": 5}  # business days, Standard tier
TIER_SLA_REDUCTION = {"Standard": 0, "Gold": 0, "Platinum": 1}  # Platinum ships 1 day faster
LATE_COMP = [  # (min_days_late, max_days_late, credit_pct)
    (1, 2, 5),
    (3, 5, 10),
    (6, 999, 15),
]
CATEGORY_WARRANTY = {
    "Furniture": 36,
    "Electronics": 12,
    "Printers & Toner": 6,
    "Stationery": 0,
    "Breakroom": 0,
}
VOLUME_DISCOUNTS = [(50, 99, 5), (100, 249, 8), (250, 10**6, 12)]
TIER_EXTRA_DISCOUNT = {"Standard": 0, "Gold": 2, "Platinum": 4}

# ---------------------------------------------------------------------- PDFs
_styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=_styles["Title"], fontSize=20, spaceAfter=6)
SUB = ParagraphStyle("SUB", parent=_styles["Normal"], textColor=colors.grey, fontSize=9, spaceAfter=14)
H2 = ParagraphStyle("H2", parent=_styles["Heading2"], fontSize=13, spaceBefore=12, spaceAfter=4)
BODY = ParagraphStyle("BODY", parent=_styles["BodyText"], fontSize=10.5, leading=15, spaceAfter=6)


def _table(rows: list[list[str]]) -> Table:
    t = Table(rows, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c2cc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f6f9")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def build_pdf(filename: str, title: str, doc_id: str, sections: list) -> None:
    """sections: list of (heading, [item]) where item is a str paragraph or a list-of-rows table."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(DOCS_DIR / filename), pagesize=LETTER, title=title, author="Brightline Supplies",
        leftMargin=0.9 * inch, rightMargin=0.9 * inch, topMargin=0.8 * inch, bottomMargin=0.8 * inch,
    )
    flow = [
        Paragraph(title, H1),
        Paragraph(f"Brightline Supplies Inc. &nbsp;|&nbsp; Document {doc_id} &nbsp;|&nbsp; Version 3.2 &nbsp;|&nbsp; Effective 1 July 2025", SUB),
    ]
    for heading, items in sections:
        flow.append(Paragraph(heading, H2))
        for it in items:
            if isinstance(it, str):
                flow.append(Paragraph(it, BODY))
            else:
                flow.append(_table(it))
                flow.append(Spacer(1, 8))
    doc.build(flow)


def make_pdfs() -> None:
    comp_rows = [["Days late", "Credit on order value"]] + [
        [f"{a}-{b}" if b < 999 else f"{a}+", f"{pct}%"] for a, b, pct in LATE_COMP
    ]
    sla_rows = [["Region", "Standard / Gold SLA", "Platinum SLA"]] + [
        [r, f"{d} business days", f"{max(1, d - 1)} business days"] for r, d in REGION_SLA.items()
    ]

    # 1 -- Returns & Refund Policy
    build_pdf("01_returns_and_refund_policy.pdf", "Returns & Refund Policy", "POL-RET-001", [
        ("1. Purpose and scope", [
            "This policy explains how Brightline Supplies customers may return products and receive refunds, "
            "replacements or credits. It applies to all B2B accounts in every region and every customer tier.",
        ]),
        ("2. Standard return window", [
            "Customers may return unopened, undamaged products within <b>30 days</b> of the delivery date for a full refund. "
            "<b>Platinum tier</b> customers receive an extended window of <b>45 days</b>. The window is counted from the "
            "delivered date recorded in our shipment system, not the order date.",
            [["Customer tier", "Return window", "Restocking fee (opened, non-defective)"],
             ["Standard", "30 days", "15%"], ["Gold", "30 days", "10%"], ["Platinum", "45 days", "0%"]],
        ]),
        ("3. Damaged or defective items", [
            "Damage in transit must be reported within <b>7 days</b> of delivery, with photographs of the item and packaging. "
            "Approved damage claims are resolved with a full refund or a free replacement at the customer's choice, and "
            "Brightline pays the return shipping. Claims reported after 7 days are handled as warranty claims where applicable "
            "(see the Product Catalog &amp; Warranty Guide, POL-PRD-005).",
            "Wrong-item shipments are treated the same way as damaged items: full refund or replacement, no restocking fee, "
            "return shipping paid by Brightline, regardless of the 7-day reporting rule if reported within 30 days.",
        ]),
        ("4. Non-returnable items", [
            "The following cannot be returned unless they arrive damaged or defective: custom-printed or personalised items, "
            "opened toner and ink cartridges, opened breakroom consumables, and clearance items marked 'Final Sale'.",
        ]),
        ("5. Restocking fees", [
            "Opened but non-defective returns in returnable categories incur the restocking fee shown in section 2. "
            "The fee is deducted from the refund. No restocking fee applies to damaged, defective or wrong-item returns.",
        ]),
        ("6. How refunds are issued", [
            "Refunds are issued to the original payment method or as account credit, at the customer's choice. Approved refunds "
            "are processed within <b>5 business days</b> of the returned goods being received and inspected. Credit notes appear "
            "in the customer's account immediately after approval.",
        ]),
        ("7. Late-delivery interaction", [
            "If an order was delivered later than its Shipping SLA, the customer is entitled to a late-delivery credit as set out in "
            "the Shipping &amp; Delivery SLA (POL-SHP-002). A late-delivery credit is separate from, and can be combined with, "
            "a refund under this policy. A customer whose order was more than 5 days late may also return the whole order "
            "with no restocking fee, even if the goods were opened.",
        ]),
        ("8. Approval authority", [
            "Support agents may approve refunds up to $2,500. Refunds above $2,500 require Support Team Lead approval; "
            "refunds above $10,000 require the Director of Customer Operations.",
        ]),
    ])

    # 2 -- Shipping & Delivery SLA
    build_pdf("02_shipping_and_delivery_sla.pdf", "Shipping & Delivery SLA", "POL-SHP-002", [
        ("1. Purpose", [
            "This document defines the delivery commitments Brightline Supplies makes to customers and the compensation "
            "owed when those commitments are missed.",
        ]),
        ("2. Delivery SLA by region", [
            "The SLA is measured in <b>business days from the ship date to the delivered date</b>. Weekends and public holidays "
            "do not count. The SLA depends on the delivery region of the order and the customer tier.",
            sla_rows,
            "Platinum tier customers receive priority handling and a delivery SLA that is one business day shorter than the "
            "regional standard (minimum 1 day). Gold tier customers receive the standard regional SLA with priority dispatch.",
        ]),
        ("3. Order processing", [
            "Orders placed before 2:00 PM local warehouse time on a business day ship the same day. Orders placed after the cut-off "
            "ship the next business day. Orders over 500 units are split-shipped and each shipment has its own SLA.",
        ]),
        ("4. Late-delivery compensation", [
            "If a shipment is delivered after its SLA, Brightline issues an account credit calculated as a percentage of the "
            "order value (excluding tax and freight):",
            comp_rows,
            "Orders more than 5 days late additionally qualify for free return shipping and the option to return the entire "
            "order without a restocking fee (see POL-RET-001, section 7). Credits are applied automatically within "
            "<b>3 business days</b> after delivery, and customers should open a ticket if the credit is missing.",
        ]),
        ("5. Carriers and tracking", [
            "Brightline ships with SwiftFreight, NorthStar Logistics and CityHaul Express. Tracking numbers are emailed at "
            "shipment. Carrier delays caused by documented severe weather or road closures may be excluded from the SLA at the "
            "discretion of the Logistics Manager; such exclusions must be recorded on the shipment.",
        ]),
        ("6. Damaged in transit", [
            "Damaged deliveries are handled under the Returns &amp; Refund Policy (POL-RET-001). Customers should report damage "
            "within 7 days of delivery.",
        ]),
        ("7. Escalation", [
            "Customers with an order that is already 3 or more days past its SLA and not yet delivered should be escalated as a "
            "Priority 2 (P2) ticket per the Customer Support Handbook (POL-SUP-004).",
        ]),
    ])

    # 3 -- Pricing & Discount Policy
    vol_rows = [["Units per order (single product)", "Volume discount"]] + [
        [f"{a}-{b}" if b < 10**6 else f"{a}+", f"{p}%"] for a, b, p in VOLUME_DISCOUNTS
    ]
    tier_rows = [["Customer tier", "Additional tier discount"]] + [[k, f"{v}%"] for k, v in TIER_EXTRA_DISCOUNT.items()]
    build_pdf("03_pricing_and_discount_policy.pdf", "Pricing & Discount Policy", "POL-PRC-003", [
        ("1. Purpose", [
            "This policy sets out list pricing, volume discounts and the approval rules for discounts offered to B2B customers.",
        ]),
        ("2. List pricing", [
            "List prices are published in the product catalogue and are in US dollars, excluding tax and freight. "
            "List prices are reviewed every January and July. Customers are given 30 days' notice of any list price increase.",
        ]),
        ("3. Volume discounts", [
            "A volume discount applies per product line, based on the quantity of that product on a single order:",
            vol_rows,
            "Quantities below 50 units receive no volume discount.",
        ]),
        ("4. Tier discounts", [
            "Customers in higher tiers receive an additional discount, applied on top of any volume discount:",
            tier_rows,
            "Tier is reviewed annually. A customer moves to Gold after $150,000 in trailing twelve-month revenue and to "
            "Platinum after $500,000, subject to account manager approval.",
        ]),
        ("5. Stacking and caps", [
            "Volume and tier discounts stack, but the <b>total discount on any line may not exceed 20%</b>. "
            "Any discount above <b>15%</b> requires written approval from the Sales Director before the order is confirmed. "
            "Discounts above 20% are not permitted under any circumstance.",
        ]),
        ("6. Contract pricing", [
            "Customers with an annual commitment of $250,000 or more may negotiate fixed contract prices for up to 12 months. "
            "Contract prices replace volume discounts but not tier discounts, and are subject to the same 20% cap relative to list.",
        ]),
        ("7. Late-delivery credits are not discounts", [
            "Account credits issued under the Shipping &amp; Delivery SLA are service credits. They do not count toward the 20% "
            "discount cap and do not affect a customer's tier revenue calculation.",
        ]),
        ("8. Payment terms", [
            "Standard payment terms are net 30. Platinum customers may request net 45. A 1% early-payment discount applies when "
            "an invoice is paid within 10 days.",
        ]),
    ])

    # 4 -- Customer Support Handbook
    build_pdf("04_customer_support_handbook.pdf", "Customer Support Handbook", "POL-SUP-004", [
        ("1. Mission", [
            "Our support team resolves customer issues quickly, fairly and consistently. This handbook defines ticket priorities, "
            "response and resolution targets, and escalation paths.",
        ]),
        ("2. Ticket priorities and targets", [
            [["Priority", "Definition", "First response", "Resolution target"],
             ["P1 - Critical", "Customer operations blocked; large order lost", "1 hour", "8 hours"],
             ["P2 - High", "Order late by 3+ days, damaged goods on large order", "4 hours", "24 hours"],
             ["P3 - Normal", "Billing queries, wrong item, standard damage claim", "1 business day", "3 business days"],
             ["P4 - Low", "General questions, catalogue requests", "2 business days", "7 business days"]],
            "Platinum customers' tickets are automatically raised one priority level (for example P3 becomes P2).",
        ]),
        ("3. Issue types", [
            "Every ticket is tagged with one issue type: <b>Late Delivery</b>, <b>Damaged Item</b>, <b>Wrong Item</b>, "
            "<b>Billing</b>, or <b>Warranty</b>. Agents apply the matching policy: Shipping &amp; Delivery SLA for late deliveries, "
            "Returns &amp; Refund Policy for damaged or wrong items, Pricing Policy for billing and the Product Catalog &amp; "
            "Warranty Guide for warranty claims.",
        ]),
        ("4. Handling a late-delivery ticket", [
            "Step 1: confirm the ship date, delivered date and SLA days on the shipment record. "
            "Step 2: calculate days late (delivered date minus ship date, minus SLA days). "
            "Step 3: apply the compensation credit from the SLA table (5%, 10% or 15%). "
            "Step 4: record the credit on the ticket and notify the customer. "
            "Step 5: if more than 5 days late, offer free return shipping and a full return option.",
        ]),
        ("5. Handling a damaged-item ticket", [
            "Confirm the claim was raised within 7 days of delivery, collect photographs, then offer the customer a full refund or "
            "replacement. Brightline pays return shipping. Log the carrier so Logistics can raise a carrier claim.",
        ]),
        ("6. Escalation", [
            "Escalate to the Support Team Lead when: a refund exceeds $2,500, a customer has raised three or more tickets in 30 days, "
            "or a P1 ticket has not been resolved within 4 hours. Escalate to the Director of Customer Operations for refunds above "
            "$10,000 or any legal threat.",
        ]),
        ("7. Quality standards", [
            "All replies must be reviewed for tone and accuracy. Every closed ticket is followed by a one-question satisfaction survey. "
            "The team's target is a customer satisfaction score of 92% or above and 95% of tickets meeting their first-response target.",
        ]),
    ])

    # 5 -- Product Catalog & Warranty Guide
    war_rows = [["Category", "Examples", "Warranty"]] + [
        ["Furniture", "Desks, chairs, filing cabinets", "36 months"],
        ["Electronics", "Monitors, keyboards, docking stations", "12 months"],
        ["Printers & Toner", "Laser printers, toner, ink", "6 months (printers); consumables defect-only"],
        ["Stationery", "Pens, notebooks, folders", "No warranty; defective items replaced within 30 days"],
        ["Breakroom", "Coffee, cups, cleaning supplies", "No warranty; damaged items replaced on request"],
    ]
    build_pdf("05_product_catalog_and_warranty_guide.pdf", "Product Catalog & Warranty Guide", "POL-PRD-005", [
        ("1. Product categories", [
            "Brightline Supplies sells five categories of office products to business customers: Furniture, Electronics, "
            "Printers &amp; Toner, Stationery and Breakroom. This guide summarises each category and its warranty cover.",
        ]),
        ("2. Warranty terms", [
            war_rows,
            "Warranty periods start on the <b>delivered date</b>, not the order date.",
        ]),
        ("3. What the warranty covers", [
            "The warranty covers defects in materials and workmanship under normal office use. Covered remedies are repair, "
            "replacement or refund at Brightline's discretion. Brightline pays shipping on warranty replacements within the first "
            "12 months.",
        ]),
        ("4. What the warranty excludes", [
            "Excluded: accidental damage, liquid damage, misuse, unauthorised repair or modification, normal wear and tear "
            "(for example fabric wear on chairs), cosmetic damage that does not affect function, and consumables once opened.",
        ]),
        ("5. Making a warranty claim", [
            "Customers open a ticket with the issue type <b>Warranty</b>, with the order number, product, delivered date and photographs. "
            "Claims are reviewed within 3 business days. Approved claims are fulfilled within the shipping SLA for the customer's region.",
        ]),
        ("6. Product safety and recalls", [
            "If a product is recalled, Brightline notifies affected customers within 48 hours and offers a full refund or replacement, "
            "irrespective of warranty status or return window.",
        ]),
        ("7. Sustainability", [
            "Where possible Brightline stocks recycled-content paper, refillable stationery and ENERGY STAR electronics. "
            "Customers can request a sustainability report for their account each quarter.",
        ]),
    ])


# ------------------------------------------------------------------- database
FIRST = ["Apex", "Bluewave", "Cedar", "Delta", "Evergreen", "Falcon", "Granite", "Harbor", "Ironwood", "Juniper",
         "Keystone", "Lumen", "Meridian", "Northgate", "Orion", "Pinnacle", "Quarry", "Redwood", "Summit", "Titan",
         "Union", "Vertex", "Willow", "Xenon", "Yellowstone", "Zenith", "Atlas", "Beacon", "Crestview", "Dunmore",
         "Eastfield", "Fairway", "Glenmont", "Highline", "Inland", "Jadestone", "Kingsley", "Lakeside", "Monarch", "Nimbus"]
SUFFIX = ["Corp", "Industries", "Partners", "Group", "Solutions", "Holdings", "Systems", "Logistics", "Labs", "Associates"]
TIER_WEIGHTS = [("Standard", 0.6), ("Gold", 0.28), ("Platinum", 0.12)]
PRODUCTS = [
    # name, category, price
    ("ErgoMax Task Chair", "Furniture", 289.00), ("Adjustable Standing Desk", "Furniture", 549.00),
    ("4-Drawer Filing Cabinet", "Furniture", 219.00), ("Conference Table 8ft", "Furniture", 899.00),
    ("Mesh Visitor Chair", "Furniture", 129.00), ("Bookshelf 5-Tier", "Furniture", 149.00),
    ("27-inch 4K Monitor", "Electronics", 379.00), ("Wireless Keyboard", "Electronics", 59.00),
    ("Wireless Mouse", "Electronics", 29.00), ("USB-C Docking Station", "Electronics", 189.00),
    ("Webcam HD 1080p", "Electronics", 79.00), ("Noise-Cancelling Headset", "Electronics", 149.00),
    ("Laser Printer Mono", "Printers & Toner", 329.00), ("Colour Laser Printer", "Printers & Toner", 599.00),
    ("Black Toner Cartridge", "Printers & Toner", 89.00), ("Colour Toner Set", "Printers & Toner", 249.00),
    ("Ink Cartridge Pack", "Printers & Toner", 64.00), ("Label Printer", "Printers & Toner", 119.00),
    ("Ballpoint Pens (box of 50)", "Stationery", 14.50), ("A4 Notebook (pack of 10)", "Stationery", 22.00),
    ("Manila Folders (box of 100)", "Stationery", 18.00), ("Sticky Notes Bulk Pack", "Stationery", 16.50),
    ("Copy Paper A4 (case of 5 reams)", "Stationery", 39.00), ("Whiteboard Markers (box of 24)", "Stationery", 21.00),
    ("Premium Coffee Beans 2kg", "Breakroom", 34.00), ("Paper Cups (pack of 1000)", "Breakroom", 42.00),
    ("Hand Sanitizer 5L", "Breakroom", 27.00), ("All-Purpose Cleaner Case", "Breakroom", 31.00),
    ("Disposable Cutlery Set", "Breakroom", 19.00), ("Bottled Water (case of 24)", "Breakroom", 12.00),
]
CARRIERS = ["SwiftFreight", "NorthStar Logistics", "CityHaul Express"]
ISSUES = ["Late Delivery", "Damaged Item", "Wrong Item", "Billing", "Warranty"]

SCHEMA = """
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, region TEXT NOT NULL,
  tier TEXT NOT NULL CHECK (tier IN ('Standard','Gold','Platinum')), joined_date TEXT NOT NULL);
CREATE TABLE products (
  product_id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL,
  unit_price REAL NOT NULL, warranty_months INTEGER NOT NULL);
CREATE TABLE orders (
  order_id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
  order_date TEXT NOT NULL, status TEXT NOT NULL, region TEXT NOT NULL);
CREATE TABLE order_items (
  item_id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(order_id),
  product_id INTEGER NOT NULL REFERENCES products(product_id), quantity INTEGER NOT NULL,
  unit_price REAL NOT NULL, discount_pct REAL NOT NULL DEFAULT 0);
CREATE TABLE shipments (
  shipment_id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(order_id),
  shipped_date TEXT NOT NULL, delivered_date TEXT, carrier TEXT NOT NULL, sla_days INTEGER NOT NULL,
  transit_business_days INTEGER);
CREATE TABLE support_tickets (
  ticket_id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
  order_id INTEGER REFERENCES orders(order_id), issue_type TEXT NOT NULL, priority TEXT NOT NULL,
  opened_date TEXT NOT NULL, resolved_date TEXT, notes TEXT);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_items_order ON order_items(order_id);
CREATE INDEX idx_ship_order ON shipments(order_id);
"""


def add_business_days(start: date, n: int) -> date:
    d = start
    while n > 0:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def next_business_day(d: date) -> date:
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def volume_pct(qty: int) -> int:
    for lo, hi, pct in VOLUME_DISCOUNTS:
        if lo <= qty <= hi:
            return pct
    return 0


def make_db() -> None:
    rnd = random.Random(42)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)

    # customers
    names = [f"{f} {rnd.choice(SUFFIX)}" for f in FIRST]
    cust = []
    for i, name in enumerate(names, 1):
        tier = rnd.choices([t for t, _ in TIER_WEIGHTS], [w for _, w in TIER_WEIGHTS])[0]
        region = rnd.choice(list(REGION_SLA))
        joined = date(2022, 1, 1) + timedelta(days=rnd.randint(0, 1100))
        cust.append((i, name, region, tier, joined.isoformat()))
    con.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", cust)

    # products
    prods = [(i, n, c, p, CATEGORY_WARRANTY[c]) for i, (n, c, p) in enumerate(PRODUCTS, 1)]
    con.executemany("INSERT INTO products VALUES (?,?,?,?,?)", prods)
    price = {p[0]: p[3] for p in prods}
    cat = {p[0]: p[2] for p in prods}

    today = date(2026, 11, 8)
    start = date(2025, 7, 1)
    span = (today - start).days
    order_id = item_id = ship_id = ticket_id = 0
    orders, items, ships, tickets = [], [], [], []

    for _ in range(300):
        c = rnd.choice(cust)
        cid, _, c_region, tier, _ = c
        order_id += 1
        odate = start + timedelta(days=rnd.randint(0, span - 1))
        region = c_region if rnd.random() < 0.85 else rnd.choice(list(REGION_SLA))
        age = (today - odate).days

        if rnd.random() < 0.04:
            status = "Cancelled"
        elif age < 3:
            status = "Processing"
        elif age < 8 and rnd.random() < 0.5:
            status = "Shipped"
        else:
            status = "Delivered"
        orders.append((order_id, cid, odate.isoformat(), status, region))

        # items
        for pid in rnd.sample(list(price), rnd.randint(1, 4)):
            big = cat[pid] in ("Stationery", "Breakroom") and rnd.random() < 0.45
            qty = rnd.choice([60, 80, 120, 150, 300]) if big else rnd.randint(1, 25)
            disc = volume_pct(qty) + TIER_EXTRA_DISCOUNT[tier]
            disc = min(disc, 20)
            item_id += 1
            items.append((item_id, order_id, pid, qty, price[pid], float(disc)))

        # shipment
        if status in ("Shipped", "Delivered"):
            shipped = next_business_day(odate + timedelta(days=1))
            sla = max(1, REGION_SLA[region] - TIER_SLA_REDUCTION[tier])
            carrier = rnd.choice(CARRIERS)
            late_roll = rnd.random()
            if late_roll < 0.16:                       # late
                extra = rnd.choices([1, 2, 3, 4, 5, 6, 7, 9], [20, 18, 14, 12, 10, 8, 5, 3])[0]
                transit = sla + extra
            else:
                transit = max(1, sla - rnd.choice([0, 0, 1]))
            delivered = add_business_days(shipped, transit)
            ship_id += 1
            if status == "Delivered" and delivered <= today:
                ships.append((ship_id, order_id, shipped.isoformat(), delivered.isoformat(), carrier, sla, transit))
            elif status == "Delivered":
                status = "Shipped"
                orders[-1] = (order_id, cid, odate.isoformat(), "Shipped", region)
                ships.append((ship_id, order_id, shipped.isoformat(), None, carrier, sla, None))
            else:
                ships.append((ship_id, order_id, shipped.isoformat(), None, carrier, sla, None))

            # tickets linked to late/damaged outcomes
            if ships[-1][3]:
                bday_late = ships[-1][6] - sla
                if bday_late >= 1 and rnd.random() < 0.55:
                    ticket_id += 1
                    pr = "P2" if bday_late >= 3 else "P3"
                    if tier == "Platinum":
                        pr = "P1" if pr == "P2" else "P2"
                    opened = date.fromisoformat(ships[-1][3]) + timedelta(days=rnd.randint(0, 2))
                    resolved = opened + timedelta(days=rnd.randint(1, 4)) if rnd.random() < 0.85 else None
                    tickets.append((ticket_id, cid, order_id, "Late Delivery", pr, opened.isoformat(),
                                    resolved.isoformat() if resolved else None,
                                    f"Delivered {bday_late} business day(s) past SLA."))
                if rnd.random() < 0.06:
                    ticket_id += 1
                    issue = rnd.choice(["Damaged Item", "Damaged Item", "Wrong Item"])
                    opened = date.fromisoformat(ships[-1][3]) + timedelta(days=rnd.randint(0, 6))
                    pr = "P3" if tier != "Platinum" else "P2"
                    resolved = opened + timedelta(days=rnd.randint(1, 5)) if rnd.random() < 0.8 else None
                    tickets.append((ticket_id, cid, order_id, issue, pr, opened.isoformat(),
                                    resolved.isoformat() if resolved else None,
                                    "Customer reported issue with delivery contents."))

    # a few general tickets
    for _ in range(14):
        ticket_id += 1
        c = rnd.choice(cust)
        opened = start + timedelta(days=rnd.randint(0, span - 1))
        issue = rnd.choice(["Billing", "Warranty"])
        pr = "P3" if issue == "Billing" else "P4"
        resolved = opened + timedelta(days=rnd.randint(1, 6))
        tickets.append((ticket_id, c[0], None, issue, pr, opened.isoformat(), resolved.isoformat(),
                        "General account query."))

    con.executemany("INSERT INTO orders VALUES (?,?,?,?,?)", orders)
    con.executemany("INSERT INTO order_items VALUES (?,?,?,?,?,?)", items)
    con.executemany("INSERT INTO shipments VALUES (?,?,?,?,?,?,?)", ships)
    con.executemany("INSERT INTO support_tickets VALUES (?,?,?,?,?,?,?,?)", tickets)
    con.commit()
    for t in ("customers", "products", "orders", "order_items", "shipments", "support_tickets"):
        print(f"  {t}: {con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]} rows")
    con.close()


if __name__ == "__main__":
    print("Generating PDFs ...")
    make_pdfs()
    print(f"  wrote {len(list(DOCS_DIR.glob('*.pdf')))} PDFs to {DOCS_DIR}")
    print("Generating SQLite database ...")
    make_db()
    print(f"  wrote {DB_PATH}")
