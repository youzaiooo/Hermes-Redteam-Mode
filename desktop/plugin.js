import {
  Badge,
  Button,
  captureGatewayFileDownload,
  cn,
  Codicon,
  EmptyState,
  host,
  ScrollArea,
  Separator,
  Skeleton,
  StatusDot,
  Tabs,
  TabsList,
  TabsTrigger,
  useQuery,
  useQueryClient,
  useValue
} from '@hermes/plugin-sdk'
import { useState } from 'react'
import { jsx, jsxs } from 'react/jsx-runtime'

const ID = 'hermes-redteam'
const POLL_MS = 4000

const TABS = [
  ['situation', '态势'],
  ['assets', '资产'],
  ['results', '成果'],
  ['report', '报告'],
  ['resources', '资源']
]

const STAGES = [
  ['recon', '侦察'],
  ['asset', '资产'],
  ['vuln', '漏洞'],
  ['exploit', '利用'],
  ['internal', '内网']
]

const FALLBACK_ROLES = ['rt-recon', 'rt-asset', 'rt-vuln', 'rt-exploit', 'rt-internal']

function useRest(rest, key, path, enabled = true) {
  return useQuery({
    queryKey: ['hermes-redteam', ...key],
    queryFn: () => rest(path),
    enabled: Boolean(path) && enabled,
    refetchInterval: POLL_MS
  })
}

function loadingRows(count) {
  return Array.from({ length: count }, (_, index) =>
    jsx(Skeleton, { className: 'h-8 w-full' }, index)
  )
}

function errorLine() {
  return jsx('div', { className: 'py-2 text-xs text-(--ui-text-tertiary)', children: '加载失败' })
}

function stageProgress(summaryData) {
  const current = STAGES.findIndex(([id]) => id === (summaryData && summaryData.stage))

  return STAGES.map(([id, label], index) =>
    jsxs('div', {
      className: cn(
        'flex items-center gap-2 text-xs',
        index <= current ? 'text-(--ui-text-primary)' : 'text-(--ui-text-tertiary)'
      ),
      children: [
        jsx(StatusDot, { tone: index <= current ? 'good' : 'muted' }),
        jsx('span', { children: label })
      ]
    }, id)
  )
}

function resultSection(title, count, nodes) {
  return jsxs('div', {
    className: 'flex flex-col gap-1.5',
    children: [
      jsxs('div', {
        className: 'flex items-center justify-between',
        children: [
          jsx('span', { className: 'text-xs font-medium text-(--ui-text-primary)', children: title }),
          jsx(Badge, { variant: 'muted', children: String(count) })
        ]
      }),
      nodes.length
        ? nodes
        : jsx('div', { className: 'text-xs text-(--ui-text-quaternary)', children: '暂无' })
    ]
  })
}

function metricChip(label, value) {
  return jsxs('div', {
    className: 'rounded border border-(--ui-stroke-secondary) px-2 py-1.5',
    children: [
      jsx('div', { className: 'text-[0.6875rem] text-(--ui-text-tertiary)', children: label }),
      jsx('div', {
        className: 'text-sm font-semibold tabular-nums text-(--ui-text-primary)',
        children: String(value ?? 0)
      })
    ]
  })
}

function scoreHitsSection(summaryData) {
  const hits = summaryData && Array.isArray(summaryData.score_hits) ? summaryData.score_hits : []
  if (!hits.length) return null

  return jsxs('div', {
    className: 'flex flex-col gap-1.5',
    children: [
      jsx('div', { className: 'text-xs text-(--ui-text-tertiary)', children: '得分点' }),
      jsx('div', {
        className: 'flex flex-wrap gap-1',
        children: hits.map((hit) => jsx(Badge, { variant: 'muted', children: hit }, hit))
      })
    ]
  })
}

