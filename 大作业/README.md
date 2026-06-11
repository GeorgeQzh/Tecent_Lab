# 蓝鲸运维开发综合应用

本目录是大作业交付代码，将 L2、L3、L4 的能力集成在同一个蓝鲸 SaaS 应用中，使用一套前端和一套后端。

## 功能范围

- CMDB 主机资源管理：业务、集群、模块级联查询，主机列表筛选与详情展示。
- JOB 文件查询与备份：按主机、目录、后缀执行 JOB 方案，写入备份记录并提供 JOB 结果链接。
- BKVision 行为分析：Django 中间件采集接口访问行为，提供本地统计接口，并支持 BKVision iframe 仪表盘嵌入。

## 目录说明

- `backend/integrated-backend`：蓝鲸 Django 后端模块。
- `frontend/integrated-frontend`：Vue2 + MagicBox 前端模块。

## 关键环境变量

- `BK_BACKEND_API_PREFIX`：前端访问后端模块的 API 前缀。
- `JOB_BK_BIZ_ID`：JOB/CMDB 业务 ID，默认 `3`。
- `SEARCH_FILE_PLAN_ID`：文件查询 JOB 执行方案 ID。
- `BACKUP_FILE_PLAN_ID`：文件备份 JOB 执行方案 ID。
- `BK_VISION_DASHBOARD_URL`：BKVision 发布后的 iframe 嵌入地址。
