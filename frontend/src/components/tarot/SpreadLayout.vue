<template>
  <div class="spread-board relative mx-auto" :style="boardStyle">
    <div
      v-for="(item, index) in drawnCards"
      :key="item.deckIndex ?? index"
      class="absolute flex flex-col items-center gap-2 layout-piece"
      :class="{ 'overlay-card': layoutAt(index).overlay }"
      :style="pieceStyle(index)"
    >
      <span class="text-[10px] sm:text-xs tracking-[0.2em] uppercase text-gray-400 text-center max-w-[7rem] leading-tight">
        {{ positionLabel(spread, index) }}
      </span>
      <div
        class="card-rotator"
        :class="{ 'is-revealed': item.revealed }"
        :style="{ transform: `rotate(${layoutAt(index).rotate || 0}deg)` }"
      >
        <TarotCard
          :card="item.card"
          :revealed="item.revealed"
          :reversed="item.reversed"
          :size="cardSize"
          @click="$emit('reveal', index)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import TarotCard from './TarotCard.vue';
import { positionLabel } from '../../composables/useTarotDeck';

const props = defineProps({
  spread: { type: Object, default: null },
  drawnCards: { type: Array, default: () => [] },
});

defineEmits(['reveal']);

const count = computed(() => props.spread?.card_count || props.drawnCards.length || 1);

const cardSize = computed(() => {
  if (count.value >= 10) return 'xs';
  if (count.value >= 6) return 'sm';
  if (count.value >= 4) return 'md';
  return 'lg';
});

const boardStyle = computed(() => {
  const tall = count.value >= 5;
  const wide = count.value >= 7;
  return {
    width: '100%',
    maxWidth: wide ? '920px' : count.value >= 4 ? '720px' : '420px',
    height: tall ? 'min(72vh, 640px)' : 'min(52vh, 420px)',
  };
});

function layoutAt(index) {
  const layout = props.spread?.layout?.[index];
  if (layout && typeof layout.x === 'number') return layout;
  const n = Math.max(count.value, 1);
  const x = n === 1 ? 50 : 12 + (index * 76) / Math.max(n - 1, 1);
  return { x, y: 50, rotate: 0, overlay: false };
}

function pieceStyle(index) {
  const layout = layoutAt(index);
  return {
    left: `${layout.x}%`,
    top: `${layout.y}%`,
    zIndex: layout.overlay ? 20 : 10 + index,
    '--rot': '0deg',
    animationDelay: `${index * 0.08}s`,
  };
}
</script>

<style scoped>
.layout-piece {
  transform: translate(-50%, -50%) rotate(var(--rot, 0deg));
  animation: riseIn 0.7s ease-out both;
  /* 这个盒子只负责定位，它把标签和卡牌一起撑成一个远大于卡牌的透明矩形。
     凯尔特十字里「挑战」横压在「现状」上（同坐标 + z-index 20），若容器
     本身接管点击，它的空白处会吃掉盖住的那张牌几乎所有可点面积。
     只让卡牌自己可点，露出来的部分就能正常翻开。 */
  pointer-events: none;
}
.layout-piece .card-rotator {
  pointer-events: auto;
}
/* 翻开的牌不再需要点击（revealCard 对已翻开的牌本就直接 return）。
   让它退出命中测试，「挑战」翻开后压在下面的「现状」就能整张点到，
   同一个位置连点两下即可依次翻开两张，而不是去够那条十几像素的窄边。 */
.layout-piece .card-rotator.is-revealed {
  pointer-events: none;
}
@keyframes riseIn {
  from { opacity: 0; transform: translate(-50%, -32%) scale(0.86) rotate(var(--rot, 0deg)); }
  to { opacity: 1; transform: translate(-50%, -50%) rotate(var(--rot, 0deg)); }
}
</style>
