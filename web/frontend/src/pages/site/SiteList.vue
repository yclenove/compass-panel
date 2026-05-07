<template>
  <div class="site-list">
    <!-- 搜索和过滤栏 -->
    <el-card class="filter-card">
      <el-row :gutter="16" align="middle">
        <el-col :xs="24" :sm="8" :md="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索网站名称或备注"
            clearable
            prefix-icon="Search"
            @input="handleSearch"
          />
        </el-col>
        <el-col :xs="24" :sm="8" :md="4">
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="handleFilter">
            <el-option label="全部" value="" />
            <el-option label="运行中" :value="1" />
            <el-option label="已停止" :value="0" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="8" :md="4">
          <el-select v-model="typeFilter" placeholder="分类筛选" clearable @change="handleFilter">
            <el-option label="全部" value="" />
            <el-option
              v-for="t in siteTypes"
              :key="t.id"
              :label="t.name"
              :value="String(t.id)"
            />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="24" :md="10" class="action-buttons">
          <el-button type="primary" icon="Plus" @click="showAddSite">添加站点</el-button>
          <el-button icon="Folder" @click="showSiteTypesDialog">管理分类</el-button>
          <el-button icon="Refresh" @click="fetchSites">刷新</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="总站点数" :value="stats.total">
            <template #prefix><el-icon style="color: #409eff"><ChromeFilled /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="运行中" :value="stats.running">
            <template #prefix><el-icon style="color: #67c23a"><CircleCheckFilled /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="已停止" :value="stats.stopped">
            <template #prefix><el-icon style="color: #f56c6c"><CircleCloseFilled /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="SSL 证书" :value="stats.ssl">
            <template #prefix><el-icon style="color: #e6a23c"><Lock /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 网站列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>网站列表</span>
          <div class="header-actions">
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button label="table">表格</el-radio-button>
              <el-radio-button label="card">卡片</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>

      <!-- 表格视图 -->
      <el-table
        v-if="viewMode === 'table'"
        :data="filteredSiteList"
        stripe
        v-loading="loading"
        @selection-change="handleSelectionChange"
        @sort-change="handleSortChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="网站名称" min-width="180" sortable="custom" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="site-name">
              <el-icon class="site-icon"><ChromeFilled /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="根目录" min-width="200" show-overflow-tooltip />
        <el-table-column prop="type_id" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type_id)" size="small">
              {{ getTypeName(row.type_id) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" sortable="custom">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" effect="dark">
              {{ row.status === 1 ? '运行中' : '已停止' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="SSL" width="80" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.ssl" style="color: #67c23a"><Lock /></el-icon>
            <el-icon v-else style="color: #c0c4cc"><Unlock /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="edate" label="到期时间" width="120">
          <template #default="{ row }">
            <span :class="{ 'text-danger': isExpired(row.edate) }">
              {{ row.edate === '0000-00-00' ? '永久' : row.edate }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="add_time" label="创建时间" width="160" sortable="custom" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="editSite(row)">设置</el-button>
            <el-button :type="row.status === 1 ? 'warning' : 'success'" link @click="toggleSite(row)">
              {{ row.status === 1 ? '停止' : '启动' }}
            </el-button>
            <el-dropdown @command="(cmd) => handleCommand(cmd, row)">
              <el-button type="primary" link>更多</el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="ssl">SSL 证书</el-dropdown-item>
                  <el-dropdown-item command="domain">域名管理</el-dropdown-item>
                  <el-dropdown-item command="proxy">反向代理</el-dropdown-item>
                  <el-dropdown-item command="redirect">重定向</el-dropdown-item>
                  <el-dropdown-item command="security">防盗链</el-dropdown-item>
                  <el-dropdown-item command="backup">备份</el-dropdown-item>
                  <el-dropdown-item command="log">日志</el-dropdown-item>
                  <el-dropdown-item command="config">配置文件</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 卡片视图 -->
      <el-row v-else :gutter="16" v-loading="loading">
        <el-col v-for="site in filteredSiteList" :key="site.id" :xs="24" :sm="12" :md="8" :lg="6">
          <el-card shadow="hover" class="site-card" @click="editSite(site)">
            <div class="site-card-header">
              <el-icon :size="32" :style="{ color: site.status === 1 ? '#67c23a' : '#f56c6c' }">
                <ChromeFilled />
              </el-icon>
              <el-tag :type="site.status === 1 ? 'success' : 'danger'" size="small">
                {{ site.status === 1 ? '运行中' : '已停止' }}
              </el-tag>
            </div>
            <h3 class="site-card-name">{{ site.name }}</h3>
            <p class="site-card-path">{{ site.path }}</p>
            <div class="site-card-footer">
              <span class="site-card-type">{{ getTypeName(site.type_id) }}</span>
              <span class="site-card-date">{{ site.add_time }}</span>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 分页 -->
      <el-pagination
        v-if="total > 0"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <!-- 批量操作栏 -->
    <transition name="el-zoom-in-bottom">
      <div v-if="selectedSites.length > 0" class="batch-actions">
        <el-card>
          <div class="batch-content">
            <span class="batch-info">已选择 {{ selectedSites.length }} 个站点</span>
            <el-button type="success" @click="batchStart">批量启动</el-button>
            <el-button type="warning" @click="batchStop">批量停止</el-button>
            <el-button type="danger" @click="batchDelete">批量删除</el-button>
            <el-button @click="clearSelection">取消选择</el-button>
          </div>
        </el-card>
      </div>
    </transition>

    <!-- 添加站点对话框 -->
    <el-dialog v-model="addSiteVisible" title="添加站点" width="600px">
      <el-form :model="addSiteForm" :rules="addSiteRules" ref="addSiteFormRef" label-width="100px">
        <el-form-item label="网站名称" prop="name">
          <el-input v-model="addSiteForm.name" placeholder="请输入网站域名" />
        </el-form-item>
        <el-form-item label="根目录" prop="path">
          <el-input v-model="addSiteForm.path" placeholder="请输入网站根目录" />
        </el-form-item>
        <el-form-item label="网站备注" prop="ps">
          <el-input v-model="addSiteForm.ps" placeholder="请输入备注" />
        </el-form-item>
        <el-form-item label="PHP版本" prop="php_version">
          <el-select v-model="addSiteForm.php_version" placeholder="选择PHP版本">
            <el-option label="PHP-7.4" value="74" />
            <el-option label="PHP-8.0" value="80" />
            <el-option label="PHP-8.1" value="81" />
            <el-option label="PHP-8.2" value="82" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addSiteVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAddSite" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 站点管理对话框 -->
    <el-dialog v-model="siteManageVisible" :title="'站点管理 - ' + (currentSite.name || '')" width="900px" top="5vh">
      <el-tabs v-model="manageTab" @tab-change="handleManageTabChange">
        <!-- 基本设置 -->
        <el-tab-pane label="基本设置" name="basic">
          <el-form :model="siteBasicForm" label-width="100px" class="site-manage-form">
            <el-form-item label="网站名称">
              <el-input :value="currentSite.name" disabled style="max-width: 400px" />
            </el-form-item>
            <el-form-item label="根目录">
              <el-input v-model="siteBasicForm.path" style="max-width: 400px">
                <template #append>
                  <el-button @click="saveSitePath" type="primary">保存</el-button>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="网站备注">
              <el-input v-model="siteBasicForm.ps" style="max-width: 400px">
                <template #append>
                  <el-button @click="saveSiteRemark" type="primary">保存</el-button>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="到期时间">
              <el-date-picker
                v-model="siteBasicForm.edate"
                type="date"
                placeholder="选择到期时间"
                value-format="YYYY-MM-DD"
                style="max-width: 300px"
              />
              <el-button type="primary" style="margin-left: 8px" @click="saveSiteEndDate">保存</el-button>
              <el-button @click="siteBasicForm.edate = '0000-00-00'">永久</el-button>
            </el-form-item>
            <el-form-item label="PHP版本">
              <el-select v-model="siteBasicForm.phpVersion" placeholder="选择PHP版本" style="max-width: 200px">
                <el-option v-for="v in phpVersions" :key="v" :label="'PHP-' + v" :value="v" />
              </el-select>
              <el-button type="primary" style="margin-left: 8px" @click="saveSitePhpVersion">切换</el-button>
            </el-form-item>
            <el-form-item label="默认文档">
              <el-input v-model="siteBasicForm.index" type="textarea" :rows="3" style="max-width: 400px" placeholder="index.php&#10;index.html" />
              <el-button type="primary" style="margin-left: 8px" @click="saveSiteIndex">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 域名管理 -->
        <el-tab-pane label="域名管理" name="domain">
          <div class="domain-manage">
            <el-alert
              :title="`已绑定 ${domainList.length} 个域名`"
              type="info"
              :closable="false"
              show-icon
              style="margin-bottom: 16px"
            />
            <el-row :gutter="16" style="margin-bottom: 16px">
              <el-col :span="12">
                <el-input v-model="newDomain" placeholder="输入域名，如 example.com" @keyup.enter="addDomain" />
              </el-col>
              <el-col :span="6">
                <el-input v-model="newDomainPort" placeholder="端口(默认80)" />
              </el-col>
              <el-col :span="6">
                <el-button type="primary" @click="addDomain" :loading="domainLoading" style="width: 100%">
                  <el-icon><Plus /></el-icon> 添加域名
                </el-button>
              </el-col>
            </el-row>

            <el-input
              v-model="batchDomains"
              type="textarea"
              :rows="3"
              placeholder="批量添加域名，每行一个，如:&#10;example.com&#10;www.example.com&#10;api.example.com"
              style="margin-bottom: 8px"
            />
            <el-button type="success" size="small" @click="batchAddDomains" :loading="domainLoading" style="margin-bottom: 16px">
              批量添加
            </el-button>

            <el-table :data="domainList" stripe v-loading="domainLoading">
              <el-table-column prop="name" label="域名" min-width="200" />
              <el-table-column prop="port" label="端口" width="100" />
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="copyDomain(row)">复制</el-button>
                  <el-button type="danger" link size="small" @click="removeDomain(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- SSL证书 -->
        <el-tab-pane label="SSL证书" name="ssl">
          <div class="ssl-manage" v-loading="sslLoading">
            <el-alert
              v-if="sslInfo && sslInfo.notAfter"
              :title="getSslExpiryTitle(sslInfo.notAfter)"
              :type="getSslExpiryType(sslInfo.notAfter)"
              :closable="false"
              show-icon
              style="margin-bottom: 16px"
            />

            <el-descriptions :column="2" border v-if="sslInfo" style="margin-bottom: 16px">
              <el-descriptions-item label="域名">{{ sslInfo.domain || currentSite.name }}</el-descriptions-item>
              <el-descriptions-item label="品牌">{{ sslInfo.brand || '-' }}</el-descriptions-item>
              <el-descriptions-item label="到期时间">{{ sslInfo.notAfter || '-' }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="sslInfo.status ? 'success' : 'info'">
                  {{ sslInfo.status ? '已部署' : '未部署' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
            <el-empty v-else description="暂无SSL证书信息" />

            <el-divider />

            <h4>证书操作</h4>
            <div class="ssl-actions">
              <el-button type="primary" @click="forceHttps" :loading="sslActionLoading">
                <el-icon><Lock /></el-icon> 强制HTTPS
              </el-button>
              <el-button type="warning" @click="closeHttps" :loading="sslActionLoading">
                <el-icon><Unlock /></el-icon> 关闭HTTPS
              </el-button>
              <el-button type="danger" @click="closeSsl" :loading="sslActionLoading">
                <el-icon><Close /></el-icon> 关闭SSL
              </el-button>
              <el-button @click="fetchSslInfo" :loading="sslLoading">
                <el-icon><Refresh /></el-icon> 刷新
              </el-button>
            </div>

            <el-divider />

            <h4>手动上传证书</h4>
            <el-form label-width="80px">
              <el-form-item label="KEY">
                <el-input v-model="sslUploadKey" type="textarea" :rows="4" placeholder="粘贴证书KEY内容" />
              </el-form-item>
              <el-form-item label="PEM/CSR">
                <el-input v-model="sslUploadCsr" type="textarea" :rows="4" placeholder="粘贴证书PEM/CSR内容" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="uploadSsl" :loading="sslActionLoading">保存证书</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 备份管理 -->
        <el-tab-pane label="备份管理" name="backup">
          <div class="backup-manage">
            <el-button type="primary" @click="createBackup" :loading="backupLoading" style="margin-bottom: 16px">
              <el-icon><Download /></el-icon> 创建备份
            </el-button>
            <el-table :data="backupList" stripe v-loading="backupLoading">
              <el-table-column prop="filename" label="备份文件" min-width="250" show-overflow-tooltip />
              <el-table-column prop="size" label="大小" width="100">
                <template #default="{ row }">{{ formatSize(row.size) }}</template>
              </el-table-column>
              <el-table-column prop="addtime" label="备份时间" width="180" />
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button type="danger" link @click="deleteBackup(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 日志查看 -->
        <el-tab-pane label="日志查看" name="log">
          <div class="log-manage">
            <el-tabs v-model="logType" @tab-change="fetchSiteLogs">
              <el-tab-pane label="访问日志" name="access" />
              <el-tab-pane label="错误日志" name="error" />
            </el-tabs>
            <el-input
              v-model="logContent"
              type="textarea"
              :rows="15"
              readonly
              placeholder="暂无日志内容"
              v-loading="logLoading"
            />
            <div style="margin-top: 8px; text-align: right">
              <el-button @click="fetchSiteLogs" :loading="logLoading">刷新日志</el-button>
            </div>
          </div>
        </el-tab-pane>

        <!-- 伪静态 -->
        <el-tab-pane label="伪静态" name="rewrite">
          <div class="rewrite-manage" v-loading="rewriteLoading">
            <div class="rewrite-toolbar">
              <el-select
                v-model="selectedRewriteTpl"
                placeholder="选择伪静态模板"
                style="width: 200px"
                @change="loadRewriteTpl"
                clearable
              >
                <el-option
                  v-for="tpl in rewriteTplList"
                  :key="tpl"
                  :label="tpl"
                  :value="tpl"
                />
              </el-select>
              <el-button @click="fetchRewriteTpls" :loading="rewriteTplLoading">刷新模板</el-button>
            </div>
            <el-input
              v-model="rewriteContent"
              type="textarea"
              :rows="15"
              placeholder="输入伪静态规则，或从上方选择模板"
            />
            <div style="margin-top: 8px; text-align: right">
              <el-button type="primary" @click="saveRewrite" :loading="rewriteLoading">保存</el-button>
              <el-button @click="fetchRewriteConf">刷新</el-button>
            </div>
          </div>
        </el-tab-pane>

        <!-- 配置文件 -->
        <el-tab-pane label="配置文件" name="config">
          <div class="config-manage" v-loading="configLoading">
            <el-input
              v-model="configContent"
              type="textarea"
              :rows="20"
              placeholder="站点配置文件内容"
            />
            <div style="margin-top: 8px; text-align: right">
              <el-button type="primary" @click="saveConfig" :loading="configLoading">保存</el-button>
              <el-button @click="fetchSiteConfig">刷新</el-button>
            </div>
          </div>
        </el-tab-pane>

        <!-- 流量限制 -->
        <el-tab-pane label="流量限制" name="limit">
          <div class="limit-manage" v-loading="limitLoading">
            <el-form :model="limitForm" label-width="120px" style="max-width: 500px">
              <el-form-item label="并发限制">
                <el-input v-model="limitForm.perserver" placeholder="如 50" />
                <span class="form-tip">单站点最大并发数</span>
              </el-form-item>
              <el-form-item label="单IP限制">
                <el-input v-model="limitForm.perip" placeholder="如 10" />
                <span class="form-tip">单IP最大并发数</span>
              </el-form-item>
              <el-form-item label="流量限制">
                <el-input v-model="limitForm.limit_rate" placeholder="如 512" />
                <span class="form-tip">单连接限速 (KB/s)</span>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveLimitNet">保存</el-button>
                <el-button type="warning" @click="closeLimitNet">关闭限制</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 密码访问 -->
        <el-tab-pane label="密码访问" name="password">
          <div class="password-manage">
            <el-alert
              :title="pwdProtectEnabled ? '密码访问已开启' : '密码访问未开启'"
              :type="pwdProtectEnabled ? 'success' : 'info'"
              :closable="false"
              show-icon
              style="margin-bottom: 16px"
            />
            <el-form :model="pwdForm" label-width="100px" style="max-width: 500px">
              <el-form-item label="访问用户名">
                <el-input v-model="pwdForm.username" placeholder="输入用户名" />
              </el-form-item>
              <el-form-item label="访问密码">
                <el-input v-model="pwdForm.password" type="password" show-password placeholder="输入密码" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="enablePwdProtect">开启密码访问</el-button>
                <el-button type="warning" :disabled="!pwdProtectEnabled" @click="disablePwdProtect">关闭密码访问</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <el-tab-pane label="反向代理" name="proxy">
          <div class="proxy-manage">
            <div class="section-header">
              <span>反向代理列表</span>
              <el-button type="primary" size="small" @click="showAddProxy">添加代理</el-button>
            </div>
            <el-table :data="proxyList" v-loading="proxyLoading" stripe size="small">
              <el-table-column prop="name" label="名称" width="120" />
              <el-table-column prop="from" label="代理路径" width="150" />
              <el-table-column prop="to" label="目标地址" min-width="200" show-overflow-tooltip />
              <el-table-column prop="host" label="域名" width="150" />
              <el-table-column label="状态" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.open_proxy === '1' ? 'success' : 'info'" size="small">
                    {{ row.open_proxy === '1' ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="editProxy(row)">编辑</el-button>
                  <el-button type="warning" link size="small" @click="toggleProxyStatus(row)">
                    {{ row.open_proxy === '1' ? '禁用' : '启用' }}
                  </el-button>
                  <el-button type="danger" link size="small" @click="deleteProxy(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 添加/编辑代理对话框 -->
          <el-dialog v-model="proxyFormVisible" :title="proxyForm.id ? '编辑代理' : '添加代理'" width="550px" append-to-body>
            <el-form :model="proxyForm" label-width="100px">
              <el-form-item label="代理名称">
                <el-input v-model="proxyForm.name" placeholder="代理名称" />
              </el-form-item>
              <el-form-item label="代理路径">
                <el-input v-model="proxyForm.from" placeholder="例如: /api" />
              </el-form-item>
              <el-form-item label="目标地址">
                <el-input v-model="proxyForm.to" placeholder="例如: http://127.0.0.1:8080" />
              </el-form-item>
              <el-form-item label="域名">
                <el-input v-model="proxyForm.host" placeholder="发送到目标的域名（可选）" />
              </el-form-item>
              <el-form-item label="启用代理">
                <el-switch v-model="proxyForm.open_proxy" active-value="1" inactive-value="0" />
              </el-form-item>
              <el-form-item label="开启CORS">
                <el-switch v-model="proxyForm.open_cors" active-value="1" inactive-value="0" />
              </el-form-item>
              <el-form-item label="开启缓存">
                <el-switch v-model="proxyForm.open_cache" active-value="1" inactive-value="0" />
              </el-form-item>
              <el-form-item label="缓存时间" v-if="proxyForm.open_cache === '1'">
                <el-input v-model="proxyForm.cache_time" placeholder="秒" style="width: 120px" />
              </el-form-item>
            </el-form>
            <template #footer>
              <el-button @click="proxyFormVisible = false">取消</el-button>
              <el-button type="primary" @click="saveProxy" :loading="proxySaving">保存</el-button>
            </template>
          </el-dialog>
        </el-tab-pane>

        <el-tab-pane label="重定向" name="redirect">
          <div class="redirect-manage">
            <div class="section-header">
              <span>重定向列表</span>
              <el-button type="primary" size="small" @click="showAddRedirect">添加重定向</el-button>
            </div>
            <el-table :data="redirectList" v-loading="redirectLoading" stripe size="small">
              <el-table-column prop="from" label="来源路径" width="150" />
              <el-table-column prop="to" label="目标地址" min-width="200" show-overflow-tooltip />
              <el-table-column label="类型" width="100">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.type === 'path' ? '路径' : '域名' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="状态" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.status === '1' || row.status === 1 ? 'success' : 'info'" size="small">
                    {{ row.status === '1' || row.status === 1 ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="editRedirect(row)">编辑</el-button>
                  <el-button type="warning" link size="small" @click="toggleRedirectStatus(row)">
                    {{ row.status === '1' || row.status === 1 ? '禁用' : '启用' }}
                  </el-button>
                  <el-button type="danger" link size="small" @click="deleteRedirect(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 添加/编辑重定向对话框 -->
          <el-dialog v-model="redirectFormVisible" :title="redirectForm.id ? '编辑重定向' : '添加重定向'" width="550px" append-to-body>
            <el-form :model="redirectForm" label-width="100px">
              <el-form-item label="重定向类型">
                <el-radio-group v-model="redirectForm.type">
                  <el-radio value="path">路径</el-radio>
                  <el-radio value="domain">域名</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="来源路径">
                <el-input v-model="redirectForm.from" :placeholder="redirectForm.type === 'domain' ? '例如: old.example.com' : '例如: /old-path'" />
              </el-form-item>
              <el-form-item label="目标地址">
                <el-input v-model="redirectForm.to" placeholder="例如: https://new.example.com" />
              </el-form-item>
              <el-form-item label="HTTP状态码">
                <el-select v-model="redirectForm.r_type">
                  <el-option label="301 永久重定向" value="301" />
                  <el-option label="302 临时重定向" value="302" />
                </el-select>
              </el-form-item>
              <el-form-item label="保留路径">
                <el-switch v-model="redirectForm.keep_path" active-value="1" inactive-value="0" />
              </el-form-item>
            </el-form>
            <template #footer>
              <el-button @click="redirectFormVisible = false">取消</el-button>
              <el-button type="primary" @click="saveRedirectAction" :loading="redirectSaving">保存</el-button>
            </template>
          </el-dialog>
        </el-tab-pane>

        <!-- 防盗链 -->
        <el-tab-pane label="防盗链" name="security">
          <div class="security-manage">
            <el-form :model="securityForm" label-width="100px">
              <el-form-item label="防盗链状态">
                <el-switch v-model="securityForm.status" active-value="1" inactive-value="0" active-text="开启" inactive-text="关闭" />
              </el-form-item>
              <el-form-item label="允许域名">
                <el-input
                  v-model="securityForm.domains"
                  type="textarea"
                  :rows="4"
                  placeholder="每行一个域名，如:&#10;example.com&#10;www.example.com"
                />
                <div class="form-tip">每行填写一个允许的域名，不需要带http://</div>
              </el-form-item>
              <el-form-item label="资源类型">
                <el-input v-model="securityForm.fix" placeholder="如: jpg|jpeg|png|gif|bmp|zip|rar|mp4" style="width: 400px" />
                <div class="form-tip">用 | 分隔多个文件扩展名</div>
              </el-form-item>
              <el-form-item label="响应空值">
                <el-switch v-model="securityForm.none" active-value="1" inactive-value="0" active-text="开启" inactive-text="关闭" />
                <div class="form-tip">开启后未匹配的请求返回空内容</div>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveSecurity" :loading="securitySaving">保存</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>

    <!-- 站点分类管理对话框 -->
    <el-dialog v-model="siteTypesDialogVisible" title="站点分类管理" width="500px">
      <div class="site-types-header">
        <el-input v-model="newTypeName" placeholder="输入分类名称" style="width: 260px" @keyup.enter="handleAddType" />
        <el-button type="primary" @click="handleAddType" :loading="siteTypesLoading">添加分类</el-button>
      </div>
      <el-table :data="siteTypes" stripe style="margin-top: 16px" v-loading="siteTypesLoading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="分类名称" min-width="150">
          <template #default="{ row }">
            <el-input
              v-if="row._editing"
              v-model="row._editName"
              size="small"
              @keyup.enter="saveTypeName(row)"
              @blur="saveTypeName(row)"
            />
            <span v-else>{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="startEditType(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDeleteType(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  getSiteList,
  addSite,
  startSite,
  stopSite,
  deleteSite as apiDeleteSite,
  getSiteDomains,
  addSiteDomain,
  delSiteDomain,
  getSiteSsl,
  setSiteSsl,
  closeSiteSsl,
  httpToHttps,
  closeToHttps,
  getSiteBackup,
  createSiteBackup,
  delSiteBackup,
  getSiteLogs,
  getSiteErrorLogs,
  getSiteHostConf,
  saveSiteHostConf,
  setSitePath,
  setSiteRemark,
  setSiteEndDate,
  getSitePhpVersion,
  setSitePhpVersion,
  getSiteIndex,
  setSiteIndex,
  getSiteLimitNet,
  setSiteLimitNet,
  closeSiteLimitNet,
  setSiteHasPwd,
  closeSiteHasPwd,
  getSiteRewriteConf,
  saveSiteRewrite,
  getRewriteList,
  getRewriteTpl,
  getProxyList,
  setProxy,
  setProxyStatus as apiSetProxyStatus,
  delProxy,
  getRedirect,
  setRedirect,
  setRedirectStatus as apiSetRedirectStatus,
  delRedirect,
  getSiteTypes,
  addSiteType,
  removeSiteType,
  modifySiteTypeName,
  setSiteType as apiSetSiteType,
  getSiteSecurity,
  setSiteSecurity
} from '@/api/index';

const siteList = ref([]);
const loading = ref(false);
const searchQuery = ref('');
const statusFilter = ref('');
const typeFilter = ref('');
const siteTypes = ref([]);
const siteTypesLoading = ref(false);
const viewMode = ref('table');
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const selectedSites = ref([]);
const sortProp = ref('');
const sortOrder = ref('');
const addSiteVisible = ref(false);
const submitting = ref(false);
const addSiteFormRef = ref(null);

// 站点管理对话框
const siteManageVisible = ref(false);
const manageTab = ref('basic');
const currentSite = ref({});

// 基本设置
const siteBasicForm = ref({
  path: '',
  ps: '',
  edate: '',
  phpVersion: '',
  index: ''
});
const phpVersions = ref([]);

// 域名管理
const domainList = ref([]);
const newDomain = ref('');
const newDomainPort = ref('');
const batchDomains = ref('');
const domainLoading = ref(false);

// SSL
const sslInfo = ref(null);
const sslLoading = ref(false);
const sslActionLoading = ref(false);
const sslUploadKey = ref('');
const sslUploadCsr = ref('');

// 备份
const backupList = ref([]);
const backupLoading = ref(false);

// 日志
const logType = ref('access');
const logContent = ref('');
const logLoading = ref(false);

// 伪静态
const rewriteContent = ref('');
const rewriteLoading = ref(false);
const rewriteTplList = ref([]);
const rewriteTplLoading = ref(false);
const selectedRewriteTpl = ref('');

// 配置文件
const configContent = ref('');
const configLoading = ref(false);
const configPath = ref('');

// 流量限制
const limitForm = ref({ perserver: '', perip: '', limit_rate: '' });
const limitLoading = ref(false);

// 密码访问
const pwdForm = ref({ username: '', password: '' });
const pwdProtectEnabled = ref(false);

// 反向代理
const proxyList = ref([]);
const proxyLoading = ref(false);
const proxyFormVisible = ref(false);
const proxySaving = ref(false);
const proxyForm = ref({ id: '', name: '', from: '', to: '', host: '', open_proxy: '1', open_cors: '0', open_http3: '0', open_cache: '0', cache_time: '' });

// 重定向
const redirectList = ref([]);
const redirectLoading = ref(false);
const redirectFormVisible = ref(false);
const redirectSaving = ref(false);
const redirectForm = ref({ id: '', from: '', to: '', type: 'path', r_type: '301', keep_path: '0' });

// 防盗链相关
const securitySaving = ref(false);
const securityForm = ref({ status: '0', domains: '', fix: 'jpg|jpeg|png|gif|bmp|zip|rar|mp4', none: '0' });

const addSiteForm = ref({
  name: '',
  path: '',
  ps: '',
  php_version: '74'
});

const addSiteRules = {
  name: [
    { required: true, message: '请输入网站名称', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9\-\.]+$/, message: '网站名称格式不正确', trigger: 'blur' }
  ],
  path: [
    { required: true, message: '请输入根目录', trigger: 'blur' }
  ]
};

const stats = computed(() => {
  const total = siteList.value.length;
  const running = siteList.value.filter(s => s.status === 1).length;
  const stopped = total - running;
  const ssl = siteList.value.filter(s => s.ssl).length;
  return { total, running, stopped, ssl };
});

const filteredSiteList = computed(() => {
  let list = [...siteList.value];

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    list = list.filter(s =>
      s.name.toLowerCase().includes(query) ||
      (s.ps && s.ps.toLowerCase().includes(query))
    );
  }

  if (statusFilter.value !== '') {
    list = list.filter(s => s.status === statusFilter.value);
  }

  if (typeFilter.value !== '') {
    list = list.filter(s => String(s.type_id) === typeFilter.value);
  }

  return list;
});

const fetchSites = async () => {
  loading.value = true;
  try {
    const res = await getSiteList({
      page: currentPage.value,
      limit: pageSize.value,
      type_id: typeFilter.value,
      search: searchQuery.value,
      order: sortProp.value ? `${sortProp.value} ${sortOrder.value || 'desc'}` : ''
    });
    if (res && res.data) {
      siteList.value = res.data || [];
      total.value = res.data.length || 0;
    }
  } catch (error) {
    console.error('获取网站列表失败:', error);
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  currentPage.value = 1;
  fetchSites();
};

const handleFilter = () => {
  currentPage.value = 1;
  fetchSites();
};

const handleSortChange = ({ prop, order }) => {
  sortProp.value = prop;
  sortOrder.value = order === 'ascending' ? 'asc' : 'desc';
};

const handleSelectionChange = (selection) => {
  selectedSites.value = selection;
};

const handleSizeChange = (size) => {
  pageSize.value = size;
  fetchSites();
};

const handleCurrentChange = (page) => {
  currentPage.value = page;
  fetchSites();
};

const getTypeName = (typeId) => {
  const types = { 0: 'PHP', 1: 'Node.js', 2: 'Java' };
  return types[typeId] || '未知';
};

const getTypeTag = (typeId) => {
  const types = { 0: '', 1: 'success', 2: 'warning' };
  return types[typeId] || 'info';
};

const isExpired = (edate) => {
  if (edate === '0000-00-00') return false;
  return new Date(edate) < new Date();
};

const formatSize = (bytes) => {
  if (!bytes) return '-';
  const units = ['B', 'KB', 'MB', 'GB'];
  let idx = 0;
  let size = parseFloat(bytes);
  while (size >= 1024 && idx < units.length - 1) {
    size /= 1024;
    idx++;
  }
  return size.toFixed(1) + ' ' + units[idx];
};

// ==================== 添加站点 ====================

const showAddSite = () => {
  addSiteForm.value = { name: '', path: '', ps: '', php_version: '74' };
  addSiteVisible.value = true;
};

const submitAddSite = async () => {
  submitting.value = true;
  try {
    const res = await addSite(addSiteForm.value);
    if (res) {
      ElMessage.success('站点添加成功');
      addSiteVisible.value = false;
      fetchSites();
    }
  } catch (error) {
    console.error('添加站点失败:', error);
  } finally {
    submitting.value = false;
  }
};

// ==================== 站点状态切换 ====================

const toggleSite = async (site) => {
  const action = site.status === 1 ? '停止' : '启动';
  try {
    await ElMessageBox.confirm(`确定要${action} ${site.name} 吗？`, '确认');
    if (site.status === 1) {
      await stopSite(site.id);
    } else {
      await startSite(site.id);
    }
    ElMessage.success(`${action}成功`);
    fetchSites();
  } catch (error) {
    if (error !== 'cancel') ElMessage.error(`${action}失败`);
  }
};

// ==================== 站点管理对话框 ====================

const editSite = (site) => {
  currentSite.value = site;
  manageTab.value = 'basic';

  // 初始化基本设置表单
  siteBasicForm.value = {
    path: site.path || '',
    ps: site.ps || '',
    edate: site.edate === '0000-00-00' ? '' : site.edate,
    phpVersion: '',
    index: ''
  };

  siteManageVisible.value = true;

  // 加载PHP版本和默认文档
  fetchPhpVersion();
  fetchSiteIndex();
};

const handleCommand = (cmd, site) => {
  currentSite.value = site;
  siteBasicForm.value = {
    path: site.path || '',
    ps: site.ps || '',
    edate: site.edate === '0000-00-00' ? '' : site.edate,
    phpVersion: '',
    index: ''
  };
  siteManageVisible.value = true;

  switch (cmd) {
    case 'ssl':
      manageTab.value = 'ssl';
      fetchSslInfo();
      break;
    case 'domain':
      manageTab.value = 'domain';
      fetchDomains();
      break;
    case 'backup':
      manageTab.value = 'backup';
      fetchBackups();
      break;
    case 'log':
      manageTab.value = 'log';
      fetchSiteLogs();
      break;
    case 'config':
      manageTab.value = 'config';
      fetchSiteConfig();
      break;
    case 'proxy':
      manageTab.value = 'proxy';
      fetchProxyList();
      break;
    case 'redirect':
      manageTab.value = 'redirect';
      fetchRedirectList();
      break;
    case 'security':
      manageTab.value = 'security';
      fetchSecurity();
      break;
    case 'delete':
      siteManageVisible.value = false;
      deleteSiteAction(site);
      break;
  }
};

const handleManageTabChange = (tab) => {
  switch (tab) {
    case 'basic':
      fetchPhpVersion();
      fetchSiteIndex();
      break;
    case 'domain':
      fetchDomains();
      break;
    case 'ssl':
      fetchSslInfo();
      break;
    case 'backup':
      fetchBackups();
      break;
    case 'log':
      fetchSiteLogs();
      break;
    case 'rewrite':
      fetchRewriteConf();
      fetchRewriteTpls();
      break;
    case 'config':
      fetchSiteConfig();
      break;
    case 'limit':
      fetchLimitNet();
      break;
    case 'proxy':
      fetchProxyList();
      break;
    case 'redirect':
      fetchRedirectList();
      break;
    case 'security':
      fetchSecurity();
      break;
    case 'password':
      pwdProtectEnabled.value = false;
      pwdForm.value = { username: '', password: '' };
      break;
  }
};

// ==================== 防盗链设置 ====================

const fetchSecurity = async () => {
  try {
    const res = await getSiteSecurity(currentSite.value.id);
    if (res) {
      securityForm.value = {
        status: res.status ? '1' : '0',
        domains: res.domains || '',
        fix: res.fix || 'jpg|jpeg|png|gif|bmp|zip|rar|mp4',
        none: res.none ? '1' : '0'
      };
    }
  } catch {
    // use defaults
  }
};

const saveSecurity = async () => {
  securitySaving.value = true;
  try {
    await setSiteSecurity(
      currentSite.value.id,
      securityForm.value.fix,
      securityForm.value.domains,
      securityForm.value.status,
      securityForm.value.none
    );
    ElMessage.success('防盗链设置已保存');
  } catch {
    ElMessage.error('保存失败');
  } finally {
    securitySaving.value = false;
  }
};

// ==================== 基本设置 ====================

const fetchPhpVersion = async () => {
  try {
    const res = await getSitePhpVersion(currentSite.value.name);
    if (res) {
      siteBasicForm.value.phpVersion = res.phpversion || '';
      phpVersions.value = res.phpversions || [];
    }
  } catch (e) { /* ignore */ }
};

const fetchSiteIndex = async () => {
  try {
    const res = await getSiteIndex(currentSite.value.id);
    if (res && res.index) {
      siteBasicForm.value.index = Array.isArray(res.index) ? res.index.join('\n') : res.index;
    }
  } catch (e) { /* ignore */ }
};

const saveSitePath = async () => {
  try {
    await setSitePath(currentSite.value.id, siteBasicForm.value.path);
    ElMessage.success('站点路径已保存');
    fetchSites();
  } catch (e) {
    ElMessage.error('保存失败');
  }
};

const saveSiteRemark = async () => {
  try {
    await setSiteRemark(currentSite.value.id, siteBasicForm.value.ps);
    ElMessage.success('备注已保存');
    fetchSites();
  } catch (e) {
    ElMessage.error('保存失败');
  }
};

const saveSiteEndDate = async () => {
  try {
    await setSiteEndDate(currentSite.value.id, siteBasicForm.value.edate || '0000-00-00');
    ElMessage.success('到期时间已保存');
    fetchSites();
  } catch (e) {
    ElMessage.error('保存失败');
  }
};

const saveSitePhpVersion = async () => {
  try {
    await setSitePhpVersion(currentSite.value.name, siteBasicForm.value.phpVersion);
    ElMessage.success('PHP版本已切换');
  } catch (e) {
    ElMessage.error('切换失败');
  }
};

const saveSiteIndex = async () => {
  try {
    await setSiteIndex(currentSite.value.id, siteBasicForm.value.index);
    ElMessage.success('默认文档已保存');
  } catch (e) {
    ElMessage.error('保存失败');
  }
};

// ==================== 域名管理 ====================

const fetchDomains = async () => {
  domainLoading.value = true;
  try {
    const res = await getSiteDomains(currentSite.value.id);
    if (res && res.data) {
      domainList.value = Array.isArray(res.data) ? res.data : [];
    }
  } catch (e) {
    domainList.value = [];
  } finally {
    domainLoading.value = false;
  }
};

const addDomain = async () => {
  if (!newDomain.value.trim()) {
    ElMessage.warning('请输入域名');
    return;
  }
  domainLoading.value = true;
  try {
    await addSiteDomain(currentSite.value.id, currentSite.value.name, newDomain.value.trim(), newDomainPort.value || '80');
    ElMessage.success('域名添加成功');
    newDomain.value = '';
    newDomainPort.value = '';
    fetchDomains();
  } catch (e) {
    ElMessage.error('添加失败');
  } finally {
    domainLoading.value = false;
  }
};

const batchAddDomains = async () => {
  if (!batchDomains.value.trim()) {
    ElMessage.warning('请输入域名');
    return;
  }
  const domains = batchDomains.value.split('\n').map(d => d.trim()).filter(d => d);
  if (domains.length === 0) {
    ElMessage.warning('请输入有效的域名');
    return;
  }

  domainLoading.value = true;
  let successCount = 0;
  let errorCount = 0;

  for (const domain of domains) {
    try {
      await addSiteDomain(currentSite.value.id, currentSite.value.name, domain, '80');
      successCount++;
    } catch {
      errorCount++;
    }
  }

  ElMessage.success(`批量添加完成: 成功 ${successCount} 个${errorCount > 0 ? `, 失败 ${errorCount} 个` : ''}`);
  batchDomains.value = '';
  fetchDomains();
  domainLoading.value = false;
};

const copyDomain = (domain) => {
  const text = domain.port === '80' || domain.port === 80 ? domain.name : `${domain.name}:${domain.port}`;
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板');
  }).catch(() => {
    ElMessage.error('复制失败');
  });
};

const removeDomain = async (domain) => {
  try {
    await ElMessageBox.confirm(`确定要删除域名 ${domain.name} 吗？`, '删除确认', { type: 'warning' });
    await delSiteDomain(currentSite.value.id, currentSite.value.name, domain.name, domain.port);
    ElMessage.success('域名已删除');
    fetchDomains();
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败');
  }
};

// ==================== SSL证书 ====================

const getSslExpiryType = (notAfter) => {
  if (!notAfter) return 'info';
  const expiry = new Date(notAfter);
  const now = new Date();
  const daysLeft = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24));
  if (daysLeft < 0) return 'error';
  if (daysLeft < 7) return 'error';
  if (daysLeft < 30) return 'warning';
  return 'success';
};

const getSslExpiryTitle = (notAfter) => {
  if (!notAfter) return '';
  const expiry = new Date(notAfter);
  const now = new Date();
  const daysLeft = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24));
  if (daysLeft < 0) return `证书已过期 ${Math.abs(daysLeft)} 天`;
  if (daysLeft === 0) return '证书今天到期';
  if (daysLeft < 7) return `证书将在 ${daysLeft} 天后过期，请尽快续期`;
  if (daysLeft < 30) return `证书将在 ${daysLeft} 天后过期`;
  return `证书有效期还有 ${daysLeft} 天`;
};

const fetchSslInfo = async () => {
  sslLoading.value = true;
  sslInfo.value = null;
  try {
    const res = await getSiteSsl(currentSite.value.name, '');
    if (res) {
      sslInfo.value = res;
    }
  } catch (e) {
    // 没有SSL证书
  } finally {
    sslLoading.value = false;
  }
};

const uploadSsl = async () => {
  if (!sslUploadKey.value || !sslUploadCsr.value) {
    ElMessage.warning('请填写KEY和PEM/CSR内容');
    return;
  }
  sslActionLoading.value = true;
  try {
    await setSiteSsl(currentSite.value.name, sslUploadKey.value, sslUploadCsr.value);
    ElMessage.success('证书保存成功');
    sslUploadKey.value = '';
    sslUploadCsr.value = '';
    fetchSslInfo();
  } catch (e) {
    ElMessage.error('证书保存失败');
  } finally {
    sslActionLoading.value = false;
  }
};

const forceHttps = async () => {
  sslActionLoading.value = true;
  try {
    await httpToHttps(currentSite.value.name);
    ElMessage.success('已强制HTTPS');
    fetchSslInfo();
  } catch (e) {
    ElMessage.error('操作失败');
  } finally {
    sslActionLoading.value = false;
  }
};

const closeHttps = async () => {
  sslActionLoading.value = true;
  try {
    await closeToHttps(currentSite.value.name);
    ElMessage.success('已关闭强制HTTPS');
    fetchSslInfo();
  } catch (e) {
    ElMessage.error('操作失败');
  } finally {
    sslActionLoading.value = false;
  }
};

const closeSsl = async () => {
  try {
    await ElMessageBox.confirm('确定要关闭SSL吗？', '确认', { type: 'warning' });
    sslActionLoading.value = true;
    await closeSiteSsl(currentSite.value.name);
    ElMessage.success('SSL已关闭');
    fetchSslInfo();
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败');
  } finally {
    sslActionLoading.value = false;
  }
};

// ==================== 备份管理 ====================

const fetchBackups = async () => {
  backupLoading.value = true;
  try {
    const res = await getSiteBackup(currentSite.value.id);
    if (res && res.data) {
      backupList.value = Array.isArray(res.data) ? res.data : [];
    }
  } catch (e) {
    backupList.value = [];
  } finally {
    backupLoading.value = false;
  }
};

const createBackup = async () => {
  backupLoading.value = true;
  try {
    await createSiteBackup(currentSite.value.id);
    ElMessage.success('备份创建成功');
    fetchBackups();
  } catch (e) {
    ElMessage.error('备份创建失败');
  } finally {
    backupLoading.value = false;
  }
};

const deleteBackup = async (backup) => {
  try {
    await ElMessageBox.confirm('确定要删除此备份吗？', '删除确认', { type: 'warning' });
    await delSiteBackup(backup.id);
    ElMessage.success('备份已删除');
    fetchBackups();
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败');
  }
};

// ==================== 日志查看 ====================

const fetchSiteLogs = async () => {
  logLoading.value = true;
  try {
    const fn = logType.value === 'access' ? getSiteLogs : getSiteErrorLogs;
    const res = await fn(currentSite.value.name);
    if (res) {
      logContent.value = typeof res === 'string' ? res : (res.data || res.msg || JSON.stringify(res));
    }
  } catch (e) {
    logContent.value = '获取日志失败';
  } finally {
    logLoading.value = false;
  }
};

// ==================== 伪静态 ====================

const fetchRewriteConf = async () => {
  rewriteLoading.value = true;
  try {
    const res = await getSiteRewriteConf(currentSite.value.name);
    if (res && res.rewrite) {
      rewriteContent.value = res.rewrite;
    }
  } catch (e) {
    rewriteContent.value = '';
  } finally {
    rewriteLoading.value = false;
  }
};

const saveRewrite = async () => {
  rewriteLoading.value = true;
  try {
    await saveSiteRewrite('', rewriteContent.value, '');
    ElMessage.success('伪静态规则已保存');
  } catch (e) {
    ElMessage.error('保存失败');
  } finally {
    rewriteLoading.value = false;
  }
};

const fetchRewriteTpls = async () => {
  rewriteTplLoading.value = true;
  try {
    const res = await getRewriteList();
    if (res && Array.isArray(res.data)) {
      rewriteTplList.value = res.data;
    }
  } catch {
    rewriteTplList.value = [];
  } finally {
    rewriteTplLoading.value = false;
  }
};

const loadRewriteTpl = async (name) => {
  if (!name) return;
  try {
    const res = await getRewriteTpl(name);
    if (res && res.data) {
      rewriteContent.value = res.data;
      ElMessage.success(`已加载 ${name} 模板`);
    }
  } catch {
    ElMessage.error('加载模板失败');
  }
};

// ==================== 配置文件 ====================

const fetchSiteConfig = async () => {
  configLoading.value = true;
  try {
    const res = await getSiteHostConf(currentSite.value.name);
    if (res) {
      configContent.value = res.host || '';
      configPath.value = res.path || '';
    }
  } catch (e) {
    configContent.value = '';
  } finally {
    configLoading.value = false;
  }
};

const saveConfig = async () => {
  configLoading.value = true;
  try {
    await saveSiteHostConf(configPath.value, configContent.value, '');
    ElMessage.success('配置文件已保存');
  } catch (e) {
    ElMessage.error('保存失败');
  } finally {
    configLoading.value = false;
  }
};

// ==================== 流量限制 ====================

const fetchLimitNet = async () => {
  limitLoading.value = true;
  try {
    const res = await getSiteLimitNet(currentSite.value.id);
    if (res) {
      limitForm.value = {
        perserver: res.perserver || '',
        perip: res.perip || '',
        limit_rate: res.limit_rate || ''
      };
    }
  } catch (e) {
    limitForm.value = { perserver: '', perip: '', limit_rate: '' };
  } finally {
    limitLoading.value = false;
  }
};

const saveLimitNet = async () => {
  limitLoading.value = true;
  try {
    await setSiteLimitNet(
      currentSite.value.id,
      limitForm.value.perserver,
      limitForm.value.perip,
      limitForm.value.limit_rate
    );
    ElMessage.success('流量限制已保存');
  } catch (e) {
    ElMessage.error('保存失败');
  } finally {
    limitLoading.value = false;
  }
};

const closeLimitNet = async () => {
  limitLoading.value = true;
  try {
    await closeSiteLimitNet(currentSite.value.id);
    ElMessage.success('流量限制已关闭');
    limitForm.value = { perserver: '', perip: '', limit_rate: '' };
  } catch (e) {
    ElMessage.error('操作失败');
  } finally {
    limitLoading.value = false;
  }
};

// ==================== 密码访问 ====================

const enablePwdProtect = async () => {
  if (!pwdForm.value.username || !pwdForm.value.password) {
    ElMessage.warning('请填写用户名和密码');
    return;
  }
  try {
    await setSiteHasPwd(currentSite.value.id, pwdForm.value.username, pwdForm.value.password);
    pwdProtectEnabled.value = true;
    ElMessage.success('密码访问已开启');
  } catch (e) {
    ElMessage.error('开启失败');
  }
};

const disablePwdProtect = async () => {
  try {
    await closeSiteHasPwd(currentSite.value.id);
    pwdProtectEnabled.value = false;
    pwdForm.value = { username: '', password: '' };
    ElMessage.success('密码访问已关闭');
  } catch (e) {
    ElMessage.error('关闭失败');
  }
};

// ==================== 反向代理 ====================

const fetchProxyList = async () => {
  proxyLoading.value = true;
  try {
    const res = await getProxyList(currentSite.value.name);
    proxyList.value = res.data || [];
  } catch {
    proxyList.value = [];
  } finally {
    proxyLoading.value = false;
  }
};

const showAddProxy = () => {
  proxyForm.value = { id: '', name: '', from: '/', to: 'http://127.0.0.1:8080', host: '', open_proxy: '1', open_cors: '0', open_http3: '0', open_cache: '0', cache_time: '' };
  proxyFormVisible.value = true;
};

const editProxy = (row) => {
  proxyForm.value = {
    id: row.id || '',
    name: row.name || '',
    from: row.from || '',
    to: row.to || '',
    host: row.host || '',
    open_proxy: row.open_proxy || '0',
    open_cors: row.open_cors || '0',
    open_http3: row.open_http3 || '0',
    open_cache: row.open_cache || '0',
    cache_time: row.cache_time || '',
  };
  proxyFormVisible.value = true;
};

const saveProxy = async () => {
  proxySaving.value = true;
  try {
    await setProxy({
      siteName: currentSite.value.name,
      from: proxyForm.value.from,
      to: proxyForm.value.to,
      host: proxyForm.value.host,
      name: proxyForm.value.name,
      open_proxy: proxyForm.value.open_proxy,
      open_cors: proxyForm.value.open_cors,
      open_http3: proxyForm.value.open_http3,
      open_cache: proxyForm.value.open_cache,
      cache_time: proxyForm.value.cache_time,
      id: proxyForm.value.id,
    });
    ElMessage.success(proxyForm.value.id ? '代理已更新' : '代理已添加');
    proxyFormVisible.value = false;
    fetchProxyList();
  } catch (e) {
    ElMessage.error('操作失败');
  } finally {
    proxySaving.value = false;
  }
};

const toggleProxyStatus = async (row) => {
  try {
    const newStatus = row.open_proxy === '1' ? '0' : '1';
    await apiSetProxyStatus(currentSite.value.name, row.id, newStatus);
    ElMessage.success('状态已更新');
    fetchProxyList();
  } catch {
    ElMessage.error('操作失败');
  }
};

const deleteProxy = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除此代理规则吗？', '确认删除', { type: 'warning' });
    await delProxy(currentSite.value.name, row.id);
    ElMessage.success('已删除');
    fetchProxyList();
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败');
  }
};

// ==================== 重定向 ====================

const fetchRedirectList = async () => {
  redirectLoading.value = true;
  try {
    const res = await getRedirect(currentSite.value.name);
    redirectList.value = res.data || [];
  } catch {
    redirectList.value = [];
  } finally {
    redirectLoading.value = false;
  }
};

const showAddRedirect = () => {
  redirectForm.value = { id: '', from: '', to: '', type: 'path', r_type: '301', keep_path: '0' };
  redirectFormVisible.value = true;
};

const editRedirect = (row) => {
  redirectForm.value = {
    id: row.id || '',
    from: row.from || '',
    to: row.to || '',
    type: row.type || 'path',
    r_type: row.r_type || '301',
    keep_path: row.keep_path || '0',
  };
  redirectFormVisible.value = true;
};

const saveRedirectAction = async () => {
  redirectSaving.value = true;
  try {
    await setRedirect({
      siteName: currentSite.value.name,
      from: redirectForm.value.from,
      to: redirectForm.value.to,
      type: redirectForm.value.type,
      r_type: redirectForm.value.r_type,
      keep_path: redirectForm.value.keep_path,
    });
    ElMessage.success(redirectForm.value.id ? '重定向已更新' : '重定向已添加');
    redirectFormVisible.value = false;
    fetchRedirectList();
  } catch (e) {
    ElMessage.error('操作失败');
  } finally {
    redirectSaving.value = false;
  }
};

const toggleRedirectStatus = async (row) => {
  try {
    const currentStatus = row.status === '1' || row.status === 1;
    const newStatus = currentStatus ? '0' : '1';
    await apiSetRedirectStatus(currentSite.value.name, row.id, newStatus);
    ElMessage.success('状态已更新');
    fetchRedirectList();
  } catch {
    ElMessage.error('操作失败');
  }
};

const deleteRedirect = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除此重定向规则吗？', '确认删除', { type: 'warning' });
    await delRedirect(currentSite.value.name, row.id);
    ElMessage.success('已删除');
    fetchRedirectList();
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败');
  }
};

// ==================== 删除站点 ====================

const deleteSiteAction = async (site) => {
  try {
    await ElMessageBox.confirm(`确定要删除 ${site.name} 吗？此操作不可恢复！`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确定删除',
      cancelButtonText: '取消'
    });
    await apiDeleteSite(site.id, site.path);
    ElMessage.success('删除成功');
    fetchSites();
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败');
  }
};