function situationChildren({ engagement, summaryData, loading, error, roleNames }) {
  if (!engagement) {
    return [jsx(EmptyState, { title: '还没有靶标', description: '先在会话里打开一个演练靶标' })]
  }
  if (loading) return loadingRows(3)
  if (error) return [errorLine()]

  return [
    jsxs('div', {
      className: 'flex items-center justify-between rounded border border-(--ui-stroke-secondary) px-3 py-2.5',
      children: [
        jsx('span', { className: 'text-xs text-(--ui-text-tertiary)', children: '当前得分' }),
        jsx('span', {
          className: 'text-xl font-semibold tabular-nums text-(--ui-text-primary)',
          children: String(summaryData ? summaryData.score : 0)
        })
      ]
    }),
    jsxs('div', {
      className: 'grid grid-cols-3 gap-1.5',
      children: [
        metricChip('资产', summaryData && summaryData.assets),
        metricChip('服务', summaryData && summaryData.services),
        metricChip('漏洞', summaryData && summaryData.vulns),
        metricChip('凭据', summaryData && summaryData.credentials),
        metricChip('隧道', summaryData && summaryData.tunnels)
      ]
    }),
    jsxs('div', {
      className: 'flex flex-col gap-1.5',
      children: [
        jsx('div', { className: 'text-xs text-(--ui-text-tertiary)', children: '阶段进度' }),
        ...stageProgress(summaryData)
      ]
    }),
    scoreHitsSection(summaryData),
    jsxs('div', {
      className: 'flex flex-col gap-1.5',
      children: [
        jsx('div', { className: 'text-xs text-(--ui-text-tertiary)', children: '工人角色' }),
        jsx('div', {
          className: 'flex flex-wrap gap-1',
          children: roleNames.map((role) => jsx(Badge, { variant: 'outline', children: role }, role))
        })
      ]
    })
  ].filter(Boolean)
}

function assetsChildren({ engagement, assetRows, loading, error }) {
  if (!engagement) return [jsx(EmptyState, { title: '还没有靶标' })]
  if (loading) return loadingRows(4)
  if (error) return [errorLine()]
  if (!assetRows.length) {
    return [jsx(EmptyState, { title: '还没有资产', description: '侦察角色落库后这里会显示地址' })]
  }

  return [
    jsx('div', { className: 'text-xs text-(--ui-text-tertiary)', children: `资产 ${assetRows.length}` }),
    ...assetRows.slice(0, 100).map((asset) =>
      jsxs('div', {
        className: 'rounded border border-(--ui-stroke-secondary) px-2 py-1.5',
        children: [
          jsxs('div', {
            className: 'flex items-center justify-between gap-2',
            children: [
              jsx('span', {
                className: 'truncate text-xs text-(--ui-text-primary)',
                children: asset.address || asset.stable_key
              }),
              jsx(Badge, { variant: 'outline', children: asset.status || 'new' })
            ]
          }),
          jsxs('div', {
            className: 'mt-1 flex flex-wrap gap-x-3 gap-y-0.5 text-[0.6875rem] text-(--ui-text-tertiary)',
            children: [
              jsx('span', { children: `端口 ${asset.port || 0}` }),
              jsx('span', { children: `服务 ${asset.service || '-'}` }),
              jsx('span', { children: `标题 ${asset.title || '-'}` })
            ]
          })
        ]
      }, asset.stable_key || asset.address)
    )
  ]
}

function resultsChildren({ engagement, vulnRows, credRows, tunnelRows, loading, error }) {
  if (!engagement) return [jsx(EmptyState, { title: '还没有靶标' })]
  if (loading) return loadingRows(4)
  if (error) return [errorLine()]
  if (!vulnRows.length && !credRows.length && !tunnelRows.length) {
    return [jsx(EmptyState, { title: '还没有成果', description: '漏洞、凭据指针与隧道会汇总在这里' })]
  }

  const vulnNodes = vulnRows.map((vuln) =>
    jsxs('div', {
      className: 'rounded border border-(--ui-stroke-secondary) px-2 py-1.5',
      children: [
        jsxs('div', {
          className: 'flex items-center justify-between gap-2',
          children: [
            jsx('div', {
              className: 'truncate text-xs text-(--ui-text-primary)',
              children: vuln.title || vuln.asset_key
            }),
            jsx(Badge, { variant: 'outline', children: vuln.status || '-' })
          ]
        }),
        jsxs('div', {
          className: 'mt-1 flex flex-wrap gap-x-3 gap-y-0.5 text-[0.6875rem] text-(--ui-text-tertiary)',
          children: [
            jsx('span', { children: `等级 ${vuln.severity || '-'}` }),
            jsx('span', { children: `资产 ${vuln.asset_key || '-'}` })
          ]
        })
      ]
    }, vuln.asset_key)
  )

  const credNodes = credRows.map((cred) =>
    jsxs('div', {
      className: 'rounded border border-(--ui-stroke-secondary) px-2 py-1.5',
      children: [
        jsx('div', { className: 'truncate text-xs text-(--ui-text-primary)', children: cred.asset_key }),
        jsx('div', { className: 'truncate text-xs text-(--ui-text-tertiary)', children: cred.evidence_path || '' })
      ]
    }, cred.asset_key)
  )

  const tunnelNodes = tunnelRows.map((tunnel) =>
    jsxs('div', {
      className: 'rounded border border-(--ui-stroke-secondary) px-2 py-1.5',
      children: [
        jsx('div', { className: 'truncate text-xs text-(--ui-text-primary)', children: tunnel.asset_key }),
        jsx('div', {
          className: 'truncate text-xs text-(--ui-text-tertiary)',
          children: `${tunnel.entry_kind || ''} · ${tunnel.evidence_path || ''}`
        })
      ]
    }, tunnel.asset_key)
  )

  return [
    resultSection('漏洞', vulnRows.length, vulnNodes),
    resultSection('凭据', credRows.length, credNodes),
    resultSection('隧道', tunnelRows.length, tunnelNodes)
  ]
}

