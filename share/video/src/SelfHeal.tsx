import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import tlJson from './timeline.json';
import dataJson from './data.json';
import claims from '../../claims.json';
// house style from tasty_tunez/promo (symlinked as kit/)
import {label, px, sig, useHouseFonts} from '../kit/src/tunez/Promo';
import {Hop, Slot, TypeOn, Words} from '../kit/src/tunez/type';
import {F, P, arrive, carry, cells, on} from '../kit/src/tunez/lib';

// "When does a value earn a token?": a real 48px in Carbon, the desire-path question, what's solved, the real
// problem, four tests, and the question back to designers. Every time comes from timeline.json, every number from
// share/claims.json (recompute.py) or data.json (prep.py).

/* eslint-disable @typescript-eslint/no-explicit-any */
const tl = tlJson as any;
const D = dataJson as any;
const K = claims as any;
const W = 1080, H = 1920, M = 48, CW = W - 2 * M;
const pct = (x: number, d = 1) => `${(x * 100).toFixed(d)}%`;

/** One big Hopscotch line; `\n` splits it into lines that land one after another. */
const Big: React.FC<{text: string; t: number; t0: number; size?: number}> = ({text, t, t0, size = 72}) => (
  <div style={{fontFamily: F.play, fontSize: size, lineHeight: `${size + 8}px`, color: P.ink}}>
    {text.split('\n').map((ln, i) => <div key={i}><Hop text={ln} t={t} t0={t0 + i * 0.3} bpm={80} size={size} /></div>)}
  </div>
);
const Running: React.FC<{text: string; t: number; t0: number; size?: number; color?: string}> = ({text, t, t0, size = 40, color = P.ink}) => (
  <div style={{fontFamily: F.text, fontWeight: 700, fontSize: size, lineHeight: `${size + 8}px`, color}}><Words text={text} t={t} t0={t0} stagger={0.04} /></div>
);
const at = (top: number, children: React.ReactNode, left = M, width = CW) => <div style={{position: 'absolute', left, top, width}}>{children}</div>;

// ---------- chrome (the DiveV pattern: typed chapter label, cell progress bar, rules, source footer) ----------

const FOOT: string[] = [
  'SOURCE · CARBON DESIGN SYSTEM (IBM) · REAL GIT HISTORY, MINED LOCALLY',
  'SOURCE · CARBON DESIGN SYSTEM (IBM) · $SPACING-3XL ADDED 17 JAN 2018, PR #506',
  `SOURCE · ${K.carbon_fix_labels} DRIFT FIXES IN ${K.carbon_fix_commits} CARBON COMMITS · LITERAL REPLACED BY A TOKEN`,
  'SOURCE · CARBON · A VALUE NO TOKEN HAS, USED 3+ TIMES IN 2+ FILES · OUTCOME 24 MONTHS LATER',
  'SYNTHETIC = 5 GENERATED REPOS · CARBON = REAL HISTORY · SELFHEAL RESEARCH',
  'SELFHEAL · SELF-HEALING DESIGN SYSTEMS RESEARCH',
];

const Chrome: React.FC<{t: number}> = ({t}) => {
  const ch = tl.chapters as [number, string][];
  const si = ch.reduce((acc, [t0], i) => (t >= t0 ? i : acc), 0);
  return (
    <>
      <div style={{...label, position: 'absolute', left: M, top: 48}}>
        <TypeOn text={`0${si + 1} · ${ch[si][1]}`} t={t} t0={si === 0 ? -1 : ch[si][0]} />
      </div>
      <div style={{position: 'absolute', right: M, top: 46, display: 'flex', gap: 4}}>
        {ch.map((_, i) => (
          <div key={i} style={{width: 16, height: 16, boxSizing: 'border-box', background: i <= si ? P.cobalt : 'transparent', border: i <= si ? 'none' : `2px solid ${P.rule}`}} />
        ))}
      </div>
      <div style={{position: 'absolute', left: M, right: M, top: 88, height: 2, background: P.rule}} />
      <div style={{position: 'absolute', left: M, right: M, top: H - 120, height: 2, background: P.rule}} />
      <div style={{...label, position: 'absolute', left: M, top: H - 96, width: CW, lineHeight: '32px'}}>{FOOT[si]}</div>
    </>
  );
};

