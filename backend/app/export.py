"""Offline browser game and separate printable player/organizer documents."""

import json
from html import escape
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import BaseDocTemplate, Frame, KeepTogether, PageBreak, PageTemplate, Paragraph, Spacer

from .engine import clue_text


def intro(project: dict) -> str:
    scenes = {
        "museum": "The museum doors close at midnight. A hidden trail leads to the Star Diamond.",
        "agent": "A coded transmission has reached headquarters. Follow its trail before the dossier disappears.",
        "library": "An enchanted library has locked its oldest chamber. Follow the clues to recover its lost secret.",
    }
    return f"{project['player_alias']}, {scenes[project['theme']]}"


def _prompt_lines(puzzle: dict) -> list[str]:
    params = puzzle["parameters"]
    lines = [params["story"], params["prompt"]]
    if puzzle["type"] == "cipher":
        lines.append(f"Inscription: {params['ciphertext']}")
    elif puzzle["type"] == "logic_grid":
        lines.append(f"People: {', '.join(params['people'])}.")
        lines.append(f"Objects: {', '.join(params['objects'])}.")
        lines.append(f"Places: {', '.join(params['places'])}.")
        lines.extend(clue_text(clue) for clue in params["clues"])
    elif puzzle["type"] == "sequence":
        lines.extend(f"{left} must happen before {right}." for left, right in params["edges"])
    return lines


def _draw_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D9B56D"))
    canvas.line(42, A4[1] - 45, A4[0] - 42, A4[1] - 45)
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#222844"))
    canvas.drawString(42, 32, "PuzzleMint | Turn Any Occasion Into an Adventure")
    canvas.drawRightString(A4[0] - 42, 32, str(doc.page))
    canvas.restoreState()


def _pdf_document(project: dict, puzzles: list[dict], answer_key: bool) -> bytes:
    buffer = BytesIO()
    document = BaseDocTemplate(buffer, pagesize=A4, leftMargin=48, rightMargin=48, topMargin=65, bottomMargin=52)
    frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    document.addPageTemplates(PageTemplate(id="standard", frames=frame, onPage=_draw_page))
    styles = getSampleStyleSheet()
    styles["Title"].textColor = colors.HexColor("#14182E")
    styles["Heading2"].textColor = colors.HexColor("#222844")
    styles["BodyText"].leading = 16
    styles.add(ParagraphStyle(name="CoverLabel", parent=styles["BodyText"], alignment=TA_CENTER,
        fontName="Helvetica-Bold", fontSize=10, textColor=colors.HexColor("#A27C3A"), spaceAfter=24))
    styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Times-Bold",
        fontSize=32, leading=38, alignment=TA_CENTER))
    if answer_key:
        body = [Paragraph(escape(project["title"]), styles["Title"]), Spacer(1, 16),
            Paragraph("Organizer answer key", styles["BodyText"]), Spacer(1, 20)]
    else:
        body = [Spacer(1, 70), Paragraph("PUZZLEMINT PRESENTS", styles["CoverLabel"]),
            Paragraph(escape(project["title"]), styles["CoverTitle"]), Spacer(1, 28),
            Paragraph(escape(intro(project)), styles["BodyText"]), Spacer(1, 36)]
        body.append(Paragraph("Solve each chamber in order. Write answers before moving on. Keep the answer key with the organizer.", styles["BodyText"]))
        body.append(Spacer(1, 20))
        body.append(Paragraph(f"MADE FOR {escape(project['player_alias']).upper()}  |  {escape(project['occasion']).upper()}  |  {project['duration_minutes']} MINUTES", styles["CoverLabel"]))
        body.append(PageBreak())
    for index, puzzle in enumerate(puzzles, start=1):
        section = [Paragraph(f"{index}. {escape(puzzle['title'])}", styles["Heading2"]), Spacer(1, 8)]
        if answer_key:
            section.append(Paragraph(f"Answer: {escape(puzzle['solution']['answer'])}", styles["BodyText"]))
            section.extend(Paragraph(f"Hint {i}: {escape(hint)}", styles["BodyText"]) for i, hint in enumerate(puzzle["hints"], 1))
        else:
            section.extend(Paragraph(escape(line), styles["BodyText"]) for line in _prompt_lines(puzzle))
            section.extend([Spacer(1, 18), Paragraph("Answer: ______________________________________________", styles["BodyText"])])
        body.append(KeepTogether(section))
        if not answer_key and index < len(puzzles):
            body.append(PageBreak())
        else:
            body.append(Spacer(1, 22))
    if not answer_key:
        body.extend([PageBreak(), Paragraph("Adventure complete", styles["Title"]), Spacer(1, 18), Paragraph(escape(project["final_message"]), styles["BodyText"])])
    document.build(body)
    return buffer.getvalue()


