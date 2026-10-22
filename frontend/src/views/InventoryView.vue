<script setup>
import { ref, computed, onMounted } from 'vue'
import API_BASE_URL from '../config/api'
import { chefApi, useChefGuard } from '../composables/useChefAuth'

const { ensureChef } = useChefGuard()

const ingredients = ref([])
const loading = ref(true)
const newIngredientName = ref('')
const newIngredientCategory = ref('other')
const editingIngredient = ref(null)
const activeCategory = ref('all')

// 分类配置
const categories = {
    meat: { name: '肉类', icon: '🥩', color: 'rose', gradient: 'from-rose-500 to-red-600' },
    seafood: { name: '海鲜', icon: '🦐', color: 'cyan', gradient: 'from-cyan-500 to-blue-600' },
    vegetable: { name: '蔬菜', icon: '🥬', color: 'emerald', gradient: 'from-emerald-500 to-green-600' },
    seasoning: { name: '调味料', icon: '🧂', color: 'amber', gradient: 'from-amber-500 to-orange-600' },
    staple: { name: '主食/干货', icon: '🍚', color: 'yellow', gradient: 'from-yellow-500 to-amber-600' },
    dairy: { name: '乳制品', icon: '🧀', color: 'indigo', gradient: 'from-indigo-500 to-purple-600' },
    other: { name: '其他', icon: '📦', color: 'stone', gradient: 'from-stone-500 to-gray-600' }
}

// 按分类分组的食材
const groupedIngredients = computed(() => {
    const groups = {}
    for (const key of Object.keys(categories)) {
        groups[key] = ingredients.value.filter(i => i.category === key)
    }
    return groups
})

// 当前显示的分类
const visibleCategories = computed(() => {
    if (activeCategory.value === 'all') {
        return Object.keys(categories).filter(key => groupedIngredients.value[key].length > 0)
    }
    return [activeCategory.value]
})

// 统计信息
const stats = computed(() => {
    const total = ingredients.value.length
    const inStock = ingredients.value.filter(i => i.in_stock).length
    const outOfStock = total - inStock
    return { total, inStock, outOfStock }
})

