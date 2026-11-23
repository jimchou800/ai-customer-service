<template>
  <section class="brand">
    <div class="brand-mask"></div>
    <div class="brand-text">
      <h1>基于LangGraph的AI智能电商客服系统</h1>
      <div class="sub sub-1"><img src="@/assets/logos/ai.svg" alt="" /><span>多Agent协作，智能识别每一次咨询</span></div>
      <div class="sub sub-2"><img src="@/assets/logos/book.svg" alt="" /><span>RAG知识库，政策问答有据可依</span></div>
      <div class="sub sub-3"><img src="@/assets/logos/box.svg" alt="" /><span>订单物流工具，查询办理一步到位</span></div>
      <div class="sub sub-4"><img src="@/assets/logos/truck.svg" alt="" /><span>复杂问题自动升级，工单闭环处理</span></div>
      <div class="sub sub-5"><img src="@/assets/logos/shield.svg" alt="" /><span>支持图片识别，多模态售后更安心</span></div>
    </div>
  </section>
</template>

<style scoped>
.brand {
  position: relative;
  flex: 1;
  min-width: 0;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: url('@/assets/login-bg.jpg') center center / cover no-repeat;
}

.brand-mask {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(68, 18, 140, 0.62), rgba(92, 36, 168, 0.28) 46%, rgba(32, 12, 84, 0.55));
}

.brand-text {
  position: relative;
  z-index: 1;
  height: 66.67%;
  width: min(860px, 86%);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

h1 {
  margin: 0 0 18px;
  font-size: 60px;
  line-height: 1.22;
  font-weight: 800;
  background: linear-gradient(100deg, #fff36b 0%, #8dfff3 48%, #ff8ad8 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  filter: drop-shadow(0 8px 18px rgba(48, 0, 90, 0.35));
}

.sub {
  display: grid;
  grid-template-columns: 46px 1fr;
  align-items: center;
  column-gap: 14px;
  margin-top: 16px;
  font-size: 30px;
  font-weight: 700;
  line-height: 1.35;
  text-shadow: 0 3px 12px rgba(40, 0, 80, 0.45);
}

.sub img {
  width: 40px;
  height: 40px;
}

.sub-1 { color: #ffe56a; }
.sub-2 { color: #9fffee; }
.sub-3 { color: #ffd0f2; }
.sub-4 { color: #c9dcff; }
.sub-5 { color: #ffe1b0; }
</style>
