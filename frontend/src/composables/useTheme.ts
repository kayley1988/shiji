import { ref, computed } from 'vue'

export interface ThemeItem {
  id: string
  name: string
  icon: string
  desc: string
}

// 主题清单：id 与 main.css 里的 [data-theme] 对应
// yaji = 默认（无 data-theme 属性）
export const THEMES: ThemeItem[] = [
  { id: 'yaji', name: '鎏金·雅集', icon: '✨', desc: '雅金宣纸，暖调庄重' },
  { id: 'meihua', name: '梅花·暗香', icon: '🌺', desc: '红梅雪白，冷艳孤傲' },
  { id: 'qinglv', name: '青绿·山水', icon: '⛰️', desc: '青绿远黛，淡雅留白' },
  { id: 'shuimo', name: '水墨·素白', icon: '🖤', desc: '黑白极简，墨韵悠长' },
]

const STORAGE_KEY = 'shiji_theme'

const currentTheme = ref<string>('yaji')

export function useTheme() {
  function applyTheme(id: string) {
    currentTheme.value = id
    if (id === 'yaji') {
      document.documentElement.removeAttribute('data-theme')
    } else {
      document.documentElement.setAttribute('data-theme', id)
    }
    try {
      localStorage.setItem(STORAGE_KEY, id)
    } catch {
      // 忽略（隐私模式等）
    }
  }

  function initTheme() {
    let saved = 'yaji'
    try {
      saved = localStorage.getItem(STORAGE_KEY) || 'yaji'
    } catch {
      saved = 'yaji'
    }
    if (!THEMES.some(t => t.id === saved)) saved = 'yaji'
    applyTheme(saved)
  }

  const current = computed(() => THEMES.find(t => t.id === currentTheme.value) || THEMES[0])

  return { currentTheme, current, THEMES, applyTheme, initTheme }
}
