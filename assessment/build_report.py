"""Build the single-PDF case-study submission from the recorded project evidence."""
from pathlib import Path
from xml.sax.saxutils import escape
import argparse
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable, KeepTogether
from PIL import Image as PILImage

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
EVIDENCE = ROOT / 'evidence'
PR = 'https://github.com/rakamindev/ai-interview-platform/pull/192'
FORK = 'https://github.com/dixonfrederick/ai-interview-platform'
BRANCH = FORK + '/tree/feat/reliable-assessment-review'
VIDEO = FORK + '/releases/download/case-study-review-v1/review-walkthrough.mp4'
CI = FORK + '/actions?query=branch%3Afeat%2Freliable-assessment-review'
FAULT = FORK + '/commit/1ca12dc1551e52ad0c2d99a6e85a1cca8e93c0ec'
REVERT = FORK + '/commit/1426ef547306b542d7d2a1cad62bc5bf969ba5de'
TEAL = colors.HexColor('#0F6E70')
INK = colors.HexColor('#172B3A')
MUTED = colors.HexColor('#526473')
LINE = colors.HexColor('#D8E2E8')
FONTDIR = REPO / 'api/assets/fonts'
pdfmetrics.registerFont(TTFont('Review', str(FONTDIR / 'Vera.ttf')))
pdfmetrics.registerFont(TTFont('ReviewBold', str(FONTDIR / 'VeraBd.ttf')))
pdfmetrics.registerFontFamily('Review', normal='Review', bold='ReviewBold', italic='Review', boldItalic='ReviewBold')
styles = {
 'body': ParagraphStyle('body', fontName='Review', fontSize=10, leading=14.5, textColor=INK, spaceAfter=9, splitLongWords=True),
 'small': ParagraphStyle('small', fontName='Review', fontSize=8.3, leading=12, textColor=MUTED, spaceAfter=7, splitLongWords=True),
 'h1': ParagraphStyle('h1', fontName='ReviewBold', fontSize=24, leading=30, textColor=INK, spaceAfter=14),
 'h2': ParagraphStyle('h2', fontName='ReviewBold', fontSize=14, leading=19, textColor=TEAL, spaceBefore=10, spaceAfter=8),
 'label': ParagraphStyle('label', fontName='ReviewBold', fontSize=9, leading=13, textColor=TEAL, spaceAfter=10),
 'lead': ParagraphStyle('lead', fontName='Review', fontSize=14, leading=21, textColor=INK, spaceAfter=16),
 'cell': ParagraphStyle('cell', fontName='Review', fontSize=8.5, leading=12, textColor=INK),
 'cellhead': ParagraphStyle('cellhead', fontName='ReviewBold', fontSize=8.5, leading=12, textColor=colors.white),
}
story = []

def p(text, style='body'):
    return Paragraph(text, styles[style])

def add(text, style='body'):
    story.append(p(text, style))

def link(label, url):
    return f'<link href="{escape(url, {chr(34): "&quot;"})}" color="#0F6E70"><u>{escape(label)}</u></link>'

def heading(step, title):
    if story: story.append(PageBreak())
    add(step, 'label'); add(title, 'h1')

def table(headers, rows, widths):
    cells = [[p(escape(str(c)), 'cellhead') for c in headers]]
    cells += [[p(str(c), 'cell') for c in row] for row in rows]
    t = Table(cells, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([
      ('BACKGROUND', (0,0), (-1,0), TEAL), ('VALIGN',(0,0),(-1,-1),'TOP'),
      ('LEFTPADDING',(0,0),(-1,-1),8), ('RIGHTPADDING',(0,0),(-1,-1),8),
      ('TOPPADDING',(0,0),(-1,-1),8), ('BOTTOMPADDING',(0,0),(-1,-1),8),
      ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, colors.HexColor('#F4F8F9')]),
      ('LINEBELOW',(0,0),(-1,0),0.5,TEAL), ('LINEBELOW',(0,1),(-1,-1),0.4,LINE),
    ]))
    story.append(t); story.append(Spacer(1,10))

