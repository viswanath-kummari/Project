import os
import zipfile
import xml.etree.ElementTree as ET

def create_presentation():
    output_filename = "FreshCut_MeatShop_Management_System.pptx"
    
    # 12 slides data
    slides_data = [
        {
            "tag": "PROJECT PRESENTATION & ARCHITECTURE",
            "title": "FRESH CUT – Meat Shop Management System",
            "subtitle": "A Next-Generation Commercial Cloud POS, Weight-Based Inventory Engine & Automated Spoilage Control Platform",
            "cards": [
                ("Viswanath", "Store Owner, System Administrator & Project Architect\n• Full administrative master oversight\n• Catalog, pricing, financials & P&L control"),
                ("Hemanth", "Lead Cashier & Touch POS Operator\n• High-speed touch PIN keypad (PIN: 5678)\n• Fast counter checkout & shift sales lookup"),
                ("Tech & Infrastructure", "Python Flask Backend + Supabase PostgreSQL\n• Vercel Serverless cloud deployment\n• Chart.js real-time analytics & telemetry")
            ],
            "notes": "Hello everyone. Today I am proud to present FRESH CUT, an enterprise-grade cloud management and high-speed POS software engineered specifically for the fresh meat, poultry, and seafood retail sector. I am Viswanath, the project architect and administrator, working alongside Hemanth as our lead POS cashier."
        },
        {
            "tag": "THE PROBLEM STATEMENT",
            "title": "Why Traditional Retail Software Fails Meat Shops",
            "subtitle": "Meat shops operate on perishable goods, continuous weight variations, and rapid price fluctuations.",
            "cards": [
                ("Decimal Weights vs Pieces", "Standard POS software only tracks integer barcodes. Meat shops sell fractional cuts (e.g. 1.345 kg) alongside whole items (e.g. 30 eggs)."),
                ("Unrecorded Shrinkage", "De-boning scraps, fat trimming, and cold-chain temperature shifts cause 5%-12% unrecorded loss, wiping out retail profit margins."),
                ("Peak Rush Bottlenecks", "Sunday morning rushes require checkout speeds under 10 seconds. Complex multi-step supermarket screens create queues and customer churn."),
                ("Strict Regional Compliance", "Regional dietary requirements demand guaranteed isolation (100% zero-beef catalog compliance) and rigorous staff audit logs.")
            ],
            "notes": "Traditional POS software is built for packaged groceries. Meat shops face three unique hurdles: fractional decimal weights, high shrinkage from carcass trimming and cold-chain shelf-life, and extreme Sunday morning counter traffic. FRESH CUT was purpose-built to conquer every one of these pain points."
        },
        {
            "tag": "THE SOLUTION",
            "title": "Unified POS, Inventory & Analytics Engine",
            "subtitle": "A high-speed touch terminal backed by transactional PostgreSQL inventory decrement and automated financial reporting.",
            "cards": [
                ("High-Speed Touch POS", "1-Click quick scale dial buttons (+0.25kg, +0.5kg, +1.0kg), barcode search, simulated UPI QR code generator, and 80mm thermal receipt printing in under 8 seconds."),
                ("Stock Intake & Spoilage Auditing", "Atomic inventory decrement upon checkout, real-time +Add Stock intake modal with quick preset chips, and mandatory 4-reason wastage logging."),
                ("Real-Time P&L & Analytics", "Dynamic Profit & Loss dashboard calculating Revenue minus COGS minus Spoilage = EBITDA, with Chart.js visualizations and 1-click Excel/PDF exports.")
            ],
            "notes": "Our solution provides an integrated tripartite ecosystem: an intuitive touch POS for high-speed counter checkouts, an atomic inventory movement ledger that tracks shrinkage and prevents negative stock, and an automated P&L engine that provides real-time gross and net profit figures as sales occur."
        },
        {
            "tag": "SYSTEM ARCHITECTURE",
            "title": "End-to-End Enterprise Cloud Architecture",
            "subtitle": "Three-tier architecture ensuring clean separation of presentation, business logic, and cloud persistence.",
            "cards": [
                ("1. Presentation Tier (Client)", "• HTML5, CSS3, Modern Bootstrap 5\n• Butcher Crimson & Obsidian Theme\n• Chart.js Interactive Visualizations\n• Touch PIN Keypad & Virtual Scale\n• Ready for iOS & Android Mobile Apps"),
                ("2. Application Tier (Flask API)", "• Python Flask WSGI REST Framework\n• Vercel Serverless Gateway (api/index.py)\n• SQLAlchemy ORM Data Layer\n• RBAC Security & JWT Authorization\n• Pandas Sales & Financial Aggregation"),
                ("3. Database Tier (Supabase)", "• Managed Supabase Cloud PostgreSQL\n• Connection Pooling (pool_pre_ping=True)\n• Atomic Stock Decrement Transactions\n• Zero-Beef Catalog Enforcement\n• Audit Trail for Spoilage & Intake")
            ],
            "notes": "From an architectural standpoint, the system is divided into three scalable tiers: a responsive, mobile-ready HTML5/Bootstrap frontend, a high-throughput Python Flask serverless REST API deployed on Vercel, and a cloud-hosted Supabase PostgreSQL database equipped with connection pooling and atomic transactional guarantees."
        },
        {
            "tag": "TECHNOLOGY STACK",
            "title": "Modern, Reliable & Scalable Technologies",
            "subtitle": "Selected for ultra-fast performance, zero software licensing costs, and seamless cloud deployment.",
            "cards": [
                ("Python 3.10+ & Flask", "Lightweight, high-speed RESTful microservices backend with zero framework overhead and rapid cold-start times on serverless infrastructure."),
                ("Supabase PostgreSQL", "Enterprise ACID transactions, connection resilience, row-level security, and cloud scalability hosted on AWS/Supabase."),
                ("Bootstrap 5 & Vanilla JS", "Clean 60fps animations, zero heavy node_modules build bundlers, instantaneous browser rendering on low-cost POS touch hardware."),
                ("Chart.js & Pandas", "Interactive revenue trend graphs, category distribution doughnuts, and automated server-side P&L financial calculations.")
            ],
            "notes": "We intentionally chose a lean, robust tech stack: Python Flask provides rock-solid backend endpoints, Supabase PostgreSQL ensures data integrity and cloud availability, and clean Bootstrap 5 with Chart.js guarantees lightning-fast counter rendering without JavaScript framework bloat."
        },
        {
            "tag": "MODULE 1: HIGH-SPEED POS",
            "title": "Built for Butcher Counter High-Traffic Rushes",
            "subtitle": "Precision dual-unit billing (KG decimals & Piece counts) with multi-tender payment processing.",
            "cards": [
                ("Dual Unit Precision", "• KG Weight Items: Support precise 3-decimal values (e.g. 1.250 kg Chicken Breast).\n• Piece Items: Whole number quantities for eggs, whole crabs, and quail.\n• Quick dial buttons (+0.25kg, +0.5kg, +1.0kg) for single-tap cart updates."),
                ("Multi-Tender Payments", "• Cash: Tendered amount input with instant change calculation.\n• UPI / QR Code: Interactive dynamic payment modal with sound cue.\n• Card & Credit: Supports customer accounts and split bills."),
                ("Thermal Receipt Engine", "• Formatted for standard 80mm & 58mm thermal printers.\n• Displays Store Name, Viswanath (Admin), Hemanth (Cashier), itemized weights, tax breakdown, and QR verification.")
            ],
            "notes": "Our POS billing counter was designed for maximum speed. Hemanth can select an item, tap the quick dial weight chips, review the live tax calculation, accept cash or UPI via dynamic QR codes, and trigger a formatted 80mm thermal receipt in under 8 seconds."
        },
        {
            "tag": "MODULE 2: INVENTORY CONTROL",
            "title": "Stock Intake & Automated Shrinkage Control",
            "subtitle": "Prevents negative stock, records wholesale intake, and forces accountability on meat trimming loss.",
            "cards": [
                ("+ Add Stock Intake Modal", "• Dedicated stock increment modal with quick presets: +0.5 kg to +50 kg or +5 to +100 pcs.\n• Live projected balance box shows existing stock, incoming delivery, and new balance before committing."),
                ("Spoilage Audit Logging", "• Mandatory loss categorization: Trimming Loss, De-boning Scrap, Cold-Chain Fluctuation, Shelf Expiry.\n• Links wasted weight directly to cost price to deduct from gross profit automatically."),
                ("Real-Time Movement Ledger", "• Every transaction (Sale, Intake, Spoilage, Manual Adjustment) is permanently logged in the movement ledger with timestamp, user ID, and batch reference.")
            ],
            "notes": "Inventory control is where meat shops either thrive or lose money. We introduced an intuitive '+ Add Stock' intake modal that lets managers increment inventory in seconds, while our spoilage logger requires cashiers to categorize meat waste so shrinkage is never hidden."
        },
        {
            "tag": "MODULE 3: SECURITY & RBAC",
            "title": "Role-Based Access Control & Dual Login",
            "subtitle": "Granular privileges separating administrative oversight from cashier billing counters.",
            "cards": [
                ("Viswanath (Store Owner / Admin)", "• FULL MASTER PRIVILEGES\n• Master catalog management (Add/Edit products, pricing, stock)\n• Spoilage review & staff user account creation\n• Complete Financials: Sales Revenue, COGS, Net Profit (EBITDA)\n• 1-click Excel/PDF report generation"),
                ("Hemanth (Lead Cashier)", "• CASHIER OPERATIONAL PRIVILEGES\n• High-speed touch PIN keypad authentication (PIN: 5678)\n• Fast POS billing counter, active product catalog, and weight dials\n• Read-only access to current available stock\n• Blocked from P&L, operating expenses, and system settings"),
                ("Customer Self-Service", "• Built-in public Sign Up / Registration tab\n• Instant JWT token issuance & authenticated session creation\n• Prepares the platform for customer loyalty and online ordering")
            ],
            "notes": "Security is enforced at both the UI and backend route levels. Viswanath has complete master oversight of profit margins and catalog rules, while Hemanth logs in through a fast 4-digit touch keypad designed for quick shift handovers, with unauthorized routes strictly returning HTTP 403 Forbidden."
        },
        {
            "tag": "MODULE 4: BI ANALYTICS",
            "title": "Actionable Telemetry & Financial Insights",
            "subtitle": "Transforming daily counter transactions into executive-level financial intelligence.",
            "cards": [
                ("Daily Sales Velocity", "Interactive 7-day and 30-day Chart.js line charts tracking peak sales hours, counter velocity, and Sunday surge patterns to optimize butchery staffing."),
                ("Category Revenue Share", "Doughnut visualizations showcasing percentage share of Chicken, Mutton, Country Poultry, and Fresh Seafood sales."),
                ("True P&L Breakdown Formula", "Formula: Gross Revenue minus Cost of Goods Sold (COGS) minus Spoilage Loss minus Operating Overhead = Net Operating Result (EBITDA).")
            ],
            "notes": "Our analytics module turns raw receipt data into visual intelligence. Viswanath can immediately see whether Chicken Curry Cut or Tender Mutton is driving the week's revenue, identify peak Sunday shopping hours, and review true net EBITDA after deducting wholesale purchase costs and spoilage."
        },
        {
            "tag": "QUALITY & COMPLIANCE",
            "title": "100% Zero-Beef Catalog & Authentic Media",
            "subtitle": "Engineered specifically to respect regional market preferences and deliver a premium retail experience.",
            "cards": [
                ("Zero-Beef Compliance", "All beef products, seed items, and references were permanently removed from the Supabase PostgreSQL database, routes, and UI to ensure complete market alignment."),
                ("High-Resolution Meat Imagery", "Every product card features appetizing, high-resolution photography for fresh chicken cuts, tender mutton, country poultry, and sea fish cuts."),
                ("Strict Category Hierarchy", "Products are cleanly sorted into Chicken (Curry cut, Boneless, Wings), Mutton (Curry cut, Chops, Keema), Seafood (Prawns, Rohu, Pomfret), and Eggs.")
            ],
            "notes": "In accordance with our strict operational guidelines, the product catalog is 100% zero-beef compliant across database tables, backend routes, and UI components. Furthermore, every product card is paired with high-definition imagery and precise pricing per kilogram."
        },
        {
            "tag": "DEVOPS & DEPLOYMENT",
            "title": "Live Cloud Deployment & Vercel Pipeline",
            "subtitle": "Continuous integration via GitHub connected directly to Vercel Serverless Functions and Supabase Cloud.",
            "cards": [
                ("GitHub Version Control", "• Repository: viswanath-kummari/Project on branch main\n• Automated push triggers instant Vercel redeployment\n• Comprehensive test suite (test_system.py) validating all 7 core subsystems"),
                ("Vercel Serverless Gateway", "• WSGI Entry Point: api/index.py handling all HTTP routes\n• vercel.json rewrites standardizing routing\n• Dynamic connection pooling to Supabase Cloud PostgreSQL with pool_pre_ping resilience")
            ],
            "notes": "The application is fully cloud-deployed. Our GitHub repository is integrated with Vercel's serverless infrastructure. Every commit automatically builds and deploys the application with zero downtime, connected to our managed Supabase cloud database with built-in connection recovery."
        },
        {
            "tag": "CONCLUSION & ROADMAP",
            "title": "Future Expansion & Project Summary",
            "subtitle": "Ready for mobile app expansion, IoT scale integration, and enterprise multi-store franchising.",
            "cards": [
                ("1. Android & iOS Apps", "Our RESTful API architecture is ready for React Native or Flutter mobile apps for remote owner monitoring and on-the-go billing."),
                ("2. IoT Bluetooth Scales", "Direct Web Bluetooth integration with digital weighing scales for automatic weight transmission without manual keyboard entry."),
                ("3. Multi-Branch Franchising", "Centralized warehouse distribution, inter-branch stock transfers, and multi-store consolidated financial reporting.")
            ],
            "notes": "To conclude: FRESH CUT solves real-world operational challenges in meat retailing by merging high-speed POS billing, precise dual-unit weight tracking, atomic inventory intake, and clear financial analytics. Thank you for your time, and Viswanath and Hemanth are now open to any questions!"
        }
    ]

    # Package structure in memory/dict
    files = {}

    # 1. [Content_Types].xml
    content_types = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '  <Default Extension="xml" ContentType="application/xml"/>',
        '  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
        '  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
        '  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
        '  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
    ]
    for i in range(1, len(slides_data) + 1):
        content_types.append(f'  <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
        content_types.append(f'  <Override PartName="/ppt/notesSlides/notesSlide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/>')
    content_types.append('</Types>')
    files["[Content_Types].xml"] = "\n".join(content_types)

    # 2. _rels/.rels
    files["_rels/.rels"] = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>'''

    # 3. ppt/_rels/presentation.xml.rels
    pres_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
        '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
    ]
    for i in range(1, len(slides_data) + 1):
        pres_rels.append(f'  <Relationship Id="rId{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>')
    pres_rels.append('</Relationships>')
    files["ppt/_rels/presentation.xml.rels"] = "\n".join(pres_rels)

    # 4. ppt/presentation.xml
    pres_xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">',
        '  <p:sldMasterIdLst>',
        '    <p:sldMasterId id="2147483648" r:id="rId1"/>',
        '  </p:sldMasterIdLst>',
        '  <p:sldIdLst>'
    ]
    for i in range(1, len(slides_data) + 1):
        pres_xml.append(f'    <p:sldId id="{255+i}" r:id="rId{i+1}"/>')
    pres_xml.extend([
        '  </p:sldIdLst>',
        '  <p:sldSz cx="12192000" cy="6858000" type="screen16x9"/>',
        '  <p:notesSz cx="6858000" cy="9144000"/>',
        '</p:presentation>'
    ])
    files["ppt/presentation.xml"] = "\n".join(pres_xml)

    # 5. ppt/theme/theme1.xml (Dark Obsidian & Butcher Crimson)
    files["ppt/theme/theme1.xml"] = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="FreshCutTheme">
  <a:themeElements>
    <a:clrScheme name="FreshCut">
      <a:dk1><a:srgbClr val="0B0F19"/></a:dk1>
      <a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="111827"/></a:dk2>
      <a:lt2><a:srgbClr val="F3F4F6"/></a:lt2>
      <a:accent1><a:srgbClr val="881337"/></a:accent1>
      <a:accent2><a:srgbClr val="F43F5E"/></a:accent2>
      <a:accent3><a:srgbClr val="059669"/></a:accent3>
      <a:accent4><a:srgbClr val="D97706"/></a:accent4>
      <a:accent5><a:srgbClr val="2563EB"/></a:accent5>
      <a:accent6><a:srgbClr val="9333EA"/></a:accent6>
      <a:hlink><a:srgbClr val="38BDF8"/></a:hlink>
      <a:folHlink><a:srgbClr val="A855F7"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="FreshCutFonts">
      <a:majorFont><a:latin typeface="Segoe UI Semibold"/></a:majorFont>
      <a:minorFont><a:latin typeface="Segoe UI"/></a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="FreshCutFormat">
      <a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>
      <a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>
      <a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
      <a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
</a:theme>'''

    # 6. ppt/slideMasters/slideMaster1.xml
    files["ppt/slideMasters/slideMaster1.xml"] = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:bg>
      <p:bgRef idx="1001">
        <a:schemeClr val="dk1"/>
      </p:bgRef>
    </p:bg>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMap bg1="dk1" tx1="lt1" bg2="dk2" tx2="lt2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst>
    <p:sldLayoutId id="2147483649" r:id="rId1"/>
  </p:sldLayoutIdLst>
</p:sldMaster>'''

    # ppt/slideMasters/_rels/slideMaster1.xml.rels
    files["ppt/slideMasters/_rels/slideMaster1.xml.rels"] = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>'''

    # 7. ppt/slideLayouts/slideLayout1.xml
    files["ppt/slideLayouts/slideLayout1.xml"] = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank">
  <p:cSld name="Blank Layout">
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>'''

    files["ppt/slideLayouts/_rels/slideLayout1.xml.rels"] = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>'''

    # Helper function to generate shape XML
    def make_shape(sp_id, name, x, y, cx, cy, fill_hex, border_hex, paragraphs, is_rounded=False):
        geom = "roundRect" if is_rounded else "rect"
        fill_xml = f'<a:solidFill><a:srgbClr val="{fill_hex}"/></a:solidFill>' if fill_hex else '<a:noFill/>'
        ln_xml = f'<a:ln w="12700"><a:solidFill><a:srgbClr val="{border_hex}"/></a:solidFill></a:ln>' if border_hex else '<a:ln><a:noFill/></a:ln>'
        
        paras_xml = []
        for p in paragraphs:
            text = p.get("text", "")
            size = p.get("size", 1400)
            bold = ' b="1"' if p.get("bold", False) else ''
            color = p.get("color", "FFFFFF")
            align = p.get("align", "l")
            
            # escape xml special chars
            text_clean = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
            
            lines = text_clean.split("\n")
            for line in lines:
                paras_xml.append(f'''<a:p>
  <a:pPr algn="{align}"/>
  <a:r>
    <a:rPr lang="en-US" sz="{size}"{bold}>
      <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
    </a:rPr>
    <a:t>{line}</a:t>
  </a:r>
</a:p>''')
        
        return f'''<p:sp>
  <p:nvSpPr>
    <p:cNvPr id="{sp_id}" name="{name}"/>
    <p:cNvSpPr/>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
    <a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>
    {fill_xml}
    {ln_xml}
  </p:spPr>
  <p:txBody>
    <a:bodyPr vert="horz" lIns="182880" tIns="146304" rIns="182880" bIns="146304"/>
    <a:lstStyle/>
    {''.join(paras_xml)}
  </p:txBody>
</p:sp>'''

    # Build slides
    for i, sdata in enumerate(slides_data, start=1):
        shapes = []
        shape_id = 10
        
        # 1. Dark Background Card
        shape_id += 1
        shapes.append(make_shape(shape_id, "BgCard", 365760, 365760, 11460480, 6126480, "111827", "1F2937", [], is_rounded=True))
        
        # 2. Tag Badge
        shape_id += 1
        shapes.append(make_shape(shape_id, "TagBadge", 609600, 548640, 3800000, 360000, "881337", "F43F5E", [
            {"text": sdata["tag"], "size": 1000, "bold": True, "color": "FDA4AF", "align": "l"}
        ], is_rounded=True))
        
        # 3. Slide Title
        shape_id += 1
        shapes.append(make_shape(shape_id, "SlideTitle", 609600, 960000, 10800000, 650000, None, None, [
            {"text": sdata["title"], "size": 2600, "bold": True, "color": "FFFFFF", "align": "l"}
        ]))
        
        # 4. Slide Subtitle
        shape_id += 1
        shapes.append(make_shape(shape_id, "SlideSubtitle", 609600, 1610000, 10800000, 480000, None, None, [
            {"text": sdata["subtitle"], "size": 1300, "bold": False, "color": "9CA3AF", "align": "l"}
        ]))
        
        # 5. Content Cards Grid
        cards = sdata["cards"]
        n_cards = len(cards)
        top_y = 2250000
        card_h = 3450000
        
        if n_cards == 2:
            card_w = 5100000
            spacing = 400000
            start_x = 750000
            for c_idx, (ctitle, cdesc) in enumerate(cards):
                cx = start_x + c_idx * (card_w + spacing)
                shape_id += 1
                shapes.append(make_shape(shape_id, f"CardBg{c_idx}", cx, top_y, card_w, card_h, "1F2937", "374151", [
                    {"text": ctitle, "size": 1600, "bold": True, "color": "F43F5E", "align": "l"},
                    {"text": "", "size": 800},
                    {"text": cdesc, "size": 1250, "bold": False, "color": "E5E7EB", "align": "l"}
                ], is_rounded=True))
        elif n_cards == 3:
            card_w = 3380000
            spacing = 330000
            start_x = 609600
            accent_colors = ["F43F5E", "10B981", "38BDF8"]
            for c_idx, (ctitle, cdesc) in enumerate(cards):
                cx = start_x + c_idx * (card_w + spacing)
                accent = accent_colors[c_idx % len(accent_colors)]
                shape_id += 1
                shapes.append(make_shape(shape_id, f"CardBg{c_idx}", cx, top_y, card_w, card_h, "1F2937", "374151", [
                    {"text": ctitle, "size": 1500, "bold": True, "color": accent, "align": "l"},
                    {"text": "", "size": 800},
                    {"text": cdesc, "size": 1200, "bold": False, "color": "D1D5DB", "align": "l"}
                ], is_rounded=True))
        elif n_cards == 4:
            card_w = 2500000
            spacing = 260000
            start_x = 609600
            accent_colors = ["F43F5E", "F59E0B", "38BDF8", "A855F7"]
            for c_idx, (ctitle, cdesc) in enumerate(cards):
                cx = start_x + c_idx * (card_w + spacing)
                accent = accent_colors[c_idx % len(accent_colors)]
                shape_id += 1
                shapes.append(make_shape(shape_id, f"CardBg{c_idx}", cx, top_y, card_w, card_h, "1F2937", "374151", [
                    {"text": ctitle, "size": 1400, "bold": True, "color": accent, "align": "l"},
                    {"text": "", "size": 800},
                    {"text": cdesc, "size": 1150, "bold": False, "color": "D1D5DB", "align": "l"}
                ], is_rounded=True))
        
        # 6. Footer Note
        shape_id += 1
        shapes.append(make_shape(shape_id, "Footer", 609600, 5950000, 10800000, 350000, None, None, [
            {"text": f"FRESH CUT • Slide {i} of {len(slides_data)}  |  Admin: Viswanath  •  Cashier: Hemanth", "size": 950, "bold": False, "color": "6B7280", "align": "r"}
        ]))

        # Slide XML
        slide_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      {''.join(shapes)}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''
        files[f"ppt/slides/slide{i}.xml"] = slide_xml
        
        # Slide rels
        files[f"ppt/slides/_rels/slide{i}.xml.rels"] = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide{i}.xml"/>
</Relationships>'''

        # Notes slide
        notes_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:notes xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      {make_shape(2, "NotesBody", 457200, 3048000, 5943600, 5029200, None, None, [
          {"text": "PRESENTER SCRIPT FOR VISWANATH:", "size": 1300, "bold": True, "color": "881337"},
          {"text": "", "size": 600},
          {"text": sdata["notes"], "size": 1200, "bold": False, "color": "111827"}
      ])}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:notes>'''
        files[f"ppt/notesSlides/notesSlide{i}.xml"] = notes_xml
        
        files[f"ppt/notesSlides/_rels/notesSlide{i}.xml.rels"] = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="../slides/slide{i}.xml"/>
</Relationships>'''

    # Write to zip (.pptx)
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, content in files.items():
            zf.writestr(path, content.encode("utf-8"))
            
    print(f"SUCCESS: Successfully generated {output_filename} ({len(slides_data)} slides)")

if __name__ == "__main__":
    create_presentation()