// ---------- 01 · the moment ----------

const MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
const Moment: React.FC<{t: number}> = ({t}) => {
  const m = tl.moment;
  const lines = D.lines as {file: string; prop: string}[];
  const n = cells(t, m.lines, lines.length, m.step);
  // the date runs Feb 2016 (first hand-written 48px) to Jan 2018 (the token) while the lines land
  const span = (lines.length - 1) * m.step;
  const mi = 1 + Math.round(Math.min(1, Math.max(0, (t - m.lines) / span)) * 23);
  const date = `${MONTHS[mi % 12]} ${2016 + Math.floor(mi / 12)}`;
  const line = t < m.again ? 'Someone typed 48px.' : t < m.again2 ? 'Again.' : 'And again.';
  const lt0 = t < m.again ? m.lines + 0.2 : t < m.again2 ? m.again : m.again2;
  return (
    <>
      {at(136, <div style={label}><TypeOn text="CARBON DESIGN SYSTEM · 48PX TYPED BY HAND" t={t} t0={0.1} /></div>)}
      {at(196, lines.slice(0, n).map((l, i) => (
        <div key={i} style={{display: 'flex', fontFamily: F.mono, fontSize: 32, lineHeight: '58px', height: 58, borderBottom: `2px solid ${P.faint}`, whiteSpace: 'pre'}}>
          <span style={{color: P.muted, width: 500}}>{l.file}</span>
          <span style={{color: P.ink}}>{l.prop}: </span>
          <span style={{color: P.vermilion, fontWeight: 600}}>48px</span>
          <span style={{color: P.ink}}>;</span>
        </div>
      )))}
      {at(1050, (
        <div style={{display: 'flex', alignItems: 'baseline', gap: 32}}>
          <span style={px(96)}>{on(t, m.lines) ? date : 'FEB 2016'}</span>
          <span style={label}>NO 48PX TOKEN YET</span>
        </div>
      ))}
      {at(1220, <Big key={line} text={line} t={t} t0={lt0} size={96} />)}
      {on(t, m.tally) && at(1480, (
        <div style={{display: 'flex', gap: 48}}>
          {[[String(K['48_uses_before_token']), 'TIMES'], [String(K['48_files_before_token']), 'FILES'], ['0', 'TOKENS']].map(([v, l], i) => (
            <div key={l}>
              <div style={{...px(120), color: i === 2 ? P.vermilion : P.ink}}><Slot value={v} t={t} t0={m.tally + i * 0.12} /></div>
              <div style={{...label, marginTop: 16}}>{l}</div>
            </div>
          ))}
        </div>
      ))}
    </>
  );
};

// ---------- 02 · the question: a desire path ----------

const LC = 24, LR = 17, LP = CW / LC;
const LAWN_TOP = 160;
// paved L: along the bottom, then up the right side; the worn path cuts the corner
const PAVED = new Set<string>();
for (let x = 1; x <= 21; x++) { PAVED.add(`${x},14`); PAVED.add(`${x},15`); }
for (let y = 1; y <= 15; y++) { PAVED.add(`20,${y}`); PAVED.add(`21,${y}`); }
const WORN: [number, number][] = [];
for (let k = 0; k <= 26; k++) {
  const x = Math.round(2 + (k / 26) * 17), y = Math.round(13 - (k / 26) * 12);
  for (const [dx, dy] of [[0, 0], [1, 0]]) {
    const key = `${x + dx},${y + dy}`;
    if (!PAVED.has(key) && !WORN.some(([a, b]) => `${a},${b}` === key)) WORN.push([x + dx, y + dy]);
  }
}

