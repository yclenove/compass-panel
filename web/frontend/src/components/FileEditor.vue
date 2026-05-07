<template>
  <div class="file-editor-wrapper">
    <!-- 编辑器工具栏 -->
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <el-tooltip content="搜索 (Ctrl+F)" placement="top">
          <el-button :icon="Search" size="small" circle @click="openSearch" />
        </el-tooltip>
        <el-tooltip content="替换 (Ctrl+H)" placement="top">
          <el-button :icon="Edit" size="small" circle @click="openReplace" />
        </el-tooltip>
        <el-tooltip content="跳转到行 (Ctrl+G)" placement="top">
          <el-button :icon="Position" size="small" circle @click="showGoToLine = true" />
        </el-tooltip>
        <el-divider direction="vertical" />
        <el-tooltip content="折叠全部" placement="top">
          <el-button :icon="Fold" size="small" circle @click="foldAll" />
        </el-tooltip>
        <el-tooltip content="展开全部" placement="top">
          <el-button :icon="Expand" size="small" circle @click="unfoldAll" />
        </el-tooltip>
        <el-divider direction="vertical" />
        <el-tooltip content="撤销 (Ctrl+Z)" placement="top">
          <el-button :icon="RefreshLeft" size="small" circle @click="undo" />
        </el-tooltip>
        <el-tooltip content="重做 (Ctrl+Y)" placement="top">
          <el-button :icon="RefreshRight" size="small" circle @click="redo" />
        </el-tooltip>
      </div>
      <div class="toolbar-right">
        <el-select v-model="currentLanguage" size="small" style="width: 120px" @change="handleLanguageChange">
          <el-option label="JavaScript" value="javascript" />
          <el-option label="TypeScript" value="typescript" />
          <el-option label="HTML" value="html" />
          <el-option label="CSS" value="css" />
          <el-option label="JSON" value="json" />
          <el-option label="Python" value="python" />
          <el-option label="Shell" value="shell" />
          <el-option label="SQL" value="sql" />
          <el-option label="PHP" value="php" />
          <el-option label="Go" value="go" />
          <el-option label="Java" value="java" />
          <el-option label="Rust" value="rust" />
          <el-option label="YAML" value="yaml" />
          <el-option label="Markdown" value="markdown" />
          <el-option label="纯文本" value="plaintext" />
        </el-select>
        <el-select v-model="currentTheme" size="small" style="width: 120px; margin-left: 8px" @change="handleThemeChange">
          <el-option label="深色主题" value="vs-dark" />
          <el-option label="浅色主题" value="vs" />
          <el-option label="高对比度" value="hc-black" />
        </el-select>
      </div>
    </div>
    <div ref="editorContainer" class="editor-container" :style="{ height: editorHeight }"></div>
    <!-- 跳转到行对话框 -->
    <el-dialog v-model="showGoToLine" title="跳转到行" width="300px" append-to-body>
      <el-input-number v-model="goToLineNumber" :min="1" :max="totalLines" style="width: 100%" />
      <template #footer>
        <el-button @click="showGoToLine = false">取消</el-button>
        <el-button type="primary" @click="goToLine">跳转</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import {
  Search, Edit, Position, Fold, Expand,
  RefreshLeft, RefreshRight,
} from '@element-plus/icons-vue';

// Monaco Editor 延迟加载
let monaco = null;
let monacoLoadPromise = null;

