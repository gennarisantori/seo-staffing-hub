# -*- coding: utf-8 -*-
"""Build the staffing seed (people + 2026 projects + allocations) from the Excel extract.

Inputs : xl.json   (produced by extract.py from the two workbooks)
         seed.json (previous run, reused for the consolidated people list)
Outputs: seed.json, seed_js.txt  (the JS the build injects into index.html)
"""
import json, io, re, os, random

SCR = os.path.dirname(os.path.abspath(__file__))
random.seed(20260618)

d = json.load(io.open(os.path.join(SCR, 'xl.json'), encoding='utf-8'))
prev = json.load(io.open(os.path.join(SCR, 'seed.json'), encoding='utf-8'))
people = [dict(p) for p in prev['people']]          # consolidated roster (43)


def nkey(s):
    return re.sub(r'[^a-z]', '', (s or '').lower())


VARIANT = {nkey('Gabriele Mereu Milla'): nkey('Gabriele Mereu Milia'),
           nkey('Federico Gennari Santori'): nkey('Federico Gennari')}

# stream per person: Content vs SEO (from the Risorse sheet; default SEO)
stream_of = {}
for p in d['people']:
    k = VARIANT.get(nkey(p['name']), nkey(p['name']))
    stream_of[k] = 'Content' if 'content' in (p['sub'] or p['rank'] or '').lower() else 'SEO'

# ── Projects: every non-finished project from SEO 26 + Content 26 ──
ALIAS = {
    'KEMPINSKI': 'KEMPISKI', 'SOLE24ORE': 'ILSOLE24ORE', 'GINORI': 'RICHARDGINORI',
    'BBITALIA': 'FLOSBBITALIA', 'FLOS': 'FLOSBBITALIA', 'BBPM': 'BANCOBPM',
    'PLENITUDE': 'ENI', 'SVAROWSKI': 'SWAROVSKI', 'SWAROWSKI': 'SWAROVSKI',
    'TEVAITALIA': 'TEVA', 'PONZIOALUMINIUM': 'PONZIO', 'WIND': 'WIND3',
    'REPLAYJEANS': 'FASHIONBOX', 'MIUMIU': 'PRADA', 'ZONA': 'SIDAL',
}


def ckey(s):
    k = re.sub(r'[^A-Z0-9]', '', (s or '').upper())
    return ALIAS.get(k, k)


def is_project(p):
    """Skip the sheets' summary rows (e.g. a trailing 'Totale' line) and finished work."""
    name = (p['name'] or '').strip()
    if not name or re.match(r'^(totale?|total)\b', name, re.I):
        return False
    if p['status'].strip().lower() == 'finished':
        return False
    # a real project row carries a job id and a start date
    return bool((p['jobId'] or '').strip()) and bool((p['startDate'] or '').strip())


projects, by_client, pid_n = [], {}, 0
for src, rows in (('SEO', d['seo']), ('Content', d['content'])):
    for p in rows:
        if not is_project(p):
            continue
        pid_n += 1
        rec = dict(id='p%d' % pid_n, jobId=p['jobId'] or '-', name=p['name'],
                   client=p['client'], startDate=p['startDate'], endDate=p['endDate'],
                   totalDays=round(p['total'], 1),
                   daysByRole={k: p['pl'].get(k, 0) for k in ['PL4', 'PL3', 'PL2', 'PL1']},
                   asgn={}, stream=src)
        projects.append(rec)
        by_client.setdefault(ckey(p['client']), []).append(rec)

NB = [('Internal / Management', 'NON BILLABLE'), ('Training', 'NON BILLABLE'),
      ('New Business / Presale', 'NON BILLABLE'), ('Holidays / Leave', 'NON BILLABLE')]
nb_recs = [dict(id='nb%d' % i, jobId='-', name=nm, client=cl,
                startDate='2026-01-01', endDate='2026-12-31', totalDays=0,
                daysByRole={k: 0 for k in ['PL4', 'PL3', 'PL2', 'PL1']}, asgn={}, nb=True)
           for i, (nm, cl) in enumerate(NB, 1)]

by_stream = {'SEO': [p for p in projects if p['stream'] == 'SEO'],
             'Content': [p for p in projects if p['stream'] == 'Content']}

# ── Who works on what: client rows from the Raw sheet + the Project N columns ──
person_clients = {}
for r in d['raw']:
    person_clients.setdefault(VARIANT.get(nkey(r['name']), nkey(r['name'])), set()).add(ckey(r['client']))
for p in d['people']:
    k = VARIANT.get(nkey(p['name']), nkey(p['name']))
    for c in p['projects']:
        person_clients.setdefault(k, set()).add(ckey(c))

unmatched, from_file, filled = set(), 0, 0
for person in people:
    key = nkey(person['name'])
    mine = []
    for c in person_clients.get(key, ()):
        if c in by_client:
            mine.extend(by_client[c])
        else:
            unmatched.add(c)
    mine = list({m['id']: m for m in mine}.values())
    if mine:
        from_file += 1
    else:
        # Not mapped in the workbooks (Content team, externals, some managers):
        # give them projects from their own stream so billability stays realistic.
        pool = by_stream.get(stream_of.get(key, 'SEO')) or by_stream['SEO']
        mine = random.sample(pool, k=min(len(pool), random.randint(3, 6)))
        filled += 1
    random.shuffle(mine)
    mine = mine[:8]

    # 10-25% of the year on internal work / presale, the rest on client projects
    nb_share = random.choice([10, 10, 15, 15, 20, 25])
    a = max(5, round(nb_share * random.uniform(.4, .6) / 5) * 5)
    picks = random.sample(nb_recs, k=2)
    picks[0]['asgn'][person['id']] = a
    if nb_share - a > 0:
        picks[1]['asgn'][person['id']] = nb_share - a

    rest, n = 100 - nb_share, len(mine)
    base = [1] * n
    for _ in range(rest // 5 - n):
        base[random.randrange(n)] += 1
    for prj, u in zip(mine, base):
        prj['asgn'][person['id']] = u * 5

all_projects = projects + nb_recs
io.open(os.path.join(SCR, 'seed.json'), 'w', encoding='utf-8').write(
    json.dumps(dict(people=people, projects=all_projects), ensure_ascii=False))
io.open(os.path.join(SCR, 'seed_js.txt'), 'w', encoding='utf-8').write(
    'const IM=' + json.dumps(people, ensure_ascii=False, separators=(',', ':')) +
    ';\nconst IP=' + json.dumps(all_projects, ensure_ascii=False, separators=(',', ':')) + ';')

# ── report ──
tot, bill, nb = {}, {}, {}
for p in all_projects:
    for mid, pct in p['asgn'].items():
        tot[mid] = tot.get(mid, 0) + pct
        tgt = nb if p.get('nb') else bill
        tgt[mid] = tgt.get(mid, 0) + pct
print('PEOPLE:', len(people), '| PROJECTS:', len(projects), 'ongoing +', len(nb_recs), 'non-billable')
print('allocations from the workbooks:', from_file, '| filled by stream:', filled)
print('allocation != 100%:', {k: v for k, v in tot.items() if v != 100} or 'none')
print('people with 0% billable:', [p['name'] for p in people if bill.get(p['id'], 0) == 0] or 'none')
print('avg billable: %.0f%% | avg non-billable: %.0f%%'
      % (sum(bill.values()) / len(people), sum(nb.values()) / len(people)))
print('projects with a team:', sum(1 for p in projects if p['asgn']), '/', len(projects))
print('unmatched clients:', sorted(unmatched))
