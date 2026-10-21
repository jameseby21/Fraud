"""Generic course content, reproducible lesson analysis, and dependency-free charts."""
from collections import defaultdict, Counter
import csv
from datetime import date
import html
import json
from pathlib import Path
import re
import statistics

ROOT = Path(__file__).resolve().parent


def load_catalog():
    return json.loads((ROOT / 'courses/catalog.json').read_text(encoding='utf-8'))


def load_glossary():
    """Return the reviewed, versioned learning-term index."""
    return json.loads((ROOT / 'data/learning/glossary.json').read_text(encoding='utf-8'))


def load_common_errors():
    """Return reusable learner-error signatures and corrective suggestions."""
    return json.loads((ROOT / 'data/learning/common_errors.json').read_text(encoding='utf-8'))


def load_quizzes():
    """Build one small check for each standard lesson section from reviewed Markdown."""
    section_config = {
        'Question': ('question', 'Which question is this section asking you to investigate?',
                     ['Does every unusual value prove that a crime occurred?', 'Can provenance and record grain be skipped?']),
        'Try it': ('try-it', 'Which action is part of this section?',
                   ['Open the answer key first and copy its conclusion.', 'Remove unusual records before checking their grain.']),
        'Check your work': ('check', 'Which result matches the worked check?',
                            ['Every alert in the exercise proves misconduct.', 'The section has no reproducible result to compare.']),
        'Debugging': ('debugging', 'Which debugging advice applies to this section?',
                      ['Change source records until the expected answer appears.', 'Ignore units, filters, and row grain.']),
        'Reflection': ('reflection', 'Which prompt belongs to this section’s reflection?',
                       ['Which person should be accused from this exercise alone?', 'How can review limits be omitted from the memo?'])
    }
    quizzes, by_lesson = [], {}
    for course in load_catalog()['courses']:
        for lesson in course['lessons']:
            markdown = (ROOT / 'courses' / course['id'] / f'{lesson["id"]}.md').read_text(encoding='utf-8')
            sections = {name: body.strip() for name, body in re.findall(r'^## ([^\n]+)\n\n(.*?)(?=^## |\Z)', markdown, re.M | re.S)}
            lesson_key = f'{course["id"]}/{lesson["id"]}'
            by_lesson[lesson_key] = []
            for section, (slug, prompt, distractors) in section_config.items():
                quiz_id = f'{course["id"]}-{lesson["id"]}-{slug}'
                answer = re.split(r'(?<=[.!?])\s+', sections[section], maxsplit=1)[0]
                item = dict(id=quiz_id, section=section, prompt=prompt, input_type='choice',
                            answer=answer, choices=[answer, *distractors],
                            suggestion=f'Reread “{section}” and compare the wording, grain, filters, and units before trying again.',
                            success='Correct. Explain why that answer fits before continuing.')
                if quiz_id == 'operations-summaries-try-it':
                    item.update(prompt='Filter category to Travel. What is the mean transaction amount in USD, rounded to cents?',
                                input_type='numeric', answer=2203.76, choices=[], tolerance=.01,
                                suggestion='Check that category equals Travel, use a mean rather than a total or median, divide cents by 100 once, and round only the final result.')
                quizzes.append(item)
                by_lesson[lesson_key].append(quiz_id)
    return dict(schema_version=1, quizzes=quizzes, by_lesson=by_lesson)


def glossary_markdown(glossary=None):
    glossary = glossary or load_glossary()
    lines = [
        '# Data analysis and forensic review glossary', '',
        'This index is generated from `data/learning/glossary.json`, the same reviewed source used by the course interface. Terms explain analytical use and limits; they do not turn a screening signal into a finding of misconduct.', ''
    ]
    for term in glossary['terms']:
        lines.extend([
            f'## {term["term"]}', '',
            f'**Definition:** {term["definition"]}', '',
            f'**More context:** {term["context"]}', '',
            f'**Implications:** {term["implications"]}', '',
            '**Also shown as:** ' + ', '.join(term['aliases']) + '.', ''
        ])
    return '\n'.join(lines)


