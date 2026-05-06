import sqlite3
import os
import secrets
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nda.db')

TEMPLATES = [
    {'id': 1,  'name': 'Startup Mutual NDA',          'category': 'startup',      'color': '#7c3aed', 'description': 'Clean, founder-friendly mutual NDA for early-stage discussions'},
    {'id': 2,  'name': 'Corporate One-Way NDA',        'category': 'corporate',    'color': '#1d4ed8', 'description': 'Formal one-directional agreement for corporate disclosures'},
    {'id': 3,  'name': 'Freelance Developer NDA',      'category': 'freelance',    'color': '#0891b2', 'description': 'Tailored for software developers and technical contractors'},
    {'id': 4,  'name': 'Healthcare Confidentiality',   'category': 'healthcare',   'color': '#059669', 'description': 'HIPAA-aware NDA for healthcare organizations and providers'},
    {'id': 5,  'name': 'Financial Services NDA',       'category': 'finance',      'color': '#d97706', 'description': 'Comprehensive NDA for banking, investment, and financial data'},
    {'id': 6,  'name': 'Software Development NDA',     'category': 'technology',   'color': '#7c3aed', 'description': 'IP-focused NDA for software development partnerships'},
    {'id': 7,  'name': 'Employee Confidentiality',     'category': 'employment',   'color': '#dc2626', 'description': 'Employment-context NDA for staff and onboarding'},
    {'id': 8,  'name': 'Vendor & Supplier NDA',        'category': 'supply-chain', 'color': '#0891b2', 'description': 'B2B supply chain and vendor relationship NDA'},
    {'id': 9,  'name': 'Research Partnership NDA',     'category': 'research',     'color': '#059669', 'description': 'Academic and R&D collaboration confidentiality agreement'},
    {'id': 10, 'name': 'Real Estate NDA',              'category': 'real-estate',  'color': '#b45309', 'description': 'Property transactions, development, and brokerage NDA'},
    {'id': 11, 'name': 'Marketing Agency NDA',         'category': 'marketing',    'color': '#be185d', 'description': 'Campaign strategies, brand data, and marketing NDA'},
    {'id': 12, 'name': 'Creative Services NDA',        'category': 'creative',     'color': '#7c3aed', 'description': 'Design, creative work, and artistic collaboration NDA'},
    {'id': 13, 'name': 'Manufacturing & Trade Secrets','category': 'manufacturing','color': '#374151', 'description': 'Protecting formulas, processes, and manufacturing IP'},
    {'id': 14, 'name': 'Legal Services NDA',           'category': 'legal',        'color': '#1e3a5f', 'description': 'Law firm and legal advisory confidentiality agreement'},
    {'id': 15, 'name': 'Technology Transfer NDA',      'category': 'technology',   'color': '#0891b2', 'description': 'Patent licensing and technology transfer protection'},
    {'id': 16, 'name': 'Investment & Venture Capital', 'category': 'investment',   'color': '#d97706', 'description': 'Investor, VC, and fundraising due-diligence NDA'},
    {'id': 17, 'name': 'Merger & Acquisition NDA',    'category': 'corporate',    'color': '#1d4ed8', 'description': 'M&A due diligence and transaction confidentiality'},
    {'id': 18, 'name': 'Product Development NDA',      'category': 'product',      'color': '#dc2626', 'description': 'New product R&D, prototypes, and launch strategies'},
    {'id': 19, 'name': 'International Business NDA',   'category': 'international','color': '#374151', 'description': 'Cross-border commercial agreements and partnerships'},
    {'id': 20, 'name': 'Consulting Services NDA',      'category': 'consulting',   'color': '#be185d', 'description': 'Advisory, strategy, and consulting engagement NDA'},
]

