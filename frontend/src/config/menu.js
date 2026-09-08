export const menuGroups = [
  {
    key: 'home',
    title: '首页',
    icon: 'HomeFilled',
    path: '/app/home',
  },
  {
    key: 'collection',
    title: '数据采集',
    icon: 'Download',
    children: [
      { path: '/app/crawl', title: '爬虫管理', icon: 'Download' },
      { path: '/app/raw-data', title: '原始数据', icon: 'Document' },
    ],
  },
  {
    key: 'analysis',
    title: '数据统计与分析',
    icon: 'DataAnalysis',
    children: [
      { path: '/app/clean-data', title: '数据清洗', icon: 'Filter' },
    ],
  },
  {
    key: 'visual',
    title: '数据可视化',
    icon: 'Monitor',
    children: [
      { path: '/app/visual/national', title: '全国情况', icon: 'MapLocation' },
      { path: '/app/visual/salary', title: '薪资情况', icon: 'Money' },
      { path: '/app/visual/enterprise', title: '企业情况', icon: 'OfficeBuilding' },
      { path: '/app/visual/welfare', title: '福利情况', icon: 'Present' },
      { path: '/app/visual/education', title: '学历情况', icon: 'Reading' },
      { path: '/app/visual/financing', title: '融资情况', icon: 'Coin' },
      { path: '/app/visual/job-type', title: '职位类型', icon: 'Briefcase' },
      { path: '/app/visual/skill-city', title: '技能交叉', icon: 'Grid' },
    ],
  },
  {
    key: 'predict',
    title: '薪资预测',
    icon: 'TrendCharts',
    children: [
      { path: '/app/predict', title: '薪资预测', icon: 'TrendCharts' },
    ],
  },
]

export function flattenMenuItems(groups = menuGroups) {
  const items = []
  for (const group of groups) {
    if (group.path) {
      items.push({ ...group, groupTitle: group.title })
    }
    if (group.children) {
      for (const child of group.children) {
        items.push({ ...child, groupTitle: group.title })
      }
    }
  }
  return items
}

export function findMenuByPath(path) {
  return flattenMenuItems().find(item => item.path === path)
}