const fetchIngredients = async () => {
    try {
        const response = await chefApi.get(`${API_BASE_URL}/api/ingredients/`)
        ingredients.value = response.data
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const toggleStock = async (ingredient) => {
    const originalQuantity = ingredient.quantity
    const originalInStock = ingredient.in_stock
    
    const newQuantity = ingredient.in_stock ? 0 : 100
    
    ingredient.quantity = newQuantity
    ingredient.in_stock = newQuantity > 0
    
    try {
        await chefApi.patch(`${API_BASE_URL}/api/ingredients/${ingredient.id}/`, {
            quantity: newQuantity
        })
    } catch (e) {
        ingredient.quantity = originalQuantity
        ingredient.in_stock = originalInStock
        alert('更新失败')
    }
}

const addIngredient = async () => {
    if (!newIngredientName.value.trim()) return
    try {
        const response = await chefApi.post(`${API_BASE_URL}/api/ingredients/`, {
            name: newIngredientName.value,
            category: newIngredientCategory.value,
            quantity: 100,
            unit: 'g'
        })
        ingredients.value.push(response.data)
        newIngredientName.value = ''
        newIngredientCategory.value = 'other'
    } catch (e) {
        alert('添加失败')
    }
}

const deleteIngredient = async (id) => {
    if (!confirm('确定删除该食材？')) return
    try {
        await chefApi.delete(`${API_BASE_URL}/api/ingredients/${id}/`)
        ingredients.value = ingredients.value.filter(i => i.id !== id)
    } catch (e) {
        alert('删除失败')
    }
}

const startEdit = (ingredient) => {
    editingIngredient.value = { ...ingredient }
}

const cancelEdit = () => {
    editingIngredient.value = null
}

const saveEdit = async () => {
    if (!editingIngredient.value) return
    try {
        await chefApi.patch(`${API_BASE_URL}/api/ingredients/${editingIngredient.value.id}/`, {
            name: editingIngredient.value.name,
            category: editingIngredient.value.category
        })
        const idx = ingredients.value.findIndex(i => i.id === editingIngredient.value.id)
        if (idx !== -1) {
            ingredients.value[idx].name = editingIngredient.value.name
            ingredients.value[idx].category = editingIngredient.value.category
        }
        editingIngredient.value = null
    } catch (e) {
        alert('保存失败')
    }
}

onMounted(async () => {
    if (await ensureChef()) fetchIngredients()
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-stone-100 via-amber-50 to-emerald-50">
    <div class="max-w-6xl mx-auto py-8 px-4">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-4xl font-bold bg-gradient-to-r from-emerald-600 to-amber-600 bg-clip-text text-transparent font-display">
          🧊 库存管理
        </h1>
        <p class="text-stone-500 mt-2">管理厨房食材与库存状态</p>
      </div>

      <!-- 统计卡片 -->
      <div class="grid grid-cols-3 gap-4 mb-8">
        <div class="bg-white/80 backdrop-blur rounded-2xl p-5 border border-stone-200/50 shadow-sm">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xl">
              📊
            </div>
            <div>
              <div class="text-2xl font-bold text-stone-800">{{ stats.total }}</div>
              <div class="text-sm text-stone-500">食材总数</div>
            </div>
          </div>
        </div>
        <div class="bg-white/80 backdrop-blur rounded-2xl p-5 border border-emerald-200/50 shadow-sm">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center text-white text-xl">
              ✅
            </div>
            <div>
              <div class="text-2xl font-bold text-emerald-600">{{ stats.inStock }}</div>
              <div class="text-sm text-stone-500">有库存</div>
            </div>
          </div>
        </div>
        <div class="bg-white/80 backdrop-blur rounded-2xl p-5 border border-red-200/50 shadow-sm">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-rose-600 flex items-center justify-center text-white text-xl">
              ⚠️
            </div>
            <div>
              <div class="text-2xl font-bold text-red-500">{{ stats.outOfStock }}</div>
              <div class="text-sm text-stone-500">缺货</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 添加新食材 -->
      <div class="bg-white/90 backdrop-blur p-6 rounded-2xl shadow-lg border border-stone-200/50 mb-8">
        <h3 class="text-lg font-bold text-stone-700 mb-4 flex items-center gap-2">
          <span class="text-2xl">➕</span> 添加新食材
        </h3>
        <div class="flex gap-4 flex-wrap">
          <input 
            v-model="newIngredientName" 
            @keyup.enter="addIngredient"
            class="flex-1 min-w-[200px] border border-stone-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 focus:outline-none transition-all bg-white"
            placeholder="输入食材名称，例如：黑胡椒..." 
          />
          <select 
            v-model="newIngredientCategory"
            class="border border-stone-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 focus:outline-none transition-all bg-white min-w-[140px]"
          >
            <option v-for="(cat, key) in categories" :key="key" :value="key">
              {{ cat.icon }} {{ cat.name }}
            </option>
          </select>
          <button 
            @click="addIngredient" 
            class="bg-gradient-to-r from-emerald-500 to-green-600 text-white px-8 py-3 rounded-xl font-bold hover:from-emerald-600 hover:to-green-700 transition-all shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
          >
            + 添加
          </button>
        </div>
      </div>

      <!-- 分类筛选标签 -->
      <div class="flex flex-wrap gap-2 mb-6">
        <button 
          @click="activeCategory = 'all'"
          class="px-4 py-2 rounded-full font-medium transition-all"
          :class="activeCategory === 'all' 
            ? 'bg-gradient-to-r from-stone-700 to-stone-800 text-white shadow-md' 
            : 'bg-white text-stone-600 hover:bg-stone-100 border border-stone-200'"
        >
          🏠 全部
        </button>
        <button 
          v-for="(cat, key) in categories" 
          :key="key"
          @click="activeCategory = key"
          class="px-4 py-2 rounded-full font-medium transition-all"
          :class="activeCategory === key 
            ? `bg-gradient-to-r ${cat.gradient} text-white shadow-md` 
            : 'bg-white text-stone-600 hover:bg-stone-100 border border-stone-200'"
        >
          {{ cat.icon }} {{ cat.name }}
          <span class="ml-1 text-xs opacity-75">({{ groupedIngredients[key].length }})</span>
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-16">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-emerald-500 border-t-transparent"></div>
        <p class="text-stone-500 mt-4">加载中...</p>
      </div>

      <!-- 分类食材列表 -->
      <div v-else class="space-y-8">
        <div 
          v-for="categoryKey in visibleCategories" 
          :key="categoryKey"
          class="bg-white/80 backdrop-blur rounded-2xl overflow-hidden shadow-lg border border-stone-200/50"
        >
          <!-- 分类标题 -->
          <div 
            class="px-6 py-4 flex items-center gap-3"
            :class="`bg-gradient-to-r ${categories[categoryKey].gradient}`"
          >
            <span class="text-3xl">{{ categories[categoryKey].icon }}</span>
            <div>
              <h2 class="text-xl font-bold text-white">{{ categories[categoryKey].name }}</h2>
              <p class="text-white/80 text-sm">{{ groupedIngredients[categoryKey].length }} 种食材</p>
            </div>
          </div>
          
          <!-- 食材网格 -->
          <div class="p-6">
            <div 
              v-if="groupedIngredients[categoryKey].length === 0" 
              class="text-center py-8 text-stone-400"
            >
              暂无此类食材
            </div>
            <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div 
                v-for="ing in groupedIngredients[categoryKey]" 
                :key="ing.id" 
                class="group relative bg-gradient-to-br from-white to-stone-50 p-4 rounded-xl border-2 transition-all duration-300 hover:shadow-md"
                :class="ing.in_stock 
                  ? 'border-stone-200 hover:border-emerald-300' 
                  : 'border-red-200 bg-gradient-to-br from-red-50 to-rose-50'"
              >
                <!-- 编辑模式 -->
                <div v-if="editingIngredient && editingIngredient.id === ing.id" class="space-y-3">
                  <input 
                    v-model="editingIngredient.name"
                    class="w-full border border-stone-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                    placeholder="食材名称"
                  />
                  <select 
                    v-model="editingIngredient.category"
                    class="w-full border border-stone-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  >
                    <option v-for="(cat, key) in categories" :key="key" :value="key">
                      {{ cat.icon }} {{ cat.name }}
                    </option>
                  </select>
                  <div class="flex gap-2">
                    <button 
                      @click="saveEdit"
                      class="flex-1 bg-emerald-500 text-white px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-emerald-600"
                    >
                      保存
                    </button>
                    <button 
                      @click="cancelEdit"
                      class="flex-1 bg-stone-200 text-stone-600 px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-stone-300"
                    >
                      取消
                    </button>
                  </div>
                </div>
                
                <!-- 显示模式 -->
                <div v-else class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                    <!-- 库存状态切换 -->
                    <button 
                      @click="toggleStock(ing)"
                      class="w-7 h-7 rounded-lg border-2 flex items-center justify-center transition-all duration-300 transform hover:scale-110"
                      :class="ing.in_stock 
                        ? 'bg-gradient-to-br from-emerald-400 to-green-500 border-emerald-500 text-white shadow-sm' 
                        : 'bg-white border-stone-300 text-transparent hover:border-emerald-400'"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                      </svg>
                    </button>
                    <!-- 食材名称 -->
                    <span 
                      class="font-semibold text-lg transition-colors"
                      :class="ing.in_stock ? 'text-stone-700' : 'text-red-400 line-through'"
                    >
                      {{ ing.name }}
                    </span>
                  </div>
                  
                  <!-- 操作按钮 -->
                  <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button 
                      @click="startEdit(ing)"
                      class="p-2 rounded-lg text-stone-400 hover:text-blue-500 hover:bg-blue-50 transition-colors"
                      title="编辑"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                      </svg>
                    </button>
                    <button 
                      @click="deleteIngredient(ing.id)"
                      class="p-2 rounded-lg text-stone-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                      title="删除"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                      </svg>
                    </button>
                  </div>
                </div>

                <!-- 缺货标识 -->
                <div 
                  v-if="!ing.in_stock" 
                  class="absolute -top-2 -right-2 bg-red-500 text-white text-xs px-2 py-0.5 rounded-full font-medium shadow-sm"
                >
                  缺货
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div 
          v-if="visibleCategories.length === 0 && !loading" 
          class="text-center py-16 bg-white/80 rounded-2xl"
        >
          <div class="text-6xl mb-4">📭</div>
          <p class="text-stone-500 text-lg">暂无食材数据</p>
          <p class="text-stone-400 text-sm mt-2">点击上方「添加」按钮创建第一个食材</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #d6d3d1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a29e;
}
</style>
