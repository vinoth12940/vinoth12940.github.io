#!/usr/bin/env python3
"""Render the buildless portfolio from its editable content files."""
import json
from pathlib import Path
from html import escape as esc

ROOT = Path(__file__).resolve().parents[1]
def read(name, default):
    p=ROOT/'data'/name
    return json.loads(p.read_text()) if p.exists() else default
p=read('profile.json', {})
g=read('github.json', {})
c=read('certifications.json', [])
w=read('writing.json', {})
repos=g.get('featured_projects',g.get('featured',[]))
if isinstance(c,dict): c=c.get('certifications',c.get('credentials',[]))
articles=w.get('articles',[]) if isinstance(w,dict) else w
blog_articles=w.get('blog_articles',[]) if isinstance(w,dict) else []

def text(s): return esc(str(s or ''))
def tags(items): return '<div class="tags">'+''.join('<span>'+text(t)+'</span>' for t in items)+'</div>'
def external(url,label,cls='text-link'):
    return f'<a class="{cls}" href="{text(url)}" target="_blank" rel="noopener noreferrer">{text(label)}<span class="sr-only"> (opens in a new tab)</span></a>'

featured_cert_ids = (
    'claude-architect-professional', 'claude-architect-foundations',
    'claude-developer-foundations', 'claude-associate-foundations',
)
certs_by_id = {credential['id']: credential for credential in c}
hero_badges = ''
for cert_id in featured_cert_ids:
    credential = certs_by_id[cert_id]
    role, level = credential['title'].removeprefix('Claude Certified ').split(' - ', 1)
    hero_badges += f'''<a class="hero-badge" href="{text(credential['url'])}" target="_blank" rel="noopener noreferrer" aria-label="{text(credential['title'])} — view credential (opens in a new tab)"><img src="{text(credential['image'])}" alt="" width="100" height="100" decoding="async"><strong>{text(role)}</strong><span>{text(level)}</span></a>'''
hero_credentials = f'''<section class="hero-certifications" aria-labelledby="hero-credentials-title"><span class="eyebrow">ANTHROPIC CERTIFICATIONS</span><h2 id="hero-credentials-title">Claude Certified<br> Architect<span class="accent">.</span></h2><div class="hero-badges">{hero_badges}</div><a class="hero-credential-link" href="#certifications">All credentials <span aria-hidden="true">↗</span></a></section>'''

projects=[]
for n,r in enumerate(repos):
    url=r.get('url',r.get('html_url',''))
    title=r.get('title',r.get('name',''))
    tech=r.get('tags',r.get('tech_stack',r.get('topics',[])))
    if not tech: tech=[r.get('language')] if r.get('language') else []
    cat=r.get('category','Open source')
    projects.append(f'''<article class="project-card" data-category="{text(cat)}"><div class="card-top"><span class="eyebrow">{text(cat)}</span><span class="index">{n+1:02d}</span></div><h3>{external(url,title,'card-title')}</h3><p>{text(r.get('summary',r.get('description','')))}</p>{tags(tech[:5])}<div class="card-foot">{external(url,'View repository')}<span>{text(r.get('language',''))}</span></div></article>''')

solutions=''.join(f'''<article class="solution"><h4>{text(s['title'])}</h4><p>{text(s['description'])}</p>{tags(s['tags'])}</article>''' for s in p['solutions'])
repo_archive=''.join(f'<li>{external(r["url"],r["name"])}<span>{text(r.get("language",""))}{" · Fork" if r.get("fork") else ""}</span></li>' for r in g.get('repositories',[]))
repo_archive=f'<details class="archive-panel"><summary>All public repositories <span aria-hidden="true">+</span></summary><ul class="archive-list">{repo_archive}</ul></details>'

