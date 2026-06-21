<script setup lang="ts">
import { ArrowRight, Check, Promotion } from '@element-plus/icons-vue'

defineProps<{ eyebrow: string; title: string; description: string; step: string }>()
</script>

<template>
  <section class="auth-stage">
    <div class="auth-frame">
      <aside class="auth-story">
        <img class="auth-story-image" src="/auth-silver-wing.png" alt="" aria-hidden="true" />
        <div class="auth-story-shade"></div>
        <div class="story-topline">
          <span class="story-index">{{ step }}</span><span class="story-rule"></span><span>LIUYING COMMUNITY</span>
        </div>
        <div class="story-copy">
          <span class="story-kicker"><el-icon><Promotion /></el-icon>让知识持续流动</span>
          <h1>在银色微光里，<br />与新的灵感相遇。</h1>
          <p>记录技术思考，连接同路创作者。每一次分享，都会成为照亮下一段路的微光。</p>
        </div>
        <div class="story-points" aria-label="社区特性">
          <span><el-icon><Check /></el-icon>专注技术创作</span>
          <span><el-icon><Check /></el-icon>发现优质内容</span>
          <span><el-icon><Check /></el-icon>沉淀个人知识</span>
        </div>
      </aside>
      <div class="auth-workspace">
        <div class="auth-workspace-inner">
          <div class="auth-heading">
            <div><span class="auth-eyebrow">{{ eyebrow }}</span><h2>{{ title }}</h2></div>
            <span class="heading-mark" aria-hidden="true">LY</span>
          </div>
          <p class="auth-description">{{ description }}</p>
          <slot />
          <div class="auth-security">
            <span class="security-dot"></span>信息将通过加密连接安全传输<el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.auth-stage{min-height:calc(100vh - 113px);padding:clamp(24px,4vw,64px);overflow:hidden;background:radial-gradient(circle at 76% 15%,rgba(69,210,219,.15),transparent 26%),linear-gradient(135deg,#e9edef 0%,#f8fafb 45%,#dfe6e8 100%)}
.auth-frame{display:grid;grid-template-columns:minmax(420px,1.05fr) minmax(410px,.95fr);width:min(1120px,100%);min-height:650px;margin:0 auto;overflow:hidden;border:1px solid rgba(255,255,255,.9);border-radius:28px;background:rgba(246,249,250,.86);box-shadow:0 32px 80px rgba(39,59,65,.15),inset 0 0 0 1px rgba(117,139,145,.12)}
.auth-story{position:relative;display:flex;min-height:650px;flex-direction:column;justify-content:space-between;isolation:isolate;padding:42px;overflow:hidden;color:#17343a}
.auth-story-image,.auth-story-shade{position:absolute;inset:0;width:100%;height:100%}.auth-story-image{z-index:-3;object-fit:cover;filter:saturate(.82) contrast(.96)}
.auth-story-shade{z-index:-2;background:linear-gradient(180deg,rgba(237,245,246,.2),rgba(229,238,240,.9)),linear-gradient(90deg,rgba(235,243,244,.7),transparent 70%)}
.story-topline,.story-points,.story-kicker{display:flex;align-items:center}.story-topline{gap:12px;color:rgba(36,66,72,.68);font-size:.68rem;font-weight:700;letter-spacing:.14em}
.story-index{color:var(--cyan-700);font-size:.78rem}.story-rule{width:44px;height:1px;background:rgba(8,127,140,.48)}
.story-copy{max-width:470px;margin-top:auto;padding:80px 0 42px}.story-kicker{width:fit-content;gap:8px;margin-bottom:22px;padding:8px 12px;border:1px solid rgba(7,150,165,.18);border-radius:999px;background:rgba(247,253,253,.58);color:var(--cyan-700);font-size:.78rem;font-weight:700;backdrop-filter:blur(10px)}
.story-copy h1{margin:0;color:#173137;font-family:'Noto Serif SC','Source Han Serif SC','Songti SC',serif;font-size:clamp(2.1rem,3.4vw,3.45rem);font-weight:700;line-height:1.24;letter-spacing:-.055em}
.story-copy p{max-width:410px;margin:24px 0 0;color:rgba(36,64,70,.72);font-size:.93rem;line-height:1.9}
.story-points{flex-wrap:wrap;gap:10px 22px;padding-top:22px;border-top:1px solid rgba(65,102,109,.16);color:rgba(36,64,70,.75);font-size:.76rem}.story-points span{display:flex;align-items:center;gap:5px}.story-points .el-icon{color:var(--cyan-600)}
.auth-workspace{display:grid;place-items:center;padding:48px clamp(34px,5vw,72px);border-left:1px solid rgba(117,139,145,.14);background:linear-gradient(145deg,rgba(255,255,255,.94),rgba(244,248,249,.9))}
.auth-workspace-inner{width:min(100%,410px)}.auth-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:24px}.auth-eyebrow{display:block;margin-bottom:9px;color:var(--cyan-700);font-size:.72rem;font-weight:800;letter-spacing:.16em}
.auth-heading h2{margin:0;color:#1e3035;font-size:clamp(1.9rem,3vw,2.45rem);line-height:1.2;letter-spacing:-.045em}
.heading-mark{display:grid;width:42px;height:42px;flex:0 0 auto;place-items:center;border:1px solid rgba(7,150,165,.25);border-radius:13px;background:linear-gradient(145deg,#fff,#dfeaec);color:var(--cyan-700);font-size:.72rem;font-weight:900;box-shadow:0 8px 24px rgba(44,99,106,.12)}
.auth-description{margin:14px 0 30px;color:var(--silver-500);font-size:.88rem;line-height:1.75}.auth-security{display:flex;align-items:center;gap:8px;margin-top:24px;color:var(--silver-500);font-size:.72rem}.auth-security .el-icon{margin-left:auto}
.security-dot{width:6px;height:6px;border-radius:50%;background:var(--cyan-500);box-shadow:0 0 0 5px rgba(18,173,186,.1)}
@media(max-width:900px){.auth-stage{padding:24px}.auth-frame{grid-template-columns:minmax(260px,.72fr) minmax(390px,1fr)}.auth-story{padding:32px}.story-copy h1{font-size:2.2rem}.story-points{display:grid}}
@media(max-width:720px){.auth-stage{min-height:calc(100vh - 102px);padding:14px 12px 28px}.auth-frame{display:block;min-height:0;border-radius:22px}.auth-story{min-height:220px;padding:24px}.story-copy{padding:38px 0 0}.story-copy h1{font-size:1.8rem}.story-copy p,.story-points{display:none}.auth-workspace{padding:34px 24px 30px;border-top:1px solid rgba(117,139,145,.14);border-left:0}}
</style>
