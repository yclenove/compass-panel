<template>
  <div class="empty-state">
    <el-icon :size="64" :color="color"><component :is="icon" /></el-icon>
    <h3 class="empty-title">{{ title }}</h3>
    <p class="empty-desc">{{ description }}</p>
    <slot name="actions" />
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '暂无数据' },
  description: { type: String, default: '' },
  icon: { type: String, default: 'FolderOpened' },
  color: { type: String, default: '#c0c4cc' },
});
</script>

<style lang="scss" scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-title {
  margin: 16px 0 8px;
  font-size: 16px;
  font-weight: 500;
  color: #606266;
}

.empty-desc {
  margin: 0 0 20px;
  font-size: 13px;
  color: #909399;
  max-width: 300px;
  line-height: 1.5;
}
</style>
