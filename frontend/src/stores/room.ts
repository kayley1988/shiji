import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../api'
import { socket } from '../socket'
import { useAuthStore } from './auth'

export interface Room {
  id?: string
  room_id?: string
  code: string
  host_user_id: string
  mode: 'CLASSIC' | 'SOLAR_TERM_ELEMENT'
  status: string
  keywords: string[]
  time_limit_sec: number
  max_players: number
  current_turn_no: number
  current_player_id?: string
  members?: Member[]
}

export interface Member {
  id: string
  user_id: string
  nickname: string
  role: 'host' | 'member'
  is_alive: boolean
  is_online: boolean
  seat_no?: number
  score?: number
}

export interface Turn {
  turn_id: string
  turn_no: number
  player_id: string
  deadline_at: string
  time_limit_sec: number
}

export const useRoomStore = defineStore('room', () => {
  const room = ref<Room | null>(null)
  const members = ref<Member[]>([])
  const currentTurn = ref<Turn | null>(null)
  const myRole = ref<'host' | 'member'>('member')
  const isMyTurn = computed(() => currentTurn.value?.player_id === getMyUserId())
  const isHost = computed(() => myRole.value === 'host')

  function getMyUserId() {
    const authStore = useAuthStore()
    return authStore.user?.id
  }

  // ── 房间操作 ───────────────────────────────
  async function createRoom(config: {
    mode: string
    keywords: string[]
    time_limit_sec: number
    max_players: number
  }) {
    const res = await api.createRoom(config)
    // 拦截器 unwrap → res = Flask { data: { room_id: ... } }
    const roomId = res.data.room_id
    room.value = { ...res.data, id: roomId }
    await joinRoom(roomId)
    return res.data
  }

  async function joinRoom(roomId: string, code?: string) {
    await api.joinRoom(roomId, code)
    await fetchRoom(roomId)
    socket.connectRoom(roomId)
  }

  async function fetchRoom(roomId: string) {
    const res = await api.getRoom(roomId)
    // res = Flask { data: { room_id, members, status, ... } }
    room.value = { ...res.data, id: res.data.room_id }
    members.value = res.data.members || []

    const myId = getMyUserId()
    const myMember = members.value.find(m => m.user_id === myId)
    myRole.value = myMember?.role || 'member'

    return res.data
  }

  async function startGame() {
    if (!room.value) throw new Error('房间不存在')
    const myId = getMyUserId()
    if (room.value.host_user_id !== myId) throw new Error('只有房主可以开始')
    return api.startRoom(room.value.room_id!)
  }

  // ── Socket 事件 ────────────────────────────
  function setCurrentTurn(turn: Turn) {
    currentTurn.value = turn
  }

  function updateRoom(patch: Partial<Room>) {
    room.value = { ...(room.value || ({} as Room)), ...patch }
  }

  function updateMembers(list: Member[]) {
    members.value = list || []
    const myId = getMyUserId()
    const myMember = members.value.find(m => m.user_id === myId)
    if (myMember) myRole.value = myMember.role
  }

  function handleGameFinished(_data: any) {
    currentTurn.value = null
    if (room.value) room.value.status = 'FINISHED'
  }

  function handleMemberJoined(member: Member) {
    if (!members.value.find(m => m.user_id === member.user_id)) {
      members.value.push(member)
    }
  }

  function handleMemberLeft(userId: string) {
    const idx = members.value.findIndex(m => m.user_id === userId)
    if (idx !== -1) members.value.splice(idx, 1)
  }

  function updateMemberStatus(userId: string, patch: Partial<Member>) {
    const m = members.value.find(m => m.user_id === userId)
    if (m) Object.assign(m, patch)
  }

  function reset() {
    room.value = null
    members.value = []
    currentTurn.value = null
    myRole.value = 'member'
  }

  return {
    room, members, currentTurn, myRole,
    isMyTurn, isHost,
    createRoom, joinRoom, fetchRoom, startGame,
    setCurrentTurn, updateRoom, updateMembers, handleGameFinished,
    handleMemberJoined, handleMemberLeft,
    updateMemberStatus, reset,
  }
})