experience=''
for i,e in enumerate(p['experience']):
    engagements=''.join(f'''<div class="engagement"><div class="engagement-top"><h4>{text(a['title'])}</h4><span>{text(a['period'])}</span></div><p>{text(a['description'])}</p>{tags(a['tags'])}</div>''' for a in e['engagements'])
    experience+=f'''<article class="experience-row"><div class="experience-date"><span>{text(e['period'])}</span><span class="muted">{text(e['location'])}</span></div><div class="experience-body"><h3>{text(e['company'])}</h3><p class="role">{text(e['role'])}</p><p>{text(e['description'])}</p>{f'<details class="engagements"><summary>Explore client engagements <span aria-hidden="true">+</span></summary>{engagements}</details>' if engagements else ''}</div></article>'''

skills=''.join(f'''<article class="skill-group"><h3><span class="index">{i+1:02d}</span>{text(s['category'])}</h3>{tags(s['items'])}</article>''' for i,s in enumerate(p['skills']))

certs=''
for x in c:
    title=x.get('title',x.get('name',''))
    issuer=x.get('issuer','')
    url=x.get('url',x.get('credential_url',''))
    image=x.get('image',x.get('badge_image_url',''))
    issued=x.get('date',x.get('issued',x.get('issued_date','')))
    expiry=x.get('expires',x.get('expiry',x.get('expiration_date','')))
    category=x.get('category','Other')
    details=x.get('display_note','')
    related=''
    if x.get('relatedAwards'):
        related='<div class="related-awards">'+''.join(external(a.get('credentialUrl',a.get('url','')), 'Related award · '+a.get('issued','')) for a in x['relatedAwards'] if a.get('credentialUrl',a.get('url','')))+'</div>'
    art=f'<img src="{text(image)}" alt="{text(title)} badge" width="100" height="100" loading="lazy">' if image else f'<span class="issuer-mark" aria-hidden="true">{text(x.get("issuer_short",issuer.split()[0] if issuer else "CERT"))}</span>'
    certs+=f'''<article class="credential" data-category="{text(category)}"><div class="credential-art">{art}</div><div class="credential-info"><span class="eyebrow">{text(issuer)}</span><h3>{text(title)}</h3><p class="credential-date">{text(issued)}{(' · '+text(details)) if details else ''}{(' · Expires '+text(expiry)) if expiry and not details else ''}</p>{external(url,x.get('link_label','View credential')) if url else '<span class="credential-note">Listed in resume</span>'}{related}</div></article>'''

writing=''
featured_articles=[a for a in articles if a.get('featured')][:5]
dashboard=next((a for a in blog_articles if 'Admin Dashboard' in a['title']),None)
if dashboard: featured_articles.insert(1,dashboard)
for i,a in enumerate(featured_articles):
    url=a.get('url',a.get('canonical_url',''))
    writing+=f'''<article class="article"><span class="index">{i+1:02d}</span><div><span class="eyebrow">{text(a.get('topic',a.get('source',a.get('platform','Medium'))))}</span><h3>{external(url,a['title'],'article-title')}</h3><p>{text(a.get('summary',a.get('description','')))}</p></div>{external(url,'Read article')}</article>'''
for heading,records in [('All Medium articles',articles),('Technical blog archive',blog_articles)]:
    links=''.join(f'<li>{external(a["url"],a["title"])}<span>{text(a.get("date",""))}</span></li>' for a in records)
    writing+=f'<details class="archive-panel"><summary>{heading} <span aria-hidden="true">+</span></summary><ul class="archive-list">{links}</ul></details>'

