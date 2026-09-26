/**
 * 语音合成 (Text-to-Speech) Composable
 * 支持多种 TTS 引擎：Web Speech API / Azure / 百度等
 */

import { ref, onMounted, onUnmounted } from 'vue'

// TTS 配置
interface TTSConfig {
  provider: 'webspeech' | 'azure' | 'baidu' | 'custom'
  apiKey?: string
  region?: string
  voiceName?: string
}

const defaultConfig: TTSConfig = {
  provider: 'webspeech'
}

export interface SpeechSynthesisOptions {
  lang?: string
  rate?: number
  pitch?: number
  volume?: number
  voice?: SpeechSynthesisVoice | null
}

// 中文语音偏好列表（按优先级）
const CHINESE_VOICE_PREFERENCES = [
  // 微软中文语音
  'Microsoft Xiaoxiao',
  'Microsoft Yuni',
  'Microsoft Xiaoxiao Neural',
  'Microsoft Yaoyao',
  'Microsoft Xiaohan',
  'Microsoft Xiaomeng',
  'Microsoft Xiaorus',
  'Microsoft Xiaoshuang',
  'Microsoft Sin-jen',
  'Microsoft Zhiwei',
  // 谷歌中文语音
  'Google 简体中文',
  'Google Chinese (Simplified)',
  'zh-CN',
  'zh-CN-Wavenet-A',
  'zh-CN-Wavenet-B',
  'zh-CN-Wavenet-C',
  'zh-CN-Wavenet-D',
  // 通用中文
  'Mandarin',
  'Chinese',
  'zh'
]

export function useSpeechSynthesis(config: Partial<TTSConfig> = {}) {
  const finalConfig = { ...defaultConfig, ...config }
  
  const isSupported = ref(false)
  const isSpeaking = ref(false)
  const voices = ref<SpeechSynthesisVoice[]>([])
  const currentVoice = ref<SpeechSynthesisVoice | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 检查支持
  onMounted(() => {
    if ('speechSynthesis' in window) {
      isSupported.value = true
      loadVoices()
      
      // 某些浏览器需要等待 voiceschanged 事件
      window.speechSynthesis.onvoiceschanged = () => {
        loadVoices()
      }
    }
  })

  // 加载并选择最佳语音
  function loadVoices() {
    const availableVoices = window.speechSynthesis.getVoices()
    voices.value = availableVoices
    
    // 智能选择最佳中文语音
    currentVoice.value = selectBestChineseVoice(availableVoices)
  }

  // 选择最佳中文语音
  function selectBestChineseVoice(availableVoices: SpeechSynthesisVoice[]): SpeechSynthesisVoice | null {
    // 方法1: 遍历偏好列表
    for (const pref of CHINESE_VOICE_PREFERENCES) {
      const found = availableVoices.find(v => 
        v.name.includes(pref) || 
        v.lang.includes(pref.replace('Microsoft ', ''))
      )
      if (found) return found
    }

    // 方法2: 直接搜索中文语音
    const chineseVoice = availableVoices.find(v => 
      v.lang.includes('zh') || 
      v.lang.includes('CN') ||
      v.lang.includes('cmn')
    )
    if (chineseVoice) return chineseVoice

    // 方法3: 返回第一个可用的
    return availableVoices[0] || null
  }

  // 获取所有中文语音
  function getChineseVoices(): SpeechSynthesisVoice[] {
    return voices.value.filter(v => 
      v.lang.includes('zh') || 
      v.lang.includes('CN')
    )
  }

  // 预览语音
  function previewVoice(voice: SpeechSynthesisVoice) {
    const text = '床前明月光，疑是地上霜。举头望明月，低头思故乡。'
    speak(text, { voice, rate: 0.9 })
  }

  // Web Speech API 朗读
  function speakWebSpeech(text: string, options: SpeechSynthesisOptions = {}): Promise<void> {
    return new Promise((resolve, reject) => {
      // 停止之前的朗读
      window.speechSynthesis.cancel()

      const utterance = new SpeechSynthesisUtterance(text)
      
      // 设置语言为中文
      utterance.lang = options.lang || 'zh-CN'
      utterance.rate = options.rate || 0.85 // 稍慢更自然
      utterance.pitch = options.pitch || 1.0
      utterance.volume = options.volume || 1.0
      
      // 设置语音
      if (options.voice) {
        utterance.voice = options.voice
      } else if (currentVoice.value) {
        utterance.voice = currentVoice.value
      }

      // 添加停顿使古诗更抑扬顿挫
      utterance.text = addPauseForPoetry(text)

      utterance.onstart = () => {
        isSpeaking.value = true
        error.value = null
      }

      utterance.onend = () => {
        isSpeaking.value = false
        resolve()
      }

      utterance.onerror = (event) => {
        isSpeaking.value = false
        error.value = event.error
        console.error('语音合成错误:', event.error)
        reject(event)
      }

      window.speechSynthesis.speak(utterance)
    })
  }

  // 为古诗词添加停顿
  function addPauseForPoetry(text: string): string {
    // 在句末添加短暂停顿
    const punctuations = ['，', '。', '！', '？', '、', '；', '：']
    let result = text
    
    for (const p of punctuations) {
      result = result.replace(new RegExp(p, 'g'), p + ' ')
    }
    
    return result
  }

  // 统一朗读接口
  async function speak(text: string, options: SpeechSynthesisOptions = {}): Promise<void> {
    if (!isSupported.value) {
      console.warn('语音合成不支持')
      return
    }

    try {
      switch (finalConfig.provider) {
        case 'webspeech':
        default:
          return speakWebSpeech(text, options)
      }
    } catch (err) {
      error.value = '语音合成失败'
      throw err
    }
  }

  // 停止朗读
  function stop() {
    if (isSupported.value) {
      window.speechSynthesis.cancel()
      isSpeaking.value = false
    }
  }

  // 暂停
  function pause() {
    if (isSupported.value) {
      window.speechSynthesis.pause()
    }
  }

  // 继续
  function resume() {
    if (isSupported.value) {
      window.speechSynthesis.resume()
    }
  }

  // 选择语音
  function selectVoice(voice: SpeechSynthesisVoice) {
    currentVoice.value = voice
    console.log('已选择语音:', voice.name, voice.lang)
  }

  // 获取当前配置信息
  function getConfig() {
    return {
      ...finalConfig,
      currentVoice: currentVoice.value?.name || '未选择',
      availableChineseVoices: getChineseVoices().map(v => v.name)
    }
  }

  // 清理
  onUnmounted(() => {
    stop()
  })

  return {
    // 状态
    isSupported,
    isSpeaking,
    isLoading,
    error,
    voices,
    currentVoice,
    
    // 方法
    speak,
    stop,
    pause,
    resume,
    selectVoice,
    previewVoice,
    getChineseVoices,
    getConfig
  }
}