def evaluate_quiz(quiz_id, answer):
    """Evaluate a short answer and return a specific, non-punitive next step."""
    if not isinstance(answer, (str, int, float)) or isinstance(answer, bool):
        raise ValueError('Answer must be text or a number')
    quizzes = {quiz['id']: quiz for quiz in load_quizzes()['quizzes']}
    if quiz_id not in quizzes:
        raise KeyError(quiz_id)
    quiz = quizzes[quiz_id]
    supplied = str(answer).strip()
    if quiz['input_type'] == 'numeric':
        try:
            numeric = float(supplied.replace(',', '').replace('$', ''))
        except ValueError:
            numeric = None
        correct = numeric is not None and abs(numeric - float(quiz['answer'])) <= quiz.get('tolerance', 0)
    else:
        correct = supplied.casefold() == str(quiz['answer']).strip().casefold()
    if correct:
        return {'correct': True, 'message': quiz.get('success', 'Correct. Continue with your analysis.')}
    normalized = supplied.replace(',', '').replace('$', '').casefold()
    for error in load_common_errors()['errors']:
        if error.get('quiz_id') in (None, quiz_id) and normalized in [str(value).casefold() for value in error.get('matches', [])]:
            return {'correct': False, 'message': 'Not yet.', 'suggestion_id': error['id'], 'suggestion': error['suggestion']}
    return {'correct': False, 'message': 'Not yet.', 'suggestion_id': 'review-section', 'suggestion': quiz['suggestion']}


def lesson_document(course_id, lesson_id):
    quiz_bank = load_quizzes()
    quiz_groups = quiz_bank['by_lesson']
    for course in load_catalog()['courses']:
        if course['id'] == course_id:
            for lesson in course['lessons']:
                if lesson['id'] == lesson_id:
                    quizzes = []
                    for quiz_id in quiz_groups[f'{course_id}/{lesson_id}']:
                        source = next(q for q in quiz_bank['quizzes'] if q['id'] == quiz_id)
                        quizzes.append({key: value for key, value in source.items() if key not in ('answer', 'tolerance', 'suggestion', 'success')})
                    return dict(lesson, course_id=course_id,dataset=course['dataset'],
                                markdown=(ROOT / 'courses' / course_id / (lesson_id + '.md')).read_text(encoding='utf-8'),
                                quizzes=quizzes,
                                tracks={'python': f'courses/{course_id}/{lesson_id}.ipynb',
                                        'r': 'courses/tracks/forensic.R' if course['dataset']=='forensic-v2' else 'courses/tracks/analysis.R',
                                        'powerbi': 'courses/tracks/forensic-powerbi.md' if course['dataset']=='forensic-v2' else 'courses/tracks/powerbi.md'})
    raise KeyError('Unknown course or lesson')


def render_markdown(text):
    """Small escaped subset: headings, paragraphs, lists, fenced code; no raw HTML."""
    result, paragraph, in_code, code, in_list = [], [], False, [], False
    table_rows = []

    def inline(value):
        value = html.escape(value)
        value = re.sub(r'`([^`]+)`', r'<code>\1</code>', value)
        return value

    def flush():
        if paragraph:
            result.append('<p>' + inline(' '.join(paragraph)) + '</p>')
            paragraph.clear()

    def flush_table():
        if table_rows:
            result.append('<div class="table-wrap"><table><thead><tr>' + ''.join('<th scope="col">' + inline(c) + '</th>' for c in table_rows[0]) + '</tr></thead><tbody>')
            for row in table_rows[1:]:
                result.append('<tr>' + ''.join('<td>' + inline(c) + '</td>' for c in row) + '</tr>')
            result.append('</tbody></table></div>')
            table_rows.clear()

    for line in text.splitlines():
        if not in_code and line.startswith('|') and line.endswith('|'):
            flush()
            if in_list:
                result.append('</ul>'); in_list = False
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            if not all(re.fullmatch(r':?-+:?', c) for c in cells):
                table_rows.append(cells)
            continue
        flush_table()
        if line.startswith('```'):
            flush()
            if in_list:
                result.append('</ul>'); in_list = False
            if in_code:
                result.append('<pre><code>' + html.escape('\n'.join(code)) + '</code></pre>')
                code = []
            in_code = not in_code
            continue
        if in_code:
            code.append(line); continue
        heading = re.match(r'^(#{1,4}) (.+)$', line)
        if not line.startswith('- ') and in_list:
            result.append('</ul>'); in_list = False
        if heading:
            flush(); level = len(heading[1])
            result.append(f'<h{level}>' + inline(heading[2]) + f'</h{level}>')
        elif line.startswith('- '):
            flush()
            if not in_list:
                result.append('<ul>'); in_list = True
            result.append('<li>' + inline(line[2:]) + '</li>')
        elif not line.strip():
            flush()
        else:
            paragraph.append(line)
    flush(); flush_table()
    if in_list:
        result.append('</ul>')
    if in_code:
        result.append('<pre><code>' + html.escape('\n'.join(code)) + '</code></pre>')
    return '\n'.join(result)