const Lawn: React.FC<{t: number}> = ({t}) => {
  const q = tl.question;
  const worn = cells(t, q.path, WORN.length, 0.05);
  const paved = on(t, q.paved) ? cells(t, q.paved, WORN.length, 0.03) : 0;
  return (
    <svg width={CW} height={LR * LP} style={{position: 'absolute', left: M, top: LAWN_TOP}}>
      {Array.from({length: LC * LR}, (_, i) => {
        const x = i % LC, y = Math.floor(i / LC);
        return PAVED.has(`${x},${y}`)
          ? <rect key={i} x={x * LP} y={y * LP} width={LP - 4} height={LP - 4} fill={P.cobalt} />
          : <rect key={i} x={x * LP + LP / 2 - 5} y={y * LP + LP / 2 - 5} width={8} height={8} fill={P.rule} />;
      })}
      {WORN.slice(0, worn).map(([x, y], i) => <rect key={`w${i}`} x={x * LP} y={y * LP} width={LP - 4} height={LP - 4} fill={i < paved ? P.cobalt : P.vermilion} />)}
    </svg>
  );
};

const Question: React.FC<{t: number}> = ({t}) => {
  const q = tl.question;
  const line = t < q.named ? 'A mistake? Or a decision\nthe system hasn’t\ncaught up to yet?' : t < q.paved ? 'A desire path.' : 'Two years later,\nCarbon paved it.';
  const lt0 = t < q.named ? q.ask : t < q.paved ? q.named : q.paved + 0.4;
  return (
    <>
      {at(124, <div style={label}><TypeOn text={on(t, q.named) ? 'DESIRE PATH · THE TRAIL WORN WHERE PEOPLE ACTUALLY WALK' : 'THE SYSTEM · ITS PAVED PATHS'} t={t} t0={on(t, q.named) ? q.named : q.in + 0.1} /></div>)}
      <Lawn t={t} />
      {at(LAWN_TOP + LR * LP + 48, <Big key={line} text={line} t={t} t0={lt0} size={line.includes('\n') ? 80 : 96} />)}
      {on(t, q.named + 0.6) && !on(t, q.paved) && at(1100, <Running text="The shortcut people wear into the grass, where they actually walk instead of the paved route." t={t} t0={q.named + 0.6} size={40} color={P.muted} />)}
      {on(t, q.paved) && at(1500, (
        <div style={{background: P.sheet, border: `2px solid ${P.rule}`, padding: '28px 32px'}}>
          <div style={{fontFamily: F.mono, fontSize: 44, lineHeight: '56px', color: P.ink}}>
            <TypeOn text="$spacing-3xl → 48px" t={t} t0={q.paved + 0.2} rate={0.04} />
          </div>
          <div style={{...label, marginTop: 12}}>ADDED 17 JAN 2018 · CARBON PR #506</div>
        </div>
      ))}
    </>
  );
};

// ---------- 03 · what's solved ----------

const Solved: React.FC<{t: number}> = ({t}) => {
  const s = tl.solved;
  const fixes = D.fixes as boolean[];
  const cols = 16, pitch = CW / cols, size = pitch - 8;
  const n = cells(t, s.grid, fixes.length, s.step);
  const right = fixes.filter(Boolean).length;
  return (
    <>
      {at(136, <div style={label}><TypeOn text={`${fixes.length} REAL DRIFT FIXES FROM CARBON'S HISTORY`} t={t} t0={s.in + 0.1} /></div>)}
      <svg width={CW} height={Math.ceil(fixes.length / cols) * pitch} style={{position: 'absolute', left: M, top: 196}}>
        {fixes.map((ok, i) => {
          const x = (i % cols) * pitch, y = Math.floor(i / cols) * pitch;
          return i < n
            ? <rect key={i} x={x} y={y} width={size} height={size} fill={ok ? P.cobalt : P.vermilion} />
            : <rect key={i} x={x + 1} y={y + 1} width={size - 2} height={size - 2} fill="none" stroke={P.rule} strokeWidth={2} />;
        })}
      </svg>
      {at(196 + 10 * pitch + 16, (
        <div style={{display: 'flex', gap: 40}}>
          {[[P.cobalt, 'NEAREST TOKEN = THE HUMAN’S PICK'], [P.vermilion, 'A DIFFERENT PICK']].map(([c, l]) => (
            <div key={l} style={{display: 'flex', alignItems: 'center', gap: 12}}>
              <div style={{width: 24, height: 24, background: c}} />
              <span style={{...label, color: P.ink}}>{l}</span>
            </div>
          ))}
        </div>
      ))}
      {on(t, s.num) && at(940, <div style={px(220)}><Slot value={pct(K.carbon_nearest_acc)} t={t} t0={s.num} /></div>)}
      {on(t, s.num + 0.4) && at(1190, <Running text={`Snap each stray value to the nearest token. It picks what the human picked, ${right} of ${fixes.length} times.`} t={t} t0={s.num + 0.4} size={40} color={P.muted} />)}
      {on(t, s.line) && at(1420, <Big text={'Your linter already\nhandles this.'} t={t} t0={s.line + 0.6} size={88} />)}
    </>
  );
};

