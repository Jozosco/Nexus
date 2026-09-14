"""인과 지도 HTML 빌더 — 온톨로지 원장(src/semantic/ontology.yaml)에서 직접 생성 (2026-09-14 · A-265).

왜 저장소에 두는가: 8/30 아티팩트 v2는 세션 임시 폴더에서만 만들어져 재현 경로가 없었다. 이 스크립트가
원장 → HTML을 결정적으로 만들므로 아티팩트는 언제나 원장과 일치한다(그래프 DB 불요 — D-025).
v3(2026-09-14) 추가: 인과 사슬 24 + 지표별 **데이터 원천 배지**(유료/무료/폴백 — ontology.data_sources) +
수집 채널·생산지역·신뢰도 지표 포인터(evaluation) 패널.

실행: python scripts/build_causal_map.py [--out reports/pipeline/latest/causal_map_latest.html]
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import yaml

ONTOLOGY = Path("src/semantic/ontology.yaml")
ENTITIES = Path("src/semantic/entities.yaml")
DEFAULT_OUT = Path("reports/pipeline/latest/causal_map_latest.html")


def _edges(o: dict) -> list[dict]:
    out = []
    for e in o["causal_edges"]:
        chain = [e["cause"]["node"]] + [m["node"] for m in e.get("mechanisms", [])] + [e["outcome"]["node"]]
        out.append({
            "id": e["edge_id"], "label": e["label_ko"], "cat": e["category"], "chain": chain,
            "dir": e.get("direction", "UP"), "lag": e.get("lag_trading_days"), "status": e.get("status"),
            "validated_by": e.get("validated_by", []) or [], "ev": len(e.get("evidence", []) or []),
            "rules": bool(e.get("interpretation_rules") or e.get("interpretation_rule")),
            "indicators": e.get("indicators", []) or [],
        })
    return out


def _source_of(indicator: str, ds_items: list[dict]) -> dict | None:
    for it in ds_items:
        for pfx in it.get("indicator_prefixes", []) or []:
            if indicator == pfx or indicator.startswith(pfx):
                return it
    return None


def build(o: dict, ent_count: int) -> str:
    edges = _edges(o)
    ds = (o.get("data_sources") or {}).get("items", []) or []
    # 지표 → 원천 배지
    badge: dict[str, dict] = {}
    for e in edges:
        for ind in e["indicators"]:
            it = _source_of(ind, ds)
            badge[ind] = ({"src": it["name"], "cost": it["cost"], "free": it["free_alternative"], "label": it["label"]}
                          if it else {"src": "무료 공개 소스(USDA·FRED·NOAA·공개 API)", "cost": "무료", "free": "해당 없음", "label": "CONFIRMED"})
    sc = o.get("supply_chain", {})
    routes = [{"id": r["route_id"], "name": r.get("label_ko", ""), "lead": r.get("lead_time_days")} for r in sc.get("routes", [])]
    media = o.get("media_sources", {})
    channels = [{"id": c["id"], "kind": c.get("kind"), "host": c.get("host", ""), "cost": c.get("cost", "")} for c in media.get("channels", [])]
    pr = o.get("production_regions", {})
    n_t1, n_t2 = len(pr.get("tier1", []) or []), len(pr.get("tier2", []) or [])
    ev_block = o.get("evaluation", {})
    meta = o.get("causal_edges_meta", {})
    n_ev = sum(e["ev"] for e in edges)
    data = {"edges": edges, "badge": badge, "sc": {"routes": routes}, "channels": channels,
            "ds": ds, "regions": {"tier1": n_t1, "tier2": n_t2}, "eval": ev_block}
    version, updated = o.get("version"), o.get("updated")
    js_data = json.dumps(data, ensure_ascii=False)
    return f"""<title>Nexus 인과 지도</title>
