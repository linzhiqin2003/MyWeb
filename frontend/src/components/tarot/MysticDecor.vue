<template>
  <div class="pointer-events-none absolute inset-0 overflow-hidden z-[1]">
    <img
      src="/mystic/tarot-nebula.jpg"
      alt=""
      class="absolute inset-0 w-full h-full object-cover opacity-40 mix-blend-screen nebula-drift"
    />
    <img
      v-if="showMoon"
      src="/mystic/tarot-moon.jpg"
      alt=""
      class="absolute -top-8 -right-10 w-48 sm:w-64 md:w-80 opacity-70 mix-blend-screen moon-float"
    />
    <img
      v-if="showSigil"
      src="/mystic/tarot-sigil.jpg"
      alt=""
      class="absolute -bottom-16 -left-12 w-40 sm:w-56 opacity-50 mix-blend-screen sigil-spin"
    />
    <img
      src="/mystic/tarot-flourish.jpg"
      alt=""
      class="absolute top-0 left-0 w-24 sm:w-36 opacity-40 mix-blend-screen"
    />
    <img
      src="/mystic/tarot-flourish.jpg"
      alt=""
      class="absolute top-0 right-0 w-24 sm:w-36 opacity-40 mix-blend-screen scale-x-[-1]"
    />
    <img
      src="/mystic/tarot-flourish.jpg"
      alt=""
      class="absolute bottom-0 left-0 w-24 sm:w-36 opacity-30 mix-blend-screen scale-y-[-1]"
    />
    <img
      src="/mystic/tarot-flourish.jpg"
      alt=""
      class="absolute bottom-0 right-0 w-24 sm:w-36 opacity-30 mix-blend-screen scale-[-1]"
    />
    <img
      v-if="showCandle"
      src="/mystic/tarot-candle.jpg"
      alt=""
      class="absolute bottom-4 right-4 sm:right-10 w-16 sm:w-24 opacity-80 mix-blend-screen candle-flicker"
    />
    <div class="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-[#0a0a12] via-[#0a0a12]/70 to-transparent fog-breathe"></div>
    <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_40%,#0a0a12_100%)]"></div>
  </div>
</template>

<script setup>
defineProps({
  showMoon: { type: Boolean, default: true },
  showSigil: { type: Boolean, default: true },
  showCandle: { type: Boolean, default: false },
});
</script>

<style scoped>
.nebula-drift {
  animation: nebulaDrift 48s ease-in-out infinite alternate;
}
.moon-float {
  animation: moonFloat 9s ease-in-out infinite;
}
.sigil-spin {
  animation: sigilSpin 80s linear infinite;
}
.candle-flicker {
  animation: candleFlicker 2.4s ease-in-out infinite;
}
.fog-breathe {
  animation: fogBreathe 8s ease-in-out infinite;
}

@keyframes nebulaDrift {
  from { transform: scale(1.05) translate3d(-2%, 0, 0); }
  to { transform: scale(1.12) translate3d(3%, -2%, 0); }
}
@keyframes moonFloat {
  0%, 100% { transform: translateY(0) rotate(-4deg); }
  50% { transform: translateY(14px) rotate(3deg); }
}
@keyframes sigilSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes candleFlicker {
  0%, 100% { filter: brightness(1) drop-shadow(0 0 12px rgba(255, 180, 60, 0.45)); }
  40% { filter: brightness(1.18) drop-shadow(0 0 22px rgba(255, 200, 80, 0.7)); }
  70% { filter: brightness(0.92) drop-shadow(0 0 8px rgba(255, 160, 40, 0.35)); }
}
@keyframes fogBreathe {
  0%, 100% { opacity: 0.85; }
  50% { opacity: 1; }
}
</style>