function reportChildren({ engagement, reportPath, loading, error, exportReport }) {
  if (!engagement) return [jsx(EmptyState, { title: '还没有靶标' })]
  if (loading) return loadingRows(2)
  if (error) return [errorLine()]

  return [
    jsxs('div', {
      className: 'flex flex-col gap-1.5',
      children: [
        jsx('div', { className: 'text-xs text-(--ui-text-tertiary)', children: '报告索引' }),
        jsxs('div', {
          className: 'flex items-center gap-2 rounded border border-(--ui-stroke-secondary) px-2 py-1.5',
          children: [
            jsx('span', {
              className: 'min-w-0 flex-1 truncate text-xs text-(--ui-text-primary)',
              children: reportPath || '还没有报告'
            }),
            jsx(Button, {
              variant: 'secondary',
              size: 'sm',
              disabled: !reportPath,
              onClick: exportReport,
              children: '导出'
            })
          ]
        })
      ]
    }),
    jsx('div', { className: 'text-xs text-(--ui-text-quaternary)', children: '报告与得分报告由报告索引页汇总' })
  ]
}

function resourcesChildren({ skillNames, roleNames, loading, error }) {
  if (loading) return loadingRows(2)
  if (error) return [errorLine()]

  return [
    jsxs('div', {
      className: 'flex flex-col gap-1.5',
      children: [
        jsx('div', { className: 'text-xs font-medium text-(--ui-text-primary)', children: '技能可用性' }),
        jsx('div', {
          className: 'flex flex-wrap gap-1',
          children: skillNames.length
            ? skillNames.map((name) => jsx(Badge, { variant: 'outline', children: name }, name))
            : jsx('div', { className: 'text-xs text-(--ui-text-quaternary)', children: '暂无技能' })
        })
      ]
    }),
    jsx(Separator, {}),
    jsxs('div', {
      className: 'flex flex-col gap-1.5',
      children: [
        jsx('div', { className: 'text-xs font-medium text-(--ui-text-primary)', children: '角色' }),
        jsx('div', {
          className: 'flex flex-wrap gap-1',
          children: roleNames.map((role) => jsx(Badge, { variant: 'muted', children: role }, role))
        })
      ]
    })
  ]
}

function tabChildren(state) {
  switch (state.tab) {
    case 'assets':
      return assetsChildren({ ...state, loading: state.assets.isLoading, error: state.assets.isError })
    case 'results':
      return resultsChildren({
        ...state,
        loading: state.findings.isLoading || state.credentials.isLoading || state.tunnels.isLoading,
        error: state.findings.isError || state.credentials.isError || state.tunnels.isError
      })
    case 'report':
      return reportChildren({ ...state, loading: state.report.isLoading, error: state.report.isError })
    case 'resources':
      return resourcesChildren({
        ...state,
        loading: state.skills.isLoading || state.roles.isLoading,
        error: state.skills.isError || state.roles.isError
      })
    case 'situation':
    default:
      return situationChildren({ ...state, loading: state.summary.isLoading, error: state.summary.isError })
  }
}

function header({ engagement, refresh }) {
  return jsxs('div', {
    className: 'flex items-center justify-between gap-2 border-b border-(--ui-stroke-secondary) px-3 py-2',
    children: [
      jsxs('div', {
        className: 'flex items-center gap-2',
        children: [
          jsx('span', {
            className: 'text-[0.8125rem] font-semibold text-(--ui-text-primary)',
            children: 'RedTeam 控制台'
          }),
          jsx(StatusDot, { tone: engagement ? 'good' : 'muted' })
        ]
      }),
      jsx('span', {
        className: 'min-w-0 flex-1 truncate text-right text-xs text-(--ui-text-tertiary)',
        children: engagement ? engagement.display_name : '未绑定靶标'
      }),
      jsx(Button, {
        variant: 'ghost',
        size: 'icon-xs',
        onClick: refresh,
        children: jsx(Codicon, { name: 'refresh', size: 14 })
      })
    ]
  })
}