class Screenshot(Flowable):
    def __init__(self, filename, width, height, top=0):
        Flowable.__init__(self)
        self.file = EVIDENCE / filename
        self.width, self.height, self.top = width, height, top
    def draw(self):
        iw, ih = PILImage.open(self.file).size
        scale = self.width / iw
        self.canv.saveState()
        clip = self.canv.beginPath(); clip.rect(0,0,self.width,self.height)
        self.canv.clipPath(clip, stroke=0, fill=0)
        self.canv.drawImage(str(self.file), 0, self.height-ih*scale+self.top*scale,
          width=self.width, height=ih*scale, mask='auto')
        self.canv.restoreState()
        self.canv.setStrokeColor(LINE); self.canv.rect(0,0,self.width,self.height,stroke=1,fill=0)

def source_image(filename):
    return link('Open the full-resolution screenshot', FORK + '/blob/feat/reliable-assessment-review/assessment/evidence/' + filename)

heading('FULLSTACK PRODUCT ENGINEER CASE STUDY', 'Evidence-based fit/gap review')
add('Dixon Frederick', 'h2')
add('Prepared 25 October 2026 · Asia/Jakarta (WIB)<br/>Repository baseline: b836d02f45c6300b238b98ad50e66ead706723b6', 'small')
add('A recruiter should be able to inspect the benchmark, evidence, and rating source behind every comparison. Missing evidence must remain distinct from a demonstrated skill gap.', 'lead')
table(['Submission artifact', 'Access'], [
 ['Open upstream pull request', link('PR #192: evidence-based fit/gap review', PR)],
 ['Implementation and written evidence', link('Feature branch and assessment folder', BRANCH)],
 ['Video demonstration', link('3 minute 30 second captioned walkthrough (MP4)', VIDEO)],
 ['Continuous integration', link('GitHub Actions: review integrity checks', CI)],
 ['Seeded fault and recovery', link('Deliberate fault commit', FAULT) + ' · ' + link('Revert commit', REVERT)],
], [162, 337])
add('What ships', 'h2')
add('One coherent fullstack review workflow: correct required levels, explicit unassessed requirements, preserved human-review provenance, deterministic comparisons, durable refresh/retry states, tenant ownership checks, and PDF/JSON export parity. AI portfolio responses are validated and saved atomically without discarding human reviews.')
add('Recorded verification', 'h2')
add('<b>61 backend examples</b>, <b>11 frontend tests</b>, <b>4 browser regression tests</b>, a recorded real browser flow, an automated mobile accessibility scan, and migration down/up with existing rows. The seeded arithmetic fault caused <b>28 of 35 comparison examples to fail</b> before it was reverted.')
add('Evidence boundaries', 'h2')
add('All candidate names, notes, quotes, and accounts shown are synthetic fixtures. UI fault simulations are labeled. No live Gemini interview, production deployment, user interview study, or measured improvement in hiring accuracy is claimed. This report and implementation were prepared with AI assistance; the candidate should review and understand the code before the live technical defense.', 'small')

heading('STEP 1 / SETUP AND LOCAL EXPLORATION', 'Establish a reproducible baseline')
add('Cloned the supplied repository, read both service READMEs and the product wiki, and created a feature branch from main. The stack was retained: Ruby 3.3.2, Rails, PostgreSQL, Redis/Sidekiq, React, TypeScript, and Vite. Docker services isolate this exercise from the existing Windows PostgreSQL installation.')
add('The workstation had no native Ruby or Redis. Docker through Ubuntu WSL provided the runtime. Port 5173 was occupied, so this submission uses 5174 for Vite and 3001 for the API. The demo seed is development-only and rerunnable. No provider key is needed for the selected comparison path.')
add('Exploration covered login, assessment list, completed synthetic session, portfolio evidence and human override, vacancy selection, comparison, refresh, transcript, and downloads. API responses and database models were checked against the UI. The original frontend was captured before its replacement; backend lifecycle work was already in progress during that visual reproduction.', 'small')
story.append(Screenshot('before-comparison.png', 499, 360))
story.append(Spacer(1,9))
add('Observed defect: the Required column is blank. The engine emits expected_level, while the table reads required_level. The screenshot uses synthetic data. ' + source_image('before-comparison.png'), 'small')
add('The first frontend regression run failed all three targeted checks: required-level/provenance rendering, missing-rating clarity, and empty requirements. The failure log is preserved in assessment/evidence/frontend-before.txt. This established an observable baseline before the UI fix.')