// ==================== 批量操作 ====================

const clearSelection = () => {
  selectedSites.value = [];
};

const batchStart = async () => {
  try {
    await ElMessageBox.confirm(`确定要启动选中的 ${selectedSites.value.length} 个站点吗？`, '批量启动');
    let successCount = 0;
    for (const site of selectedSites.value) {
      try {
        await startSite(site.id);
        successCount++;
      } catch (e) { /* skip failed */ }
    }
    ElMessage.success(`成功启动 ${successCount} 个站点`);
    clearSelection();
    fetchSites();
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('批量启动失败');
  }
};

const batchStop = async () => {
  try {
    await ElMessageBox.confirm(`确定要停止选中的 ${selectedSites.value.length} 个站点吗？`, '批量停止');
    let successCount = 0;
    for (const site of selectedSites.value) {
      try {
        await stopSite(site.id);
        successCount++;
      } catch (e) { /* skip failed */ }
    }
    ElMessage.success(`成功停止 ${successCount} 个站点`);
    clearSelection();
    fetchSites();
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('批量停止失败');
  }
};

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedSites.value.length} 个站点吗？此操作不可恢复！`,
      '批量删除',
      { type: 'warning' }
    );
    let successCount = 0;
    for (const site of selectedSites.value) {
      try {
        await apiDeleteSite(site.id, site.path);
        successCount++;
      } catch (e) { /* skip failed */ }
    }
    ElMessage.success(`成功删除 ${successCount} 个站点`);
    clearSelection();
    fetchSites();
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('批量删除失败');
  }
};

// ==================== 站点分类管理 ====================

const siteTypesDialogVisible = ref(false);
const newTypeName = ref('');

const showSiteTypesDialog = () => {
  newTypeName.value = '';
  siteTypesDialogVisible.value = true;
  fetchSiteTypes();
};

const handleAddType = async () => {
  const name = newTypeName.value.trim();
  if (!name) {
    ElMessage.warning('请输入分类名称');
    return;
  }
  siteTypesLoading.value = true;
  try {
    const res = await addSiteType(name);
    if (res && res.status === false) {
      ElMessage.error(res.msg || '添加失败');
      return;
    }
    ElMessage.success('分类添加成功');
    newTypeName.value = '';
    fetchSiteTypes();
  } catch {
    ElMessage.error('添加分类失败');
  } finally {
    siteTypesLoading.value = false;
  }
};

const startEditType = (row) => {
  row._editing = true;
  row._editName = row.name;
};

const saveTypeName = async (row) => {
  const name = (row._editName || '').trim();
  if (!name || name === row.name) {
    row._editing = false;
    return;
  }
  try {
    await modifySiteTypeName(row.id, name);
    row.name = name;
    row._editing = false;
    ElMessage.success('分类名称已更新');
  } catch {
    ElMessage.error('修改失败');
  }
};

const handleDeleteType = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除分类 "${row.name}" 吗？该分类下的站点将变为默认分类。`, '删除分类', { type: 'warning' });
    await removeSiteType(row.id);
    ElMessage.success('分类已删除');
    fetchSiteTypes();
  } catch {
    // cancelled
  }
};

