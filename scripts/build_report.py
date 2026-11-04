"""AI-assisted report and diagram, built only from saved actual execution evidence.
Requires reportlab. Run after results/execution_evidence.json has been verified.
"""
from pathlib import Path
import json, textwrap
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'docs'; DOC.mkdir(exist_ok=True)
E=json.loads((ROOT/'results/execution_evidence.json').read_text(encoding='utf-8'))
NAVY=colors.HexColor('#17324D'); TEAL=colors.HexColor('#087E8B')
PALE=colors.HexColor('#EFF5F8'); GRAY=colors.HexColor('#536471'); LINE=colors.HexColor('#CBD5DF')

def draw_diagram():
    c=canvas.Canvas(str(DOC/'CA3_Database_Diagram.pdf'),pagesize=landscape(A4))
    c.setTitle('CA3 Group 6 - JSONB and Vector Database Diagram')
    c.setAuthor('Group 6 working draft; AI assistance disclosed')
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold',21); c.drawString(32,558,'Streaming catalogue and activity database')
    c.setFillColor(GRAY); c.setFont('Helvetica',10); c.drawString(32,540,'Group 6  |  PostgreSQL 18 + pgvector  |  Physical foreign keys shown with solid lines')
    def box(x,y,w,h,title,rows,notes=''):
        c.setStrokeColor(LINE); c.setFillColor(colors.white); c.roundRect(x,y,w,h,6,fill=1,stroke=1)
        c.setFillColor(NAVY); c.roundRect(x,y+h-31,w,31,6,fill=1,stroke=0)
        c.rect(x,y+h-31,w,8,fill=1,stroke=0)
        c.setFillColor(colors.white); c.setFont('Helvetica-Bold',12); c.drawString(x+12,y+h-21,title)
        pos=y+h-50
        for name,typ in rows:
            c.setFillColor(NAVY); c.setFont('Helvetica',10); c.drawString(x+12,pos,name)
            c.setFillColor(GRAY); c.setFont('Courier',9); c.drawString(x+w-145,pos,typ); pos-=17
        if notes:
            c.setFillColor(GRAY); c.setFont('Helvetica',8.5)
            for ln in textwrap.wrap(notes,62): c.drawString(x+12,pos-3,ln); pos-=12
    box(32,330,330,187,'users  |  24 rows',[
        ('user_id  [PK]','integer NOT NULL'),('full_name','text NOT NULL'),('email  [UNIQUE]','text NOT NULL'),('country','char(2) NOT NULL'),('plan','text NOT NULL'),('preferences','jsonb NOT NULL')],
        'GIN(preferences). Required favourite_genres array; optional preference keys.')
    box(480,330,330,187,'activity_logs  |  144 rows',[
        ('activity_id  [PK]','bigint NOT NULL'),('user_id  [FK]','integer NOT NULL'),('title_id  [FK]','integer NULL'),('occurred_at','timestamptz NOT NULL'),('event_data','jsonb NOT NULL')],
        'GIN(event_data). Types: play, pause, rate, search. Search has no title; other types require a title.')
    box(480,70,330,207,'titles  |  60 rows',[
        ('title_id  [PK]','integer NOT NULL'),('title','text NOT NULL'),('kind','text NOT NULL'),('release_year','integer NULL'),('genre','text NULL'),('description','text NOT NULL'),('embedding','vector(384) NULL')],
        'HNSW(embedding vector_cosine_ops). All 60 supplied title embeddings are populated.')
    box(32,200,330,108,'search_phrases  |  5 rows',[
        ('phrase_id  [PK]','integer NOT NULL'),('phrase','text NOT NULL'),('embedding','vector(384) NOT NULL')])
    c.setStrokeColor(TEAL); c.setLineWidth(1.5)
    c.line(362,450,480,450)
    c.setFillColor(TEAL); c.setFont('Helvetica-Bold',10)
    c.drawString(369,458,'1'); c.drawRightString(473,458,'0..*')
    c.setFont('Helvetica',8); c.drawCentredString(421,436,'users.user_id')
    c.line(645,330,645,277)
    c.setFont('Helvetica-Bold',10); c.drawString(653,319,'0..* activities'); c.drawString(653,286,'0..1 title')
    c.setDash(4,3); c.line(362,240,428,240); c.line(428,240,428,176); c.line(428,176,480,176); c.setDash()
    c.setFont('Helvetica',8); c.drawCentredString(414,251,'cosine comparison'); c.drawCentredString(415,263,'No foreign key')
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold',11); c.drawString(32,179,'JSONB examples (actual sample payload shapes)')
    c.setFont('Courier',8.4)
    examples=[
        'preferences:',
        '{"favourite_genres":["Mystery","Sci-fi"],',
        ' "subtitle_language":"en"}',
        'event_data (selected fields):',
        '{"event_type":"play","minutes_watched":21}',
        '{"event_type":"pause","paused_at_minute":11}',
        '{"event_type":"rate","stars":2}',
        '{"event_type":"search",',
        ' "query":"a cozy mystery in a small town"}',
    ]
    for n,line in enumerate(examples): c.drawString(32,164-12*n,line)
    c.setFillColor(GRAY); c.setFont('Helvetica',8)
    c.drawString(32,22,'PK = primary key; FK = foreign key. All users and events are fictional. AI-assisted draft; review and adapt before submission.')
    c.save()

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='MainTitleCA3',fontName='Helvetica-Bold',fontSize=27,leading=32,textColor=NAVY,spaceAfter=17))
styles.add(ParagraphStyle(name='HeadingCA3',fontName='Helvetica-Bold',fontSize=17,leading=21,textColor=NAVY,spaceAfter=12))
styles.add(ParagraphStyle(name='SubCA3',fontName='Helvetica-Bold',fontSize=11,leading=15,textColor=TEAL,spaceBefore=12,spaceAfter=7))
styles.add(ParagraphStyle(name='BodyCA3',fontName='Helvetica',fontSize=10.3,leading=15,textColor=NAVY,spaceAfter=9))
styles.add(ParagraphStyle(name='SmallCA3',fontName='Helvetica',fontSize=8.7,leading=12,textColor=GRAY,spaceAfter=7))
styles.add(ParagraphStyle(name='CellCA3',fontName='Helvetica',fontSize=9,leading=12,textColor=NAVY))
styles.add(ParagraphStyle(name='CodeCA3',fontName='Courier',fontSize=7.8,leading=10.5,textColor=NAVY,backColor=PALE,borderPadding=9,spaceBefore=6,spaceAfter=13))

