<template>
  <div class="home">

    <!-- ═══ A. 品牌 + 今日推荐 ═══════════════════════════ -->
    <section class="section-brand">
      <div class="brand-title">
        <h1 class="brand-name">诗语雅集</h1>
        <p class="brand-sub">以诗会友 · 飞花传情</p>
      </div>
      <div class="today-card" @click="$router.push('/explore')">
        <div class="today-badge">
          <van-icon name="fire-o" size="11" />
          今日推荐
        </div>
        <p class="today-line" v-if="dailyRecommend[0]">
          「{{ dailyRecommend[0].line }}」
        </p>
        <p class="today-line" v-else>「春眠不觉晓，处处闻啼鸟」</p>
        <p class="today-meta" v-if="dailyRecommend[0]">
          —— {{ dailyRecommend[0].title }} · {{ dailyRecommend[0].author }}
        </p>
        <p class="today-meta" v-else>—— 春晓 · 孟浩然</p>
      </div>
    </section>

    <!-- ═══ B. 游戏玩法 ══════════════════════════════════ -->
    <section class="section-games">
      <div class="section-header">
        <span class="header-title">诗词游戏</span>
        <div class="header-bar qinglu"></div>
      </div>
      <div class="games-grid">

        <!-- 飞花令练习 -->
        <div class="game-card primary" @click="$router.push('/solo-feihua')">
          <div class="game-icon-wrap">
            <van-icon name="fire-o" size="30" />
          </div>
          <div class="game-body">
            <div class="game-title">飞花令练习</div>
            <div class="game-desc">自由练习 / 限时挑战 / 接尾练习</div>
          </div>
          <div class="game-arrow">
            <van-icon name="arrow" size="20" />
          </div>
        </div>

        <div class="games-row">
          <!-- 接尾飞花令 -->
          <div class="game-card secondary" @click="$router.push('/tail-connect')">
            <div class="game-icon-wrap">
              <van-icon name="link" size="24" />
            </div>
            <div class="game-body">
              <div class="game-title">接尾飞花令</div>
              <div class="game-desc">多人接龙对战</div>
            </div>
          </div>
          <!-- 诗词品鉴 -->
          <div class="game-card secondary" @click="$router.push('/explore')">
            <div class="game-icon-wrap">
              <van-icon name="bookmark-o" size="24" />
            </div>
            <div class="game-body">
              <div class="game-title">诗词品鉴</div>
              <div class="game-desc">按朝代、意象、作者浏览</div>
            </div>
          </div>
        </div>

        <div class="games-row">
          <!-- 诗人雅集 -->
          <div class="game-card secondary" @click="$router.push('/poets')">
            <div class="game-icon-wrap">
              <van-icon name="friends-o" size="24" />
            </div>
            <div class="game-body">
              <div class="game-title">诗人雅集</div>
              <div class="game-desc">与李白、苏轼对坐清谈</div>
            </div>
          </div>
          <!-- 藏书阁 -->
          <div class="game-card secondary" @click="$router.push('/library')">
            <div class="game-icon-wrap">
              <van-icon name="bookmark" size="24" />
            </div>
            <div class="game-body">
              <div class="game-title">藏书阁</div>
              <div class="game-desc">金句卡片 · 书架收藏</div>
            </div>
          </div>
        </div>

        <div class="games-row">
          <!-- 语音对战 -->
          <div class="game-card secondary voice-battle" @click="$router.push('/voice-battle')">
            <div class="game-icon-wrap">
              <van-icon name="volume-o" size="24" />
            </div>
            <div class="game-body">
              <div class="game-title">语音对战</div>
              <div class="game-desc">AI朗读 · 语音回答</div>
            </div>
          </div>
          <!-- AI 成画 -->
          <div class="game-card secondary" @click="$router.push('/poem-card/p001')">
            <div class="game-icon-wrap">
              <van-icon name="photo-o" size="24" />
            </div>
            <div class="game-body">
              <div class="game-title">AI 诗词成画</div>
              <div class="game-desc">生成意境图片</div>
            </div>
          </div>
        </div>

      </div>
    </section>

    <!-- ═══ C. 文化探索【核心】 ═══════════════════════════ -->
    <section class="section-explore">
      <div class="section-header">
        <span class="header-title">文化探索</span>
        <div class="header-bar shiliu"></div>
      </div>

      <!-- 重点双卡片 -->
      <div class="explore-hero">
        <!-- 题库闯关 — 核心入口 -->
        <div class="explore-card hero-card challenge-card" @click="$router.push('/challenge')">
          <div class="hero-content">
            <div class="hero-badge">
              <van-icon name="award-o" size="12" />
              核心功能
            </div>
            <div class="hero-icon">
              <van-icon name="aim" size="36" />
            </div>
            <div class="hero-title">题库闯关</div>
            <div class="hero-desc">四维筛选，62万+诗句随机出题</div>
            <div class="hero-cta">开始挑战 →</div>
          </div>
        </div>

        <!-- 中国传统色 — 核心入口 -->
        <div class="explore-card hero-card color-card" @click="$router.push('/colors')">
          <div class="hero-content">
            <div class="hero-badge">
              <van-icon name="palette-o" size="12" />
              核心功能
            </div>
            <div class="hero-icon">
              <van-icon name="apps-o" size="36" />
            </div>
            <div class="hero-title">中国传统色</div>
            <div class="hero-desc">青绿山水，矿物颜料色值</div>
            <div class="hero-cta">探索色卡 →</div>
          </div>
        </div>
      </div>

      <!-- 次级四卡片 -->
      <div class="explore-sub">
        <div class="sub-card" @click="$router.push('/solar-term')">
          <van-icon name="calendar-o" size="18" />
          <span>二十四节气</span>
        </div>
        <div class="sub-card" @click="$router.push('/badges')">
          <van-icon name="award-o" size="18" />
          <span>徽章馆</span>
        </div>
        <div class="sub-card" @click="$router.push('/zen')">
          <van-icon name="flower-o" size="18" />
          <span>静心诗境</span>
        </div>
        <div class="sub-card" @click="$router.push('/me/favorites')">
          <van-icon name="star-o" size="18" />
          <span>我的收藏</span>
        </div>
      </div>
    </section>

    <!-- ═══ D. 雅集对战 ══════════════════════════════════ -->
    <section class="section-battle">
      <div class="section-header">
        <span class="header-title">雅集对战</span>
        <div class="header-bar zheshi"></div>
      </div>
      <div class="battle-grid">
        <div class="battle-card create-card" @click="$router.push('/room/create')">
          <div class="battle-icon-wrap">
            <van-icon name="plus" size="26" />
          </div>
          <div class="battle-title">创建雅集</div>
          <div class="battle-desc">邀请好友同席</div>
        </div>
        <div class="battle-card join-card" @click="$router.push('/join')">
          <div class="battle-icon-wrap">
            <van-icon name="friends-o" size="26" />
          </div>
          <div class="battle-title">加入雅集</div>
          <div class="battle-desc">输入房间号入席</div>
        </div>
      </div>
    </section>

    <!-- ═══ E. 次要工具 ═══════════════════════════════════ -->
    <section class="section-tools">
      <div class="tools-chips">
        <div class="tool-chip" @click="$router.push('/notes')">
          <van-icon name="description" size="14" />
          <span>私人诗摘</span>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'

