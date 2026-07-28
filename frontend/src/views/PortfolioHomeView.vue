<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'

/* ══ 可配置区：词表与文案都在这里 ═══════════════════════════════
   g 决定字体语言：fin=衬线（旧世界） tech=等宽（新世界） life=细体（生活）
   两个世界的词混在同一片天上，视觉差异本身就把故事讲完了。          */
const WORDS = [
  { t: '复利', g: 'fin' }, { t: '风险', g: 'fin' }, { t: '套利', g: 'fin' },
  { t: '市场', g: 'fin' }, { t: '回测', g: 'fin' }, { t: '波动率', g: 'fin' },
  { t: 'Alpha', g: 'fin' }, { t: 'Signal', g: 'fin' },

  { t: 'Agent', g: 'tech' }, { t: '上下文', g: 'tech' }, { t: '推理', g: 'tech' },
  { t: '并发', g: 'tech' }, { t: '收敛', g: 'tech' }, { t: '泛化', g: 'tech' },
  { t: 'Context', g: 'tech' }, { t: 'Latency', g: 'tech' },
  { t: 'Prompt', g: 'tech' }, { t: 'Vector', g: 'tech' },

  { t: '厨房', g: 'life' }, { t: '塔罗', g: 'life' }, { t: '写作', g: 'life' },
  { t: '好奇', g: 'life' }, { t: '直觉', g: 'life' }, { t: '咖啡', g: 'life' },
  { t: 'Kitchen', g: 'life' }, { t: 'Tarot', g: 'life' }, { t: 'Blog', g: 'life' },
  { t: 'Questions', g: 'life' }, { t: 'Curiosity', g: 'life' },
  { t: '在路上', g: 'life' }, { t: '深夜', g: 'life' }, { t: 'Sketch', g: 'life' },
]

const LINES = ['你好，我是 LZQ.', '猛猛干 就是玩。', '技术理想，一直在路上。']
const SUBS = ['personal site · still walking', '猛猛干 就是玩', 'building small worlds']

const MODULES = [
  { to: '/kitchen',     label: '私人厨房', cls: 'ms-cook',  dx: -232, dy: -104 },
  { to: '/blog',        label: '技术博客', cls: 'ms-read',  dx:  232, dy: -104 },
  { to: '/questiongen', label: '智能题库', cls: 'ms-code',  dx: -268, dy:   16 },
  { to: '/tarot',       label: '塔罗秘仪', cls: 'ms-tarot', dx:  268, dy:   16 },
]
/* ════════════════════════════════════════════════════════════ */

const stageEl = ref(null)
const fieldEl = ref(null)
const hubEl = ref(null)
const spriteEl = ref(null)
const groundEl = ref(null)
const centerEl = ref(null)

const typed = ref('')
const sub = ref('')
const clock = ref('--:--')
const hubOpen = ref(false)

// 词云：随机特征只掷一次，位置随视口重算 —— 否则改窗口大小整片词云会换一副样子
const seeds = WORDS.map((w, i) => {
  const big = i % 3 === 0
  const ang = big
    ? Math.PI * (0.10 + Math.random() * 0.80)      // 大词压在下半当前景
    : (i / WORDS.length) * Math.PI * 2 + (Math.random() - 0.5) * 0.6
  const dur = 11 + Math.random() * 8
  return {
    ...w, big,
    ca: Math.cos(ang), sa: Math.sin(ang),
    f0: (big ? 0.62 : 0.42) + Math.random() * 0.46,
    sz: Math.random(),
    peak: big ? (0.20 + Math.random() * 0.12) : (0.44 + Math.random() * 0.2),
    b0: big ? (4 + Math.random() * 3) : 0,
    rot: (Math.random() - 0.5) * 11,
    dur, delay: -Math.random() * dur,
  }
})
const cloud = reactive(seeds.map(s => ({
  t: s.t, g: s.g, big: s.big,
  style: {
    '--peak': s.peak.toFixed(2),
    '--b0': s.b0.toFixed(0) + 'px',
    '--rot': s.rot.toFixed(1) + 'deg',
    animationDuration: s.dur.toFixed(2) + 's',
    animationDelay: s.delay.toFixed(2) + 's',
    '--x': '0px', '--y': '0px', fontSize: '16px',
  },
})))

