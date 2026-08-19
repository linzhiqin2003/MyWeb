<template>
  <TarotShell :show-moon="true" :show-sigil="true" back-to="/" back-label="返回家园">
    <div class="stage">
      <p class="kicker">lzqqq.org · tarot</p>
      <h1 class="title glow-text">Tarot Sanctum</h1>
      <p class="subtitle font-chinese-title">塔罗圣所</p>

      <div class="hero" :class="{ entering }">
        <OracleSprite
          :pose="heroPose"
          size="hero"
          :sparkle="!entering"
          interactive
        />
      </div>

      <div class="w-full max-w-xl mb-8">
        <OracleHud :pose="heroPose" :line="line" hide-sprite />
      </div>

      <div class="w-full max-w-xl text-left space-y-2">
        <p class="font-pixel text-[10px] tracking-[0.2em] text-mystic-gold/80 mb-3">SELECT A PATH</p>
        <router-link
          v-for="(portal, index) in portals"
          :key="portal.to"
          :to="portal.to"
          class="menu-row group"
        >
          <span class="cursor">▶</span>
          <span class="idx">{{ index + 1 }}</span>
          <span class="title-row font-chinese-title">{{ portal.title }}</span>
          <span class="desc font-chinese-body">{{ portal.desc }}</span>
        </router-link>
      </div>
    </div>
  </TarotShell>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';
import TarotShell from '../../components/tarot/TarotShell.vue';
import OracleSprite from '../../components/tarot/OracleSprite.vue';
import OracleHud from '../../components/tarot/OracleHud.vue';

const entering = ref(true);
let timer = null;

onMounted(() => {
  timer = setTimeout(() => { entering.value = false; }, 1400);
});
onUnmounted(() => { if (timer) clearTimeout(timer); });

const heroPose = computed(() => (entering.value ? 'walk' : 'greet'));
const line = computed(() => (
  entering.value
    ? '……我到了。'
    : '你来了。今晚想问哪一层？选一条路，我把牌摊开。'
));

const portals = [
  { to: '/tarot/ritual', title: '占卜仪式', desc: '选阵、洗牌、亲手抽' },
  { to: '/tarot/daily', title: '今日神谕', desc: '每天只给一张脸' },
  { to: '/tarot/yesno', title: '是非一问', desc: '只问是，或不是' },
  { to: '/tarot/codex', title: '星图典藏', desc: '七十八张牌的光与影' },
  { to: '/tarot/journal', title: '占卜手记', desc: '你问过的话还在' },
];
</script>

<style scoped>
.stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  min-height: 78vh;
  padding: 8px 16px 40px;
}
.kicker {
  font-family: 'Press Start 2P', monospace;
  font-size: 9px;
  letter-spacing: 0.18em;
  color: #a855f7;
  margin-bottom: 10px;
}
.title {
  font-size: clamp(1.8rem, 5vw, 3.2rem);
  letter-spacing: 0.22em;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.subtitle {
  font-size: 1.15rem;
  color: rgba(255, 215, 0, 0.8);
  margin-bottom: 8px;
}
.glow-text {
  text-shadow: 0 0 10px rgba(255, 215, 0, 0.5), 0 0 24px rgba(168, 85, 247, 0.25);
}
.hero {
  margin: 8px 0 18px;
}
.hero.entering {
  animation: walkIn 1.4s ease-out both;
}
@keyframes walkIn {
  from { transform: translateX(-42vw); }
  to { transform: translateX(0); }
}
.font-pixel {
  font-family: 'Press Start 2P', monospace;
}
.menu-row {
  display: grid;
  grid-template-columns: 18px 28px minmax(5.5rem, auto) 1fr;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  border: 1px solid #2a2a3a;
  background: rgba(0, 0, 0, 0.45);
  color: inherit;
  text-decoration: none;
  transition: border-color 0.2s ease, background 0.2s ease, transform 0.2s ease;
}
.menu-row:hover,
.menu-row:focus-visible {
  border-color: #ffd700;
  background: rgba(255, 215, 0, 0.08);
  transform: translateX(6px);
}
.cursor { color: transparent; font-size: 12px; }
.menu-row:hover .cursor,
.menu-row:focus-visible .cursor {
  color: #ffd700;
  animation: nudge 0.6s ease-in-out infinite;
}
.idx {
  font-family: 'Press Start 2P', monospace;
  font-size: 10px;
  color: #a855f7;
}
.title-row { color: #ffd700; font-size: 1.15rem; }
.desc { color: #9ca3af; font-size: 0.85rem; }
@keyframes nudge {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(3px); }
}
</style>