// ---------- 04 · the real problem ----------

const fmtV = (v: number) => `${Number.isInteger(v) ? v : v}px`;
const Problem: React.FC<{t: number}> = ({t}) => {
  const p = tl.problem;
  const C = D.clusters as {v: number; label: string}[];
  const cols = 20, pitch = CW / cols;
  const n = cells(t, p.dots, C.length, 0.015);
  const lit = on(t, p.light);
  const desire = C.filter((c) => c.label === 'desire').map((c) => c.v).sort((a, b) => a - b);
  const line = t < p.cards ? `${C.length} values kept repeating.\n${desire.length} became tokens.` : 'In one snapshot,\nthey look the same.';
  const pair = [['48', K.pair_48px], ['42', K.pair_42px]] as [string, any][];
  const rv = on(t, p.reveal);
  return (
    <>
      {at(136, <div style={label}><TypeOn text="OFF-SPEC VALUES THAT KEPT REPEATING · CARBON" t={t} t0={p.in + 0.1} /></div>)}
      <svg width={CW} height={6 * pitch} style={{position: 'absolute', left: M, top: 196}}>
        {C.slice(0, n).map((c, i) => {
          const hot = lit && c.label === 'desire';
          const r = hot ? pitch * 0.42 : pitch * 0.26;
          return <circle key={i} cx={(i % cols) * pitch + pitch / 2} cy={Math.floor(i / cols) * pitch + pitch / 2} r={r} fill={hot ? P.vermilion : lit ? P.rule : P.ink} />;
        })}
      </svg>
      {lit && at(196 + 6 * pitch + 16, <div style={{...label, color: P.vermilion}}><TypeOn text={`BECAME TOKENS: ${desire.join(' · ')} PX`} t={t} t0={p.light + 0.2} /></div>)}
      {at(640, <Big key={line} text={line} t={t} t0={t < p.cards ? p.dots + 0.4 : p.cards + 0.3} size={72} />)}
      {on(t, p.cards) && at(880, (
        <div style={{display: 'flex', gap: 24}}>
          {pair.map(([v, c], i) => {
            const k = arrive(t, p.cards + i * 0.15, 0.4);
            const good = c.label === 'desire';
            return (
              <div key={v} style={{width: (CW - 24) / 2, opacity: k, transform: `translateY(${(1 - k) * 24}px)`}}>
                <div style={{background: P.sheet, border: `2px solid ${P.rule}`, padding: 32, boxSizing: 'border-box', height: 400}}>
                  <div style={px(140)}>{v}px</div>
                  <div style={{...label, color: P.ink, marginTop: 32, lineHeight: '40px'}}>{c.month.replace('2016-02', 'FEB 2016')}<br />{c.uses} USES · {c.files} FILES<br />NO TOKEN</div>
                </div>
                <div style={{height: 160, marginTop: 16, boxSizing: 'border-box', padding: '24px 32px', background: rv ? (good ? P.vermilion : P.faint) : 'transparent', border: rv ? 'none' : `2px dashed ${P.rule}`}}>
                  {rv ? (
                    <>
                      <div style={{...label, color: P.ink}}>{good ? 'BY JAN 2018' : 'TWO YEARS LATER'}</div>
                      <div style={{fontFamily: F.text, fontWeight: 700, fontSize: 34, lineHeight: '42px', color: P.ink, marginTop: 12, whiteSpace: 'nowrap'}}>{good ? 'Became $spacing-3xl' : 'Faded. No token.'}</div>
                    </>
                  ) : <div style={{...label, lineHeight: '112px'}}>WHAT HAPPENS NEXT?</div>}
                </div>
              </div>
            );
          })}
        </div>
      ))}
      {on(t, p.reveal + 0.8) && at(1600, <div style={{...label, lineHeight: '32px'}}>{`${desire.length} IS A SMALL SAMPLE. OF ${C.length}: ${K.carbon_cluster_labels.drift} FADED, ${K.carbon_cluster_labels.unresolved} STAYED WITHOUT A TOKEN, ${K.carbon_cluster_labels.coincident} GOT A TOKEN NOBODY MOVED TO, ${K.carbon_cluster_labels.censored} TOO RECENT.`}</div>)}
    </>
  );
};

