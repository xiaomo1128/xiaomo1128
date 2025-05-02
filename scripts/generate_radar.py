import os
import requests
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from math import pi
from github import Github

# 设置认证
github_token = os.environ.get("GITHUB_TOKEN")
username = os.environ.get("GITHUB_REPOSITORY", "").split("/")[0]  # 从仓库名获取用户名

# 如果无法从环境变量获取，可以手动设置
if not username:
    username = "xiaomo1128"  # 替换为你的用户名

# 初始化 GitHub API
g = Github(github_token)
user = g.get_user(username)

# 获取最近90天的活动数据
end_date = datetime.now()
start_date = end_date - timedelta(days=180)

# 初始化计数器
commits = 0
pull_requests = 0
issues = 0
code_review = 0
discussions = 0

# 获取提交数据
for repo in user.get_repos():
    try:
        # 获取提交
        for commit in repo.get_commits(author=username, since=start_date):
            commits += 1
            
        # 获取 PR
        for pr in repo.get_pulls(state='all'):
            if pr.user.login == username and start_date <= pr.created_at <= end_date:
                pull_requests += 1
                
        # 获取 Issue
        for issue in repo.get_issues(state='all'):
            if issue.user.login == username and start_date <= issue.created_at <= end_date:
                if not issue.pull_request:  # 确保这是一个 issue 而不是 PR
                    issues += 1
    except Exception as e:
        print(f"跳过仓库 {repo.name}: {e}")

# 获取评论和审阅 (近似值)
code_review = int(commits * 0.5)  # 假设审阅约为提交的50%
discussions = int((issues + pull_requests) * 0.3)  # 假设讨论约为issues和PR总数的30%

# 计算百分比
total = commits + pull_requests + issues + code_review + discussions
if total == 0:
    total = 1  # 避免除以零

commit_percent = round(commits / total * 100)
pr_percent = round(pull_requests / total * 100)
issue_percent = round(issues / total * 100)
review_percent = round(code_review / total * 100)
discussion_percent = round(discussions / total * 100)

# 调整百分比总和为100%
values = [commit_percent, pr_percent, issue_percent, review_percent, discussion_percent]
if sum(values) != 100:
    diff = 100 - sum(values)
    values[0] += diff  # 将差值添加到第一个值

# 绘制雷达图
categories = ['Commits', 'Pull Requests', 'Issues', 'Code Review', 'Discussions']
N = len(categories)

# 角度值
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]  # 闭合图形

# 值（确保与角度列表长度匹配）
values_normalized = [v/100 for v in values]
values_normalized += values_normalized[:1]  # 闭合图形

# 绘图
fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))

# 绘制背景圆环
for i in range(1, 5):
    radius = i * 0.25
    ax.plot(angles, [radius] * len(angles), color="#ebedf0", linewidth=0.5, linestyle='solid')

# 绘制轴线
ax.plot(angles, [1] * len(angles), color="#ebedf0", linewidth=0.5, linestyle='solid')
for angle in angles[:-1]:
    ax.plot([angle, angle], [0, 1], color="#ebedf0", linewidth=0.5, linestyle='solid')

# 填充雷达图
ax.fill(angles, values_normalized, color='#9be9a8', alpha=0.5)
ax.plot(angles, values_normalized, color='#40c463', linewidth=2, linestyle='solid')

# 添加数据点
for i, angle in enumerate(angles[:-1]):
    ax.scatter(angle, values_normalized[i], s=50, color='#40c463')

# 添加分类标签
for i, angle in enumerate(angles[:-1]):
    ha = 'center'
    if angle == 0:
        ha = 'center'
    elif 0 < angle < pi:
        ha = 'left'
    elif angle > pi:
        ha = 'right'
    
    ax.text(angle, 1.15, categories[i], ha=ha, va='center', fontsize=12)
    ax.text(angle, values_normalized[i] - 0.05, f"{values[i]}%", ha='center', va='center', fontsize=10, fontweight='bold')

# 移除轴标签和刻度
ax.set_yticklabels([])
ax.set_xticklabels([])
ax.set_yticks([])
ax.set_xticks([])

# 设置标题
plt.title('GitHub Activity Overview', pad=20, fontsize=14, fontweight='bold')

# 保存为SVG
plt.savefig('radar_chart.svg', format='svg', bbox_inches='tight', transparent=True)
print(f"已生成雷达图: radar_chart.svg")