def create_pdf(project: dict, puzzles: list[dict]) -> tuple[bytes, bytes]:
    return _pdf_document(project, puzzles, False), _pdf_document(project, puzzles, True)


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PuzzleMint Adventure</title><style>
:root{font-family:system-ui,Segoe UI,sans-serif;color:#f7f4ee;background:#14182e}*{box-sizing:border-box}
body{margin:0;min-height:100vh}header{padding:24px 5vw;border-bottom:1px solid #424966;display:flex;justify-content:space-between;align-items:center;gap:12px}
.brand{color:#d9b56d;font-weight:800;letter-spacing:.1em}.shell{max-width:850px;margin:auto;padding:36px 24px 90px}
h1{font-family:Georgia,serif;font-size:clamp(34px,6vw,56px);line-height:1.1;margin:0 0 18px}h2{font-family:Georgia,serif;font-size:30px}
p{line-height:1.65;color:#d7dbe8}.eyebrow{color:#d9b56d;text-transform:uppercase;letter-spacing:.14em;font-size:12px;font-weight:800}
.card{background:#222844;border:1px solid #404864;border-radius:18px;padding:28px;margin:24px 0;box-shadow:0 15px 38px #090d2433}
button,input,select{font:inherit}button{background:#19a99b;color:#061a1b;border:0;border-radius:10px;padding:12px 18px;font-weight:750;cursor:pointer;margin:8px 8px 8px 0}
button.secondary{background:#343c5d;color:#f7f4ee}button:disabled{opacity:.5;cursor:not-allowed}button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #d9b56d;outline-offset:3px}
input,select{background:#12172d;border:1px solid #69718b;border-radius:8px;padding:12px;color:#fff;min-width:180px;max-width:100%}
.clue{padding:12px 14px;border-left:3px solid #d9b56d;background:#171d37;margin:9px 0}.status{min-height:24px;font-weight:700}.good{color:#65dab0}.bad{color:#ff969c}
.progress{height:8px;border-radius:8px;background:#3c4562;overflow:hidden}.progress span{display:block;height:100%;background:#19a99b;transition:width .25s}
.row{display:flex;align-items:center;gap:12px;flex-wrap:wrap}.sequence-row{display:flex;align-items:center;justify-content:space-between;border:1px solid #505979;border-radius:8px;padding:4px 8px;margin:8px 0}
table{border-collapse:collapse;width:100%;margin:16px 0}th,td{padding:10px;border-bottom:1px solid #434c68;text-align:left}table select{min-width:100px;width:100%}
@media(max-width:600px){header{padding:16px}.shell{padding:28px 16px}.card{padding:20px}th,td{padding:5px;font-size:14px}table select{min-width:70px}}
@media(prefers-reduced-motion:reduce){.progress span{transition:none}}
body[data-theme="agent"]{background:#0d1a22}body[data-theme="agent"] .card{background:#172c38;border-color:#365665}body[data-theme="agent"] button:not(.secondary){background:#7bd8c8}
body[data-theme="library"]{background:#2b2333}body[data-theme="library"] .card{background:#3b3041;border-color:#72566d}body[data-theme="library"] button:not(.secondary){background:#d9b56d}
</style></head><body><header><div class="brand">PUZZLEMINT</div><div id="step"></div></header><main class="shell" id="app"></main>
<script type="application/json" id="game-data">__DATA__</script><script>
const game=JSON.parse(document.getElementById('game-data').textContent);
document.body.dataset.theme=game.project.theme;
const app=document.getElementById('app'),step=document.getElementById('step');
const key='puzzlemint:'+game.project.id;
let state={started:false,nickname:'',completed:[],attempts:{},hints:{},finished:false};
try{const saved=JSON.parse(localStorage.getItem(key));if(saved&&Array.isArray(saved.completed))state={...state,...saved}}catch(e){}
function save(){try{localStorage.setItem(key,JSON.stringify(state))}catch(e){}}
function node(tag,text,className){const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(className)el.className=className;return el}
function add(parent,tag,text,className){const el=node(tag,text,className);parent.append(el);return el}
function button(parent,label,click,secondary=false){const b=add(parent,'button',label,secondary?'secondary':'');b.onclick=click;return b}
function current(){return game.puzzles.find(p=>!state.completed.includes(p.id)&&p.dependencies.every(id=>state.completed.includes(id)))}
function normalize(s){return String(s).trim().toUpperCase().replace(/\s+/g,' ')}
function restart(){if(!confirm('Restart this adventure and erase saved progress?'))return;state={started:false,nickname:'',completed:[],attempts:{},hints:{},finished:false};save();render()}
function render(){app.replaceChildren();const count=state.completed.length;step.textContent=`${count} / ${game.puzzles.length} solved`;
if(!state.started){add(app,'div',game.project.occasion+' · '+game.project.theme,'eyebrow');add(app,'h1',game.project.title);add(app,'p',game.intro);const card=add(app,'section',undefined,'card');add(card,'label','Your nickname (optional)');card.append(document.createElement('br'));const input=add(card,'input');input.maxLength=60;input.value=state.nickname;button(card,'Begin adventure',()=>{state.nickname=input.value.trim().slice(0,60);state.started=true;save();render()});return}
if(count===game.puzzles.length){add(app,'div','ADVENTURE COMPLETE','eyebrow');add(app,'h1','The mystery is solved');add(app,'p',game.project.final_message);add(app,'p',`Solved ${count} chambers with ${Object.values(state.attempts).reduce((a,b)=>a+b,0)} attempts and ${Object.values(state.hints).reduce((a,b)=>a+b,0)} hints.`);button(app,'Play again',restart,true);return}
const p=current();if(!p){add(app,'h1','Unable to continue');add(app,'p','This game has a broken dependency. Contact the organizer.');return}
const progress=add(app,'div',undefined,'progress');const fill=add(progress,'span');fill.style.width=(count/game.puzzles.length*100)+'%';add(app,'div',`CHAMBER ${p.position+1} OF ${game.puzzles.length}`,'eyebrow');add(app,'h1',p.title);const card=add(app,'section',undefined,'card');add(card,'p',p.parameters.story);add(card,'p',p.parameters.prompt);
if(p.type==='cipher')add(card,'div',p.parameters.ciphertext,'clue');
if(p.type==='logic_grid')p.parameters.clue_texts.forEach(clue=>add(card,'div',clue,'clue'));
if(p.type==='sequence')p.parameters.edges.forEach(edge=>add(card,'div',`${edge[0]} must happen before ${edge[1]}.`,'clue'));
let answer=()=>'';
if(p.type==='logic_grid'){const table=add(card,'table'),head=add(table,'tr');['Person','Object','Place'].forEach(t=>add(head,'th',t));const rows=[];p.parameters.people.forEach(person=>{const tr=add(table,'tr');add(tr,'td',person);const cells=[];for(const values of [p.parameters.objects,p.parameters.places]){const td=add(tr,'td'),select=add(td,'select');add(select,'option','Choose');values.forEach(v=>{const option=add(select,'option',v);option.value=v});cells.push(select)}rows.push([person,...cells])});answer=()=>JSON.stringify(Object.fromEntries(rows.map(([person,obj,place])=>[person,{object:obj.value,place:place.value}])))}
else if(p.type==='sequence'){let items=[...p.parameters.items];const wrap=add(card,'div');function draw(){wrap.replaceChildren();items.forEach((item,i)=>{const row=add(wrap,'div',undefined,'sequence-row');add(row,'span',item);const controls=add(row,'span');button(controls,'↑',()=>{if(i){[items[i-1],items[i]]=[items[i],items[i-1]];draw()}},true);button(controls,'↓',()=>{if(i<items.length-1){[items[i+1],items[i]]=[items[i],items[i+1]];draw()}},true)})}draw();answer=()=>JSON.stringify(items)}
else{const input=add(card,'input');input.placeholder=p.type==='number_lock'?'Three digits':'Decoded word';input.autocomplete='off';if(p.type==='number_lock'){input.inputMode='numeric';input.maxLength=3}answer=()=>input.value;input.onkeydown=e=>{if(e.key==='Enter')submit()}}
const status=add(card,'p','', 'status');function submit(){state.attempts[p.id]=(state.attempts[p.id]||0)+1;let correct=false;if(p.type==='logic_grid'){try{const attempt=JSON.parse(answer());correct=JSON.stringify(attempt)===JSON.stringify(p.solution.assignment)}catch(e){}}else if(p.type==='sequence'){correct=JSON.stringify(JSON.parse(answer()))===JSON.stringify(p.solution.order)}else{correct=normalize(answer())===normalize(p.solution.answer)}if(correct){state.completed.push(p.id);save();status.textContent='Correct. The next chamber is unlocked.';status.className='status good';setTimeout(render,450)}else{save();status.textContent='Not quite. Review the clues and try again.';status.className='status bad'}}
button(card,'Submit answer',submit);const level=state.hints[p.id]||0;button(card,level<3?'Reveal hint':'All hints used',()=>{if((state.hints[p.id]||0)<3){state.hints[p.id]=(state.hints[p.id]||0)+1;save();render()}},true).disabled=level>=3;
for(let i=0;i<level;i++)add(card,'p',`Hint ${i+1}: ${p.hints[i]}`,'clue');button(app,'Restart game',restart,true)
}render();
</script></body></html>"""


def create_html(project: dict, puzzles: list[dict]) -> str:
    payload = json.dumps({"project": project, "puzzles": puzzles, "intro": intro(project)}, ensure_ascii=False, separators=(",", ":"))
    # JSON is parsed as text, but an HTML parser would still recognize a literal closing script tag.
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return HTML_TEMPLATE.replace("__DATA__", payload)