function layoutWords () {
  const el = fieldEl.value
  if (!el) return
  // 用 clientWidth 兜底：容器以 0 尺寸完成首次渲染时 innerWidth 可能为 0，
  // 那样半径全塌成 0，整片词云会堆死在原点。
  const vw = el.clientWidth || window.innerWidth || 1280
  const vh = el.clientHeight || window.innerHeight || 720
  if (!vw || !vh) return

  // 半径与字号都要把透视放大折算进去：起始 z=420、perspective=800，
  // 屏幕上被放大约 2.1 倍。照半屏宽直接布点，词会整片飞出视野。
  const PERSP = 800 / (800 - 420)
  const Rx = vw * 0.52 / PERSP
  const Ry = vh * 0.50 / PERSP
  // 禁区按标题实际占的宽度算，不是容器宽度
  const keepW = Math.min(vw * 0.30, 430)
  const keepH = 200

  seeds.forEach((s, i) => {
    let f = s.f0
    let px = s.ca * Rx * f
    let py = s.sa * Ry * f
    // 禁区比的是屏幕上的实际位置，所以要乘回透视放大倍数
    while (Math.abs(px * PERSP) < keepW && Math.abs(py * PERSP) < keepH && f < 1.35) {
      f += 0.08; px = s.ca * Rx * f; py = s.sa * Ry * f
    }
    const st = cloud[i].style
    st['--x'] = px.toFixed(0) + 'px'
    st['--y'] = py.toFixed(0) + 'px'
    // 字号是折算前的基准值，入场瞬间会被放大到约 2.1 倍
    st.fontSize = (s.big ? Math.max(34, vw * 0.027) + s.sz * 34
                         : 12 + s.sz * 14).toFixed(0) + 'px'
  })
}

/* 人物锚定到背景图中云丘顶面的同一比例点：背景走 cover 缩放，
   只有复算一遍它的几何，才能保证任何视口比例下他都踩在同一片云上。 */
const IMG_W = 1536, IMG_H = 1024
const RIDGE_X = 0.505, RIDGE_Y = 0.60
const POS_Y = 0.22, INSET_X = 0.07, INSET_Y = 0.05

function placeHub () {
  const stage = stageEl.value, hub = hubEl.value
  const sprite = spriteEl.value, ground = groundEl.value, center = centerEl.value
  if (!stage || !hub || !sprite) return

  const vw = stage.clientWidth, vh = stage.clientHeight
  const cw = vw * (1 + INSET_X * 2), ch = vh * (1 + INSET_Y * 2)
  const ox = -vw * INSET_X, oy = -vh * INSET_Y

  const scale = Math.max(cw / IMG_W, ch / IMG_H)          // cover
  const dw = IMG_W * scale, dh = IMG_H * scale

  const x = ox + (cw - dw) * 0.5 + dw * RIDGE_X
  const feetY = oy + (ch - dh) * POS_Y + dh * RIDGE_Y
  const headY = feetY - sprite.offsetHeight

  hub.style.left = x + 'px'
  hub.style.top = (feetY - hub.offsetHeight) + 'px'
  ground.style.left = x + 'px'
  ground.style.top = (feetY - 7) + 'px'

  // 文案排在人物头顶之上。两者若各写各的百分比，矮视口下必然相撞。
  const bar = parseFloat(getComputedStyle(document.documentElement)
    .getPropertyValue('--hero-bar')) || 58
  center.style.top = Math.max(bar + 22, headY - 30 - center.offsetHeight) + 'px'
}

let closeTimer = null
const openHub = () => { clearTimeout(closeTimer); hubOpen.value = true }
// 关闭留 260ms 缓冲，鼠标在人物与分身之间移动时不会闪断
const closeHub = () => { closeTimer = setTimeout(() => { hubOpen.value = false }, 260) }

