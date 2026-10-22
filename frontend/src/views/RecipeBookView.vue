<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import API_BASE_URL from '../config/api'
import { chefApi, useChefGuard } from '../composables/useChefAuth'

const { ensureChef } = useChefGuard()

const route = useRoute()
const router = useRouter()
const recipe = ref(null)
const loading = ref(true)
const currentSection = ref(0) // 0=封面, 1=食材, 2+=步骤

onMounted(async () => {
  if (!(await ensureChef())) return
  try {
    const id = route.params.id
    const response = await chefApi.get(`${API_BASE_URL}/api/recipes/${id}/?mode=chef`)
    recipe.value = response.data
  } catch (error) {
    console.error('Failed to fetch recipe', error)
    alert('无法加载菜谱，请稍后再试。')
    router.push('/')
  } finally {
    loading.value = false
  }
})

// 总页数
const totalSections = computed(() => {
  if (!recipe.value) return 0
  return 2 + (recipe.value.steps?.length || 0) // 封面 + 食材 + 步骤数
})

const nextSection = () => {
  if (currentSection.value < totalSections.value - 1) {
    currentSection.value++
  }
}

const prevSection = () => {
  if (currentSection.value > 0) {
    currentSection.value--
  }
}

const goToSection = (idx) => {
  currentSection.value = idx
}
</script>