function tabsBar(tab, setTab) {
  return jsx(Tabs, {
    value: tab,
    onValueChange: setTab,
    className: 'px-3 pt-2',
    children: jsx(TabsList, {
      className: 'w-full',
      children: TABS.map(([id, label]) =>
        jsx(TabsTrigger, { value: id, className: 'flex-1 px-1', children: label }, id)
      )
    })
  })
}

function footer(unboundHint) {
  return jsx('div', {
    className: 'border-t border-(--ui-stroke-secondary) px-3 py-1.5 text-[0.6875rem] text-(--ui-text-quaternary)',
    children: unboundHint
      ? '本会话未绑靶标，显示最近一次演练'
      : '只读索引。不显示命令、凭据或 payload。'
  })
}

function Pane({ rest }) {
  const [tab, setTab] = useState('situation')
  const activeSessionId = useValue(host.state.activeSessionId)
  const queryClient = useQueryClient()

  const forSession = useRest(
    rest,
    ['for-session', activeSessionId],
    activeSessionId ? `/engagements/for-session/${activeSessionId}` : null
  )
  const engagementsQuery = useRest(rest, ['engagements'], '/engagements')

  const bound = forSession.data && forSession.data.ok !== false ? forSession.data.engagement : null
  const listed = engagementsQuery.data && Array.isArray(engagementsQuery.data.engagements)
    ? engagementsQuery.data.engagements
    : []
  const engagement = bound || listed[0] || null
  const engagementId = engagement ? engagement.id : null
  const unboundHint = Boolean(engagement) && !bound

  const summary = useRest(rest, ['summary', engagementId], engagementId ? `/summary/${engagementId}` : null)
  const assets = useRest(rest, ['assets', engagementId], engagementId ? `/assets/${engagementId}` : null)
  const findings = useRest(rest, ['findings', engagementId], engagementId ? `/findings/${engagementId}` : null)
  const credentials = useRest(rest, ['credentials', engagementId], engagementId ? `/credentials/${engagementId}` : null)
  const tunnels = useRest(rest, ['tunnels', engagementId], engagementId ? `/tunnels/${engagementId}` : null)
  const report = useRest(rest, ['report', engagementId], engagementId ? `/report/${engagementId}` : null)
  const skills = useRest(rest, ['skills'], '/skills')
  const roles = useRest(rest, ['roles'], '/roles')

  const summaryData = summary.data && summary.data.ok !== false ? summary.data.summary : null
  const assetRows = assets.data && Array.isArray(assets.data.assets) ? assets.data.assets : []
  const vulnRows = findings.data && Array.isArray(findings.data.vulns) ? findings.data.vulns : []
  const credRows = credentials.data && Array.isArray(credentials.data.credentials) ? credentials.data.credentials : []
  const tunnelRows = tunnels.data && Array.isArray(tunnels.data.tunnels) ? tunnels.data.tunnels : []
  const reportPath = report.data && report.data.path ? report.data.path : ''
  const skillNames = skills.data && Array.isArray(skills.data.skills) ? skills.data.skills : []
  const roleNames = roles.data && Array.isArray(roles.data.roles) ? roles.data.roles : FALLBACK_ROLES

  const refresh = () => queryClient.invalidateQueries({ queryKey: ['hermes-redteam'] })
  const exportReport = () => {
    if (!engagementId) return
    const download = captureGatewayFileDownload()
    rest(`/report/${engagementId}`)
      .then((found) => {
        if (found && found.path) download(found.path, 'report-index.md')
      })
      .catch(() => {})
  }

  const state = {
    tab,
    engagement,
    unboundHint,
    summaryData,
    assetRows,
    vulnRows,
    credRows,
    tunnelRows,
    reportPath,
    skillNames,
    roleNames,
    summary,
    assets,
    findings,
    credentials,
    tunnels,
    report,
    skills,
    roles,
    exportReport
  }

  return jsxs('div', {
    className: 'flex h-full flex-col text-sm text-(--ui-text-secondary)',
    children: [
      header({ engagement, refresh }),
      tabsBar(tab, setTab),
      jsx(ScrollArea, {
        className: 'min-h-0 flex-1',
        children: jsx('div', {
          className: 'flex flex-col gap-3 px-3 py-3',
          children: tabChildren(state)
        })
      }),
      footer(unboundHint)
    ]
  })
}

export default {
  id: ID,
  name: 'RedTeam 控制台',
  defaultEnabled: true,
  register(ctx) {
    ctx.register({
      id: 'pane',
      area: 'panes',
      title: 'RedTeam 控制台',
      data: { placement: 'right', width: '340px' },
      render: () => jsx(Pane, { rest: ctx.rest })
    })
  }
}
