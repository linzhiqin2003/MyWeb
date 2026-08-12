<template>
  <div class="min-h-screen bg-mystic-dark text-mystic-gold relative overflow-hidden font-mystic">
    <StarField />
    <MysticDecor :show-moon="showMoon" :show-sigil="showSigil" :show-candle="showCandle" />

    <div class="relative z-10 min-h-screen flex flex-col">
      <header class="flex items-center justify-between px-4 sm:px-8 py-4">
        <router-link
          :to="backTo"
          class="text-xs sm:text-sm tracking-[0.25em] uppercase text-gray-400 hover:text-mystic-gold transition-colors flex items-center gap-2"
        >
          <span>←</span>
          <span>{{ backLabel }}</span>
        </router-link>
        <span class="text-[10px] sm:text-xs tracking-[0.35em] uppercase text-mystic-gold/70 glow-soft">Tarot Sanctum</span>
      </header>
      <main class="flex-1 w-full">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import StarField from './StarField.vue';
import MysticDecor from './MysticDecor.vue';

defineProps({
  backTo: { type: String, default: '/tarot' },
  backLabel: { type: String, default: '圣所' },
  showMoon: { type: Boolean, default: true },
  showSigil: { type: Boolean, default: true },
  showCandle: { type: Boolean, default: false },
});
</script>

<style scoped>
.glow-soft {
  text-shadow: 0 0 12px rgba(255, 215, 0, 0.35);
}
</style>