heading('STEP 2 / CONTEXT AND DOMAIN IMMERSION', 'Design for the reviewer and the candidate')
add('The specification describes an AI-led interview, a portfolio supported by transcript quotes, and a vacancy comparison. Its review step is most useful when it supports a defensible follow-up decision. A numeric delta alone cannot establish culture fit or a hiring verdict.')
table(['Person', 'Job to do', 'Design consequence'], [
 ['Assessor', 'Check behavioral evidence and revise an AI rating.', 'Expose quotes, review notes, original AI level, and effective human level.'],
 ['Recruiter', 'Understand whether observed skills meet the role requirement.', 'Put the required level next to the observed level; count unassessed separately.'],
 ['Hiring manager', 'Identify what needs another conversation.', 'Provide a follow-up filter for gaps, missing evidence, and low-confidence AI ratings.'],
 ['Candidate', 'Receive an accurate and correctable assessment.', 'Do not invent L1 for missing output, silently erase human review, or disclose data across tenants.'],
], [88, 180, 231])
add('Industry interpretation', 'h2')
add('The Indonesian labor-market information published by Kemnaker provides local hiring context. The product decision here is to invest in dependable evidence at the point a recruiter acts, rather than another generated paragraph. This is a reasoned hypothesis, not a market-share or customer-research finding. Narrow-screen readability and incomplete-evidence handling matter for practical review access.')
add('Candidate privacy and UU PDP', 'h2')
add('UU 27/2022 includes rights to correct inaccurate personal data (Article 6), obtain access/copies (Article 7), and object to solely automated decisions with legal or significant effects (Article 10). Articles 35-36 concern security and confidentiality. The design implication is to support human inspection and correction, enforce tenant boundaries, and limit data exposure. Retention, notices, legal bases, provider agreements, and rights-request operations require broader organizational work; this patch does not certify compliance.')
add('Sources inspected 25 October 2026', 'h2')
add(link('PRD 01: evidence, behavioral anchors, and confidence', 'https://github.com/rakamindev/ai-interview-platform/wiki/PRD-01-%E2%80%94-First-Principles:-AI-Interview-Behavior') + '<br/>' + link('PRD 02: end-to-end simulation and review phase', 'https://github.com/rakamindev/ai-interview-platform/wiki/PRD-02-%E2%80%94-Real-Simulation:-End%E2%80%90to%E2%80%90End-Interview') + '<br/>' + link('Kemnaker Pasker ID: official labor-market information', 'https://paskerid.kemnaker.go.id/') + '<br/>' + link('UU 27/2022: official Komdigi text', 'https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/crc32/'), 'small')

heading('STEP 3 / PROBLEM AND GAP TO THE IDEAL', 'Rank problems by the harm they cause')
add('P0 = immediate broad exposure/unusable system; P1 = incorrect assessment or unauthorized disclosure; P2 = recoverable reliability/workflow issue; P3 = minor clarity/polish. These are qualitative engineering priorities, not measured incident probabilities.', 'small')
table(['ID / severity', 'Finding and one-line impact', 'Type / implementation evidence'], [
 ['F1 · P1', 'Required levels disappear at the API/UI seam; reviewers cannot inspect the benchmark behind a gap.', 'Defect: FitGap::Engine and ComparisonTable. Fixed with one expected_level contract.'],
 ['F2 · P1', 'Human-rating provenance is dropped from comparisons; reviewers cannot distinguish AI from assessor judgment.', 'Defect: comparison serialization. Fixed with original AI level, effective level, source, and notes.'],
 ['F3 · P1', 'Child portfolio/skill lookups lack tenant ownership; an authenticated assessor can attempt foreign IDs.', 'Defect: portfolio and override controllers. Fixed with explicit session-tenant joins and vacancy ownership checks.'],
 ['F4 · P2', 'Missing reports are repeatedly queued and failures lack durable state; a reviewer can wait indefinitely or lose a prior report.', 'Defect / missing lifecycle specification. Added state, token, lease, safe errors, and explicit retry.'],
 ['F5 · P1', 'Model ratings are coerced into 1..5, and regeneration deletes old skills before validation; unsupported ratings or lost reviews can result.', 'Defect: portfolio generator. Added strict level validation, atomic writes, and retained human reviews.'],
 ['F6 · P1', 'Narrative requests culture fit and a hiring recommendation from comparison levels without grounding.', 'Missing evidence policy. Deliberate product change: deterministic summary; no culture/hiring inference.'],
 ['F7 · P3', 'Missing evidence is absent from the summary and empty/error/narrow states are incomplete.', 'Defect / missing state design. Added completeness counts, inline evidence, responsive rows, and recovery actions.'],
], [70, 239, 190])
add('Constraint signal raised early', 'h2')
add('External Gemini credentials and live audio are dependencies for the original interview, not for this comparison. The shared tenant/auth assumptions and background-job contract need explicit review. A provider-free comparison and an isolated runtime allow useful work without pretending a live model was exercised. The four-day window supplied by the candidate favors one complete workflow over a platform rewrite.')