// ---------- 05 · four tests ----------

type Bar = [string, number, string];
type Test = {name: string; sub: string; bars: Bar[]; result: string; note: string; verdict: string; vc: string};
const VOTES = K.carbon_votes_precision, BASE = K.carbon_base_rate;
const [BIND_OK, BIND_N] = (K.synth_ambiguous_bind_correct as string).split('/').map(Number);
const TESTS: Test[] = [
  {name: 'PICK THE RIGHT TOKEN', sub: 'SYNTHETIC · IN-BETWEEN VALUES', bars: [['PICKED RIGHT', BIND_OK / BIND_N, P.cobalt]],
    result: `${BIND_OK} of ${BIND_N} right`, note: 'When it maps an in-between value to a token.', verdict: 'SOLVED', vc: P.cobalt},
  {name: 'TYPO OR NEW TOKEN?', sub: 'EVERY REPEATING VALUE CALLED A NEW TOKEN', bars: [['CARBON', BASE, P.vermilion], ['SYNTHETIC', K.synth_newtoken_precision, P.tint]],
    result: `${pct(BASE, 0)} right on Carbon`, note: `${K.carbon_desire_vs_drift.split(' ')[0]} of ${Number(K.carbon_desire_vs_drift.split(' ')[0]) + Number(K.carbon_desire_vs_drift.split(' ')[2])} real. Synthetic: ${pct(K.synth_newtoken_precision, 0)}.`, verdict: 'OPEN', vc: P.vermilion},
  {name: 'ADD TIME HISTORY', sub: 'BURST · AUTHORS · DID IT SURVIVE', bars: [['SIM. BEFORE', K.synth_newtoken_precision, P.tint], ['SIM. + TIME', K.synth_time_newtoken_precision, P.cobalt], ['CARBON BEFORE', BASE, P.rule], ['CARBON + TIME', VOTES, P.vermilion]],
    result: 'Near chance on Carbon', note: `Helped on simulated history (${pct(K.synth_newtoken_precision, 0)} → ${pct(K.synth_time_newtoken_precision, 0)}). Carbon: ${pct(BASE, 0)} → ${pct(VOTES, 0)}.`, verdict: 'OPEN', vc: P.vermilion},
  {name: 'FRONTIER AGENTS', sub: 'SYNTHETIC · 5 REPOS · FIX-OR-KEEP ACCURACY', bars: [['OPUS 5.5', K.agent_opus_action_acc, P.cobalt], ['CODEX', K.agent_codex_action_acc, P.cobalt], ['OUR MODEL', K.synth_model_action_acc, P.ink], ['SONNET 5.5', K.agent_sonnet_action_acc, P.rule]],
    result: 'The best agents win', note: `Opus 5.5 ${pct(K.agent_opus_action_acc)} vs our model ${pct(K.synth_model_action_acc)}. Sonnet 5.5 trails.`, verdict: 'AGENTS AHEAD', vc: P.ink},
];

