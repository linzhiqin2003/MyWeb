<template>
  <TarotShell :show-moon="true" :show-sigil="true" back-to="/" back-label="返回家园">
    <div class="flex flex-col items-center px-4 pb-10 pt-2 text-center min-h-[78vh]">
      <p class="text-[10px] tracking-[0.45em] uppercase text-mystic-purple mb-2">NPC · Oracle</p>
      <h1 class="text-3xl sm:text-5xl tracking-[0.22em] uppercase glow-text mb-1">Tarot Sanctum</h1>
      <p class="font-chinese-title text-lg sm:text-xl text-mystic-gold/80 mb-4">塔罗圣所</p>

      <OracleSprite pose="greet" size="hero" :sparkle="true" class="mb-2" />

      <div class="w-full max-w-xl mb-8">
        <OracleHud pose="greet" :line="greeting" hide-sprite />
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
          <span class="title font-chinese-title">{{ portal.title }}</span>
          <span class="desc font-chinese-body">{{ portal.desc }}</span>
        </router-link>
      </div>
    </div>
  </TarotShell>
</template>

<script setup>
import TarotShell from '../../components/tarot/TarotShell.vue';
import OracleSprite from '../../components/tarot/OracleSprite.vue';
import OracleHud from '../../components/tarot/OracleHud.vue';

const greeting = '你来了。今晚想问哪一层？选一条路，我把牌摊开。';

const portals = [
  { to: '/tarot/ritual', title: '占卜仪式', desc: '选阵、洗牌、亲手抽' },
  { to: '/tarot/daily', title: '今日神谕', desc: '每天只给一张脸' },
  { to: '/tarot/yesno', title: '是非一问', desc: '只问是，或不是' },
  { to: '/tarot/codex', title: '星图典藏', desc: '七十八张牌的光与影' },
  { to: '/tarot/journal', title: '占卜手记', desc: '你问过的话还在' },
];
</script>

<style scoped>
.glow-text {
  text-shadow: 0 0 10px rgba(255, 215, 0, 0.5), 0 0 24px rgba(168, 85, 247, 0.25);
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
.cursor {
  color: transparent;
  font-size: 12px;
}
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
.title { color: #ffd700; font-size: 1.15rem; }
.desc { color: #9ca3af; font-size: 0.85rem; }
@keyframes nudge {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(3px); }
}
</style>
