import { io, Socket } from 'socket.io-client'
import { useRoomStore } from './stores/room'

class SocketClient {
  private socket: Socket | null = null
  private roomStore: ReturnType<typeof useRoomStore> | null = null

  connect() {
    if (this.socket?.connected) return

    this.socket = io({
      path: '/socket.io',
      transports: ['websocket', 'polling']
    })

    this.socket.on('connect', () => {
      console.log('Socket connected')
    })

    this.socket.on('disconnect', () => {
      console.log('Socket disconnected')
    })

    // 房间快照
    this.socket.on('room:snapshot', (data) => {
      this.roomStore?.updateRoom(data.room)
      this.roomStore?.updateMembers(data.members)
    })

    // 成员变化
    this.socket.on('room:member-changed', (data) => {
      this.roomStore?.fetchRoom(data.room_id)
    })

    // 游戏开始
    this.socket.on('game:started', (data) => {
      this.roomStore?.updateRoom({
        status: 'PLAYING',
        keywords: data.keywords,
        time_limit_sec: data.time_limit_sec
      })
    })

    // 回合开始
    this.socket.on('turn:started', (data) => {
      this.roomStore?.setCurrentTurn(data)
    })

    // 答案结果
    this.socket.on('answer:result', (data) => {
      console.log('Answer result:', data)
      // 可以在此显示结果 toast
    })

    // 玩家淘汰
    this.socket.on('player:eliminated', (data) => {
      console.log('Player eliminated:', data)
      this.roomStore?.fetchRoom(data.room_id)
    })

    // 游戏结束
    this.socket.on('game:finished', (data) => {
      console.log('Game finished:', data)
      window.location.href = `/room/${data.room_id}/result`
    })

    // 错误
    this.socket.on('system:error', (data) => {
      console.error('Socket error:', data)
    })
  }

  disconnect() {
    this.socket?.disconnect()
    this.socket = null
  }

  connectRoom(roomId: string) {
    if (!this.socket?.connected) {
      this.connect()
    }
    
    const token = localStorage.getItem('access_token')
    this.socket?.emit('room:subscribe', {
      room_id: roomId,
      access_token: token
    })
  }

  disconnectRoom() {
    this.socket?.emit('room:leave')
  }

  submitAnswer(roomId: string, turnId: string, text: string) {
    this.socket?.emit('answer:submit', {
      room_id: roomId,
      turn_id: turnId,
      text
    })
  }

  setRoomStore(store: ReturnType<typeof useRoomStore>) {
    this.roomStore = store
  }

  // 让组件自行注册/注销事件，避免内部硬编码冲突
  on(event: string, handler: (...args: any[]) => void) {
    this.socket?.on(event, handler)
  }
  off(event: string, handler: (...args: any[]) => void) {
    this.socket?.off(event, handler)
  }
  emit(event: string, payload?: any) {
    this.socket?.emit(event, payload)
  }
}

export const socket = new SocketClient()