<template>
  <div class="fixed inset-0 z-50 bg-gradient-to-br from-stone-900 via-stone-800 to-emerald-900 overflow-hidden">
    <!-- 背景装饰 -->
    <div class="absolute inset-0 opacity-30">
      <div class="absolute top-0 left-0 w-96 h-96 bg-emerald-500/20 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2"></div>
      <div class="absolute bottom-0 right-0 w-96 h-96 bg-amber-500/20 rounded-full blur-3xl translate-x-1/2 translate-y-1/2"></div>
    </div>
    
    <!-- 顶部导航 -->
    <div class="absolute top-0 left-0 right-0 z-50 p-4 flex justify-between items-center">
      <button @click="router.back()" class="text-white/70 hover:text-white transition-colors flex items-center gap-2 text-sm">
        <span class="text-lg">←</span> 返回
      </button>
      <div v-if="recipe" class="text-white/50 text-xs">
        {{ currentSection + 1 }} / {{ totalSections }}
      </div>
      <button @click="router.push('/')" class="text-white/70 hover:text-white transition-colors text-xl">
        ✕
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex-1 flex items-center justify-center h-full text-white">
      <div class="text-center">
        <div class="text-4xl mb-4 animate-bounce">🍳</div>
        <p class="text-lg animate-pulse">正在打开菜谱...</p>
      </div>
    </div>
    
    <!-- 主内容区 -->
    <div v-else-if="recipe" class="h-full flex flex-col pt-14 pb-20">
      <!-- 内容卡片 -->
      <div class="flex-1 flex items-center justify-center px-4 md:px-8">
        <div class="w-full max-w-2xl">
          <Transition name="slide-fade" mode="out-in">
            
            <!-- 封面 -->
            <div v-if="currentSection === 0" key="cover" class="bg-white rounded-2xl shadow-2xl overflow-hidden">
              <div class="relative h-64 md:h-80 overflow-hidden">
                <img v-if="recipe.cover_image" :src="recipe.cover_image" class="w-full h-full object-cover" />
                <div v-else class="w-full h-full bg-gradient-to-br from-emerald-100 to-amber-50 flex items-center justify-center text-6xl">🍽️</div>
                <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>
                <div class="absolute bottom-0 left-0 right-0 p-6 text-white">
                  <span class="text-xs uppercase tracking-widest text-emerald-300 mb-2 block">{{ recipe.category || '私房菜' }}</span>
                  <h1 class="text-3xl md:text-4xl font-bold mb-2">{{ recipe.title }}</h1>
                </div>
              </div>
              <div class="p-6">
                <p class="text-stone-600 text-lg leading-relaxed mb-6 font-serif italic">"{{ recipe.description || '用心烹饪的美味' }}"</p>
                <div class="flex items-center gap-6 text-sm text-stone-500">
                  <div class="flex items-center gap-2">
                    <span class="text-lg">⏱️</span>
                    <span>{{ recipe.cooking_time }} 分钟</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-lg">📝</span>
                    <span>{{ recipe.steps?.length || 0 }} 个步骤</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 食材页 -->
            <div v-else-if="currentSection === 1" key="ingredients" class="bg-white rounded-2xl shadow-2xl overflow-hidden p-6 md:p-8">
              <div class="flex items-center gap-3 mb-6">
                <span class="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center text-xl">🥬</span>
                <h2 class="text-2xl font-bold text-stone-800">准备食材</h2>
              </div>
              
              <div class="space-y-3 mb-8">
                <div 
                  v-for="(ing, idx) in recipe.ingredients" 
                  :key="ing.id" 
                  class="flex items-center justify-between p-3 rounded-lg hover:bg-stone-50 transition-colors group"
                  :style="{ animationDelay: `${idx * 50}ms` }"
                >
                  <div class="flex items-center gap-3">
                    <span class="w-6 h-6 rounded-full bg-emerald-500 text-white text-xs flex items-center justify-center font-bold">{{ idx + 1 }}</span>
                    <span class="text-stone-800 font-medium">{{ ing.ingredient_name }}</span>
                  </div>
                  <span class="text-emerald-600 font-bold bg-emerald-50 px-3 py-1 rounded-full text-sm">{{ ing.quantity }}</span>
                </div>
              </div>

              <div class="bg-amber-50 rounded-xl p-4 border border-amber-100">
                <div class="flex items-start gap-3">
                  <span class="text-2xl">💡</span>
                  <div>
                    <h4 class="font-bold text-amber-800 text-sm mb-1">主厨提示</h4>
                    <p class="text-amber-700 text-sm">{{ recipe.chef_notes || '确保食材新鲜，烹饪前准备就绪。' }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- 步骤页 -->
            <div 
              v-else 
              :key="`step-${currentSection}`" 
              class="bg-white rounded-2xl shadow-2xl overflow-hidden"
            >
              <div v-if="recipe.steps && recipe.steps[currentSection - 2]" class="flex flex-col">
                <!-- 步骤图片 -->
                <div v-if="recipe.steps[currentSection - 2].image" class="h-56 md:h-72 overflow-hidden relative">
                  <img :src="recipe.steps[currentSection - 2].image" class="w-full h-full object-cover" />
                  <div class="absolute top-4 left-4 bg-white/90 backdrop-blur-sm px-4 py-2 rounded-full">
                    <span class="text-emerald-700 font-bold">步骤 {{ recipe.steps[currentSection - 2].step_number }}</span>
                  </div>
                </div>
                
                <!-- 无图片时的步骤标题 -->
                <div v-else class="bg-gradient-to-r from-emerald-500 to-emerald-600 p-6">
                  <span class="text-white/70 text-sm">步骤</span>
                  <div class="text-white text-5xl font-bold">{{ String(recipe.steps[currentSection - 2].step_number).padStart(2, '0') }}</div>
                </div>

                <!-- 步骤内容 -->
                <div class="p-6 md:p-8">
                  <p class="text-stone-700 text-lg leading-relaxed">
                    {{ recipe.steps[currentSection - 2].description }}
                  </p>
                </div>
              </div>
            </div>

          </Transition>
        </div>
      </div>

      <!-- 底部导航 -->
      <div class="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-stone-900/80 to-transparent">
        <div class="max-w-2xl mx-auto">
          <!-- 进度指示器 -->
          <div class="flex justify-center gap-1.5 mb-4">
            <button 
              v-for="(_, idx) in totalSections" 
              :key="idx"
              @click="goToSection(idx)"
              class="transition-all duration-300"
              :class="idx === currentSection 
                ? 'w-6 h-2 bg-emerald-400 rounded-full' 
                : 'w-2 h-2 bg-white/30 hover:bg-white/50 rounded-full'"
            ></button>
          </div>
          
          <!-- 导航按钮 -->
          <div class="flex justify-between items-center">
            <button 
              @click="prevSection"
              :disabled="currentSection === 0"
              class="px-6 py-2 rounded-full text-white transition-all disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white/10"
            >
              ← 上一页
            </button>
            
            <button 
              v-if="currentSection < totalSections - 1"
              @click="nextSection"
              class="px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-white rounded-full font-bold transition-all shadow-lg hover:shadow-emerald-500/25 active:scale-95"
            >
              下一步 →
            </button>
            <button 
              v-else
              @click="router.push('/kitchen/chef/orders')"
              class="px-6 py-3 bg-amber-500 hover:bg-amber-400 text-white rounded-full font-bold transition-all shadow-lg hover:shadow-amber-500/25 active:scale-95"
            >
              完成阅读 ✓
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 页面切换动画 */
.slide-fade-enter-active {
  transition: all 0.4s ease-out;
}
.slide-fade-leave-active {
  transition: all 0.3s ease-in;
}
.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
</style>