def read_transactions(dataset='payments-v1'):
    files={'payments-v1':'data/learning/transactions.csv','forensic-v2':'data/forensic/v2/payments.csv'}
    with (ROOT / files[dataset]).open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        row['amount_cents'] = int(row['amount_cents'])
        row['payment_delay_days'] = (date.fromisoformat(row['payment_date']) - date.fromisoformat(row['invoice_date'])).days
    return rows


def analyze(dataset='payments-v1'):
    rows = read_transactions(dataset)
    duplicates, supplier_days = defaultdict(list), defaultdict(list)
    monthly, categories, regions, heatmap = Counter(), Counter(), Counter(), Counter()
    category_values = defaultdict(list)
    edges = [0, 100000, 250000, 500000, 1000000, 5000000, 30000000]
    histogram = [dict(label=f'${a/100:g} to <${b/100:g}', count=0) for a, b in zip(edges, edges[1:])]
    for r in rows:
        duplicates[(r['supplier'], r['invoice_id'])].append(r)
        supplier_days[(r['supplier'], r['invoice_date'])].append(r)
        monthly[r['invoice_date'][:7]] += r['amount_cents']
        categories[r['category']] += r['amount_cents']
        regions[r['region']] += r['amount_cents']
        heatmap[(r['department'], r['category'])] += r['amount_cents']
        category_values[r['category']].append(r['amount_cents'] / 100)
        for i, (low, high) in enumerate(zip(edges, edges[1:])):
            if low <= r['amount_cents'] < high:
                histogram[i]['count'] += 1
    return dict(row_count=len(rows), total_cents=sum(r['amount_cents'] for r in rows),
                duplicate_groups=[dict(supplier=k[0], invoice_id=k[1], transaction_ids=[r['transaction_id'] for r in v]) for k, v in sorted(duplicates.items()) if len(v) > 1],
                supplier_days_over_threshold=[dict(supplier=k[0], invoice_date=k[1], total_cents=sum(r['amount_cents'] for r in v), transaction_ids=[r['transaction_id'] for r in v])
                    for k, v in sorted(supplier_days.items()) if len(v) >= 3 and all(r['amount_cents'] < 1000000 for r in v) and sum(r['amount_cents'] for r in v) > 1000000],
                late_payments=[r['transaction_id'] for r in rows if r['payment_delay_days'] > 90],
                monthly=[dict(month=k, amount_cents=v) for k, v in sorted(monthly.items())],
                categories=[dict(category=k, amount_cents=v) for k, v in sorted(categories.items())],
                pareto=[dict(region=k, amount_cents=v) for k, v in regions.most_common()],
                histogram=histogram,
                boxes=[dict(category=k, minimum=min(v), q1=statistics.quantiles(v, n=4, method='inclusive')[0], median=statistics.median(v),
                            q3=statistics.quantiles(v, n=4, method='inclusive')[2], maximum=max(v)) for k, v in sorted(category_values.items())],
                heatmap=[dict(department=k[0], category=k[1], amount_cents=v) for k, v in sorted(heatmap.items())])


CHARTS = {
    'bar': ('Category comparison', 'Total synthetic USD by category. Zero baseline.'),
    'line': ('Invoice-month trend', 'Sum of synthetic amounts by invoice month, not payment month. Zero baseline.'),
    'histogram': ('Amount distribution', 'Counts in explicitly unequal-width amount bins, shown as categorical bars, not density. Zero baseline.'),
    'scatter': ('Amount and payment delay', 'First 500 rows only, including planted records. Horizontal axis USD, vertical axis delay days. This subset is not representative.'),
    'box': ('Category spread', 'Inclusive quartiles with minimum/maximum whiskers, not Tukey whiskers. USD axis; large planted amount stretches the scale.'),
    'heatmap': ('Department and category', 'Cell intensity is total synthetic USD; values are printed so color is not required.'),
    'pareto': ('Regional concentration', 'Bars sorted by total USD; line is cumulative percentage on the right axis. Four fictional regions.')}