let typeTimer = null
function typewriter () {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    typed.value = LINES[0]; sub.value = SUBS[0]; return
  }
  let li = 0
  const TYPE = 68, ERASE = 30, HOLD = 2100
  const type = (i = 0) => {
    if (i === 0) sub.value = SUBS[li % SUBS.length]
    if (i <= LINES[li].length) {
      typed.value = LINES[li].slice(0, i)
      typeTimer = setTimeout(() => type(i + 1), TYPE)
    } else {
      typeTimer = setTimeout(() => erase(LINES[li].length), HOLD)
    }
  }
  const erase = (i) => {
    if (i >= 0) {
      typed.value = LINES[li].slice(0, i)
      typeTimer = setTimeout(() => erase(i - 1), ERASE)
    } else {
      li = (li + 1) % LINES.length
      typeTimer = setTimeout(() => type(0), 360)
    }
  }
  type()
}

let clockTimer = null
let ro = null
function onParallax (e) {
  const el = fieldEl.value
  if (!el) return
  const dx = e.clientX / window.innerWidth - 0.5
  const dy = e.clientY / window.innerHeight - 0.5
  el.style.transform = `translate3d(${(-dx * 26).toFixed(1)}px, ${(-dy * 18).toFixed(1)}px, 0)`
}

function relayout () { layoutWords(); placeHub() }

onMounted(async () => {
  await nextTick()
  relayout()
  window.addEventListener('resize', relayout)
  window.addEventListener('load', relayout)
  // 容器尺寸未必随窗口变化（分栏、预览面板），直接盯容器本身
  if (window.ResizeObserver && fieldEl.value) {
    ro = new ResizeObserver(relayout); ro.observe(fieldEl.value)
  }
  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    window.addEventListener('mousemove', onParallax, { passive: true })
  }
  typewriter()
  const tick = () => {
    const d = new Date()
    clock.value = String(d.getHours()).padStart(2, '0') + ':' +
                  String(d.getMinutes()).padStart(2, '0')
  }
  tick(); clockTimer = setInterval(tick, 20000)
})

onUnmounted(() => {
  window.removeEventListener('resize', relayout)
  window.removeEventListener('load', relayout)
  window.removeEventListener('mousemove', onParallax)
  clearTimeout(typeTimer); clearTimeout(closeTimer); clearInterval(clockTimer)
  if (ro) ro.disconnect()
})
</script>

<template>
  <div class="stage" ref="stageEl" :class="{ 'hub-open': hubOpen }">
    <div class="cloud-back"></div>
    <div class="band band-high"></div>
    <div class="band band-low"></div>
    <div class="glow"></div>

    <div class="field" ref="fieldEl">
      <span
        v-for="(w, i) in cloud" :key="i"
        class="word" :class="['g-' + w.g, { soft: w.big }]"
        :style="w.style"
      >{{ w.t }}</span>
    </div>

    <div class="vignette"></div>
    <div class="ground" ref="groundEl"></div>

    <div
      class="hub" ref="hubEl"
      @mouseenter="openHub" @mouseleave="closeHub"
      @focusin="openHub" @focusout="closeHub"
    >
      <div class="hero-sprite" ref="spriteEl"></div>
      <div class="modules">
        <router-link
          v-for="m in MODULES" :key="m.to"
          class="mod" :to="m.to"
          :style="{ '--dx': m.dx + 'px', '--dy': m.dy + 'px' }"
        >
          <span class="mod-sprite" :class="m.cls"></span>
          <span class="mod-label">{{ m.label }}</span>
        </router-link>
      </div>
    </div>

    <div class="bar top">
      <span>lzqqq.org</span>
      <nav>
        <router-link to="/kitchen">厨房</router-link>
        <router-link to="/blog">博客</router-link>
        <router-link to="/questiongen">题库</router-link>
        <router-link to="/tarot">塔罗</router-link>
        <a href="https://github.com/linzhiqin2003" target="_blank" rel="noopener">GitHub</a>
      </nav>
    </div>

    <div class="center" ref="centerEl">
      <div class="line"><span>{{ typed }}</span><span class="caret"></span></div>
      <div class="sub">{{ sub }}</div>
    </div>

    <div class="scroll"></div>

    <div class="bar bottom">
      <div class="slate">
        <span>LOCATION: <b>在路上</b></span>
        <span class="hide-sm">TIME: <b>{{ clock }}</b></span>
      </div>
      <div class="slate">
        <span class="hide-sm">FRAMES: <b>&infin;</b></span>
        <span>MEMORY: <b>IN PROGRESS</b></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stage{
  --sky-1:#c8dff6; --sky-2:#e2eefa; --sky-3:#fbfdff;
  --ink:#1b2836; --ink-soft:#42586e; --muted:#8399ac;
  --band:#f7fafd; --hero-bar:58px;
  --mono:"Geist Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --sans:"Noto Sans SC","Inter",system-ui,sans-serif;

  position:relative; height:100vh; min-height:600px; overflow:hidden;
  font-family:var(--sans); color:var(--ink);
  background:linear-gradient(180deg,var(--sky-1) 0%,var(--sky-2) 46%,var(--sky-3) 100%);
}

