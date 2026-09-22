"""Public classification regression: ordered routing and DNS use the same families."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'rules'
def index(name):
    exact,suffix=set(),set()
    for l in (R/(name+'.list')).read_text().splitlines():
        if not l or l.startswith('#'):continue
        k,v=l.split(',');(exact if k=='DOMAIN' else suffix).add(v)
    return exact,suffix
data={n:index(n) for n in ['ai-services','model-downloads','windows-downloads','overseas-services','china-direct-v2']}
def has(n,d):
    exact,suffix=data[n];p=d.split('.')
    return d in exact or any('.'.join(p[i:]) in suffix for i in range(len(p)))
def route(d):
    for n,p in [('model-downloads','download'),('ai-services','AI'),('windows-downloads','DIRECT'),('overseas-services','proxy'),('china-direct-v2','DIRECT')]:
        if has(n,d):return p
    return 'proxy'
def dns(d):
    if has('ai-services',d):return 'overseas'
    if has('windows-downloads',d):return 'domestic'
    if has('overseas-services',d):return 'overseas'
    return 'domestic' if has('china-direct-v2',d) else 'overseas'
cases={
 'chatgpt.com':('AI','overseas'),'claude.ai':('AI','overseas'),
 'api.x.ai':('AI','overseas'),'gemini.google.com':('AI','overseas'),
 'www.gov.cn':('DIRECT','domestic'),'www.miit.gov.cn':('DIRECT','domestic'),
 'new-domestic.example.cn':('DIRECT','domestic'),'wifi.vivo.com.cn':('DIRECT','domestic'),
 'jpush.cn':('DIRECT','domestic'),'189.cn':('DIRECT','domestic'),
 'mijia.tech':('DIRECT','domestic'),'miinsurtech.com':('DIRECT','domestic'),
 'www.bilibili.com':('DIRECT','domestic'),
 'google.cn':('proxy','overseas'),'www.microsoft.com.cn':('proxy','overseas'),
 'outlook.com':('proxy','overseas'),'github.com':('proxy','overseas'),
 'unknown-foreign.example':('proxy','overseas'),'unlisted.ms':('proxy','overseas'),
 'huggingface.co':('download','overseas'),
 'skydrive.wns.windows.com':('proxy','overseas'),'client.wns.windows.com':('proxy','overseas'),
 'ctldl.windowsupdate.com':('DIRECT','domestic'),'download.windowsupdate.com':('DIRECT','domestic'),
 'au.download.windowsupdate.com':('DIRECT','domestic'),'tlu.dl.delivery.mp.microsoft.com':('DIRECT','domestic'),
 'fe3.delivery.mp.microsoft.com':('proxy','overseas'),'login.live.com':('proxy','overseas'),
 'copilot.microsoft.com':('AI','overseas'),'unlisted.windowsupdate.com':('proxy','overseas')}
for d,want in cases.items():assert (route(d),dns(d))==want,(d,route(d),dns(d),want)
# A future protected cn domain must win through order, even though cn matches it.
data['ai-services'][1].add('future-ai.example.cn')
assert route('api.future-ai.example.cn')=='AI' and dns('api.future-ai.example.cn')=='overseas'
print(f'{len(cases)+1} routing/DNS classification regressions passed.')