def p(text,style='BodyCA3'): return Paragraph(text,styles[style])
def table(rows,widths,header=True):
    parsed=[[p(escape(str(v)),'CellCA3') for v in row] for row in rows]
    t=Table(parsed,colWidths=widths,hAlign='LEFT',repeatRows=1 if header else 0)
    commands=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,-1),.4,LINE)]
    if header: commands += [('BACKGROUND',(0,0),(-1,0),PALE)]
    t.setStyle(TableStyle(commands)); return t

def footer(c,doc):
    c.setStrokeColor(LINE); c.line(44,40,A4[0]-44,40)
    c.setFont('Helvetica',8); c.setFillColor(GRAY)
    c.drawString(44,27,'DBAD 4000 | Class Activity 3 | Group 6 | AI-assisted working draft')
    c.drawRightString(A4[0]-44,27,str(doc.page))

def build_report():
    s=[]
    s.extend([p('JSONB and<br/>Vector Databases','MainTitleCA3'),p('Class Activity 3  /  Group 6','HeadingCA3'),
        p('A streaming catalogue with flexible preferences, activity events and semantic recommendations.'),Spacer(1,10),
        p('Verified local implementation','SubCA3'),
        table([['Component','Actual result'],['Database','ca3_streaming, existing local PostgreSQL service on port 5432'],['Versions','PostgreSQL 18.6; pgvector 0.8.7'],['Catalogue','60 title embeddings and 5 phrase embeddings; 384 dimensions each'],['Synthetic sample','24 users; 144 events (72 play, 24 pause, 24 rate, 24 search)'],['Validation','Six queries executed; four invalid inserts rejected; no orphan events or missing genre arrays'],['Captured at',E['executed_at_utc']]],[116,391]),
        Spacer(1,16),p('Purpose and scope','SubCA3'),
        p('The design combines relational identifiers and foreign keys with JSONB fields whose attributes vary. The supplied sentence embeddings support ranking titles by meaning, while normal SQL applies activity-based filters.'),
        p('The teacher\'s notebook was executed with its original code and five default phrases. It generated the two SQL files included in this package. All user profiles and activity events were generated deterministically for this exercise; they do not describe real customers.'),
        p('Provenance and review status','SubCA3'),
        p('Codex assisted with environment setup, executing the instructor notebook, schema and query drafting, synthetic data generation, validation, the diagram and this report. This is an attributed working draft for the team to review and adapt. It is not represented as independently authored student work. The contribution table is intentionally deferred at the user\'s request. This work has not been submitted to Brightspace.','SmallCA3'),PageBreak()])
    s += [p('Design decisions','HeadingCA3'),
        table([['Table','Purpose and key choices'],['users','user_id primary key; unique email; country and subscription plan as structured fields. preferences JSONB is an object with a required favourite_genres array.'],['activity_logs','activity_id primary key; user_id references users; title_id references titles. A search event has no title, while play, pause and rate events require one. occurred_at is timestamptz.'],['titles','Instructor catalogue schema with text description and vector(384). Title IDs link activity to the catalogue.'],['search_phrases','Independent phrase IDs, phrase text and vector(384). The phrase vectors are compared with title vectors; there is no foreign key relationship.']],[110,397]),
        p('Why these fields are JSONB','SubCA3'),
        p('Users share a genre array and subtitle language, but only some profiles contain autoplay or nested parental controls. Keeping these optional settings in JSONB allows another preference key without adding a nullable column to every profile. Identity, email, plan and relationships remain structured.'),
        p('Events use different payloads: plays store minutes_watched and device, pauses store paused_at_minute and reason, ratings store stars, and searches store query and results_count. A shared event table keeps one timeline while JSONB holds event-specific fields.'),
        Preformatted('{"favourite_genres":["Mystery","Sci-fi"],\n "subtitle_language":"en"}\n\n{"event_type":"play","minutes_watched":21,"device":"tv"}\n{"event_type":"rate","stars":2}',styles['CodeCA3']),
        p('Constraints and indexes','SubCA3'),
        p('CHECK constraints enforce JSON objects, the required genre array, four supported event types and typed event details. Ratings must be integers from 1 to 5. Two GIN indexes cover preferences and event_data; B-tree indexes support user timelines and title joins. The supplied titles table has a cosine HNSW index. The separate CA3_Database_Diagram.pdf shows types and relationship cardinalities.'),
        p('The four negative tests rejected a missing genre array, an unknown user ID, a rating of 6 and a play with no title. These checks validate the chosen cases, not every possible bad input.','SmallCA3'),PageBreak()]
    explanations=[
        'The @&gt; operator finds profiles whose genre array contains Mystery, even when the object has other keys. Six users match: IDs 1, 8, 9, 16, 17 and 24.',
        'The -&gt;&gt; operator extracts minutes as text, so the query casts it to numeric before summing play events. Fourth Quarter ranks first with 116 recorded minutes from two plays; these are synthetic viewing totals, not unique viewers or a popularity estimate.',
        'jsonb_array_elements_text expands each favourite_genres array into one row per entry. Each of the eight genres appears for six users in this balanced sample; each profile has distinct genre entries, so count(*) equals the user count here.',
        'Phrase 4 is "something scary in the woods". The Woods Remember has the lowest cosine distance (0.602), while the mixed-genre results show that semantic similarity is not a strict horror-genre filter.',
        'Title 3, Crumb &amp; Clue, is the seed and is excluded from its own recommendations. Small Town Spells is the nearest remaining title at 0.572; the distance measures embedding proximity, not a probability that a viewer will like it.',
        'The latest play for user 1 is title 3, and NOT EXISTS removes all three previously played titles (1, 2 and 3). This run returns the same five rows as Query 5 because titles 1 and 2 were not in that top five, and the seed was already excluded there.'
    ]
    for n,(q,explanation) in enumerate(zip(E['results'],explanations),start=1):
        s += [p(f'Query {n:02d}','SubCA3'),p(escape(q['title']),'HeadingCA3')]
        # Wrap only long lines at whitespace; no SQL token is rewritten.
        code='\n'.join('\n'.join(textwrap.wrap(line,width=88,subsequent_indent='    ',replace_whitespace=False,drop_whitespace=True)) if len(line)>88 else line for line in q['sql'].splitlines())
        s += [Preformatted(code,styles['CodeCA3']),p('Actual PostgreSQL output','SubCA3')]
        if n==1:
            fields=['user_id','full_name','plan','favourite_genres']; labels=['User ID','Name','Plan','Favourite genres']; widths=[50,132,90,235]
        elif n==2:
            fields=['title_id','title','total_minutes','play_events']; labels=['Title ID','Title','Minutes','Plays']; widths=[52,295,80,80]
        elif n==3:
            fields=['genre','users_with_genre']; labels=['Genre','Users']; widths=[360,147]
        else:
            fields=['title_id','title','genre','cosine_distance']; labels=['Title ID','Title','Genre','Distance']; widths=[51,237,142,77]
        rows=[labels]
        for row in q['rows']:
            rows.append([', '.join(row[k]) if isinstance(row[k],list) else f"{row[k]:.3f}" if k=='cosine_distance' else row[k] for k in fields])
        s += [table(rows,widths),Spacer(1,13),p(explanation),
              p('Source: results/'+q['slug']+'.csv. Values copied from the captured database execution; row order preserved.','SmallCA3'),PageBreak()]
    s += [p('Validation, tradeoffs and next steps','HeadingCA3'),
        p('What was verified','SubCA3'),
        p('The teacher\'s temporary vector test produced IDs 1, 3 and 2 with cosine distances 0.0000, 0.0085 and 0.2857. All 60 title vectors and five phrase vectors contain 384 values. The database has no orphan events and no missing favourite_genres arrays. All six query outputs were independently checked against the saved input data, including exhaustive cosine ranking over the generated title vectors.'),
        p('What the indexes do','SubCA3'),
        p('JSONB stores a parsed binary representation and supports GIN indexing. General GIN indexes can support the containment predicates used here, but do not automatically speed up every extraction or aggregate. The captured plans used sequential scans for these small JSONB tables. [1, 2]'),
        p('Cosine ranking uses the same model and dimensions for catalogue items and phrases. HNSW supports approximate nearest-neighbour search, with a recall, speed and memory tradeoff. The captured vector queries used sorting over scanned title rows rather than the HNSW index, so the reported top five agrees with exhaustive comparison on this small sample. This run is not a benchmark of HNSW performance. [3]'),
        p('Flexibility and scaling','SubCA3'),
        p('A new optional preference key or extra attribute for an existing event can be stored without adding a table column. A new event type would require changing the deliberate known_event_type and valid_event_details checks. JSONB flexibility therefore still needs an agreed payload contract.'),
        p('For a larger service, proposed next steps are to measure representative queries, consider time partitions and retention for activity, add indexes for frequent extracted attributes, and test vector recall with filters. Partitioning, retention and recall tuning are not implemented in this exercise. Genre names and array-entry types could also receive stronger validation; the current array check only checks that an array exists.'),
        p('References and supplied materials','SubCA3'),
        p('[1] PostgreSQL 18, JSON Types: <link href="https://www.postgresql.org/docs/18/datatype-json.html" color="#087E8B">postgresql.org/docs/18/datatype-json.html</link><br/>[2] PostgreSQL 18, JSON Functions and Operators: <link href="https://www.postgresql.org/docs/18/functions-json.html" color="#087E8B">postgresql.org/docs/18/functions-json.html</link><br/>[3] pgvector official README (installation, cosine distance and indexes): <link href="https://github.com/pgvector/pgvector" color="#087E8B">github.com/pgvector/pgvector</link>','SmallCA3'),
        p('Course sources: Class Activity 3 instructions; Week 9 pgvector installation guide; CA3_Making_the_Embeddings.docx; ca3_make_embeddings_vscode.ipynb; ca3_titles.csv; requirements.txt. The instructor notebook uses sentence-transformers/all-MiniLM-L6-v2, revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41. Its source code and default phrases were preserved.','SmallCA3'),
        p('Reproduction: follow README.md. Exact SQL, per-query CSVs, query plans and validation records are included. Team contribution details remain deferred and must not be inferred from the generated materials.','SmallCA3')]
    doc=SimpleDocTemplate(str(DOC/'CA3_Report_Group6.pdf'),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=43,bottomMargin=54,title='CA3 JSONB and Vector Databases - Group 6',author='Group 6 working draft; AI assistance disclosed')
    doc.build(s,onFirstPage=footer,onLaterPages=footer)

if __name__=='__main__':
    draw_diagram(); build_report()
    print('Created CA3_Database_Diagram.pdf and CA3_Report_Group6.pdf from actual database evidence.')