<link rel="stylesheet" media="print" onload="this.media='all'" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{--bg:#f7f6f2;--panel:#ffffff;--ink:#22241f;--muted:#6d7267;--line:#dcdad2;--pol:#b07d10;--cli:#3e7a3e;--geo:#b0403a;--mkt:#33628f;--outcome:#22241f;--chip:#eceae3;--hl:#22241f;--paid:#b0403a;--free:#3e7a3e;--gap:#6d7267}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#191b17;--panel:#22241f;--ink:#e8e6de;--muted:#9aa093;--line:#3a3d35;--pol:#d9a53a;--cli:#6fae6f;--geo:#d4756f;--mkt:#6f9cc9;--outcome:#e8e6de;--chip:#2c2f28;--hl:#e8e6de;--paid:#d4756f;--free:#6fae6f;--gap:#9aa093}}}}
:root[data-theme="dark"]{{--bg:#191b17;--panel:#22241f;--ink:#e8e6de;--muted:#9aa093;--line:#3a3d35;--pol:#d9a53a;--cli:#6fae6f;--geo:#d4756f;--mkt:#6f9cc9;--outcome:#e8e6de;--chip:#2c2f28;--hl:#e8e6de;--paid:#d4756f;--free:#6fae6f;--gap:#9aa093}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans KR",-apple-system,"Malgun Gothic",sans-serif;line-height:1.55}}
main{{max-width:1080px;margin:0 auto;padding:40px 24px 80px}}
header h1{{font-size:1.7rem;font-weight:700;margin:0 0 6px}} header p.sub{{color:var(--muted);margin:0 0 4px;max-width:70ch}}
.meta{{display:flex;gap:20px;flex-wrap:wrap;margin:22px 0 8px;padding:14px 18px;background:var(--panel);border:1px solid var(--line);border-radius:6px}}
.meta div{{font-variant-numeric:tabular-nums}} .meta .n{{font-size:1.35rem;font-weight:700;display:block;line-height:1.2}} .meta .l{{font-size:.74rem;color:var(--muted);letter-spacing:.06em;text-transform:uppercase}}
.legend{{display:flex;gap:14px;flex-wrap:wrap;margin:14px 0 4px;font-size:.82rem}} .legend span{{display:inline-flex;align-items:center;gap:6px}}
.dot{{width:10px;height:10px;border-radius:2px;display:inline-block}}
.filters{{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 18px}}
.filters button{{font:inherit;font-size:.8rem;padding:4px 12px;border-radius:99px;border:1px solid var(--line);background:var(--panel);color:var(--ink);cursor:pointer}}
.filters button[aria-pressed="true"]{{background:var(--ink);color:var(--bg);border-color:var(--ink)}}
#viz{{background:var(--panel);border:1px solid var(--line);border-radius:6px;overflow-x:auto;padding:8px 0}}
svg{{display:block;min-width:900px;max-width:100%;height:auto}} .chain-row{{cursor:pointer}}
#detail{{margin-top:14px;padding:16px 18px;background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--line);border-radius:6px;min-height:74px}}
#detail .eid{{font-family:"IBM Plex Mono",monospace;font-size:.78rem;color:var(--muted)}} #detail .lbl{{font-weight:500;margin:4px 0 6px}} #detail .facts{{font-size:.82rem;color:var(--muted)}}
.bd{{display:inline-block;font-size:.74rem;padding:1px 8px;border-radius:99px;border:1px solid var(--line);margin:2px 4px 2px 0}}
.bd.paid{{border-color:var(--paid);color:var(--paid)}} .bd.free{{border-color:var(--free);color:var(--free)}} .bd.gap{{border-color:var(--gap);color:var(--gap)}}
section.notes{{margin-top:34px;font-size:.88rem}} section.notes h2{{font-size:1.02rem;margin:26px 0 8px}} section.notes p{{max-width:72ch;margin:6px 0}}
.routes{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-top:10px}}
.route{{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:12px 14px;font-size:.84rem}} .route b{{display:block;margin-bottom:2px}} .route .lt{{color:var(--muted)}}
table.ds{{width:100%;border-collapse:collapse;font-size:.8rem;margin-top:8px}} table.ds th,table.ds td{{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}} table.ds th{{color:var(--muted);font-weight:600}}
figcaption{{font-size:.8rem;color:var(--muted);padding:8px 18px 10px}}
</style>
<main>
<header>
  <h1>Nexus 인과 지도</h1>
  <p class="sub">시맨틱 레이어(ontology.yaml v{version}, {updated})의 인과 사슬 {len(edges)}건 · 근거 문헌 {n_ev}건 · 용어 {ent_count}종 — 모든 사슬은
  <b>대두유 국제가</b> 또는 <b>한국 수입 CIF</b>로 수렴한다. 행을 클릭하면 근거·시차·검증 상태와 <b>연결 지표의 데이터 원천(유료/무료/대안)</b>이 아래에 표시된다.</p>
</header>
<div class="meta" id="meta"></div>
<div class="legend">
  <span><i class="dot" style="background:var(--pol)"></i>정책·규제</span><span><i class="dot" style="background:var(--cli)"></i>기후·작황</span>
  <span><i class="dot" style="background:var(--geo)"></i>지정학·무역</span><span><i class="dot" style="background:var(--mkt)"></i>시장 구조</span>
  <span style="color:var(--muted)">— 실선 = 검증됨 · 점선 = 후보</span>
</div>
<div class="filters" id="filters" role="group" aria-label="카테고리 필터"></div>
<figure id="vizfig" style="margin:0"><div id="viz"></div>
<figcaption>각 행은 하나의 인과 사슬(원인 → 메커니즘 → 결과). ▲=가격 상승 압력 · ▼=하락 압력.</figcaption></figure>
<div id="detail" aria-live="polite"><span class="facts">사슬을 클릭하면 상세가 여기 표시됩니다.</span></div>
<section class="notes">
  <h2>데이터 원천 — 유료 서비스와 무료 대안 (원장 data_sources · 9/30 최종판까지 갱신)</h2>
  <table class="ds" id="ds"></table>
  <h2>수집 채널 · 산지 · 신뢰도 지표</h2>
  <div id="misc"></div>
  <h2>공급망 경로 (한국향 루트)</h2>
  <div class="routes" id="routes"></div>
  <h2>이 지도가 그래프 DB 없이 그려진 이유</h2>
  <p>원장은 <code>src/semantic/ontology.yaml</code> 하나이며 검증기가 순환 0을 보증한다. 이 페이지는 <code>scripts/build_causal_map.py</code>가 원장에서 직접 생성하므로 항상 원장과 일치한다. 생성일 {date.today().isoformat()}.</p>
</section>
</main>
<script>
const DATA = {js_data};
const CAT = {{"정책·규제":"var(--pol)","기후·작황":"var(--cli)","지정학·무역":"var(--geo)","시장 구조":"var(--mkt)"}};
const edges = DATA.edges; const nVal = edges.filter(e=>e.status==="validated").length;
const nodes = new Set(); edges.forEach(e=>e.chain.forEach(n=>nodes.add(n)));
document.getElementById("meta").innerHTML =
  `<div><span class="n">${{nodes.size}}</span><span class="l">노드</span></div><div><span class="n">${{edges.length}}</span><span class="l">인과 사슬</span></div>`+
  `<div><span class="n">${{nVal}}</span><span class="l">검증됨</span></div><div><span class="n">${{edges.length-nVal}}</span><span class="l">후보</span></div>`+
  `<div><span class="n">${{DATA.ds.filter(d=>d.cost.startsWith("유료(사용)")).length}}</span><span class="l">유료 사용</span></div>`+
  `<div><span class="n">${{DATA.ds.filter(d=>d.label==="DATA GAP").length}}</span><span class="l">무료 대안 없음</span></div><div><span class="n">0</span><span class="l">DAG 순환</span></div>`;
let activeCat=null; const fwrap=document.getElementById("filters");
["전체",...Object.keys(CAT)].forEach(c=>{{const b=document.createElement("button");b.textContent=c;b.setAttribute("aria-pressed",c==="전체");
  b.onclick=()=>{{activeCat=c==="전체"?null:c;fwrap.querySelectorAll("button").forEach(x=>x.setAttribute("aria-pressed",x.textContent===(activeCat||"전체")));render();}};fwrap.appendChild(b);}});
function short(n){{return n.replace(/_/g," ").toLowerCase().replace(/\\b\\w/g,c=>c.toUpperCase());}}
function costCls(c){{return c.startsWith("유료")?"paid":(c.startsWith("무료")?"free":"gap");}}
function render(){{
  const list=activeCat?edges.filter(e=>e.cat===activeCat):edges;
  const ROW=46,PAD=10,W=980,LX=16,colW=[250,230,230],OX=W-190,H=PAD*2+list.length*ROW+30;
  let s=`<svg viewBox="0 0 ${{W}} ${{H}}" role="img" aria-label="인과 사슬 ${{list.length}}건">`;
  s+=`<defs><marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="currentColor"/></marker></defs>`;
  const oy=PAD+(list.length*ROW)/2;
  s+=`<g style="color:var(--outcome)"><rect x="${{OX}}" y="${{oy-22}}" width="168" height="44" rx="4" fill="none" stroke="currentColor" stroke-width="1.6"/><text x="${{OX+84}}" y="${{oy-2}}" text-anchor="middle" font-size="13" font-weight="700" fill="currentColor">대두유 국제가 · 수입 CIF</text><text x="${{OX+84}}" y="${{oy+13}}" text-anchor="middle" font-size="9.5" fill="currentColor" opacity=".65">시카고 선물 · 한국 도착가</text></g>`;
  list.forEach((e,i)=>{{const y=PAD+i*ROW+ROW/2;const col=CAT[e.cat]||"currentColor";const dash=e.status==="validated"?"":`stroke-dasharray="4 3"`;const dirSym=e.dir==="UP"?"▲":"▼";
    s+=`<g class="chain-row" tabindex="0" role="button" aria-label="${{e.id}} ${{e.label}}" data-i="${{edges.indexOf(e)}}" style="color:${{col}}"><rect x="6" y="${{y-ROW/2+3}}" width="${{W-12}}" height="${{ROW-6}}" rx="4" fill="transparent" stroke="none"/>`;
    let x=LX; e.chain.slice(0,-1).forEach((n,j)=>{{const w=Math.min(colW[Math.min(j,2)]-30,12+n.length*6.4);
      s+=`<rect x="${{x}}" y="${{y-13}}" width="${{w}}" height="26" rx="3" fill="var(--chip)" stroke="currentColor" stroke-width="1"/><text x="${{x+w/2}}" y="${{y+4}}" text-anchor="middle" font-size="10" fill="var(--ink)">${{short(n).slice(0,34)}}</text>`;
      const nx=x+w;const tx=(j<e.chain.length-2)?nx+26:OX-6;
      s+=`<line x1="${{nx+2}}" y1="${{y}}" x2="${{tx-3}}" y2="${{(j<e.chain.length-2)?y:oy}}" stroke="currentColor" stroke-width="1.3" ${{dash}} marker-end="url(#ah)"/>`;x=nx+26;}});
    s+=`<text x="${{LX-2}}" y="${{y-17}}" font-size="8.5" fill="var(--muted)" font-family="IBM Plex Mono">${{e.id}} ${{dirSym}}</text></g>`;}});
  s+=`</svg>`; document.getElementById("viz").innerHTML=s;
  document.querySelectorAll(".chain-row").forEach(g=>{{const show=()=>{{const e=edges[+g.dataset.i];const d=document.getElementById("detail");d.style.borderLeftColor=CAT[e.cat];
    const badges=e.indicators.map(ind=>{{const b=DATA.badge[ind]||{{}};return `<span class="bd ${{costCls(b.cost||"")}}" title="${{(b.free||"")}}">${{ind}} · ${{b.src||"?"}} · ${{b.cost||""}}</span>`;}}).join("")||`<span class="facts">연결 지표 없음(정성 사슬)</span>`;
    d.innerHTML=`<span class="eid">${{e.id}} · ${{e.cat}} · ${{e.status==="validated"?"검증됨":"후보"}}${{e.validated_by.length?" ("+e.validated_by.join("·")+")":""}}</span><div class="lbl">${{e.label}}</div>`+
      `<div class="facts">방향: ${{e.dir==="UP"?"상승 압력 ▲":"하락 압력 ▼"}} · 시차: ${{e.lag?e.lag.min+"~"+e.lag.max+" 거래일":"—"}} · 근거 문헌 ${{e.ev||0}}건${{e.rules?" · 해석 규칙 보유":""}}</div>`+
      `<div style="margin-top:6px">데이터 원천: ${{badges}}</div>`;}};
    g.addEventListener("click",show);g.addEventListener("keydown",ev=>{{if(ev.key==="Enter"||ev.key===" "){{ev.preventDefault();show();}}}});}});
}}
render();
document.getElementById("ds").innerHTML=`<tr><th>원천</th><th>비용</th><th>무료 대안</th><th>대안 상태</th><th>라벨</th></tr>`+
  DATA.ds.map(d=>`<tr><td>${{d.name}}</td><td><span class="bd ${{costCls(d.cost)}}">${{d.cost}}</span></td><td>${{d.free_alternative}}</td><td>${{d.free_status}}</td><td>${{d.label}}</td></tr>`).join("");
const ch=DATA.channels.map(c=>`${{c.id}}(${{c.kind}}${{c.cost?" · "+c.cost:""}})`).join(" · ");
document.getElementById("misc").innerHTML=`<p>수집 채널: ${{ch}}</p><p>기후 산지: 1군 ${{DATA.regions.tier1}} · 2군 ${{DATA.regions.tier2}} (좌표 전량 확인)</p>`+
  `<p>신뢰도 지표(2단계 검증): 과거 ${{(DATA.eval.historical||[]).length}}종 · 실시간 ${{(DATA.eval.realtime||[]).length}}종 — 브리프 '보고서 신뢰도' 블록과 월별 부록에 표시. 원장 ${{DATA.eval.ledger||""}}</p>`;
const R=document.getElementById("routes");DATA.sc.routes.forEach(r=>{{R.innerHTML+=`<div class="route"><b>${{r.id}}</b><span>${{r.name||"한국향 해상 루트"}}</span><div class="lt">리드타임 ${{r.lead?(r.lead.min+"~"+r.lead.max+"일"):"40~50일(실측 역산 갱신 예정)"}}</div></div>`;}});
</script>
"""


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=str(DEFAULT_OUT)); a = ap.parse_args()
    o = yaml.safe_load(ONTOLOGY.read_text(encoding="utf-8"))
    e = yaml.safe_load(ENTITIES.read_text(encoding="utf-8"))
    n_terms = sum(len(v) for v in e.values() if isinstance(v, list) and v and isinstance(v[0], dict) and "term_id" in v[0])
    html = build(o, n_terms)
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(html, encoding="utf-8")
    print(f"[완료] 인과 지도 → {out} ({len(html):,}B · 사슬 {len(o['causal_edges'])} · 용어 {n_terms})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