TEMPLATE_SPECS = {
    1:  {'ci_def': 'business plans, financial projections, technical architecture, product roadmaps, and investor information', 'extra': '', 'default_duration': '2 years', 'style': 'startup-friendly'},
    2:  {'ci_def': 'proprietary business processes, financial data, operational strategies, and internal communications', 'extra': '', 'default_duration': '3 years', 'style': 'formal corporate'},
    3:  {'ci_def': 'source code, algorithms, technical specifications, software architecture, API documentation, and system designs', 'extra': '<h2>6A. Intellectual Property</h2><p>All work product, inventions, and developments created by the Receiving Party in connection with the Confidential Information shall remain the exclusive property of the Disclosing Party unless otherwise agreed in writing.</p>', 'default_duration': '2 years', 'style': 'technical'},
    4:  {'ci_def': 'patient health information (PHI), medical records, clinical data, treatment protocols, and any information subject to HIPAA or applicable healthcare privacy laws', 'extra': '<h2>6A. HIPAA Compliance</h2><p>To the extent applicable, the Receiving Party agrees to comply with the Health Insurance Portability and Accountability Act (HIPAA) and any other applicable health information privacy regulations in handling Confidential Information.</p>', 'default_duration': '5 years', 'style': 'compliance-heavy'},
    5:  {'ci_def': 'financial statements, investment strategies, trading algorithms, client portfolios, regulatory filings, and non-public market information', 'extra': '<h2>6A. Regulatory Compliance</h2><p>The Receiving Party acknowledges that the Confidential Information may be subject to securities laws, banking regulations, and other financial regulatory requirements, and agrees to comply with all applicable regulations.</p>', 'default_duration': '5 years', 'style': 'regulatory'},
    6:  {'ci_def': 'source code, software specifications, system architectures, database schemas, APIs, proprietary algorithms, and technical documentation', 'extra': '<h2>6A. IP Assignment</h2><p>Any improvements, modifications, or derivative works created based on the Confidential Information shall remain the sole property of the Disclosing Party.</p>', 'default_duration': '3 years', 'style': 'technical'},
    7:  {'ci_def': 'business strategies, client lists, employee information, compensation data, internal processes, and operational procedures', 'extra': '<h2>6A. Post-Employment Obligations</h2><p>The obligations under this Agreement shall survive termination of employment and continue for the duration specified herein.</p>', 'default_duration': '2 years', 'style': 'employment'},
    8:  {'ci_def': 'pricing structures, supply chain logistics, manufacturing specifications, quality standards, and vendor relationship terms', 'extra': '', 'default_duration': '3 years', 'style': 'commercial'},
    9:  {'ci_def': 'research methodologies, unpublished findings, experimental data, laboratory protocols, grant information, and pre-publication scientific work', 'extra': '<h2>6A. Publication Rights</h2><p>Neither party shall publish, present, or publicly disclose any Confidential Information without prior written consent of the other party. Any co-authored publications shall require mutual approval of content prior to submission.</p>', 'default_duration': '3 years', 'style': 'academic'},
    10: {'ci_def': 'property valuations, financial terms of transactions, inspection reports, buyer/seller identities, and deal structures', 'extra': '', 'default_duration': '2 years', 'style': 'transactional'},
    11: {'ci_def': 'marketing strategies, campaign data, brand guidelines, audience analytics, creative briefs, and client information', 'extra': '', 'default_duration': '2 years', 'style': 'commercial'},
    12: {'ci_def': 'creative concepts, design files, brand strategies, unreleased artwork, client briefs, and creative methodologies', 'extra': '', 'default_duration': '2 years', 'style': 'creative'},
    13: {'ci_def': 'manufacturing processes, trade secrets, formulas, production methods, quality control procedures, and supplier relationships', 'extra': '<h2>6A. Trade Secret Protection</h2><p>The Receiving Party acknowledges that certain Confidential Information constitutes trade secrets under applicable law and agrees to apply the highest standard of protection to such information.</p>', 'default_duration': '5 years', 'style': 'trade-secrets'},
    14: {'ci_def': 'client matters, legal strategies, privileged communications, case files, and attorney-client privileged information', 'extra': '<h2>6A. Privilege Preservation</h2><p>The parties acknowledge that certain Confidential Information may be subject to attorney-client privilege or work product protection, and agree not to take any action that would waive such privilege.</p>', 'default_duration': '5 years', 'style': 'legal-heavy'},
    15: {'ci_def': 'patented and patent-pending inventions, licensed technology, technical know-how, and proprietary processes subject to transfer', 'extra': '<h2>6A. Patent Prosecution</h2><p>Nothing in this Agreement shall be construed as granting any license or rights under any patent, patent application, or other intellectual property right of the Disclosing Party.</p>', 'default_duration': '5 years', 'style': 'legal-heavy'},
    16: {'ci_def': 'financial projections, cap tables, term sheets, investor materials, due diligence documents, and non-public company information', 'extra': '<h2>6A. Securities Law Compliance</h2><p>The Receiving Party acknowledges that the Confidential Information may constitute material non-public information under applicable securities laws and agrees not to trade in any securities based on such information.</p>', 'default_duration': '3 years', 'style': 'investment'},
    17: {'ci_def': 'financial statements, due diligence materials, merger terms, acquisition targets, valuation reports, and transaction structures', 'extra': '<h2>6A. Standstill Provision</h2><p>During the term of this Agreement, the Receiving Party shall not, directly or indirectly, acquire or seek to acquire any securities or assets of the Disclosing Party without prior written consent.</p>', 'default_duration': '3 years', 'style': 'legal-heavy'},
    18: {'ci_def': 'product designs, prototype specifications, market research, launch strategies, and pre-release product information', 'extra': '', 'default_duration': '3 years', 'style': 'product'},
    19: {'ci_def': 'cross-border business strategies, import/export data, international partner information, and multi-jurisdictional commercial terms', 'extra': '<h2>6A. Governing Jurisdiction</h2><p>The parties acknowledge that this Agreement may be subject to multiple jurisdictions and agree to comply with all applicable laws in each jurisdiction where the Confidential Information is disclosed or used.</p>', 'default_duration': '3 years', 'style': 'international'},
    20: {'ci_def': 'strategic recommendations, client analysis, proprietary frameworks, engagement deliverables, and client relationship information', 'extra': '', 'default_duration': '2 years', 'style': 'professional-services'},
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            color TEXT,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS ndas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            public_id TEXT UNIQUE NOT NULL,
            party_a TEXT NOT NULL,
            party_b TEXT NOT NULL,
            party_a_email TEXT,
            party_b_email TEXT,
            purpose TEXT NOT NULL,
            jurisdiction TEXT,
            template_id INTEGER,
            nda_html TEXT,
            duration TEXT,
            clauses TEXT,
            mutual INTEGER DEFAULT 1,
            signature_a TEXT,
            signature_b TEXT,
            sign_token_a TEXT UNIQUE,
            sign_token_b TEXT UNIQUE,
            status TEXT DEFAULT 'draft',
            ip_a TEXT,
            ip_b TEXT,
            signed_at_a DATETIME,
            signed_at_b DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            signed_at DATETIME
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nda_id INTEGER,
            action TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (nda_id) REFERENCES ndas(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    ''')

    existing = conn.execute('SELECT COUNT(*) FROM templates').fetchone()[0]
    if existing == 0:
        for t in TEMPLATES:
            conn.execute(
                'INSERT OR IGNORE INTO templates (id, name, category, color, description) VALUES (?,?,?,?,?)',
                (t['id'], t['name'], t['category'], t['color'], t['description'])
            )
    conn.commit()
    conn.close()


def get_all_templates():
    conn = get_db()
    rows = conn.execute('SELECT * FROM templates ORDER BY id').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_template(tid):
    conn = get_db()
    row = conn.execute('SELECT * FROM templates WHERE id=?', (tid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_nda(data):
    conn = get_db()
    public_id = uuid.uuid4().hex[:12]
    token_a = secrets.token_urlsafe(24)
    token_b = secrets.token_urlsafe(24)
    c = conn.cursor()
    c.execute('''INSERT INTO ndas
        (public_id, party_a, party_b, party_a_email, party_b_email,
         purpose, jurisdiction, template_id, nda_html, duration, clauses,
         mutual, sign_token_a, sign_token_b, status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,'draft')''', (
        public_id,
        data['party_a'], data['party_b'],
        data.get('party_a_email', ''), data.get('party_b_email', ''),
        data['purpose'], data.get('jurisdiction', 'California, USA'),
        data.get('template_id', 1), data.get('nda_html', ''),
        data.get('duration', '2 years'), data.get('clauses', ''),
        1 if data.get('mutual') else 0,
        token_a, token_b,
    ))
    nda_id = c.lastrowid
    conn.commit()
    conn.close()
    return public_id, nda_id, token_a, token_b


def get_nda(public_id):
    conn = get_db()
    row = conn.execute('SELECT * FROM ndas WHERE public_id=?', (public_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_nda_by_token(token):
    conn = get_db()
    row = conn.execute(
        'SELECT *, CASE WHEN sign_token_a=? THEN "a" WHEN sign_token_b=? THEN "b" END as party '
        'FROM ndas WHERE sign_token_a=? OR sign_token_b=?',
        (token, token, token, token)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def save_signature(nda_id, party, sig_data, ip, user_agent):
    conn = get_db()
    now = datetime.utcnow().isoformat()
    if party == 'a':
        conn.execute(
            'UPDATE ndas SET signature_a=?, ip_a=?, signed_at_a=? WHERE id=?',
            (sig_data, ip, now, nda_id)
        )
    else:
        conn.execute(
            'UPDATE ndas SET signature_b=?, ip_b=?, signed_at_b=? WHERE id=?',
            (sig_data, ip, now, nda_id)
        )
    row = conn.execute('SELECT signature_a, signature_b FROM ndas WHERE id=?', (nda_id,)).fetchone()
    if row['signature_a'] and row['signature_b']:
        conn.execute(
            "UPDATE ndas SET status='signed', signed_at=? WHERE id=?",
            (now, nda_id)
        )
    else:
        conn.execute(
            "UPDATE ndas SET status='partial' WHERE id=? AND status='draft'",
            (nda_id,)
        )
        conn.execute(
            "UPDATE ndas SET status='partial' WHERE id=? AND status='sent'",
            (nda_id,)
        )
    conn.commit()
    conn.close()


def update_nda_status(nda_id, status):
    conn = get_db()
    conn.execute('UPDATE ndas SET status=? WHERE id=?', (status, nda_id))
    conn.commit()
    conn.close()


def log_audit(nda_id, action, ip='', user_agent=''):
    conn = get_db()
    conn.execute(
        'INSERT INTO audit_log (nda_id, action, ip_address, user_agent) VALUES (?,?,?,?)',
        (nda_id, action, ip or '', user_agent or '')
    )
    conn.commit()
    conn.close()


def get_audit_log(public_id):
    conn = get_db()
    nda = conn.execute('SELECT id FROM ndas WHERE public_id=?', (public_id,)).fetchone()
    if not nda:
        conn.close()
        return []
    rows = conn.execute(
        'SELECT * FROM audit_log WHERE nda_id=? ORDER BY timestamp DESC',
        (nda['id'],)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_setting(key, default=None):
    conn = get_db()
    row = conn.execute('SELECT value FROM settings WHERE key=?', (key,)).fetchone()
    conn.close()
    return row['value'] if row else default


def set_setting(key, value):
    conn = get_db()
    conn.execute(
        'INSERT INTO settings (key, value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=?',
        (key, value, value)
    )
    conn.commit()
    conn.close()


def get_all_settings():
    conn = get_db()
    rows = conn.execute('SELECT key, value FROM settings').fetchall()
    conn.close()
    return {r['key']: r['value'] for r in rows}


def generate_nda_html(template_id, data):
    template_id = int(template_id)
    spec = TEMPLATE_SPECS.get(template_id, TEMPLATE_SPECS[1])
    tmpl = get_template(template_id) or TEMPLATES[0]

    party_a = data.get('party_a', '[Party A]')
    party_b = data.get('party_b', '[Party B]')
    purpose = data.get('purpose', '[Purpose]')
    jurisdiction = data.get('jurisdiction', 'California, USA')
    duration = data.get('duration', spec['default_duration'])
    mutual = data.get('mutual', True)
    clauses = data.get('clauses', [])
    today = datetime.utcnow().strftime('%B %d, %Y')

    relationship = 'each other' if mutual else party_b
    direction = f'Both {party_a} and {party_b} may disclose' if mutual else f'{party_a} ("Disclosing Party") may disclose to {party_b} ("Receiving Party")'

    optional_sections = ''
    if 'non_compete' in clauses:
        optional_sections += f'''
<h2>Non-Competition</h2>
<p>During the term of this Agreement and for a period of one (1) year thereafter, {party_b} shall not directly or indirectly engage in any business activity that competes with {party_a}'s primary business operations in connection with the subject matter of this Agreement.</p>'''
    if 'ip_assignment' in clauses:
        optional_sections += f'''
<h2>Intellectual Property Assignment</h2>
<p>Any inventions, developments, or improvements conceived or developed by {party_b} in connection with or derived from the Confidential Information shall be promptly disclosed to {party_a} and shall be the exclusive property of {party_a}. {party_b} hereby assigns all rights, title, and interest in such work product to {party_a}.</p>'''
    if 'non_solicitation' in clauses:
        optional_sections += f'''
<h2>Non-Solicitation</h2>
<p>For a period of two (2) years from the date of this Agreement, {party_b} shall not directly or indirectly solicit, hire, or attempt to hire any employee, contractor, or consultant of {party_a} who was involved in the subject matter of this Agreement.</p>'''
    if 'arbitration' in clauses:
        optional_sections += f'''
<h2>Arbitration</h2>
<p>Any dispute arising out of or relating to this Agreement shall be resolved by binding arbitration in accordance with the rules of the American Arbitration Association (AAA), conducted in {jurisdiction}. The decision of the arbitrator shall be final and binding upon the parties.</p>'''
    if 'return_info' in clauses:
        optional_sections += f'''
<h2>Return of Information</h2>
<p>Upon written request by the Disclosing Party or upon termination of this Agreement, the Receiving Party shall promptly return or certifiably destroy all Confidential Information and any copies, notes, summaries, or extracts thereof. The Receiving Party shall provide written certification of destruction upon request.</p>'''

    html = f'''<div class="nda-document">
  <div class="nda-header">
    <div class="nda-badge">{tmpl['name']}</div>
    <h1>NON-DISCLOSURE AGREEMENT</h1>
    <p class="nda-meta">Dated: {today} &nbsp;|&nbsp; Jurisdiction: {jurisdiction}</p>
  </div>

  <h2>Parties</h2>
  <p>This Non-Disclosure Agreement (this <strong>"Agreement"</strong>) is entered into as of {today} by and between:</p>
  <ul>
    <li><strong>Party A:</strong> {party_a}</li>
    <li><strong>Party B:</strong> {party_b}</li>
  </ul>
  <p>{"This is a mutual agreement, meaning both parties may disclose and receive Confidential Information." if mutual else f"This is a one-way agreement. {party_a} is the Disclosing Party and {party_b} is the Receiving Party."}</p>

  <h2>1. Purpose</h2>
  <p>The parties wish to explore and engage in: <strong>{purpose}</strong>. In connection with this engagement, it may be necessary for one or both parties to disclose certain confidential and proprietary information.</p>

  <h2>2. Definition of Confidential Information</h2>
  <p>"Confidential Information" means any and all non-public information, technical data, or know-how, including but not limited to {spec['ci_def']}, whether disclosed orally, in writing, electronically, or by any other means, that is designated as confidential or that reasonably should be understood to be confidential given the nature of the information and the circumstances of disclosure.</p>

  <h2>3. Obligations of Receiving Party</h2>
  <p>Each party receiving Confidential Information ("Receiving Party") agrees to:</p>
  <ul>
    <li>Hold the Confidential Information in strict confidence using no less than the same degree of care used to protect its own confidential information (but in no event less than reasonable care);</li>
    <li>Not disclose the Confidential Information to any third party without prior written consent of the Disclosing Party;</li>
    <li>Use the Confidential Information solely for evaluating and pursuing {purpose};</li>
    <li>Limit access to Confidential Information to employees, advisors, and representatives who have a legitimate need to know and who are bound by confidentiality obligations no less restrictive than those herein.</li>
  </ul>

  <h2>4. Exclusions from Confidential Information</h2>
  <p>The obligations under this Agreement do not apply to information that:</p>
  <ul>
    <li>Is or becomes publicly known through no breach of this Agreement;</li>
    <li>Was rightfully known by the Receiving Party prior to disclosure without any obligation of confidentiality;</li>
    <li>Is rightfully received from a third party without restriction on disclosure;</li>
    <li>Is independently developed by the Receiving Party without use of or reference to the Confidential Information;</li>
    <li>Is required to be disclosed by applicable law, regulation, or court order, provided the Receiving Party gives prompt written notice to the Disclosing Party.</li>
  </ul>

  <h2>5. Term</h2>
  <p>This Agreement shall remain in effect for a period of <strong>{duration}</strong> from the date first written above, unless earlier terminated by mutual written consent of the parties. The confidentiality obligations herein shall survive expiration or termination of this Agreement.</p>

  {spec['extra']}

  {optional_sections}

  <h2>Remedies</h2>
  <p>The Receiving Party acknowledges that any breach of this Agreement may cause irreparable harm to the Disclosing Party for which monetary damages would be inadequate. Accordingly, the Disclosing Party shall be entitled to seek equitable relief, including injunction and specific performance, in addition to all other remedies available at law or in equity, without the requirement of posting a bond.</p>

  <h2>Governing Law</h2>
  <p>This Agreement shall be governed by and construed in accordance with the laws of {jurisdiction}, without regard to its conflict of law provisions. Each party consents to the exclusive jurisdiction of the courts located in {jurisdiction} for any dispute arising out of or relating to this Agreement.</p>

  <h2>General Provisions</h2>
  <ul>
    <li><strong>Entire Agreement:</strong> This Agreement constitutes the entire agreement between the parties with respect to its subject matter and supersedes all prior discussions and agreements.</li>
    <li><strong>Amendment:</strong> This Agreement may not be amended except by a written instrument signed by both parties.</li>
    <li><strong>Severability:</strong> If any provision of this Agreement is held to be invalid or unenforceable, the remaining provisions shall remain in full force and effect.</li>
    <li><strong>Waiver:</strong> No waiver of any right under this Agreement shall be deemed a waiver of any other right.</li>
    <li><strong>Counterparts:</strong> This Agreement may be executed in counterparts, each of which shall be deemed an original.</li>
  </ul>

  <div class="nda-signature-block">
    <p><strong>IN WITNESS WHEREOF</strong>, the parties have executed this Non-Disclosure Agreement as of the date first written above.</p>
    <div class="sig-columns">
      <div class="sig-col">
        <p><strong>{party_a}</strong></p>
        <div class="sig-line">Signature</div>
        <div class="sig-line">Printed Name</div>
        <div class="sig-line">Title</div>
        <div class="sig-line">Date</div>
      </div>
      <div class="sig-col">
        <p><strong>{party_b}</strong></p>
        <div class="sig-line">Signature</div>
        <div class="sig-line">Printed Name</div>
        <div class="sig-line">Title</div>
        <div class="sig-line">Date</div>
      </div>
    </div>
  </div>
</div>'''
    return html