heading('STEP 4 / STRATEGY, ACCEPTANCE CRITERIA, TRADE-OFFS', 'Choose a complete improvement within the deadline')
table(['Option', 'Value and cost', 'Maintenance / failure modes / decision'], [
 ['A. Frontend field repair', 'Fastest way to restore required-level visibility.', 'Leaves access control, duplicate work, and stale/lost reports. Rejected as insufficient integrity.'],
 ['B. Deterministic review slice', 'Moderate cost; fixes the API/UI seam, provenance, lifecycle, and tenant access together.', 'Retains the stack. Uses row locks, source digest, tokens, and bounded retry. Selected for coherent impact and reversible data changes.'],
 ['C. Replace the interview engine', 'Potentially broader improvement, substantially greater cost.', 'Expands model, real-time audio, and migration surface beyond the four-day window. Deferred.'],
], [100, 184, 215])
add('Acceptance criteria defined before feature implementation', 'h2')
criteria = [
 'Compare every requirement in stable order, showing expected and effective levels with a signed delta.',
 'Use normalized canonical IDs when supplied. Restrict normalized label fallback to custom skills; ambiguous duplicates remain unassessed.',
 'Missing/invalid ratings produce not_assessed with no numeric delta. Never fabricate L1 by coercion.',
 'Human revisions retain their original AI level, effective level, notes, and review time. Source changes invalidate cached comparisons.',
 'Report, export, override, and background execution enforce portfolio/session and vacancy tenant ownership. Reject missing auth, wrong roles, and foreign IDs.',
 'Persist pending/generating/complete/failed/stale states. Deduplicate active requests and job deliveries; bound lost-job recovery and provide explicit retry.',
 'Preserve the last successful snapshot across refresh failure and partial writes. Block comparison exports while stale or processing.',
 'Keep comparison deterministic and usable without Gemini; no culture-fit inference or autonomous hiring recommendation.',
 'Use an additive reversible migration and test down/up with existing rows. Support loading, empty, error, partial, long-text, responsive, and keyboard states.',
 'Prove behavior with backend/frontend/browser tests, a deliberately seeded and reverted fault, and a documented AI-verification correction.',
]
for i, item in enumerate(criteria, 1): add(f'<b>{i}.</b> {item}', 'small')
add('Assumptions: L1-L5 are ordered levels, not a calibrated interval score; no overall fit percentage is introduced. A complete portfolio may still have unassessed vacancy requirements. A human override is the effective rating until explicitly revised.', 'small')

heading('STEP 5 / ENGINEERING EXECUTION', 'Make state and evidence explicit')
add('The implementation remains in the existing services. FitGap::Snapshot reads ordered requirements, ratings, quotes, summaries, and override provenance. A SHA-256 digest identifies the inputs used for a successful comparison. Canonical identity prevents unrelated same-label skills from matching.')
table(['Lifecycle field', 'Purpose'], [
 ['generation_status', 'pending, generating, complete, failed, or stale; existing rows default to complete but require refresh when no source digest exists.'],
 ['generation_token / requested_at', 'Identifies the active attempt and starts the two-minute recovery lease. Obsolete deliveries do not overwrite a newer request.'],
 ['source_digest', 'Detects changed requirements or review inputs on reads and exports.'],
 ['error_code', 'Safe queue_unavailable, generation_failed, or derived generation_timeout; provider payloads are not persisted here.'],
], [153, 346])
add('Request and worker sequence', 'h2')
add('1. Resolve the authenticated tenant and owned portfolio/vacancy.<br/>2. Lock the portfolio, reuse an active/current report or save a pending token.<br/>3. Commit before enqueueing the Sidekiq job.<br/>4. Worker verifies tenant ownership, locks the same portfolio, and checks the token.<br/>5. Compute all comparisons and atomically save the successful snapshot.<br/>6. A worker exception rolls back partial data, then records a safe failure.')
add('Failure and data safety', 'h2')
add('An enqueue exception persists a failure without deleting the old comparison. A process loss between commit and enqueue is recovered through the two-minute lease and explicit retry; this is the chosen trade-off instead of a transactional outbox. Overrides invalidate snapshots under the same lock. Exports require a current digest. The migration was rolled down and reapplied with an existing report; comparisons and owning rows survived, and legacy reports became stale until refreshed.')
add('Portfolio response validation', 'h2')
add('Missing levels remain absent. Malformed/non-integer/out-of-range levels fail validation instead of becoming L1. Invalid response fragments roll back the entire write. Existing human override records are retained when matching skills are updated, and human-reviewed skills are kept if the provider omits them. Error storage and job retry messages avoid raw provider/transcript contents.')