repo_count=g.get('public_repos',g.get('public_repo_count',43))
if isinstance(repo_count,list): repo_count=len(repo_count)
skill_count=sum(len(s['items']) for s in p['skills'])
page=f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vinoth Rajalingam — AI Engineer & CCM Architect</title>
<meta name="description" content="Vinoth Rajalingam's portfolio: agentic AI, RAG, enterprise document platforms, open-source projects, certifications, and technical writing.">
<meta name="theme-color" content="#0c1821"><meta property="og:title" content="Vinoth Rajalingam — AI Engineer & CCM Architect"><meta property="og:description" content="13+ years of enterprise engineering. Agentic AI, RAG, open source, and customer communications."><meta property="og:type" content="website"><meta property="og:url" content="https://vinoth12940.github.io/">
<link rel="canonical" href="https://vinoth12940.github.io/"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="styles.css">
<script defer src="app.js"></script>
<noscript><style>.menu-toggle{{display:none}}@media(max-width:760px){{#site-nav{{display:flex;position:static;flex-wrap:wrap;flex-direction:row;padding:8px 0;box-shadow:none;border:0;gap:12px}}.header-inner{{flex-wrap:wrap;padding-block:15px}}#site-nav a{{padding:4px 0}}}}</style></noscript>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="container header-inner"><a class="wordmark" href="#home" aria-label="Vinoth Rajalingam home"><span class="monogram">vr<span>.</span></span><span>VINOTH RAJALINGAM</span></a><button class="menu-toggle" aria-expanded="false" aria-controls="site-nav">Menu <span aria-hidden="true">+</span></button><nav id="site-nav" aria-label="Main navigation"><a href="#projects">Projects</a><a href="#experience">Experience</a><a href="#skills">Skills</a><a href="#certifications">Credentials</a><a href="#writing">Writing</a><a href="#contact" class="nav-contact">Let’s connect</a></nav></div></header>
<main id="main">
<section class="hero" id="home"><div class="container hero-grid"><div class="hero-copy"><div class="eyebrow hero-label"><span class="small-line"></span> AI ENGINEER / CCM ARCHITECT</div><h1>Vinoth<br>Rajalingam<span class="accent">.</span></h1><p class="hero-statement">Enterprise experience.<br><span>Agentic intelligence.</span></p><p class="hero-description">{text(p['summary'])}</p><div class="hero-actions"><a class="button button-accent" href="#projects">Explore my work</a><a class="button button-outline" href="assets/Resume_Vinoth_Rajalingam_Updated_080626.docx" download="Resume_Vinoth_Rajalingam_Updated_080626.docx">Download resume<span class="sr-only"> (Word document)</span></a>{external(p['linkedin'],'Connect on LinkedIn','button button-outline')}</div><div class="hero-location">PLANO, TEXAS <span aria-hidden="true">/</span> COGNIZANT</div></div>
{hero_credentials}
<aside class="focus-card" aria-label="Current engineering focus"><div class="focus-top"><span class="eyebrow">CURRENT FOCUS</span><span class="index">2026</span></div><h2>Governed<br>agentic AI.</h2><p>{text(p['focus'])}</p><div class="architecture" aria-label="Architecture: enterprise search and document intelligence connect to orchestration, which connects to MCP tools and enterprise systems"><div class="architecture-row"><span>AI SEARCH</span><span>DOCUMENT<br>INTELLIGENCE</span></div><div class="connector"><span></span><span></span></div><div class="architecture-core"><span class="eyebrow">ORCHESTRATION</span><strong>LangGraph + AKS</strong></div><div class="connector connector-bottom"><span></span><span></span></div><div class="architecture-row"><span>MCP TOOLS</span><span>ENTERPRISE<br>SYSTEMS</span></div></div><div class="focus-footer"><span>Search. Reason. Act.</span><span>Azure / MCP</span></div></aside></div><div class="container stats"><div><strong>13<span>+</span></strong><span>Years in enterprise engineering</span></div><div><strong>7<span>+</span></strong><span>GenAI solutions delivered</span></div><div><strong>{text(repo_count)}</strong><span>Public GitHub repositories</span></div><div><strong>{len(c)}</strong><span>Credentials & learning badges</span></div></div></section>
<div class="expertise-strip" aria-label="Core expertise"><div class="container"><span>AGENTIC AI</span><i aria-hidden="true">/</i><span>RETRIEVAL SYSTEMS</span><i aria-hidden="true">/</i><span>ENTERPRISE CCM</span><i aria-hidden="true">/</i><span>FULL-STACK ENGINEERING</span></div></div>
<section class="section container" id="projects"><div class="section-heading"><div><span class="eyebrow">01 / SELECTED WORK</span><h2>Built to solve<br>real problems<span class="accent">.</span></h2></div><div class="section-intro"><p>Open-source tools and experiments in agents, memory, retrieval, and developer workflows.</p>{external(p['github']+'?tab=repositories','All repositories on GitHub')}</div></div><div class="project-grid">{''.join(projects)}</div><details class="solutions-panel"><summary><span>Enterprise AI solutions <small>7 projects from my professional work</small></span><span class="details-icon" aria-hidden="true">+</span></summary><div class="solutions-grid">{solutions}</div></details>{repo_archive}</section>
<section class="section section-tint" id="experience"><div class="container"><div class="section-heading"><div><span class="eyebrow">02 / EXPERIENCE</span><h2>Engineering meets<br>enterprise delivery<span class="accent">.</span></h2></div><p class="section-intro">A career spanning AI platforms, insurance technology, and customer communications — from requirements to production.</p></div><div class="experience-list">{experience}</div><div class="education"><span class="eyebrow">EDUCATION</span><p>{text(p['education'])}</p></div></div></section>
<section class="section container" id="skills"><div class="section-heading"><div><span class="eyebrow">03 / TOOLKIT</span><h2>Depth across<br>the stack<span class="accent">.</span></h2></div><p class="section-intro">{skill_count} technologies and capabilities across {len(p['skills'])} areas, drawn from my resume and public work.</p></div><div class="skills-grid">{skills}</div></section>
<section class="section section-tint" id="certifications"><div class="container"><div class="section-heading"><div><span class="eyebrow">04 / CERTIFICATIONS & LEARNING</span><h2>Always building<br>what’s next<span class="accent">.</span></h2></div><p class="section-intro">Professional certifications, course completions, and earned learning badges. Credential links and issue dates are included where available.</p></div><div class="filters" role="group" aria-label="Filter credentials"><button class="filter active" data-filter="All" aria-pressed="true">All <span>{len(c)}</span></button><button class="filter" data-filter="Anthropic" aria-pressed="false">Anthropic</button><button class="filter" data-filter="Google" aria-pressed="false">Google Cloud</button><button class="filter" data-filter="Enterprise" aria-pressed="false">Cloud & CCM</button><button class="filter" data-filter="Other" aria-pressed="false">Other learning</button></div><p class="sr-only" id="credential-status" role="status" aria-live="polite"></p><div class="credential-grid">{certs}</div><p class="source-note">Credential dates reflect the linked records and resume. Historical certificates are shown with their recorded validity dates; course and skill badges are separate from professional certifications.</p></div></section>
<section class="section container" id="writing"><div class="section-heading"><div><span class="eyebrow">05 / FIELD NOTES</span><h2>Build it.<br>Write it down<span class="accent">.</span></h2></div><div class="section-intro"><p>Practical notes from building AI agents, self-hosted infrastructure, and memory systems.</p><div class="inline-links">{external(p['medium'],'Medium profile')}{external('https://vinoth12940.github.io/blog/','Technical blog')}</div></div></div><div class="articles">{writing}</div></section>
<section class="contact" id="contact"><div class="container contact-grid"><div><span class="eyebrow">LET’S CONNECT</span><h2>Have a complex<br>problem to solve<span class="accent">?</span></h2><p>Connect with me about agentic AI, enterprise architecture, and customer communications.</p><a class="contact-email" href="mailto:{text(p['email'])}">{text(p['email'])}</a></div><div class="contact-links">{external(p['linkedin'],'LinkedIn')}{external(p['github'],'GitHub')}{external(p['medium'],'Medium')}{external('https://vinoth12940.github.io/blog/','Blog')}</div></div></section>
</main><footer><div class="container footer-inner"><span>© 2026 Vinoth Rajalingam</span><span>Plano, Texas · Built with curiosity.</span><a href="#home">Back to top</a></div></footer>
</body></html>'''
(ROOT/'index.html').write_text(page)
print(f'Rendered {len(repos)} projects, {skill_count} skills, {len(c)} credentials, {len(articles)} articles.')
