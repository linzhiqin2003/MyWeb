<template>
  <div
    class="relative perspective-1000 cursor-pointer group tarot-card-wrap"
    :class="[sizeClass, { 'is-reversed': reversed && isFlipped }]"
    @click="flip"
  >
    <div
      class="relative w-full h-full transition-transform duration-700 transform-style-3d shadow-xl rounded-xl card-inner"
      :class="{ 'rotate-y-180': isFlipped, 'hover-lift': !isFlipped }"
    >
      <div class="absolute w-full h-full backface-hidden rounded-xl overflow-hidden border-2 border-mystic-gold/80 card-back">
        <img src="/mystic/tarot-card-back.jpg" alt="" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-black/20"></div>
        <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 card-sheen"></div>
      </div>

      <div
        class="absolute w-full h-full backface-hidden rotate-y-180 rounded-xl overflow-hidden border-2 border-mystic-gold bg-black"
        :class="{ 'reversed-face': reversed }"
      >
        <img :src="imageSrc" :alt="card.name" class="w-full h-full object-cover" :class="{ 'rotate-180': reversed }" />
        <div v-if="showCaption" class="absolute bottom-0 w-full bg-black/75 text-center py-1 sm:py-1.5">
          <span class="text-mystic-gold font-mystic text-[10px] sm:text-xs tracking-wide">
            {{ card.name_cn || card.name }}
          </span>
          <span v-if="reversed" class="block text-[9px] text-rose-300 tracking-widest">逆位</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { cardImage } from '../../composables/useTarotDeck';

const props = defineProps({
  card: { type: Object, required: true },
  revealed: { type: Boolean, default: false },
  reversed: { type: Boolean, default: false },
  size: { type: String, default: 'md' },
  showCaption: { type: Boolean, default: true },
});

const emit = defineEmits(['click']);
const isInternalFlipped = ref(false);
const isFlipped = computed(() => props.revealed || isInternalFlipped.value);
const imageSrc = computed(() => cardImage(props.card));

const sizeClass = computed(() => {
  switch (props.size) {
    case 'xs':
      return 'w-14 h-[5.25rem] sm:w-16 sm:h-24';
    case 'sm':
      return 'w-16 h-24 sm:w-20 sm:h-[7.5rem]';
    case 'lg':
      return 'w-32 h-52 md:w-40 md:h-64';
    case 'xl':
      return 'w-36 h-56 md:w-48 md:h-80';
    default:
      return 'w-24 h-36 sm:w-28 sm:h-44 md:w-32 md:h-52';
  }
});

function flip() {
  emit('click');
  if (!props.revealed) isInternalFlipped.value = !isInternalFlipped.value;
}
</script>

<style scoped>
.perspective-1000 { perspective: 1200px; }
.transform-style-3d { transform-style: preserve-3d; }
.backface-hidden { backface-visibility: hidden; }
.rotate-y-180 { transform: rotateY(180deg); }
.hover-lift {
  transition: transform 0.7s cubic-bezier(0.2, 0.8, 0.2, 1), filter 0.3s ease;
}
.group:hover .hover-lift:not(.rotate-y-180) {
  filter: drop-shadow(0 0 16px rgba(255, 215, 0, 0.45));
}
.card-sheen {
  background: linear-gradient(115deg, transparent 30%, rgba(255, 255, 255, 0.18) 48%, transparent 62%);
  animation: sheen 2.8s ease-in-out infinite;
}
@keyframes sheen {
  0% { transform: translateX(-40%); }
  100% { transform: translateX(40%); }
}
</style>
