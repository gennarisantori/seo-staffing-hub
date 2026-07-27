# -*- coding: utf-8 -*-
"""Build the new staffing seed (people + ongoing projects + allocations) from the Excel extract."""
import json, io, re, os, random

SCR = os.path.dirname(os.path.abspath(__file__))
APP = r'C:\Users\fgennari\Downloads\seo-staffing-hub\index.html'
random.seed(20260618)

d = json.load(io.open(os.path.join(SCR, 'xl.json'), encoding='utf-8'))
html = io.open(APP, encoding='utf-8').read()

RANKS = ["Director", "Senior Expert Lead", "Senior Manager", "Manager", "Expert Lead",
         "Associate Manager", "Senior Consultant", "Senior Associate", "Associate",
         "Consultant", "Junior Associate", "Junior Consultant", "Analyst"]


def map_rank(r):
    x = re.sub(r'^(SEO|Content Marketing|Content|DMA)\s+', '', (r or '').strip())
    return x if x in RANKS else 'Consultant'


def nkey(s):
    return re.sub(r'[^a-z]', '', (s or '').lower())


# ── People: keep the current roster, add the new names from the Excel ──
app_people = re.findall(r'\{id:"(m\d+)",name:"([^"]+)",role:"([^"]+)",cap:(\d+)\}', html)
people, seen = [], {}
for pid, name, role, cap in app_people:
    rec = dict(id=pid, name=name, role=role, cap=int(cap))
    people.append(rec)
    seen[nkey(name)] = rec

# name variants: Excel spelling -> existing app person
VARIANT = {nkey('Gabriele Mereu Milla'): nkey('Gabriele Mereu Milia'),
           nkey('Federico Gennari Santori'): nkey('Federico Gennari')}

nid = max(int(p['id'][1:]) for p in people)
xl_by_key = {}
for p in d['people']:
    k = VARIANT.get(nkey(p['name']), nkey(p['name']))
    xl_by_key[k] = p
    if k in seen:                      # already in the app: refresh role/email
        seen[k]['role'] = map_rank(p['rank'])
        seen[k]['email'] = p['email']
    else:                              # brand-new person
        nid += 1
        rec = dict(id='m%d' % nid, name=p['name'], role=map_rank(p['rank']), cap=220,
                   email=p['email'])
        people.append(rec)
        seen[k] = rec
# fill emails for people not in the Excel (e.g. [EXT] consultants)
for p in people:
    if not p.get('email'):
        t = re.sub(r'\[ext\]', ' ', p['name'].lower())
        t = re.sub(r'[^a-z\s]', ' ', t).split()
        p['email'] = '.'.join(t) + '@jakala.com' if t else ''

# ── Projects: every non-finished project from SEO 26 + Content 26 ──
ALIAS = {
    'KEMPINSKI': 'KEMPISKI', 'SOLE24ORE': 'ILSOLE24ORE', 'GINORI': 'RICHARDGINORI',
    'CAPHOLDING': 'CAPHOLDING', 'BBITALIA': 'FLOSBBITALIA', 'FLOS': 'FLOSBBITALIA',
    'BBPM': 'BANCOBPM', 'PLENITUDE': 'ENI', 'SWAROWSKI': 'SWAROVSKI',
    'SAINTGOBAIN': 'SAINTGOBAIN', 'TEVAITALIA': 'TEVA', 'PONZIOALUMINIUM': 'PONZIO',
    'WIND': 'WIND3', 'HOTELDEROME': 'HOTELDEROME', 'UNISALUTE': 'UNISALUTE',
    'REPLAYJEANS': 'FASHIONBOX', 'MIUMIU': 'PRADA', 'ZONA': 'SIDAL',
    'CANTINERIUNITE': 'CANTINERIUNITE', 'INFOCAMERE': 'INFOCAMERE',
    'SVAROWSKI': 'SWAROVSKI',
}


def ckey(s):
    k = re.sub(r'[^A-Z0-9]', '', (s or '').upper())
    return ALIAS.get(k, k)


projects, pid_n = [], 0
by_client = {}
for src, rows in (('SEO', d['seo']), ('Content', d['content'])):
    for p in rows:
        if p['status'].strip().lower() == 'finished' or not p['name']:
            continue
        pid_n += 1
        rec = dict(id='p%d' % pid_n, jobId=p['jobId'] or '-', name=p['name'],
                   client=p['client'], startDate=p['startDate'], endDate=p['endDate'],
                   totalDays=round(p['total'], 1),
                   daysByRole={k: p['pl'].get(k, 0) for k in ['PL4', 'PL3', 'PL2', 'PL1']},
                   asgn={}, stream=src)
        projects.append(rec)
        by_client.setdefault(ckey(p['client']), []).append(rec)

