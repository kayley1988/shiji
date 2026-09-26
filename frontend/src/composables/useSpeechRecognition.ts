/**
 * 语音识别 composable
 * 使用浏览器原生 Web Speech API
 * 仅将识别结果转为文字填入输入框，不上传任何音频
 */
import { ref, onUnmounted, computed } from 'vue'

interface SpeechRecognitionResult {
  readonly length: number
  item(index: number): SpeechRecognitionAlternative
  [index: number]: SpeechRecognitionAlternative
}

interface SpeechRecognitionAlternative {
  readonly transcript: string
  readonly confidence: number
}

interface SpeechRecognitionEvent {
  readonly results: SpeechRecognitionResult[]
  readonly resultIndex: number
}

interface SpeechRecognitionErrorEvent {
  readonly error: string
  readonly message: string
}

// 浏览器类型检测
const SpeechRecognitionAPI = 
  typeof window !== 'undefined' 
    ? (window.SpeechRecognition || window.webkitSpeechRecognition)
    : null

export interface SpeechRecognitionOptions {
  continuous?: boolean      // 是否连续识别
  interimResults?: boolean  // 是否返回临时结果
  lang?: string            // 语言
  maxAlternatives?: number // 最大候选数
}

export function useSpeechRecognition(options: SpeechRecognitionOptions = {}) {
  const {
    continuous = false,
    interimResults = true,
    lang = 'zh-CN',
    maxAlternatives = 1
  } = options

  // 状态
  const isSupported = ref(!!SpeechRecognitionAPI)
  const isListening = ref(false)
  const transcript = ref('')
  const interimTranscript = ref('')
  const error = ref<string | null>(null)
  const confidence = ref(0)

  let recognition: ReturnType<typeof SpeechRecognitionAPI> | null = null

  // 计算属性
  const finalTranscript = computed(() => transcript.value)

  // 初始化
  function init() {
    if (!SpeechRecognitionAPI) {
      error.value = '您的浏览器不支持语音识别'
      return
    }

    recognition = new SpeechRecognitionAPI()
    recognition.continuous = continuous
    recognition.interimResults = interimResults
    recognition.lang = lang
    recognition.maxAlternatives = maxAlternatives

    // 结果处理
    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let final = ''
      let interim = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        if ((result as any).isFinal) {
          final += result[0].transcript
          confidence.value = result[0].confidence
        } else {
          interim += result[0].transcript
        }
      }

      if (final) {
        transcript.value = final.trim()
      }
      interimTranscript.value = interim
    }

    // 错误处理
    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      console.error('Speech recognition error:', event.error)
      
      switch (event.error) {
        case 'no-speech':
          error.value = '没有检测到语音，请重试'
          break
        case 'audio-capture':
          error.value = '无法访问麦克风'
          break
        case 'not-allowed':
          error.value = '麦克风权限被拒绝'
          break
        case 'network':
          error.value = '网络错误，请检查网络连接'
          break
        case 'aborted':
          // 用户主动停止，不算错误
          break
        default:
          error.value = `语音识别错误: ${event.error}`
      }

      isListening.value = false
    }

    // 开始
    recognition.onstart = () => {
      isListening.value = true
      error.value = null
    }

    // 结束
    recognition.onend = () => {
      isListening.value = false
    }
  }

  // 开始识别
  function start() {
    if (!recognition) {
      init()
    }

    if (!recognition) {
      error.value = '语音识别初始化失败'
      return
    }

    try {
      recognition.start()
    } catch (e) {
      // 如果已经在运行，先停止
      recognition.stop()
      try {
        recognition.start()
      } catch (e2) {
        error.value = '无法启动语音识别'
      }
    }
  }

  // 停止识别
  function stop() {
    if (recognition && isListening.value) {
      recognition.stop()
    }
  }

  // 中止
  function abort() {
    if (recognition) {
      recognition.abort()
      isListening.value = false
    }
  }

  // 清除结果
  function clear() {
    transcript.value = ''
    interimTranscript.value = ''
    confidence.value = 0
    error.value = null
  }

  // 销毁
  function destroy() {
    abort()
    recognition = null
  }

  // 初始化的隐私提示
  function getPrivacyNotice(): string {
    return '语音将由浏览器本地识别为文字，不会上传任何音频数据'
  }

  // 导出
  onUnmounted(() => {
    destroy()
  })

  return {
    // 状态
    isSupported,
    isListening,
    transcript: finalTranscript,
    interimTranscript,
    error,
    confidence,

    // 方法
    start,
    stop,
    abort,
    clear,
    init,
    getPrivacyNotice,
    destroy
  }
}

// 类型声明（TS DOM lib 未内置 SpeechRecognition 时兜底）
declare global {
  interface Window {
    SpeechRecognition: any
    webkitSpeechRecognition: any
  }
}
