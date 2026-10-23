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
import { useEffect, useState } from 'react'
import { jsx, jsxs } from 'react/jsx-runtime'

const ID = 'hermes-redteam'
const POLL_MS = 4000
// Keep in sync with plugin.yaml `version`; tests/test_version_sync.py guards it.
const DESKTOP_VERSION = '0.3.4'

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
        className: 'grid grid-cols-[minmax(0,1fr)_auto_auto] items-center gap-2 rounded border border-(--ui-stroke-secondary) px-2 py-1.5',
        children: [
          jsx('span', {
            className: 'truncate text-xs text-(--ui-text-primary)',
            children: asset.address || asset.stable_key
          }),
          jsx(Badge, { variant: 'outline', children: asset.status || 'new' }),
          jsx('span', {
            className: 'text-xs text-(--ui-text-tertiary)',
            children: (asset.first_seen || '').slice(0, 10)
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
        jsx('div', { className: 'truncate text-xs text-(--ui-text-primary)', children: vuln.asset_key }),
        jsx('div', {
          className: 'truncate text-xs text-(--ui-text-tertiary)',
          children: `${vuln.status || ''} · ${vuln.evidence_path || ''}`
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

function unboundChildren(listed, onPick, onNew) {
  return [
    jsxs('div', {
      className: 'flex flex-col gap-2 py-2',
      children: [
        jsx('div', { className: 'text-sm font-medium text-(--ui-text-primary)', children: '未绑定靶标' }),
        jsx('div', {
          className: 'text-xs text-(--ui-text-tertiary)',
          children: '新会话不会继承上一次演练。点下面按钮新建红队会话，输入目标即可；也可以直接说：红队模式：目标 <单位名>。'
        }),
        jsx(Button, {
          variant: 'primary',
          size: 'sm',
          className: 'justify-start',
          onClick: onNew,
          children: '+ 新建红队会话'
        })
      ]
    }),
    listed.length
      ? jsxs('div', {
          className: 'flex flex-col gap-1.5',
          children: [
            jsx('div', { className: 'text-xs font-medium text-(--ui-text-primary)', children: '手动查看最近演练' }),
            ...listed.slice(0, 5).map((item) =>
              jsx(Button, {
                variant: 'ghost',
                size: 'sm',
                className: 'justify-start',
                onClick: () => onPick(item.id),
                children: item.display_name || item.id
              }, item.id)
            )
          ]
        })
      : null
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

function header({ engagement, bound, refresh, onClear, onNew }) {
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
          jsx(StatusDot, { tone: bound ? 'good' : 'muted' })
        ]
      }),
      jsx('span', {
        className: 'min-w-0 flex-1 truncate text-right text-xs text-(--ui-text-tertiary)',
        children: engagement ? engagement.display_name : '未绑定靶标'
      }),
      engagement && !bound
        ? jsx(Button, {
            variant: 'ghost',
            size: 'icon-xs',
            title: '清除手动选择',
            onClick: onClear,
            children: jsx(Codicon, { name: 'close', size: 12 })
          })
        : null,
      jsx(Button, {
        variant: 'ghost',
        size: 'icon-xs',
        title: '新建红队会话',
        onClick: onNew,
        children: jsx(Codicon, { name: 'add', size: 14 })
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

function newSessionForm({ target, setTarget, onStart, onCancel }) {
  return jsxs('div', {
    className: 'flex flex-col gap-2 px-3 py-3',
    children: [
      jsx('div', { className: 'text-sm font-medium text-(--ui-text-primary)', children: '新建红队会话' }),
      jsx('div', {
        className: 'text-xs text-(--ui-text-tertiary)',
        children: '输入目标即可。给出目标即视为已授权，不再确认范围、不再二次确认。'
      }),
      jsx('input', {
        className: 'w-full rounded-md border border-(--ui-stroke-secondary) bg-(--ui-bg-primary) px-2 py-1.5 text-xs text-(--ui-text-primary) outline-none',
        placeholder: '目标 IP / 域名 / 单位名',
        value: target,
        onChange: (event) => setTarget(event.target.value)
      }),
      jsxs('div', {
        className: 'flex items-center gap-2',
        children: [
          jsx(Button, { variant: 'primary', size: 'sm', onClick: onStart, children: '开始' }),
          jsx(Button, { variant: 'ghost', size: 'sm', onClick: onCancel, children: '取消' })
        ]
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

function footer(mode, gatewayState) {
  const base = mode === 'bound'
    ? '只读索引。不显示命令、凭据或 payload。'
    : mode === 'manual'
      ? '手动查看历史演练（本会话未绑定）'
      : '未绑定靶标 · 新会话不继承上一次演练'
  const text = gatewayState && gatewayState !== 'open'
    ? `网关${gatewayState === 'connecting' ? '连接中' : '未连接'} · 显示上次数据`
    : base
  return jsx('div', {
    className: 'border-t border-(--ui-stroke-secondary) px-3 py-1.5 text-[0.6875rem] text-(--ui-text-quaternary)',
    children: text
  })
}

function Pane({ rest }) {
  const [tab, setTab] = useState('situation')
  const [manualId, setManualId] = useState('')
  const [showNew, setShowNew] = useState(false)
  const [newTarget, setNewTarget] = useState('')
  const runtimeSessionId = useValue(host.state.activeSessionId)
  const storedSessionId = useValue(host.state.focusedStoredSessionId)
  const activeSessionId = storedSessionId || runtimeSessionId
  const gatewayState = useValue(host.state.gateway)
  const queryClient = useQueryClient()
  const versionQuery = useRest(rest, ['plugin-version'], '/version')
  const gatewayVersion = versionQuery.data && versionQuery.data.version ? String(versionQuery.data.version) : ''
  const needsUpdate = Boolean(gatewayVersion && gatewayVersion !== DESKTOP_VERSION)

  // A new session must start clean: drop any manual selection when the active
  // session changes (including to null on a fresh, unbound session).
  useEffect(() => {
    setManualId('')
  }, [activeSessionId])

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
  const manual = manualId ? listed.find((item) => item.id === manualId) || null : null
  const engagement = bound || manual || null
  const engagementId = engagement ? engagement.id : null
  const footerMode = !engagement ? 'none' : bound ? 'bound' : 'manual'

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
      .catch((error) => host.notifyError(error, '报告导出失败'))
  }

  const updateDesktopUI = async () => {
    const bridge = window.hermesDesktop
    if (!bridge || typeof bridge.installDesktopPlugin !== 'function') {
      host.notify({ kind: 'warning', message: '请用 App 的 Install from Git 更新桌面插件' })
      return
    }
    try {
      const result = await bridge.installDesktopPlugin({
        repo: 'youzaiooo/Hermes-Redteam-Mode',
        force: true
      })
      if (result && result.ok) {
        host.notify({ kind: 'success', message: '桌面 UI 已更新；若面板未刷新，请按 Ctrl/⌘+K → Reload desktop plugins' })
      } else {
        host.notifyError(new Error(result && result.error ? result.error : 'install failed'), '桌面 UI 更新失败')
      }
    } catch (error) {
      host.notifyError(error, '桌面 UI 更新失败')
    }
  }

  const startRedteamSession = async () => {
    const target = newTarget.trim()
    if (!target) {
      host.notify({ kind: 'warning', message: '请先输入目标' })
      return
    }
    const prompt = `红队模式：目标 ${target}，已授权。不要询问范围或下一步，直接开始信息收集：先调用 redteam_preflight，再调用 redteam_engagement_open 建靶标并绑定当前会话，然后立即派 recon；recon 完成后读库并自动继续漏洞发现/利用，直到收口。`
    setShowNew(false)
    host.newChat('default')
    await new Promise((resolve) => setTimeout(resolve, 350))
    let sent = false
    try {
      if (host.composer && typeof host.composer.setDraft === 'function') {
        const drafted = await host.composer.setDraft('new', prompt)
        if (drafted && typeof host.composer.submit === 'function') {
          sent = host.composer.submit('new', prompt)
        }
        if (!sent) {
          const draftedActive = await host.composer.setDraft(null, prompt)
          if (draftedActive && typeof host.composer.submit === 'function') {
            sent = host.composer.submit(null, prompt)
          }
        }
      }
    } catch (error) {
      host.notifyError(error, '新建红队会话失败')
    }
    if (!sent) {
      host.notify({ kind: 'warning', message: '新会话已创建；请把目标补进输入框后发送' })
      if (host.composer && host.composer.focus) host.composer.focus(null)
    }
    setNewTarget('')
  }

  const state = {
    tab,
    engagement,
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
      header({ engagement, bound, refresh, onClear: () => setManualId(''), onNew: () => setShowNew((value) => !value) }),
      needsUpdate
        ? jsxs('div', {
            className: 'flex items-center gap-2 border-b border-(--ui-stroke-secondary) bg-(--ui-bg-quaternary) px-3 py-1.5 text-[0.6875rem] text-(--ui-text-secondary)',
            children: [
              jsx('span', {
                className: 'min-w-0 flex-1 truncate',
                children: `客户端 UI v${DESKTOP_VERSION} · 网关 v${gatewayVersion}`
              }),
              jsx(Button, {
                variant: 'secondary',
                size: 'xs',
                onClick: updateDesktopUI,
                children: '更新本地 UI'
              })
            ]
          })
        : null,
      showNew
        ? newSessionForm({
            target: newTarget,
            setTarget: setNewTarget,
            onStart: startRedteamSession,
            onCancel: () => setShowNew(false)
          })
        : [
            tabsBar(tab, setTab),
            jsx(ScrollArea, {
              className: 'min-h-0 flex-1',
              children: jsx('div', {
                className: 'flex flex-col gap-3 px-3 py-3',
                children: engagement ? tabChildren(state) : unboundChildren(listed, setManualId, () => setShowNew(true))
              })
            })
          ],
      footer(footerMode, gatewayState)
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
      data: {
        placement: 'right',
        dock: { pane: 'workspace', pos: 'right' },
        width: '340px'
      },
      render: () => jsx(Pane, { rest: ctx.rest })
    })
  }
}