/* 云海背景：真实体积云。纯 CSS 渐变画不出体积，这是画面质感的来源。
   定位 22% 而非居中 —— cover 会裁掉上下，必须优先保住上部的天空和地平线。 */
.cloud-back{
  position:absolute; inset:-5% -7%;
  background:url("/sprites/cloud-bg.webp") center 22%/cover no-repeat;
  will-change:transform;
  animation:sway-back 96s ease-in-out infinite alternate;
}
@keyframes sway-back{
  from{transform:translate3d(-1.4%,0,0) scale(1.03)}
  to  {transform:translate3d( 1.4%,0,0) scale(1.07)}
}

/* 流动云带：人物脚下那片云不能动（他站着），会动的是空中飘过的云。
   用 transform 而非 background-position —— 后者不是合成属性，每帧都要重绘。
   贴图是镜像拼接的，平移一个贴图宽即无缝闭环。 */
.band{
  position:absolute; left:0; pointer-events:none;
  background-repeat:repeat-x; background-position-y:center;
  will-change:transform;
}
.band-high{
  top:6%; height:190px; z-index:1; opacity:.85;
  width:calc(100% + 1560px);
  background-image:url("/sprites/band-high.webp"); background-size:1560px auto;
  animation:flow-high 210s linear infinite;
}
@keyframes flow-high{
  from{transform:translate3d(0,0,0)} to{transform:translate3d(-1560px,0,0)}
}
.band-low{
  top:34%; height:230px; z-index:2; opacity:.72;
  width:calc(100% + 1820px);
  background-image:url("/sprites/band-low.webp"); background-size:1820px auto;
  animation:flow-low 128s linear infinite;
}
@keyframes flow-low{
  from{transform:translate3d(0,0,0)} to{transform:translate3d(-1820px,0,0)}
}

.glow{
  position:absolute; left:50%; top:-14%; width:70vw; height:52vh;
  transform:translateX(-50%); pointer-events:none;
  background:radial-gradient(closest-side,rgba(255,255,255,.9),rgba(255,255,255,0));
}
.vignette{
  position:absolute; inset:0; pointer-events:none;
  background:radial-gradient(120% 90% at 50% 45%,rgba(255,255,255,0) 55%,rgba(120,150,180,.14) 100%);
}