const fetchSiteTypes = async () => {
  try {
    const res = await getSiteTypes();
    if (res && res.data) {
      siteTypes.value = Array.isArray(res.data) ? res.data : [];
    }
  } catch {
    siteTypes.value = [];
  }
};

onMounted(() => {
  fetchSites();
  fetchSiteTypes();
});
</script>

<style lang="scss" scoped>
.site-list {
  .filter-card {
    margin-bottom: 16px;

    .action-buttons {
      display: flex;
      justify-content: flex-end;
      gap: 8px;
      margin-top: 8px;

      @media (min-width: 768px) {
        margin-top: 0;
      }
    }
  }

  .stats-row {
    margin-bottom: 16px;

    .stat-card {
      text-align: center;
      margin-bottom: 8px;
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .site-name {
    display: flex;
    align-items: center;
    gap: 8px;

    .site-icon {
      color: #409eff;
    }
  }

  .site-card {
    margin-bottom: 16px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .site-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }

    .site-card-name {
      font-size: 16px;
      font-weight: 600;
      margin: 0 0 8px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .site-card-path {
      font-size: 12px;
      color: #909399;
      margin: 0 0 12px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .site-card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      color: #909399;
    }
  }

  .batch-actions {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 100;
    width: 90%;
    max-width: 600px;

    .batch-content {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;

      .batch-info {
        font-size: 14px;
        color: #606266;
      }
    }
  }

  .text-danger {
    color: #f56c6c;
  }

  .el-pagination {
    margin-top: 16px;
    justify-content: flex-end;
  }

  .site-manage-form {
    padding: 16px 0;
  }

  .ssl-manage {
    .ssl-actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
  }

  .form-tip {
    display: inline-block;
    margin-left: 8px;
    font-size: 12px;
    color: #909399;
  }

  .proxy-manage,
  .redirect-manage {
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      font-weight: 600;
    }
  }

  .rewrite-manage {
    .rewrite-toolbar {
      display: flex;
      gap: 12px;
      align-items: center;
      margin-bottom: 12px;
    }
  }

  .site-types-header {
    display: flex;
    gap: 12px;
    align-items: center;
  }
}
</style>