heading('STEP 5 / FRONTEND EXECUTION', 'Expose the evidence behind the comparison')
add('The visual direction extends the existing light Rakamin teal system. The main hierarchy is completeness first, requirement-by-requirement comparison second, and supporting evidence on demand. Status is conveyed with text as well as color. No invented fit percentage or unsupported hiring verdict is introduced.')
story.append(Screenshot('after-desktop.png', 499, 440))
story.append(Spacer(1,9))
add('Desktop review, cropped to the upper portion of the full-resolution capture. The synthetic example has three assessed requirements out of four. The API skill has required L4, human-reviewed L3, original AI L2, and a one-level gap. ' + source_image('after-desktop.png'), 'small')
add('Every new review control has a tested action: evidence disclosure, follow-up filter, refresh, retry/check-status, PDF/JSON download, portfolio navigation, and transcript navigation. The screen retains previous content while processing and marks it as a previous snapshot.', 'small')

heading('STEP 5 / EDGE STATES AND RESPONSIVE REVIEW', 'Preserve context when evidence or processing is incomplete')
images = Table([[Screenshot('after-mobile.png', 190, 345, top=560), Screenshot('simulated-failed-refresh.png', 291, 345)]], colWidths=[200,299])
images.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0)]))
story.append(images); story.append(Spacer(1,10))
add('<b>Left:</b> cropped detail from the 375-pixel layout; the same comparison becomes stacked readable cells and evidence remains keyboard-operable. <b>Right:</b> explicitly simulated queue-failure response for UI testing; the previous successful report remains visible and export is disabled.', 'small')
add(source_image('after-mobile.png') + ' · ' + source_image('simulated-failed-refresh.png'), 'small')
add('Long and empty states', 'h2')
add('A 320-pixel browser test uses an unbroken long skill label and verifies no document overflow. An empty vacancy shows a clear requirement-setup message. A pending portfolio is not silently treated as a complete assessment. Failed initial loads, refresh requests, and downloads expose an action to recover.')
add('Accessibility evidence', 'h2')
add('Browser tests exercise keyboard activation of evidence and run an axe WCAG A/AA scan on the mobile review. The initial scan found the existing active-navigation text contrast at 3.28:1; a darker teal text color fixed it. The final scoped scan has no reported violations. This is evidence for this tested screen and state, not a whole-product accessibility certification.', 'small')

heading('STEP 5 / VERIFICATION AND AI VERIFICATION MOMENT', 'Show that the checks detect regressions')
table(['Check', 'Recorded result and scope'], [
 ['Backend', '61 examples, 0 failures, including all 25 level pairs, tenant denial, malformed inputs, source matching, provenance, duplicate jobs, safe queue/provider errors, and rollback. Eager loading also passes.'],
 ['Frontend', '11 tests pass across the comparison and page lifecycle. Production TypeScript/Vite build succeeds.'],
 ['Browser', '4 regression tests pass in CI; real API evidence/filter/refresh/download/transcript flow plus narrow-screen, keyboard, accessibility, and labeled state simulations.'],
 ['Migration', 'Existing report survives down/up; owning rows remain, and restored legacy report requires refresh.'],
 ['Dependencies', 'Production npm audit reports 0 advisories. Four inherited moderate development-tool advisories remain in the Tailwind/PostCSS chain; no broad framework upgrade is claimed.'],
], [98, 401])
add('Seeded fault: visible history', 'h2')
add('On a scratch branch, the comparison delta was deliberately changed from subtraction to addition. The focused suite ran 35 examples and reported 28 failures, including boundary pairs and human-rating comparison. The bad line was committed, then reverted. No test assertion was weakened. The submitted feature branch retains the correct subtraction.')
add(link('Deliberate fault: 1ca12dc', FAULT) + ' · ' + link('Revert: 1426ef5', REVERT) + '<br/>Evidence log: assessment/evidence/seeded-fault.txt', 'small')
add('AI verification moment', 'h2')
add('AI initially selected Vitest 3.2.x. npm audit reported critical transitive advisories in tinypool and additional mocker advisories. The choice was checked against package engine/peer requirements and official Vitest documentation, then replaced with Vitest 5.0.5, compatible with Node 22.20 and Vite 6.4.5. Tests were rerun and the lockfile committed. The remaining development-only advisories are documented rather than hidden by an unreviewed major Tailwind upgrade.')
add('A separate CI-only failure exposed the baseline WebSocket constant inflection during eager loading. The constant mapping was corrected and eager loading remained enabled. On Windows, evented file watching also left an old exporter in one Puma process; development Compose now uses polling and one process. These fixes preserve verification rigor instead of disabling checks.', 'small')