const Chart: React.FC<{bars: Bar[]; w: number; h: number; k: number}> = ({bars, w, h, k}) => {
  const bh = Math.min(56, (h - (bars.length - 1) * 12) / bars.length), lw = 210, cw = w - lw, nc = 20;
  return (
    <svg width={w} height={h}>
      {bars.map(([l, v, c], i) => {
        const y = (h - bars.length * bh - (bars.length - 1) * 12) / 2 + i * (bh + 12);
        const filled = Math.round(v * nc * Math.min(1, k * 1.2));
        return (
          <g key={l}>
            <text x={0} y={y + bh / 2 + 8} fontFamily={F.tick} fontSize={20} letterSpacing={2} fill={P.muted}>{l}</text>
            {Array.from({length: nc}, (_, j) => (
              <rect key={j} x={lw + j * (cw / nc)} y={y} width={cw / nc - 3} height={bh} fill={j < filled ? c : 'none'} stroke={j < filled ? 'none' : P.faint} strokeWidth={2} />
            ))}
          </g>
        );
      })}
    </svg>
  );
};

const Tests: React.FC<{t: number}> = ({t}) => {
  const ts = tl.tests;
  const top0 = 120, rowH = (1780 - top0) / 4, cw = 480;
  return (
    <>
      {TESTS.map((x, i) => {
        if (!on(t, ts.in + i * 0.07)) return null;
        const t0 = ts.rows[i];
        const k = Math.min(1, Math.max(0, (t - t0) / 0.9));
        const live = t >= t0 && t < t0 + 3.6;
        return (
          <div key={i} style={{position: 'absolute', left: M, top: top0 + i * rowH, width: CW, height: rowH}}>
            {i > 0 && <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 2, background: P.rule}} />}
            <div style={{position: 'absolute', left: 0, top: 36, width: cw, height: rowH - 72, outline: live ? `4px solid ${P.cobalt}` : 'none', outlineOffset: 8}}>
              <Chart bars={x.bars} w={cw} h={rowH - 72} k={t >= t0 ? k : 0} />
            </div>
            <div style={{position: 'absolute', left: cw + 40, top: 36, width: CW - cw - 40}}>
              <div style={{...label, color: t >= t0 ? P.ink : P.muted}}>{String(i + 1).padStart(2, '0')} · {x.name}</div>
              <div style={{...label, marginTop: 10, lineHeight: '32px'}}>{x.sub}</div>
              {t >= t0 + 0.6 && (
                <>
                  <div style={{fontFamily: F.text, fontWeight: 700, fontSize: 40, lineHeight: '46px', color: P.ink, marginTop: 16}}><TypeOn text={x.result} t={t} t0={t0 + 0.6} rate={0.02} /></div>
                  <div style={{fontFamily: F.text, fontWeight: 400, fontSize: 28, lineHeight: '34px', color: P.muted, marginTop: 8}}><Words text={x.note} t={t} t0={t0 + 0.8} /></div>
                </>
              )}
              {t >= t0 + 1.6 && (
                <div style={{display: 'inline-block', marginTop: 16, padding: '8px 14px', background: x.vc, ...label, color: x.vc === P.ink || x.vc === P.cobalt ? P.onCobalt : P.ink}}>{x.verdict}</div>
              )}
            </div>
          </div>
        );
      })}
    </>
  );
};

// ---------- 06 · your turn, then the dh card ----------

