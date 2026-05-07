<template>
  <div class="file-edit-page">
    <!-- 顶部工具栏 -->
    <div class="page-card edit-toolbar">
      <div class="toolbar-left">
        <el-button :icon="Back" size="small" @click="goBack">返回</el-button>
        <span class="file-path">
          <el-icon><Document /></el-icon>
          {{ filePath }}
          <span v-if="isModified" class="modified-dot" title="文件已修改未保存">●</span>
        </span>
        <el-tag v-if="fileSize" size="small" type="info" effect="plain" class="file-size-tag">{{ fileSize }}</el-tag>
      </div>
      <div class="toolbar-center">
        <el-select v-model="currentLanguage" size="small" style="width: 130px" @change="handleLanguageChange">
          <el-option label="Plain Text" value="plaintext" />
          <el-option label="JavaScript" value="javascript" />
          <el-option label="TypeScript" value="typescript" />
          <el-option label="HTML" value="html" />
          <el-option label="CSS" value="css" />
          <el-option label="SCSS" value="scss" />
          <el-option label="JSON" value="json" />
          <el-option label="Python" value="python" />
          <el-option label="Shell" value="shell" />
          <el-option label="SQL" value="sql" />
          <el-option label="YAML" value="yaml" />
          <el-option label="XML" value="xml" />
          <el-option label="Markdown" value="markdown" />
          <el-option label="Go" value="go" />
          <el-option label="Java" value="java" />
          <el-option label="PHP" value="php" />
          <el-option label="Nginx" value="nginx" />
        </el-select>
        <el-select v-model="editorTheme" size="small" style="width: 120px">
          <el-option label="深色主题" value="vs-dark" />
          <el-option label="浅色主题" value="vs" />
          <el-option label="高对比度" value="hc-black" />
        </el-select>
        <div class="font-size-control">
          <el-button size="small" :icon="ZoomOut" circle @click="changeFontSize(-1)" :disabled="fontSize <= 10" />
          <span class="font-size-label">{{ fontSize }}px</span>
          <el-button size="small" :icon="ZoomIn" circle @click="changeFontSize(1)" :disabled="fontSize >= 28" />
        </div>
      </div>
      <div class="toolbar-right">
        <div class="editor-stats" v-if="fileContent">
          <span>{{ lineCount }} 行</span>
          <span class="stats-divider">|</span>
          <span>{{ charCount }} 字符</span>
        </div>
        <el-button type="primary" :icon="Check" size="small" :loading="saving" :disabled="!isModified" @click="handleSave">
          {{ isModified ? '保存 (Ctrl+S)' : '已保存' }}
        </el-button>
      </div>
    </div>

    <!-- 编辑器 -->
    <div class="editor-wrapper page-card">
      <FileEditor
        ref="editorRef"
        v-model="fileContent"
        :language="currentLanguage"
        :theme="editorTheme"
        :height="'calc(100vh - 200px)'"
        :loading="loading"
        @save="handleSave"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Back, Document, Check, ZoomIn, ZoomOut } from '@element-plus/icons-vue';
import FileEditor from '@/components/FileEditor.vue';
import { getFileContent, saveFileContent } from '@/api/files';

const router = useRouter();
const route = useRoute();

const editorRef = ref(null);
const filePath = ref('');
const fileContent = ref('');
const originalContent = ref('');
const currentLanguage = ref('plaintext');
const editorTheme = ref('vs-dark');
const loading = ref(false);
const saving = ref(false);
const fileSize = ref('');
const fontSize = ref(parseInt(localStorage.getItem('mw_editor_fontsize') || '14'));

// 文件修改状态
const isModified = computed(() => fileContent.value !== originalContent.value);

// 编辑器统计
const lineCount = computed(() => {
  if (!fileContent.value) return 0;
  return fileContent.value.split('\n').length;
});
const charCount = computed(() => fileContent.value?.length || 0);

// 字体大小调整
function changeFontSize(delta) {
  fontSize.value = Math.max(10, Math.min(28, fontSize.value + delta));
  localStorage.setItem('mw_editor_fontsize', String(fontSize.value));
  if (editorRef.value?.setFontSize) {
    editorRef.value.setFontSize(fontSize.value);
  }
}

function goBack() {
  router.push('/files');
}

function handleLanguageChange(lang) {
  if (editorRef.value) {
    editorRef.value.setLanguage(lang);
  }
}

async function loadFile() {
  const path = route.query.path;
  if (!path) {
    ElMessage.error('未指定文件路径');
    goBack();
    return;
  }

  filePath.value = path;
  loading.value = true;

  try {
    const res = await getFileContent(path);
    // API 返回格式: { status: true, msg: "OK", data: { status, encoding, data: "file content" } }
    const content = res.data?.data || res.data || '';
    fileContent.value = content;
    originalContent.value = content;

    // 文件大小
    const bytes = new Blob([content]).size;
    fileSize.value = formatBytes(bytes);

    // 自动检测语言
    if (editorRef.value) {
      const detected = editorRef.value.detectLanguage(path);
      currentLanguage.value = detected;
    }
  } catch (error) {
    ElMessage.error('读取文件失败: ' + (error.message || '未知错误'));
    goBack();
  } finally {
    loading.value = false;
  }
}

async function handleSave(content) {
  saving.value = true;
  try {
    const savedContent = content || fileContent.value;
    await saveFileContent(filePath.value, savedContent);
    originalContent.value = savedContent;
    ElMessage.success('保存成功');
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.message || '未知错误'));
  } finally {
    saving.value = false;
  }
}

function formatBytes(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const k = 1024;
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + units[i];
}

// 离开页面前提醒
function handleBeforeUnload(e) {
  if (isModified.value) {
    e.preventDefault();
    e.returnValue = '';
  }
}

onMounted(() => {
  loadFile();
  window.addEventListener('beforeunload', handleBeforeUnload);
});

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', handleBeforeUnload);
});
</script>

<style lang="scss" scoped>
.file-edit-page {
  .edit-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;

    .toolbar-left {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
      flex: 1;

      .file-path {
        display: flex;
        align-items: center;
        gap: 6px;
        color: #606266;
        font-size: 13px;
        font-family: monospace;
        max-width: 350px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;

        .modified-dot {
          color: #e6a23c;
          font-size: 16px;
          animation: pulse 1.5s ease-in-out infinite;
        }
      }

      .file-size-tag {
        flex-shrink: 0;
      }
    }

    .toolbar-center {
      display: flex;
      align-items: center;
      gap: 8px;

      .font-size-control {
        display: flex;
        align-items: center;
        gap: 4px;

        .font-size-label {
          font-size: 12px;
          color: #909399;
          min-width: 32px;
          text-align: center;
        }
      }
    }

    .toolbar-right {
      display: flex;
      align-items: center;
      gap: 12px;

      .editor-stats {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        color: #909399;

        .stats-divider {
          color: #dcdfe6;
        }
      }
    }
  }

  .editor-wrapper {
    padding: 0;
    overflow: hidden;
    margin-top: 0;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }
}
</style>