heading('STEP 6 / DELIVERY, LIMITS, AND LIVE DEFENSE', 'A reviewable submission with explicit boundaries')
add('Submission artifacts', 'h2')
add(link('Open upstream PR #192', PR) + '<br/>' + link('3:30 captioned video demonstration', VIDEO) + '<br/>' + link('Implementation, runbook, test logs, and screenshots', BRANCH) + '<br/>' + link('CI execution history', CI))
add('The video includes an actual browser recording against the local API/worker, with synthetic fixtures; it is slowed for readability. Queue-failure footage is labeled as a response simulation. It has on-screen explanatory text and no spoken narration. The PDF is the single portal document; external links provide code, proof, and video access.', 'small')
add('Material limits and follow-up work', 'h2')
limits = [
 'The original live microphone/Gemini interview was not exercised against the live service. Provider failure/response validation is tested with controlled clients; the comparison itself makes no model call.',
 'The two-minute lease bounds the commit-to-enqueue gap. A transactional outbox is a later reliability improvement if workload or recovery guarantees justify it.',
 'This patch protects the selected report, export, and override paths. Whole-product auth/WebSocket auditing, retention/deletion rights workflows, and provider privacy contracts remain separate work.',
 'Previously coerced historical AI values cannot be reconstructed without their original raw responses. Existing valid stored levels still require human evidence review.',
 'Override storage retains the current human review, original AI level, reviewer, and time; a complete immutable revision ledger is a possible extension.',
 'No production load, business-time saving, bias/fairness outcome, or hiring-accuracy improvement has been measured. Synthetic acceptance tests establish behavior, not business effectiveness.',
]
for item in limits: add('• ' + item, 'small')
add('Release and rollback', 'h2')
add('Apply the additive migration before the new code. Drain legacy two-argument fit/gap jobs before switching to the new three-argument worker contract. Rollback preserves comparison/portfolio data but removes new lifecycle metadata. The development Compose configuration is local-only and contains documented synthetic credentials; production configuration is outside this deliverable.', 'small')
add('Preparation for the 45-60 minute defense', 'h2')
add('Be ready to trace the expected_level contract, explain nil versus L1, derive a delta for any pair of levels, show a cross-tenant rejection, explain the shared portfolio lock and token, defend the no-culture-inference decision, and demonstrate the seeded test failure and revert. The candidate should understand each change and choose their own explanation before presenting it.', 'small')
add('The hiring dashboard is the deadline source. The candidate reported four days available; the stale August date in the brief was not used to invent a new due date. Final portal upload and any personal presentation remain with the candidate.', 'small')

def chrome(canvas, doc):
    canvas.saveState()
    w,h = A4
    canvas.setFillColor(TEAL); canvas.rect(0,h-8,w,8,fill=1,stroke=0)
    canvas.setFont('Review',8); canvas.setFillColor(MUTED)
    canvas.drawString(48,29,'Dixon Frederick | Rakamin case study | Synthetic data only')
    canvas.drawRightString(w-48,29,str(doc.page))
    canvas.restoreState()

parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True)
args=parser.parse_args()
output=Path(args.output); output.parent.mkdir(parents=True,exist_ok=True)
doc=SimpleDocTemplate(str(output),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=42,bottomMargin=46,
  title='Evidence-based fit/gap review - Dixon Frederick',author='Dixon Frederick (prepared with AI assistance)')
doc.build(story,onFirstPage=chrome,onLaterPages=chrome)
print(output)
