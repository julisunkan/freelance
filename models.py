import sqlite3
import os
import secrets
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'freelancer.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            project_title TEXT NOT NULL,
            description TEXT,
            price REAL,
            timeline TEXT,
            status TEXT DEFAULT 'Draft',
            content TEXT,
            views INTEGER DEFAULT 0,
            share_token TEXT UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proposal_id INTEGER NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'Open',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (proposal_id) REFERENCES proposals(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS export_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proposal_id INTEGER NOT NULL,
            format TEXT NOT NULL,
            exported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (proposal_id) REFERENCES proposals(id) ON DELETE CASCADE
        );
    ''')

    if c.execute('SELECT COUNT(*) FROM templates').fetchone()[0] == 0:
        _seed_templates(c)

    conn.commit()
    conn.close()


def _seed_templates(c):
    templates = [
        ("Web Development Proposal", "web", """<h1>Web Development Proposal</h1>
<p>Dear {{ client_name }},</p>
<p>Thank you for considering my web development services for <strong>{{ project_title }}</strong>. I am excited about the opportunity to bring your vision to life with a modern, responsive, and high-performance website.</p>
<h2>Project Overview</h2>
<p>Based on our discussions, I understand you need a professional web presence that effectively communicates your brand and converts visitors into customers.</p>
<h2>What I'll Deliver</h2>
<ul>
<li>Custom responsive design (mobile, tablet, desktop)</li>
<li>SEO-optimized HTML structure</li>
<li>Fast loading speed (&lt;3s)</li>
<li>Cross-browser compatibility</li>
<li>CMS integration for easy content updates</li>
<li>Contact forms and lead capture</li>
</ul>
<h2>Investment</h2>
<p>Total project investment: <strong>${{ price }}</strong></p>
<h2>Next Steps</h2>
<p>I'd love to get started immediately. Please review this proposal and let me know if you have any questions. I look forward to partnering with you on this exciting project.</p>"""),

        ("Mobile App Development", "mobile", """<h1>Mobile App Development Proposal</h1>
<p>Dear {{ client_name }},</p>
<p>I'm thrilled to present this proposal for <strong>{{ project_title }}</strong>. With years of experience in iOS and Android development, I'm confident I can deliver an outstanding mobile experience for your users.</p>
<h2>Project Scope</h2>
<p>This proposal covers the full lifecycle development of your mobile application from concept to App Store/Play Store launch.</p>
<h2>Technical Stack</h2>
<ul>
<li>Cross-platform development (iOS & Android)</li>
<li>RESTful API integration</li>
<li>Push notifications</li>
<li>Offline functionality</li>
<li>Analytics integration</li>
</ul>
<h2>Milestones</h2>
<ol>
<li>Discovery & wireframing</li>
<li>UI/UX design</li>
<li>Development</li>
<li>Testing & QA</li>
<li>Launch & support</li>
</ol>
<h2>Investment</h2>
<p>Total investment: <strong>${{ price }}</strong></p>"""),

        ("Brand Identity Design", "design", """<h1>Brand Identity Design Proposal</h1>
<p>Dear {{ client_name }},</p>
<p>Thank you for reaching out about <strong>{{ project_title }}</strong>. A strong brand identity is the foundation of every successful business, and I'm excited to help you create one that truly represents your vision.</p>
<h2>What's Included</h2>
<ul>
<li>Logo design (3 concepts, 2 revision rounds)</li>
<li>Color palette & typography system</li>
<li>Brand guidelines document</li>
<li>Business card design</li>
<li>Social media profile assets</li>
<li>All files in vector & raster formats</li>
</ul>
<h2>My Process</h2>
<p>I start with a deep discovery session to understand your brand values, target audience, and competitive landscape. From there, I develop concepts that are both visually compelling and strategically aligned.</p>
<h2>Investment</h2>
<p>Total: <strong>${{ price }}</strong></p>
<h2>Let's Build Your Brand</h2>
<p>Ready to stand out? Let's schedule a kickoff call and get started!</p>"""),

        ("Content Writing Services", "content", """<h1>Content Writing Proposal</h1>
<p>Dear {{ client_name }},</p>
<p>Great content is the engine that drives traffic, builds authority, and converts readers into customers. I'm excited to propose my content writing services for <strong>{{ project_title }}</strong>.</p>
<h2>Services Included</h2>
<ul>
<li>SEO-optimized blog posts & articles</li>
<li>Website copy (Home, About, Services, Contact)</li>
<li>Email newsletters</li>
<li>Social media captions</li>
<li>Product descriptions</li>
</ul>
<h2>My Writing Philosophy</h2>
<p>Every piece I write is thoroughly researched, optimized for search engines, and written in your brand's unique voice. I don't believe in filler content — every word earns its place.</p>
<h2>Deliverables & Timeline</h2>
<p>Timeline: {{ timeline }}<br>Investment: <strong>${{ price }}</strong></p>"""),

        ("SEO Optimization Package", "seo", """<h1>SEO Optimization Proposal</h1>
<p>Dear {{ client_name }},</p>
<p>Imagine your website appearing at the top of Google when your ideal customers search for what you offer. That's exactly what I'll help you achieve with <strong>{{ project_title }}</strong>.</p>
<h2>What This Package Includes</h2>
<ul>
<li>Comprehensive SEO audit</li>
<li>Keyword research & strategy</li>
<li>On-page optimization (all pages)</li>
<li>Technical SEO fixes</li>
<li>Link building campaign</li>
<li>Monthly reporting & analytics</li>
</ul>
<h2>Expected Results</h2>
<p>Clients typically see measurable ranking improvements within 60–90 days and significant organic traffic growth within 6 months.</p>
<h2>Investment</h2>
<p>Monthly retainer: <strong>${{ price }}</strong>/month</p>
<p>Minimum commitment: 6 months for optimal results.</p>"""),

        ("Social Media Management", "social", """<h1>Social Media Management Proposal</h1>
<p>Dear {{ client_name }},</p>
<p>Your social media presence is often the first impression potential customers have of your business. Let me make it unforgettable with <strong>{{ project_title }}</strong>.</p>
<h2>Monthly Services</h2>
<ul>
<li>Content calendar creation</li>
<li>20 custom-designed posts/month</li>
<li>Community management (comments & DMs)</li>
<li>Hashtag research & optimization</li>
<li>Monthly performance reports</li>
<li>Paid ad management (optional add-on)</li>
</ul>
<h2>Platforms Covered</h2>
<p>Instagram, Facebook, LinkedIn, Twitter/X, TikTok</p>
<h2>Monthly Investment</h2>
<p><strong>${{ price }}</strong>/month — includes everything listed above.</p>"""),

        ("E-Commerce Development", "ecommerce", """<h1>E-Commerce Development Proposal</h1>
<p>Dear {{ client_name }},</p>
<p>I'm excited to present this proposal for building your online store — <strong>{{ project_title }}</strong>. I'll create a high-converting e-commerce experience that turns browsers into buyers.</p>
<h2>Features & Functionality</h2>
<ul>
<li>Product catalog with filtering & search</li>
<li>Shopping cart & secure checkout</li>
<li>Payment gateway integration (Stripe/PayPal)</li>
<li>Inventory management</li>
<li>Order tracking & email notifications</li>
<li>Customer account portal</li>
<li>Mobile-optimized design</li>
</ul>
<h2>Post-Launch Support</h2>
<p>30 days of free bug fixes and support after launch.</p>
<h2>Total Investment</h2>
<p><strong>${{ price }}</strong> — payment plan available.</p>"""),

        ("UI/UX Design Services", "uxui", """<h1>UI/UX Design Proposal</h1>
<p>Dear {{ client_name }},</p>
<p>Great design isn't just about aesthetics — it's about creating experiences that delight users and drive business results. I'm excited to bring that expertise to <strong>{{ project_title }}</strong>.</p>
<h2>Design Process</h2>
<ol>
<li><strong>Research:</strong> User interviews, competitive analysis</li>
<li><strong>Strategy:</strong> User personas, journey mapping</li>
<li><strong>Wireframing:</strong> Low-fidelity layouts</li>
<li><strong>Design:</strong> High-fidelity mockups in Figma</li>
<li><strong>Prototype:</strong> Interactive clickable prototype</li>
<li><strong>Handoff:</strong> Developer-ready design specs</li>
</ol>
<h2>Deliverables</h2>
<ul>
<li>Figma design file (full ownership)</li>
<li>Clickable prototype</li>
<li>Design system / component library</li>
<li>Usability test report</li>
</ul>
<h2>Investment</h2>
<p><strong>${{ price }}</strong></p>"""),

        ("Data Analysis & Reporting", "data", """<h1>Data Analysis Proposal</h1>
<p>Dear {{ client_name }},</p>
<p>Data-driven decisions are the backbone of successful businesses. I'm excited to help you unlock the insights hidden in your data with <strong>{{ project_title }}</strong>.</p>
<h2>Scope of Work</h2>
<ul>
<li>Data cleaning & preprocessing</li>
<li>Exploratory data analysis (EDA)</li>
<li>Statistical analysis & modeling</li>
<li>Interactive dashboards (Tableau/Power BI)</li>
<li>Executive summary report</li>
<li>Actionable recommendations</li>
</ul>
<h2>Tools & Technologies</h2>
<p>Python (Pandas, NumPy, Matplotlib), SQL, Tableau/Power BI, Excel</p>
<h2>What You'll Get</h2>
<p>Clear, actionable insights presented in plain language — no jargon, just results.</p>
<h2>Investment</h2>
<p><strong>${{ price }}</strong></p>"""),

        ("Business Consulting", "consulting", """<h1>Business Consulting Proposal</h1>
<p>Dear {{ client_name }},</p>
<p>Thank you for the opportunity to partner with you on <strong>{{ project_title }}</strong>. My consulting approach is practical, results-oriented, and tailored to your unique business context.</p>
<h2>Consulting Areas</h2>
<ul>
<li>Business strategy & planning</li>
<li>Process optimization</li>
<li>Revenue growth strategies</li>
<li>Team structure & culture</li>
<li>Technology roadmapping</li>
</ul>
<h2>Engagement Model</h2>
<p>Weekly strategy sessions + unlimited email/Slack support. I embed myself as a strategic partner, not just an outside advisor.</p>
<h2>Expected Outcomes</h2>
<p>Clients typically see 20–40% efficiency gains and measurable revenue impact within the first quarter.</p>
<h2>Investment</h2>
<p><strong>${{ price }}</strong>/month (3-month minimum engagement)</p>
<h2>Ready to Grow?</h2>
<p>Let's schedule a free 30-minute strategy call to discuss your goals.</p>"""),
    ]
    for name, category, content in templates:
        c.execute('INSERT INTO templates (name, content, category) VALUES (?,?,?)',
                  (name, content, category))


# ── Proposal helpers ──────────────────────────────────────────────

def get_all_proposals(status=None):
    conn = get_db()
    if status:
        rows = conn.execute(
            'SELECT * FROM proposals WHERE status=? ORDER BY created_at DESC', (status,)
        ).fetchall()
    else:
        rows = conn.execute(
            'SELECT * FROM proposals ORDER BY created_at DESC'
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_proposal(pid):
    conn = get_db()
    row = conn.execute('SELECT * FROM proposals WHERE id=?', (pid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_proposal_by_token(token):
    conn = get_db()
    row = conn.execute('SELECT * FROM proposals WHERE share_token=?', (token,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_proposal(data):
    conn = get_db()
    token = secrets.token_urlsafe(16)
    c = conn.cursor()
    c.execute('''INSERT INTO proposals
        (client_name, project_title, description, price, timeline, status, content, share_token)
        VALUES (?,?,?,?,?,?,?,?)''', (
        data['client_name'], data['project_title'], data.get('description', ''),
        data.get('price'), data.get('timeline', ''), data.get('status', 'Draft'),
        data.get('content', ''), token
    ))
    pid = c.lastrowid
    conn.commit()
    conn.close()
    return pid


def update_proposal(pid, data):
    conn = get_db()
    conn.execute('''UPDATE proposals SET
        client_name=?, project_title=?, description=?, price=?, timeline=?,
        status=?, content=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?''', (
        data['client_name'], data['project_title'], data.get('description', ''),
        data.get('price'), data.get('timeline', ''), data.get('status', 'Draft'),
        data.get('content', ''), pid
    ))
    conn.commit()
    conn.close()


def delete_proposal(pid):
    conn = get_db()
    conn.execute('DELETE FROM proposals WHERE id=?', (pid,))
    conn.commit()
    conn.close()


def increment_views(pid):
    conn = get_db()
    conn.execute('UPDATE proposals SET views=views+1 WHERE id=?', (pid,))
    conn.commit()
    conn.close()


def get_stats():
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM proposals').fetchone()[0]
    accepted = conn.execute("SELECT COUNT(*) FROM proposals WHERE status='Accepted'").fetchone()[0]
    sent = conn.execute("SELECT COUNT(*) FROM proposals WHERE status='Sent'").fetchone()[0]
    draft = conn.execute("SELECT COUNT(*) FROM proposals WHERE status='Draft'").fetchone()[0]
    rejected = conn.execute("SELECT COUNT(*) FROM proposals WHERE status='Rejected'").fetchone()[0]
    conn.close()
    rate = round((accepted / total * 100), 1) if total > 0 else 0
    return {'total': total, 'accepted': accepted, 'sent': sent,
            'draft': draft, 'rejected': rejected, 'acceptance_rate': rate}


# ── Template helpers ───────────────────────────────────────────────

def get_all_templates():
    conn = get_db()
    rows = conn.execute('SELECT * FROM templates ORDER BY name').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_template(tid):
    conn = get_db()
    row = conn.execute('SELECT * FROM templates WHERE id=?', (tid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_template(tid, data):
    conn = get_db()
    conn.execute('UPDATE templates SET name=?, content=?, category=? WHERE id=?',
                 (data['name'], data['content'], data.get('category', ''), tid))
    conn.commit()
    conn.close()


# ── Section helpers ───────────────────────────────────────────────

def get_all_sections():
    conn = get_db()
    rows = conn.execute('SELECT * FROM sections ORDER BY name').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_section(sid):
    conn = get_db()
    row = conn.execute('SELECT * FROM sections WHERE id=?', (sid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_section(data):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO sections (name, content) VALUES (?,?)',
              (data['name'], data['content']))
    sid = c.lastrowid
    conn.commit()
    conn.close()
    return sid


def update_section(sid, data):
    conn = get_db()
    conn.execute('UPDATE sections SET name=?, content=? WHERE id=?',
                 (data['name'], data['content'], sid))
    conn.commit()
    conn.close()


def delete_section(sid):
    conn = get_db()
    conn.execute('DELETE FROM sections WHERE id=?', (sid,))
    conn.commit()
    conn.close()


# ── Report helpers ─────────────────────────────────────────────────

def create_report(proposal_id, reason):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO reports (proposal_id, reason) VALUES (?,?)', (proposal_id, reason))
    rid = c.lastrowid
    conn.commit()
    conn.close()
    return rid


def get_all_reports(status=None):
    conn = get_db()
    if status:
        rows = conn.execute('''SELECT r.*, p.project_title, p.client_name
            FROM reports r JOIN proposals p ON r.proposal_id=p.id
            WHERE r.status=? ORDER BY r.created_at DESC''', (status,)).fetchall()
    else:
        rows = conn.execute('''SELECT r.*, p.project_title, p.client_name
            FROM reports r JOIN proposals p ON r.proposal_id=p.id
            ORDER BY r.created_at DESC''').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_report_status(rid, status):
    conn = get_db()
    conn.execute('UPDATE reports SET status=? WHERE id=?', (status, rid))
    conn.commit()
    conn.close()


# ── Settings helpers ───────────────────────────────────────────────

def get_setting(key, default=None):
    conn = get_db()
    row = conn.execute('SELECT value FROM settings WHERE key=?', (key,)).fetchone()
    conn.close()
    return row['value'] if row else default


def set_setting(key, value):
    conn = get_db()
    conn.execute('INSERT INTO settings (key, value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=?',
                 (key, value, value))
    conn.commit()
    conn.close()


def get_all_settings():
    conn = get_db()
    rows = conn.execute('SELECT key, value FROM settings').fetchall()
    conn.close()
    return {r['key']: r['value'] for r in rows}


# ── Export history ─────────────────────────────────────────────────

def log_export(proposal_id, fmt):
    conn = get_db()
    conn.execute('INSERT INTO export_history (proposal_id, format) VALUES (?,?)', (proposal_id, fmt))
    conn.commit()
    conn.close()


def get_export_history(proposal_id):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM export_history WHERE proposal_id=? ORDER BY exported_at DESC', (proposal_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
