<template>
  <div class="console">
    <el-tabs>
      <el-tab-pane label="智能客服" lazy>
        <ChatPanel embedded />
      </el-tab-pane>
      <el-tab-pane label="用户会话" lazy>
        <ChatPanel scope="all" readonly embedded />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import ChatPanel from '@/components/ChatPanel.vue'
</script>

<style scoped>
.console {
  background: transparent;
}
</style>