async function loadMonaco() {
  if (monaco) return monaco;
  if (monacoLoadPromise) return monacoLoadPromise;
  monacoLoadPromise = import('monaco-editor').then((module) => {
    monaco = module;
    return module;
  });
  return monacoLoadPromise;
}

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  language: {
    type: String,
    default: 'plaintext',
  },
  theme: {
    type: String,
    default: 'vs-dark',
  },
  height: {
    type: String,
    default: '100%',
  },
  readOnly: {
    type: Boolean,
    default: false,
  },
  minimap: {
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits(['update:modelValue', 'save']);

const editorContainer = ref(null);
let editor = null;

// 工具栏状态
const currentLanguage = ref(props.language);
const currentTheme = ref(props.theme);
const showGoToLine = ref(false);
const goToLineNumber = ref(1);
const totalLines = ref(1);

// 计算编辑器高度（减去工具栏高度）
const editorHeight = computed(() => {
  if (props.height === '100%') return 'calc(100% - 40px)';
  return props.height;
});

// 语言检测
function detectLanguage(filename) {
  if (!filename) return props.language;

  const ext = filename.split('.').pop().toLowerCase();
  const langMap = {
    js: 'javascript',
    jsx: 'javascript',
    ts: 'typescript',
    tsx: 'typescript',
    vue: 'html',
    html: 'html',
    htm: 'html',
    css: 'css',
    scss: 'scss',
    sass: 'scss',
    less: 'less',
    json: 'json',
    xml: 'xml',
    yaml: 'yaml',
    yml: 'yaml',
    md: 'markdown',
    py: 'python',
    rb: 'ruby',
    go: 'go',
    java: 'java',
    c: 'c',
    cpp: 'cpp',
    h: 'c',
    hpp: 'cpp',
    sh: 'shell',
    bash: 'shell',
    zsh: 'shell',
    sql: 'sql',
    php: 'php',
    rs: 'rust',
    dockerfile: 'dockerfile',
    conf: 'ini',
    ini: 'ini',
    env: 'ini',
    txt: 'plaintext',
    log: 'plaintext',
    nginx: 'nginx',
    apache: 'apache',
  };

  return langMap[ext] || props.language;
}

// 初始化编辑器
async function initEditor() {
  if (!editorContainer.value) return;

  const monacoLib = await loadMonaco();

  editor = monacoLib.editor.create(editorContainer.value, {
    value: props.modelValue,
    language: props.language,
    theme: props.theme,
    readOnly: props.readOnly,
    minimap: { enabled: props.minimap },
    fontSize: 14,
    lineHeight: 22,
    fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', Consolas, 'Courier New', monospace",
    tabSize: 4,
    insertSpaces: true,
    wordWrap: 'on',
    automaticLayout: true,
    scrollBeyondLastLine: false,
    renderLineHighlight: 'all',
    smoothScrolling: true,
    cursorBlinking: 'smooth',
    cursorSmoothCaretAnimation: 'on',
    padding: { top: 12, bottom: 12 },
    bracketPairColorization: { enabled: true },
    guides: {
      bracketPairs: true,
      indentation: true,
    },
  });

  // 监听内容变化
  editor.onDidChangeModelContent(() => {
    const value = editor.getValue();
    emit('update:modelValue', value);
    // 更新总行数
    if (editor.getModel()) {
      totalLines.value = editor.getModel().getLineCount();
    }
  });

  // Ctrl+S 保存快捷键
  editor.addCommand(monacoLib.KeyMod.CtrlCmd | monacoLib.KeyCode.KeyS, () => {
    emit('save', editor.getValue());
  });
}

// 打开搜索
function openSearch() {
  if (editor) {
    editor.getAction('actions.find').run();
  }
}

// 打开替换
function openReplace() {
  if (editor) {
    editor.getAction('editor.action.startFindReplaceAction').run();
  }
}

// 折叠全部
function foldAll() {
  if (editor) {
    editor.getAction('editor.foldAll').run();
  }
}

// 展开全部
function unfoldAll() {
  if (editor) {
    editor.getAction('editor.unfoldAll').run();
  }
}

// 撤销
function undo() {
  if (editor) {
    editor.trigger('toolbar', 'undo');
  }
}

// 重做
function redo() {
  if (editor) {
    editor.trigger('toolbar', 'redo');
  }
}

// 跳转到行
function goToLine() {
  if (editor && goToLineNumber.value) {
    editor.revealLine(goToLineNumber.value);
    editor.setPosition({ lineNumber: goToLineNumber.value, column: 1 });
    showGoToLine.value = false;
  }
}

// 语言切换
function handleLanguageChange(lang) {
  setLanguage(lang);
}

// 主题切换
function handleThemeChange(theme) {
  if (monaco) {
    monaco.editor.setTheme(theme);
  }
}

// 更新编辑器选项
function updateOptions(options) {
  if (editor) {
    editor.updateOptions(options);
  }
}

// 设置编辑器值
function setValue(value) {
  if (editor) {
    editor.setValue(value || '');
  }
}

// 获取编辑器值
function getValue() {
  return editor ? editor.getValue() : '';
}

// 设置语言
function setLanguage(lang) {
  if (editor && monaco) {
    const model = editor.getModel();
    if (model) {
      monaco.editor.setModelLanguage(model, lang);
    }
  }
}

// 监听 props 变化
watch(
  () => props.modelValue,
  (newVal) => {
    if (editor && editor.getValue() !== newVal) {
      editor.setValue(newVal || '');
    }
  }
);

watch(
  () => props.language,
  (newLang) => {
    setLanguage(newLang);
  }
);

watch(
  () => props.theme,
  (newTheme) => {
    if (monaco) {
      monaco.editor.setTheme(newTheme);
    }
  }
);

watch(
  () => props.readOnly,
  (val) => {
    updateOptions({ readOnly: val });
  }
);

onMounted(() => {
  nextTick(() => {
    initEditor();
  });
});

onBeforeUnmount(() => {
  if (editor) {
    editor.dispose();
    editor = null;
  }
});

defineExpose({
  setValue,
  getValue,
  setLanguage,
  updateOptions,
  detectLanguage,
  openSearch,
  openReplace,
  foldAll,
  unfoldAll,
  undo,
  redo,
  goToLine,
});
</script>

<style lang="scss" scoped>
.file-editor-wrapper {
  width: 100%;
  height: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  flex-direction: column;

  .editor-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 12px;
    background: #f5f7fa;
    border-bottom: 1px solid #e4e7ed;
    min-height: 40px;
    flex-shrink: 0;

    .toolbar-left,
    .toolbar-right {
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .el-divider--vertical {
      margin: 0 4px;
      height: 16px;
    }
  }

  .editor-container {
    width: 100%;
    flex: 1;
    min-height: 400px;
  }
}
</style>