const Close: React.FC<{t: number}> = ({t}) => {
  const c = tl.close;
  const q = on(t, c.q);
  return (
    <>
      {!q && at(700, <Big text={'Picking the token\nis solved.'} t={t} t0={c.in + 0.3} size={96} />)}
      {q && at(560, (
        <>
          <div style={{...label, marginBottom: 40}}><TypeOn text="THE OPEN QUESTION · FOR DESIGNERS" t={t} t0={c.q} /></div>
          <Big text={'How does your\nteam decide when\na value earns\na token?'} t={t} t0={c.q + 0.2} size={104} />
        </>
      ))}
      {q && on(t, c.q + 1.8) && at(1240, (
        <div style={{display: 'flex', alignItems: 'center', gap: 24}}>
          <div style={{width: 24, height: 24, background: P.vermilion}} />
          <span style={{fontFamily: F.mono, fontSize: 36, lineHeight: '44px', color: P.ink}}>{c.link}</span>
        </div>
      ))}
    </>
  );
};

const MARK = ['...X...', '...X...', '...X...', 'XXXXXXX', 'X..X..X', 'X..X..X', 'XXXX..X'];
const Mark: React.FC<{cell: number; n?: number}> = ({cell, n = 99}) => {
  const pts = MARK.flatMap((r, y) => [...r].map((ch, x) => (ch === 'X' ? [x, y] : null)).filter(Boolean)) as number[][];
  pts.sort((a, b) => (a[0] === 3 && b[0] !== 3 ? -1 : b[0] === 3 && a[0] !== 3 ? 1 : a[1] - b[1] || a[0] - b[0]));
  return <svg width={cell * 7} height={cell * 7}>{pts.slice(0, n).map(([x, y]) => <rect key={`${x}-${y}`} x={x * cell} y={y * cell} width={cell} height={cell} fill={P.ink} />)}</svg>;
};

const DhCard: React.FC<{t: number}> = ({t}) => {
  const t0 = tl.close.dh;
  return (
    <AbsoluteFill style={{background: P.paper, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 56}}>
      <Mark cell={48} n={cells(t, t0, 21, 0.05)} />
      <div style={{textAlign: 'center', opacity: on(t, t0 + 1.2) ? 1 : 0}}>
        <div style={{fontFamily: F.text, fontWeight: 700, fontSize: 56, lineHeight: '64px', color: P.ink}}>David Hatley</div>
        <div style={{...sig, fontSize: 28, lineHeight: '36px', marginTop: 12}}>design · AI/ML · generative tools</div>
        <div style={{...label, marginTop: 48}}>{tl.close.link}</div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- the cut ----------

export const SelfHealV: React.FC = () => {
  useHouseFonts();
  const t = useCurrentFrame() / tl.fps;
  if (t >= tl.close.dh) return <DhCard t={t} />;
  const scene = t < tl.question.in ? <Moment t={t} /> : t < tl.solved.in ? <Question t={t} /> : t < tl.problem.in ? <Solved t={t} />
    : t < tl.tests.in ? <Problem t={t} /> : t < tl.close.in ? <Tests t={t} /> : <Close t={t} />;
  return (
    <AbsoluteFill style={{background: P.paper}}>
      <Chrome t={t} />
      {scene}
    </AbsoluteFill>
  );
};

/** Feed still: the two identical snapshots and what became of them. */
export const SelfHealSquare: React.FC = () => {
  useHouseFonts();
  const p = tl.problem;
  const t = p.reveal + 3;
  return (
    <AbsoluteFill style={{background: P.paper}}>
      <div style={{position: 'absolute', left: 0, top: -536, width: W, height: H}}><Problem t={t} /></div>
      <div style={{position: 'absolute', left: 0, top: 0, width: W, height: 96, background: P.paper}} />
      <div style={{...label, position: 'absolute', left: M, top: 48}}>CARBON DESIGN SYSTEM · FEB 2016</div>
      <div style={{position: 'absolute', left: M, right: M, top: 88, height: 2, background: P.rule}} />
      <div style={{position: 'absolute', left: M, right: M, top: 968, height: 2, background: P.rule}} />
      <div style={{...label, position: 'absolute', left: M, top: 992, width: CW, lineHeight: '32px'}}>SOURCE · CARBON GIT HISTORY · SAME MONTH, SAME COUNTS, DIFFERENT FATES</div>
    </AbsoluteFill>
  );
};

export const FRAMES = Math.round(tl.total * tl.fps);