const router = useRouter()
const dailyRecommend = ref<any[]>([])

async function loadData() {
  try {
    const recRes = await api.getExploreDaily()
    const recData = recRes.data
    if (recData?.poems?.length) dailyRecommend.value = recData.poems
  } catch {}
}

onMounted(loadData)
</script>

<style scoped>
.home {
  min-height: 100vh;
  padding-bottom: 40px;
  /* 与 main.css bg-xuanzhi 同款，但加底部渐变避免留白 */
  background-color: var(--xuan-paper);
}

/* ── 通用区块标题 ── */
.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
  margin-bottom: 14px;
}
.header-title {
  font-family: var(--font-display);
  font-size: 18px;
  color: #1A1A1A;
  white-space: nowrap;
  letter-spacing: 0.06em;
}
.header-bar {
  height: 2px;
  flex: 1;
  border-radius: 1px;
  opacity: 0.4;
}
.header-bar.qinglu   { background: linear-gradient(to right, var(--cinnabar, #D4AF37), transparent); }
.header-bar.shiliu   { background: linear-gradient(to right, var(--cinnabar, #D4AF37), transparent); }
.header-bar.zheshi    { background: linear-gradient(to right, var(--cinnabar, #D4AF37), transparent); }

/* ═══ A. 品牌区 ════════════════════════════════════════ */
.section-brand {
  padding: 28px 16px 24px;
  text-align: center;
}
.brand-name {
  font-family: var(--font-display);
  font-size: 30px;
  color: var(--ink-dark, #2C2C2C);
  margin-bottom: 6px;
  letter-spacing: 0.1em;
}
.brand-sub {
  font-size: 13px;
  color: var(--ink-mist, #7A8A8A);
  margin-bottom: 22px;
  letter-spacing: 0.12em;
}

/* 今日推荐 */
.today-card {
  background: var(--card, #FFFFFF);
  border: 1px solid var(--line, #E8E4DC);
  border-radius: var(--radius-lg);
  padding: 20px 22px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s var(--ease-out);
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(44,44,44,0.06);
}
.today-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--paper-warm, #F5F1E8) 0%, var(--card, #FFFFFF) 100%);
  pointer-events: none;
}
.today-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(212,175,55,0.1);
  border-color: var(--cinnabar, #D4AF37);
}
.today-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--cinnabar, #D4AF37);
  background: rgba(212,175,55,0.1);
  padding: 3px 12px;
  border-radius: var(--radius-full);
  margin-bottom: 12px;
  letter-spacing: 0.05em;
}
.today-line {
  font-family: var(--font-serif);
  font-size: 17px;
  line-height: 1.9;
  color: var(--ink-dark, #2C2C2C);
  margin-bottom: 10px;
  letter-spacing: 0.03em;
}
.today-meta {
  font-size: 12px;
  color: var(--ink-mist, #7A8A8A);
  letter-spacing: 0.05em;
}

/* ═══ B. 游戏玩法 ══════════════════════════════════════ */
.section-games { padding: 0 16px 28px; }

.games-grid { display: flex; flex-direction: column; gap: 10px; }

/* 主卡片 */
.game-card.primary {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 18px;
  background: var(--bamboo-pale);
  border: 1px solid rgba(42,100,70,0.28);
  border-radius: var(--radius-lg);
  box-shadow: 0 3px 16px rgba(30,70,50,0.14);
  cursor: pointer;
  transition: all 0.25s var(--ease-out);
}
.game-card.primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 20px rgba(212,175,55,0.2);
}
.game-card.primary .game-icon-wrap {
  background: rgba(255,255,255,0.15);
  color: white;
}
.game-card.primary .game-title {
  font-family: var(--font-display);
  font-size: 20px;
  color: white;
}

/* 两列次卡片 */
.games-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

.game-card.secondary {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 16px;
  background: var(--card, #FFFFFF);
  border-radius: var(--radius-md);
  border: 1px solid var(--line, #E8E4DC);
  box-shadow: 0 2px 8px rgba(44,44,44,0.04);
  cursor: pointer;
  transition: all 0.22s var(--ease-out);
}
.game-card.secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(212,175,55,0.12);
}
.game-card.secondary .game-icon-wrap {
  background: var(--paper-warm, #F5F1E8);
  color: var(--cinnabar, #D4AF37);
  margin-bottom: 10px;
}
.game-card.secondary .game-title {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--ink-dark, #2C2C2C);
  margin-bottom: 4px;
}
.game-card.secondary .game-desc {
  font-size: 11px;
  color: var(--ink-mist, #7A8A8A);
  line-height: 1.5;
}

/* 共享图标样式 */
.game-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.game-body { flex: 1; }
.game-title {
  font-family: var(--font-display);
  margin-bottom: 4px;
  letter-spacing: 0.04em;
}
.game-desc { font-size: 13px; color: var(--stone); }
.game-arrow {
  color: var(--bamboo-dark);
  opacity: 0.5;
  transition: all 0.2s;
}
.game-card.primary:hover .game-arrow { opacity: 1; transform: translateX(3px); }

/* ═══ C. 文化探索【核心板块】 ════════════════════════════ */
.section-explore { padding: 0 16px 28px; }

/* 重点双卡片 */
.explore-hero { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }

.explore-card.hero-card {
  border-radius: var(--radius-lg);
  position: relative;
  cursor: pointer;
  transition: all 0.25s var(--ease-out);
}
.explore-card.hero-card:hover {
  transform: translateY(-3px);
}

/* 题库闯关 */
.challenge-card {
  background: var(--card, #FFFFFF);
  border: 2px solid var(--line, #E8E4DC);
  min-height: 160px;
  box-shadow: 0 4px 16px rgba(44,44,44,0.08);
  transition: all 0.25s var(--ease-out);
}
.challenge-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 28px rgba(212,175,55,0.12);
}
.challenge-card .hero-badge { background: rgba(212,175,55,0.1); color: var(--cinnabar, #D4AF37); }
.challenge-card .hero-title { color: var(--ink-dark, #2C2C2C); }
.challenge-card .hero-desc  { color: var(--ink-light, #5A5A5A); }
.challenge-card .hero-cta   { color: var(--cinnabar, #D4AF37); }
.challenge-card .hero-icon   { color: var(--cinnabar, #D4AF37); }

/* 中国传统色 — 朱砂主题 */
.color-card {
  background: var(--card, #FFFFFF);
  border: 2px solid var(--line, #E8E4DC);
  border-radius: var(--radius-lg);
  min-height: 160px;
  box-shadow: 0 4px 16px rgba(44,44,44,0.08);
  transition: all 0.25s var(--ease-out);
}
.color-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 28px rgba(212,175,55,0.15);
}
.color-card .hero-badge { background: var(--cinnabar, #D4AF37); color: #fff; }
.color-card .hero-title { color: var(--ink-dark, #2C2C2C); }
.color-card .hero-desc  { color: var(--ink-light, #5A5A5A); }
.color-card .hero-cta   { color: var(--cinnabar, #D4AF37); }
.color-card .hero-icon  { color: var(--cinnabar, #D4AF37); }

.hero-content {
  position: relative;
  padding: 18px 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  margin-bottom: 10px;
  letter-spacing: 0.05em;
  width: fit-content;
}
.hero-icon { margin-bottom: 10px; }
.hero-title {
  font-family: var(--font-display);
  font-size: 17px;
  color: #1A1A1A;
  margin-bottom: 6px;
  letter-spacing: 0.06em;
}
.hero-desc { font-size: 12px; color: #333333; line-height: 1.6; margin-bottom: auto; }
.hero-cta {
  font-size: 12px;
  color: var(--bamboo-dark);
  margin-top: 10px;
  letter-spacing: 0.05em;
}

/* 次级四卡片 */
.explore-sub { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }

.sub-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  background: var(--card, #FFFFFF);
  border: 1px solid var(--line, #E8E4DC);
  border-radius: var(--radius-md);
  box-shadow: 0 2px 8px rgba(44,44,44,0.04);
  cursor: pointer;
  transition: all 0.2s var(--ease-out);
  color: var(--ink-dark, #2C2C2C);
  font-size: 13px;
}
.sub-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  color: var(--cinnabar, #D4AF37);
  border-color: var(--cinnabar, #D4AF37);
}
.sub-card .van-icon { color: var(--ink-mist, #7A8A8A); transition: color 0.2s; }
.sub-card:hover .van-icon { color: var(--cinnabar, #D4AF37); }

/* ═══ D. 雅集对战 ═══════════════════════════════════════ */
.section-battle { padding: 0 16px 28px; }

.battle-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

.battle-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 12px;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.22s var(--ease-out);
  text-align: center;
}
.battle-card:hover { transform: translateY(-2px); }

/* 创建 — 赭石 */
.battle-card.create-card {
  background: var(--card, #FFFFFF);
  border: 1px solid var(--line, #E8E4DC);
  box-shadow: 0 3px 10px rgba(44,44,44,0.06);
}
.battle-card.create-card:hover {
  box-shadow: 0 6px 24px rgba(212,175,55,0.12);
}
.battle-card.create-card .battle-icon-wrap {
  background: var(--paper-warm, #F5F1E8);
  color: var(--cinnabar, #D4AF37);
}
.battle-card.create-card .battle-title { color: var(--ink-dark, #2C2C2C); }

/* 加入 — 石绿 */
.battle-card.join-card {
  background: var(--card, #FFFFFF);
  border: 1px solid var(--line, #E8E4DC);
  box-shadow: 0 3px 10px rgba(44,44,44,0.06);
}
.battle-card.join-card:hover {
  box-shadow: 0 4px 18px rgba(212,175,55,0.12);
}
.battle-card.join-card .battle-icon-wrap {
  background: var(--paper-warm, #F5F1E8);
  color: var(--cinnabar, #D4AF37);
}
.battle-card.join-card .battle-title { color: var(--cinnabar, #D4AF37); }

.battle-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}
.battle-title {
  font-family: var(--font-display);
  font-size: 16px;
  margin-bottom: 5px;
  letter-spacing: 0.04em;
}
.battle-desc { font-size: 11px; color: var(--stone); }

/* ═══ E. 次要工具 ════════════════════════════════════════ */
.section-tools { padding: 0 16px; }

.tools-chips { display: flex; justify-content: center; gap: 8px; }

.tool-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 8px 16px;
  background: rgba(138,150,152,0.08);
  border: 1px solid rgba(138,150,152,0.15);
  border-radius: var(--radius-full);
  font-size: 12px;
  color: var(--ink-mist);
  cursor: pointer;
  transition: all 0.2s;
}
.tool-chip:hover {
  background: rgba(61,122,138,0.08);
  border-color: var(--bamboo-dark);
  color: var(--bamboo-dark);
}
</style>