def render_chart(name,dataset='payments-v1'):
    if name not in CHARTS:
        raise KeyError(name)
    title, description = CHARTS[name]
    data = analyze(dataset)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 430" role="img" aria-labelledby="title desc"><title id="title">{title}</title><desc id="desc">{description}</desc>',
             '<rect width="800" height="430" fill="white"/>', f'<text x="55" y="25" font-size="18">{title}</text>']

    def text(x, y, value, size=12):
        parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="#16352d">{html.escape(str(value))}</text>')

    def line(x, y, xx, yy, color='#176b57'):
        parts.append(f'<line x1="{x}" y1="{y}" x2="{xx}" y2="{yy}" stroke="{color}" stroke-width="2"/>')

    line(65, 60, 65, 350, '#667'); line(65, 350, 750, 350, '#667'); text(35, 355, '0')
    if name in ('bar', 'line', 'histogram', 'pareto'):
        key, label = {'bar': ('categories', 'category'), 'line': ('monthly', 'month'), 'histogram': ('histogram', 'label'), 'pareto': ('pareto', 'region')}[name]
        values = [(r[label], r.get('count', r.get('amount_cents', 0) / 100)) for r in data[key]]
        maximum = max(v for _, v in values)
        text(65, 50, f'Max scale: {maximum:,.0f} ' + ('records' if name == 'histogram' else 'USD'))
        previous, cumulative = None, 0
        for i, (label_value, value) in enumerate(values):
            x = 90 + i * 650 / len(values)
            y = 350 - 265 * value / maximum
            if name == 'line':
                if previous:
                    line(*previous, x, y)
                parts.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#176b57"/>'); previous = (x, y)
            else:
                parts.append(f'<rect x="{x}" y="{y}" width="{min(70, 480/len(values))}" height="{350-y}" fill="#176b57"/>')
            if name!='line' or len(values)<=12 or i%3==0:
                text(x, 375 + (i % 2) * 18, label_value, 10)
            if name == 'pareto':
                cumulative += value
                cy = 350 - 265 * cumulative / (data['total_cents'] / 100)
                if previous:
                    line(*previous, x, cy, '#a94a19')
                parts.append(f'<circle cx="{x}" cy="{cy}" r="4" fill="#a94a19"/>'); previous = (x, cy)
                text(x, cy - 8, f'{100*cumulative/(data["total_cents"]/100):.1f}%')
        if name == 'pareto':
            text(755, 85, '100%'); text(755, 350, '0%')
    elif name == 'scatter':
        rows = read_transactions(dataset)[:500]
        xmax = max(r['amount_cents']/100 for r in rows)
        ymax = max(r['payment_delay_days'] for r in rows)
        for r in rows:
            x, y = 65 + 660*(r['amount_cents']/100)/xmax, 350-265*r['payment_delay_days']/ymax
            parts.append(f'<circle cx="{x}" cy="{y}" r="3" fill="#176b57" opacity="0.45"><title>{r["transaction_id"]}: USD {r["amount_cents"]/100:.2f}, {r["payment_delay_days"]} days</title></circle>')
        text(65, 50, f'Y: payment delay, 0 to {ymax} days'); text(65, 380, f'X: amount, 0 to {xmax:,.0f} USD')
    elif name == 'box':
        maximum = max(r['maximum'] for r in data['boxes'])
        text(65, 50, f'Y: USD, 0 to {maximum:,.0f}')
        for i, r in enumerate(data['boxes']):
            x = 145 + 160*i
            pos = lambda v: 350-265*v/maximum
            line(x, pos(r['minimum']), x, pos(r['maximum']))
            parts.append(f'<rect x="{x-25}" y="{pos(r["q3"])}" width="50" height="{max(1,pos(r["q1"])-pos(r["q3"]))}" fill="#b8e3d1" stroke="#176b57"/>')
            line(x-25, pos(r['median']), x+25, pos(r['median']), '#a94a19')
            text(x-40, 380, r['category'])
    elif name == 'heatmap':
        maximum = max(r['amount_cents'] for r in data['heatmap'])
        categories = sorted({r['category'] for r in data['heatmap']})
        departments = sorted({r['department'] for r in data['heatmap']})
        for r in data['heatmap']:
            x, y = 180+categories.index(r['category'])*145, 75+departments.index(r['department'])*65
            parts.append(f'<rect x="{x}" y="{y}" width="140" height="60" fill="#176b57" fill-opacity="{0.08+0.5*r["amount_cents"]/maximum}"/>')
            text(x+8, y+35, f'${r["amount_cents"]/100:,.0f}')
        for i, c in enumerate(categories): text(180+145*i, 365, c)
        for i, d in enumerate(departments): text(70, 110+65*i, d)
    parts.append('</svg>')
    return ''.join(parts)