# non-billable buckets (needed by the Billability view)
NB = [('Internal / Management', 'NON BILLABLE'), ('Training', 'NON BILLABLE'),
      ('New Business / Presale', 'NON BILLABLE'), ('Holidays / Leave', 'NON BILLABLE')]
nb_recs = []
for i, (nm, cl) in enumerate(NB, 1):
    rec = dict(id='nb%d' % i, jobId='-', name=nm, client=cl,
               startDate='2026-01-01', endDate='2026-12-31', totalDays=0,
               daysByRole={k: 0 for k in ['PL4', 'PL3', 'PL2', 'PL1']}, asgn={}, nb=True)
    nb_recs.append(rec)

# ── Allocations: person -> projects of the clients they work on (Raw sheet) ──
person_clients = {}
for r in d['raw']:
    k = VARIANT.get(nkey(r['name']), nkey(r['name']))
    person_clients.setdefault(k, set()).add(ckey(r['client']))
for p in d['people']:                       # also use the Project N columns
    k = VARIANT.get(nkey(p['name']), nkey(p['name']))
    for c in p['projects']:
        person_clients.setdefault(k, set()).add(ckey(c))

unmatched = set()
stats = dict(with_projects=0, nb_only=0)
for key, clients in person_clients.items():
    person = seen.get(key)
    if not person:
        continue
    mine = []
    for c in clients:
        if c in by_client:
            mine.extend(by_client[c])
        else:
            unmatched.add(c)
    # de-dup, cap the number of projects per person so shares stay realistic
    mine = list({m['id']: m for m in mine}.values())
    random.shuffle(mine)
    mine = mine[:8]

    # non-billable share (internal + presale + training/holidays), rest on projects
    nb_share = random.choice([10, 15, 15, 20, 20, 25])
    nb_pick = random.sample(nb_recs, k=2)
    a = round(nb_share * random.uniform(.4, .6) / 5) * 5 or 5
    b = nb_share - a
    nb_pick[0]['asgn'][person['id']] = a
    if b > 0:
        nb_pick[1]['asgn'][person['id']] = b

    rest = 100 - nb_share
    if not mine:
        # nobody assigned yet (e.g. Content people): put the remainder on internal work
        nb_recs[0]['asgn'][person['id']] = nb_recs[0]['asgn'].get(person['id'], 0) + rest
        stats['nb_only'] += 1
        continue
    # random split of `rest` across their projects, in steps of 5, min 5 each
    n = len(mine)
    units = rest // 5
    base = [1] * n
    for _ in range(units - n):
        base[random.randrange(n)] += 1
    for prj, u in zip(mine, base):
        prj['asgn'][person['id']] = u * 5
    stats['with_projects'] += 1

all_projects = projects + nb_recs

# Anyone still without allocations (no client rows yet, e.g. the Content team):
# put their whole 100% on non-billable work so every person totals 100%.
allocated = set()
for p in all_projects:
    allocated.update(p['asgn'].keys())
for person in people:
    if person['id'] in allocated:
        continue
    left, picks = 100, random.sample(nb_recs, k=3)
    for i, prj in enumerate(picks):
        share = left if i == len(picks) - 1 else round(random.uniform(.2, .45) * left / 5) * 5
        share = max(5, min(share, left - 5 * (len(picks) - 1 - i)))
        prj['asgn'][person['id']] = prj['asgn'].get(person['id'], 0) + share
        left -= share
    stats['nb_only'] += 1

out = dict(people=people, projects=all_projects)
io.open(os.path.join(SCR, 'seed.json'), 'w', encoding='utf-8').write(
    json.dumps(out, ensure_ascii=False))

# JS snippet for the app seed
def js(o):
    return json.dumps(o, ensure_ascii=False, separators=(',', ':'))
io.open(os.path.join(SCR, 'seed_js.txt'), 'w', encoding='utf-8').write(
    'const IM=' + js(people) + ';\nconst IP=' + js(all_projects) + ';')

# ── report ──
print('PEOPLE:', len(people), '(new added:', len(people) - len(app_people), ')')
print('PROJECTS:', len(projects), 'ongoing +', len(nb_recs), 'non-billable')
print('people with project allocations:', stats['with_projects'], '| non-billable only:', stats['nb_only'])
print('unmatched clients from Raw:', sorted(unmatched))
tot = {}
for p in all_projects:
    for mid, pct in p['asgn'].items():
        tot[mid] = tot.get(mid, 0) + pct
bad = {k: v for k, v in tot.items() if v != 100}
print('people whose allocation != 100%:', bad if bad else 'none')
print('people with no allocation at all:', [p['name'] for p in people if p['id'] not in tot])
