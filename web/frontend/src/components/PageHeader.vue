<template>
  <div class="page-header-bar">
    <div class="page-header-left">
      <el-icon v-if="icon" :size="24" class="page-header-icon" :style="{ color: iconColor }">
        <component :is="icon" />
      </el-icon>
      <div class="page-header-text">
        <h2 class="page-header-title">{{ title }}</h2>
        <p v-if="description" class="page-header-desc">{{ description }}</p>
      </div>
    </div>
    <div class="page-header-actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  icon: { type: String, default: '' },
  iconColor: { type: String, default: '#409eff' },
});
</script>

<style lang="scss" scoped>
.page-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.page-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-header-icon {
  flex-shrink: 0;
}

.page-header-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  line-height: 1.3;
}

.page-header-desc {
  margin: 2px 0 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.4;
}

.page-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
</style>
