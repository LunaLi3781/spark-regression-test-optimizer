# GitHub 发布与 Apache Spark 上游贡献

## 发布当前独立仓库

本项目使用 `main` 分支。独立项目仓库地址：
https://github.com/LunaLi3781/spark-regression-test-optimizer 。
以下命令适用于从源码包自行发布新的副本；已有远程仓库无需重复创建。
源码 ZIP 不包含 `.git`；解压后先运行 `git init -b main`。
在此目录运行（先将 OWNER 替换成你的 GitHub 用户或组织）：

```bash
python3 -m unittest discover -s tests -v
python3 -m scripts.evaluate_demo
# 检查本次将发布的文件
 git status --short
 git add .
 git diff --cached --stat
 git diff --cached
 git commit -m "Initial regression test selection MVP"
 gh auth login
 gh repo create OWNER/spark-regression-test-optimizer --public --source=. --remote=origin --push
```

也可以在 GitHub 网页新建空仓库（不要自动生成 README/LICENSE），然后：

```bash
git remote add origin https://github.com/OWNER/spark-regression-test-optimizer.git
git push -u origin main
```

1. 等待 Actions 基础 CI 成功；本地通过并不代表远程 CI 已通过。
2. Actions → CI → Run workflow 手动执行真实 Spark smoke job，下载结果并检查日志。
3. 仓库简介注明 independent research prototype；不要使用 Apache 官方项目标识。
4. 记录真实验证范围后打 `v0.1.0` 标签并建立 Release；不要把模拟结果写成节省比例。

## 通往 Spark 上游的具体路线

独立工具先留在本仓库。优先把实验中发现的真实、可复现问题做成小范围上游贡献，
不以将整个优化器合并进 Spark 为首个目标。

1. 从公开 Spark JIRA、已有 PR 和邮件列表查重，挑选一个 SQL/PySpark 回归问题。
2. 在受影响版本、对照版本和当前开发分支确认行为；整理最小公开数据与重现步骤。
3. 建立或补充对应 JIRA，说明预期、实际结果、环境与影响。性能问题附可重复 benchmark。
4. Fork `apache/spark`，针对当前开发分支建立小分支，增加原生回归测试，必要时修复。
5. 按目标分支文档构建并运行相关测试；例如 PySpark 模块可通过
   `python/run-tests --testnames pyspark.sql.tests.test_<module>` 执行，模块名需按实际修改填写。
6. 按当前上游 PR 模板填写问题、改动、测试证据与 JIRA 链接，回应 review。
   遵守上游原创性声明和 Apache 许可要求；本仓库 MIT 许可不替代上游规则。
7. 保留公开 issue、PR、review、合并 commit、复现实验链接，作为可核实贡献记录。

参考（发布/提交前复核最新要求）：
- [Spark contribution guide](https://spark.apache.org/contributing.html)
- [Spark PR contribution checklist](https://github.com/apache/spark/blob/master/CONTRIBUTING.md)
- [PySpark testing](https://spark.apache.org/docs/latest/api/python/development/testing.html)

首个两周里程碑：先发布并跑真实 smoke；再扩充公开测试与测量；最后完成一个公开缺陷的
最小重现。能否提出修复 PR 取决于实际发现，不预设优化收益或上游接受结果。
