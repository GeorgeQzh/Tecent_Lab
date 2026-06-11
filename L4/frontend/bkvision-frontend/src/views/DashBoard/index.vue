<template>
  <div class="dashboard-wrapper">
    <bk-alert type="info" title="BKVision 仪表盘发布后，可通过环境变量 BK_VISION_DASHBOARD_URL 替换下方嵌入地址。" />
    <iframe
      class="dashboard-frame"
      :src="iframeUrl"
      frameborder="0">
    </iframe>
    <div class="summary-grid">
      <bk-card title="请求总量">
        <div class="metric">{{ summary.total }}</div>
      </bk-card>
      <bk-card title="访问用户数">
        <div class="metric">{{ summary.by_user.length }}</div>
      </bk-card>
      <bk-card title="接口数量">
        <div class="metric">{{ summary.by_path.length }}</div>
      </bk-card>
    </div>
    <bk-table :data="summary.by_path" style="margin-top: 16px;">
      <bk-table-column label="接口路径" prop="path" />
      <bk-table-column label="访问次数" prop="count" width="120" />
      <bk-table-column label="平均耗时(ms)" prop="avg_cost" width="140">
        <template slot-scope="{ row }">{{ Number(row.avg_cost || 0).toFixed(0) }}</template>
      </bk-table-column>
    </bk-table>
    <bk-table :data="summary.by_user" style="margin-top: 16px;">
      <bk-table-column label="用户" prop="username" />
      <bk-table-column label="访问次数" prop="count" width="120" />
      <bk-table-column label="平均耗时(ms)" prop="avg_cost" width="140">
        <template slot-scope="{ row }">{{ Number(row.avg_cost || 0).toFixed(0) }}</template>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      iframeUrl: 'https://apps.ce.bktencent.com/bk-vision/embed/',
      summary: {
        total: 0,
        by_path: [],
        by_user: [],
        trend: [],
      },
    };
  },
  created() {
    this.fetchPageData();
  },
  methods: {
    async fetchPageData() {
      const [configRes, summaryRes] = await Promise.all([
        this.$store.dispatch('example/getDashboardConfig', {}, { fromCache: false }),
        this.$store.dispatch('example/getBehaviorSummary', {}, { fromCache: false }),
      ]);
      this.iframeUrl = configRes.data.iframe_url || this.iframeUrl;
      this.summary = summaryRes.data;
    },
  },
};
</script>

<style scoped>
.dashboard-wrapper {
  min-height: 720px;
}

.dashboard-frame {
  width: 100%;
  height: 520px;
  margin-top: 16px;
  border: 1px solid #dcdee5;
  border-radius: 2px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.metric {
  font-size: 32px;
  color: #313238;
  line-height: 48px;
}
</style>
