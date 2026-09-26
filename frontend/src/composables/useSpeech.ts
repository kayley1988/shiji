/**
 * 朗读工具（单例模式）
 * 浏览器原生 speechSynthesis，无需任何依赖
 */
import { ref } from 'vue'

// 单例状态，模块只初始化一次
const speaking = ref(false)
let currentText = ''

// 事件只注册一次
speechSynthesis.addEventListener('start', () => { speaking.value = true })
speechSynthesis.addEventListener('end',   () => { speaking.value = false })
speechSynthesis.addEventListener('error', () => { speaking.value = false })

export function speak(text: string, options?: { rate?: number; pitch?: number }): void {
  // 点同一段 = 停止
  if (speaking.value && currentText === text) {
    stop()
    return
  }
  stop()
  currentText = text

  const utt = new SpeechSynthesisUtterance(text)
  utt.lang = 'zh-CN'
  utt.rate = options?.rate ?? 0.85
  utt.pitch = options?.pitch ?? 0.95
  utt.volume = 1

  // 选中文语音
  const voices = speechSynthesis.getVoices()
  const zhVoice =
    voices.find(v => v.lang.includes('zh') && v.lang.includes('CN')) ||
    voices.find(v => v.lang.includes('zh')) ||
    voices[0]
  if (zhVoice) utt.voice = zhVoice

  speechSynthesis.speak(utt)
}

export function stop(): void {
  speechSynthesis.cancel()
  currentText = ''
  speaking.value = false
}

export { speaking }

export function useSpeech() {
  return { speak, stop, speaking }
}
