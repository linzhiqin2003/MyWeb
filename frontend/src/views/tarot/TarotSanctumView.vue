<template>
  <TarotShell :show-moon="true" :show-sigil="true" back-to="/" back-label="返回家园">
    <div class="flex flex-col items-center justify-center px-6 pb-16 pt-4 text-center min-h-[80vh]">
      <p class="text-[10px] sm:text-xs tracking-[0.55em] uppercase text-mystic-purple mb-4">Enter the void</p>
      <h1 class="text-4xl sm:text-6xl md:text-7xl mb-3 tracking-[0.25em] uppercase glow-text">Tarot Sanctum</h1>
      <p class="font-chinese-title text-xl sm:text-2xl text-mystic-gold/80 mb-3">塔罗圣所</p>
      <p class="text-sm sm:text-base text-gray-400 mb-12 max-w-lg leading-relaxed font-chinese-body">
        问，不是为了把未来钉死，而是为了看清你已经站在哪一层雾里。
      </p>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 w-full max-w-5xl">
        <router-link
          v-for="portal in portals"
          :key="portal.to"
          :to="portal.to"
          class="portal-card group relative overflow-hidden rounded-2xl border border-mystic-gold/25 bg-black/40 text-left p-6 min-h-[180px] hover:border-mystic-gold transition-all duration-500"
        >
          <img :src="portal.art" alt="" class="absolute inset-0 w-full h-full object-cover opacity-25 group-hover:opacity-45 group-hover:scale-110 transition-all duration-700 mix-blend-screen" />
          <div class="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent"></div>
          <div class="relative z-10 flex flex-col h-full justify-end">
            <p class="text-[10px] tracking-[0.35em] uppercase text-mystic-purple mb-2">{{ portal.en }}</p>
            <h2 class="text-2xl text-mystic-gold font-chinese-title mb-1">{{ portal.title }}</h2>
            <p class="text-sm text-gray-400 font-chinese-body">{{ portal.desc }}</p>
          </div>
        </router-link>
      </div>
    </div>
  </TarotShell>
</template>

<script setup>
import TarotShell from '../../components/tarot/TarotShell.vue';

const portals = [
  { to: '/tarot/ritual', en: 'Ritual', title: '占卜仪式', desc: '选牌阵、洗牌、亲手抽出命运的形状', art: '/mystic/tarot-portal.jpg' },
  { to: '/tarot/daily', en: 'Daily Oracle', title: '今日神谕', desc: '每天只给一张牌。同一天，同一张脸', art: '/mystic/tarot-moon.jpg' },
  { to: '/tarot/yesno', en: 'Yes / No', title: '是非一问', desc: '只问是或否，看牌如何倾斜', art: '/mystic/tarot-sigil.jpg' },
  { to: '/tarot/codex', en: 'Codex', title: '星图典藏', desc: '七十八张牌的关键词、正位与逆位', art: '/mystic/tarot-card-back.jpg' },
  { to: '/tarot/journal', en: 'Journal', title: '占卜手记', desc: '把问过的话留下来，看自己如何反复归来', art: '/mystic/tarot-candle.jpg' },
];
</script>

<style scoped>
.glow-text {
  text-shadow: 0 0 10px rgba(255, 215, 0, 0.5), 0 0 20px rgba(255, 215, 0, 0.3), 0 0 40px rgba(168, 85, 247, 0.25);
  animation: glow 3s ease-in-out infinite alternate;
}
@keyframes glow {
  from { text-shadow: 0 0 10px rgba(255, 215, 0, 0.5), 0 0 20px rgba(255, 215, 0, 0.3); }
  to { text-shadow: 0 0 20px rgba(255, 215, 0, 0.85), 0 0 40px rgba(255, 215, 0, 0.5), 0 0 60px rgba(168, 85, 247, 0.35); }
}
.portal-card {
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.35);
}
.portal-card:hover {
  transform: translateY(-6px) rotateX(2deg);
  box-shadow: 0 18px 50px rgba(255, 215, 0, 0.12);
}
</style>