/* ───────── 词云：3D 汇聚 ───────── */
.field{
  position:absolute; inset:0; pointer-events:none;
  /* perspective 越小透视越强。配合更大的 z 行程，词从 2.1 倍缩到 0.35 倍，
     整整六倍的尺寸变化，「由远及近」才真的读得出来。 */
  perspective:800px; perspective-origin:50% 46%;
  transition:transform .5s cubic-bezier(.22,1,.36,1), opacity .4s ease;
}
.word{
  position:absolute; left:50%; top:46%;
  font-weight:400; white-space:nowrap; opacity:0;
  /* 云海是高频背景，纯文字会被吃掉；一圈白光晕把字从云里托出来 */
  text-shadow:0 0 14px rgba(255,255,255,.7), 0 0 4px rgba(255,255,255,.5);
  --peak:.5; --b0:0px; --rot:0deg;
  will-change:transform,opacity;
  animation-name:converge; animation-timing-function:linear;
  animation-iteration-count:infinite;
}
/* 三类词各有字体语言，视觉差异直接承载语义 */
.g-fin { font-family:"Noto Serif SC",Georgia,serif; color:#5b6d80; letter-spacing:.02em }
.g-tech{ font-family:"Geist Mono",ui-monospace,"Noto Sans SC",monospace;
         color:#3f5f7e; letter-spacing:.09em }
.g-life{ font-family:var(--sans); font-weight:200; color:#74838f; letter-spacing:.06em }
/* 只有背景层的大词才建滤镜层。模糊写成静态而非逐帧变化的变量：
   模糊值一旦每帧重算就是整页最贵的开销；而 blur(0) 同样会建层，
   所以小词干脆不带 filter 这条声明。 */
.word.soft{ filter:blur(var(--b0)) }

@keyframes converge{
  0%   {transform:translate3d(var(--x),var(--y),420px) rotate(var(--rot)); opacity:0}
  10%  {opacity:var(--peak)}
  /* 中间这帧是关键：前 45% 的时间只走完四分之一深度，词在「大」的状态
     停留得够久，由大变小才看得出来；剩下 55% 冲完全程，收尾干脆。 */
  45%  {transform:translate3d(calc(var(--x)*.84),calc(var(--y)*.84),40px)
                  rotate(calc(var(--rot) * .45));
        opacity:calc(var(--peak) * .8)}
  80%  {opacity:.09}
  100% {transform:translate3d(calc(var(--x)*.5),calc(var(--y)*.5),-1500px)
                 rotate(calc(var(--rot) * -.5)); opacity:0}
}

/* ───────── 中心文案 ───────── */
.center{
  position:absolute; left:50%; top:26%; transform:translateX(-50%);
  width:min(94vw,1040px); text-align:center; z-index:3;
  /* 纯展示，必须让出鼠标：它有 1040px 宽、排在 hub 之后，
     否则会盖住分身上半部分，鼠标看着在分身上、实际命中的是这层。 */
  pointer-events:none;
  transition:opacity .4s ease;
}
.center::before{
  content:""; position:absolute; left:50%; top:36%;
  width:112%; height:150%; transform:translate(-50%,-50%);
  background:radial-gradient(closest-side,rgba(255,255,255,.52),rgba(255,255,255,0) 72%);
  pointer-events:none; z-index:-1;
}
.line{
  font-family:var(--mono); font-size:clamp(24px,4.4vw,64px); font-weight:500;
  letter-spacing:.01em; min-height:1.4em; color:var(--ink);
}
.caret{
  display:inline-block; width:.56em; height:1.02em; margin-left:.06em;
  background:var(--ink); vertical-align:-.16em;
  animation:caret 1.05s steps(1) infinite;
}
@keyframes caret{0%,50%{opacity:1}51%,100%{opacity:0}}
.sub{
  margin-top:16px; font-family:var(--mono); font-size:clamp(11px,1.05vw,15px);
  letter-spacing:.24em; color:var(--muted); text-transform:uppercase;
  min-height:1.4em;
}

/* ───────── 人物与分身 ───────── */
.hub{
  position:absolute; z-index:3;
  width:820px; height:330px; margin-left:-410px;
  display:flex; align-items:flex-end; justify-content:center;
}
/* 展开后把命中区外扩一圈：鼠标在分身之间游走、或略微越界都不会误判为离开。
   收起时不启用，否则鼠标只是路过附近就会把分身弹出来。
   用 ::before 而非 ::after —— 前者绘制在内容之下，不会挡住分身的点击。 */
.hub::before{
  content:""; position:absolute; inset:-40px -64px -34px; pointer-events:none;
}
.hub-open .hub::before{ pointer-events:auto }

.hero-sprite{
  /* 高度跟视口走：矮屏上固定高度会把人物撑得过大、挤掉文案的位置 */
  --h:clamp(104px, 19vh, 176px); --fw:137; --fh:256; --n:3;
  position:relative; z-index:2;
  width:calc(var(--h) * var(--fw) / var(--fh)); height:var(--h);
  background-image:url("/sprites/core.png"); background-repeat:no-repeat;
  background-size:calc(var(--h) * var(--fw) * var(--n) / var(--fh)) auto;
  image-rendering:pixelated; transform-origin:bottom center; cursor:pointer;
  animation:blink 5.4s steps(1) infinite, breathe 3.8s ease-in-out infinite;
}
/* 眨眼只切 background-position，呼吸只改 transform，两条轨道互不干扰 */
@keyframes blink{
  0%,93%    {background-position:0 0}
  94%,96.4% {background-position:calc(-1 * var(--h) * var(--fw) / var(--fh)) 0}
  97%,100%  {background-position:0 0}
}
@keyframes breathe{
  0%,100%{transform:scaleY(1)} 50%{transform:scaleY(.988)}
}
.hero-sprite:hover{
  background-position:calc(-2 * var(--h) * var(--fw) / var(--fh)) 0 !important;
  animation:breathe 3.8s ease-in-out infinite;
}
.ground{
  position:absolute; left:50%; z-index:2;
  width:112px; height:12px; margin-left:-56px; border-radius:50%;
  background:radial-gradient(closest-side,rgba(96,130,166,.24),rgba(96,130,166,0));
}

/* 焦点转移：分身展开时背景整体退后，模块自然浮到前景 —— 用景深换层级，
   比给分身加边框色块干净。只降透明度不加 blur：对装着 32 个动画元素的
   容器做模糊，等于每帧把整层重新光栅化。 */
.hub-open .field { opacity:.16 }
.hub-open .center{ opacity:.34 }
.cloud-back{ transition:opacity .5s ease }
.hub-open .cloud-back{ opacity:.9 }

/* ───────── 模块入口：他的分身 ─────────
   四个分身从本体分裂出去，各自做对应模块的事。
   用动作说明模块，比挂四个文字标签直观。 */
.modules{ position:absolute; inset:0; pointer-events:none }
.mod{
  position:absolute; left:50%; bottom:14px;
  display:flex; flex-direction:column; align-items:center; gap:6px;
  text-decoration:none; white-space:nowrap;
  /* 收起态：缩成一点藏在本体身上，展开就是「分裂」 */
  transform:translate(-50%,0) scale(.28);
  opacity:0; pointer-events:none;
  transition:transform .52s cubic-bezier(.34,1.32,.5,1), opacity .34s ease;
}
.hub-open .mod{
  transform:translate(calc(-50% + var(--dx)), var(--dy)) scale(1);
  opacity:1; pointer-events:auto;
}
/* 依次浮现，比齐刷刷弹出更有生气 */
.hub-open .mod:nth-child(1){ transition-delay:0s,    0s }
.hub-open .mod:nth-child(2){ transition-delay:.055s, .055s }
.hub-open .mod:nth-child(3){ transition-delay:.11s,  .11s }
.hub-open .mod:nth-child(4){ transition-delay:.165s, .165s }

.mod-sprite{
  --h:96px; position:relative;
  width:calc(var(--h) * var(--fw) / var(--fh)); height:var(--h);
  background-repeat:no-repeat; image-rendering:pixelated;
  background-size:calc(var(--h) * var(--fw) * var(--n) / var(--fh)) auto;
  transition:transform .22s ease;
  animation-play-state:paused;      /* 收起时分身不可见，动画不必空转 */
}
.hub-open .mod-sprite{ animation-play-state:running }
.mod-sprite::after{                 /* 脚下小投影，避免看起来浮空 */
  content:""; position:absolute; left:50%; bottom:0; width:46px; height:7px;
  transform:translateX(-50%); border-radius:50%;
  background:radial-gradient(closest-side,rgba(96,130,166,.3),rgba(96,130,166,0));
}
.mod-label{
  font-family:var(--mono); font-size:12px; font-weight:500; letter-spacing:.1em;
  color:var(--ink); opacity:.72;
  text-shadow:0 0 14px #fff, 0 0 6px #fff;
  transition:opacity .2s ease;
}
.mod:hover .mod-sprite{ transform:translateY(-5px) }
.mod:hover .mod-label{ opacity:1 }

/* 每个分身的雪碧图参数。前两帧构成循环动作，第三帧是收尾姿势，只播前两帧 */
.ms-cook { --fw:144; --fh:200; --n:3; background-image:url("/sprites/cook.png");
           animation:play2-cook .78s steps(2) infinite }
.ms-read { --fw:140; --fh:200; --n:3; background-image:url("/sprites/read.png");
           animation:play2-read 1.15s steps(2) infinite }
.ms-code { --fw:159; --fh:200; --n:3; background-image:url("/sprites/code.png");
           animation:play2-code .5s steps(2) infinite }
.ms-tarot{ --fw:130; --fh:200; --n:3; background-image:url("/sprites/tarot.png");
           animation:play3-tarot 2.7s steps(3) infinite }
@keyframes play2-cook { from{background-position:0 0}
  to{background-position:calc(-2 * var(--h) * var(--fw) / var(--fh)) 0} }
@keyframes play2-read { from{background-position:0 0}
  to{background-position:calc(-2 * var(--h) * var(--fw) / var(--fh)) 0} }
@keyframes play2-code { from{background-position:0 0}
  to{background-position:calc(-2 * var(--h) * var(--fw) / var(--fh)) 0} }
@keyframes play3-tarot{ from{background-position:0 0}
  to{background-position:calc(-3 * var(--h) * var(--fw) / var(--fh)) 0} }

/* ───────── 电影 chrome ───────── */
.bar{
  position:absolute; left:0; right:0; height:var(--hero-bar); z-index:5;
  display:flex; align-items:center; justify-content:space-between;
  padding:0 26px; background:var(--band);
  font-family:var(--mono); font-size:11px; letter-spacing:.16em;
  color:var(--muted); text-transform:uppercase;
}
.bar.top{ top:0; border-bottom:1px solid rgba(120,150,180,.14) }
.bar.bottom{ bottom:0; border-top:1px solid rgba(120,150,180,.14) }
.bar nav{ display:flex; gap:26px }
.bar a{ color:var(--muted); text-decoration:none; transition:color .18s }
.bar a:hover{ color:var(--ink) }
.slate{ display:flex; gap:22px }
.slate b{ font-weight:400; color:var(--ink-soft) }

/* 滚动提示：一条细线里有个缓慢下滑的点，不用脉冲呼吸灯 */
.scroll{
  position:absolute; left:50%; bottom:calc(var(--hero-bar) + 26px);
  transform:translateX(-50%);
  width:1px; height:46px; background:rgba(120,150,180,.28); z-index:4;
}
.scroll::after{
  content:""; position:absolute; left:-2px; top:0; width:5px; height:5px;
  border-radius:50%; background:var(--ink-soft);
  animation:fall 2.6s cubic-bezier(.4,0,.5,1) infinite;
}
@keyframes fall{
  0%{transform:translateY(0);opacity:0}
  22%{opacity:.85} 75%{opacity:.85}
  100%{transform:translateY(41px);opacity:0}
}

@media (max-width:640px){
  .stage{ --hero-bar:38px }
  .hero-sprite{ --h:96px }
  .slate{ gap:12px }
  .slate .hide-sm{ display:none }
  .bar nav{ gap:16px }
}
@media (prefers-reduced-motion:reduce){
  .word{ animation-duration:.001s; animation-iteration-count:1; opacity:.34;
         transform:translate3d(var(--x),var(--y),0) }
  .band,.cloud-back,.hero-sprite,.scroll::after,.caret{ animation:none }
  .caret{ opacity:1 }
}
</style>
