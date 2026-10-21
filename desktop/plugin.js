import { host, useValue } from '@hermes/plugin-sdk'
import { useEffect, useState } from 'react'
import { jsx, jsxs } from 'react/jsx-runtime'

const ID = 'hermes-redteam'
const TABS = [
  ['board', '总览'],
  ['assets', '资产'],
  ['findings', '漏洞'],
  ['sessions', '会话'],
  ['tunnels', '隧道'],
  ['score', '得分'],
  ['skills', '技能'],
  ['roles', '角色'],
  ['report', '报告']
]
const SCORE = [
  ['off', '关闭'],
  ['visible', '可见'],
  ['enforced', '强制']
]

function textOf(item) {
  if (item == null) return '暂无记录'
  if (typeof item === 'string' || typeof item === 'number') return String(item)
  return item.stable_key || item.asset_key || item.path || item.name || item.id || item.entry_kind || '暂无记录'
}

function linesFor(tab, data) {
  if (!data || data.ok === false) return ['暂无记录']
  if (tab === 'board') {
    return [
      `资产 ${data.asset_count ?? 0}`,
      `漏洞 ${data.finding_count ?? 0}`
    ]
  }
  if (tab === 'sessions') {
    return [`访问 ${data.access ?? 0}`, `凭据指针 ${data.credentials ?? 0}`]
  }
  if (tab === 'score') return [`当前 ${data.mode || 'off'}`]
  if (tab === 'report') return [data.path || '暂无记录']
  const list = data.assets || data.vulns || data.tunnels || data.skills || data.roles || []
  if (!Array.isArray(list) || list.length === 0) return ['暂无记录']
  return list.slice(0, 8).map(textOf)
}

function Pane({ rest }) {
  const profile = useValue(host.state.focusedSessionProfile)
  const [tab, setTab] = useState('board')
  const [ids, setIds] = useState([])
  const [engagement, setEngagement] = useState('')
  const [data, setData] = useState(null)
  const [mode, setMode] = useState('off')
  const [notice, setNotice] = useState('')

  useEffect(() => {
    let stop = false
    rest('/engagements/current').then((found) => {
      if (stop) return
      const next = Array.isArray(found && found.engagements) ? found.engagements : []
      setIds(next)
      setEngagement((current) => current || next[0] || '')
    }).catch(() => {
      if (!stop) setNotice('加载失败')
    })
    rest('/score-rules').then((found) => {
      if (!stop && found && found.mode) setMode(found.mode)
    }).catch(() => {
      if (!stop) setNotice('加载失败')
    })
    return () => { stop = true }
  }, [rest])

  useEffect(() => {
    if (!engagement && tab !== 'skills' && tab !== 'roles' && tab !== 'score') {
      setData(null)
      return undefined
    }
    let stop = false
    const path = tab === 'skills' || tab === 'roles' || tab === 'score'
      ? (tab === 'score' ? '/score-rules' : `/${tab}`)
      : `/${tab}/${engagement}`
    const tick = () => {
      rest(path).then((next) => {
        if (!stop) setData(next)
      }).catch(() => {
        if (!stop) setNotice('加载失败')
      })
    }
    tick()
    const timer = setInterval(tick, 5000)
    return () => {
      stop = true
      clearInterval(timer)
    }
  }, [engagement, rest, tab])

  return jsxs('div', {
    className: 'flex h-full flex-col gap-3 p-3 text-sm text-(--ui-text-secondary)',
    children: [
      jsxs('div', {
        className: 'flex items-center justify-between gap-2',
        children: [
          jsx('div', { className: 'text-base text-(--ui-text)', children: '红队面板' }),
          jsx('div', { children: profile || 'Sekhmet' })
        ]
      }),
      jsx('select', {
        value: engagement,
        onChange: (event) => setEngagement(event.target.value),
        children: ids.length
          ? ids.map((id) => jsx('option', { value: id, children: id }, id))
          : jsx('option', { value: '', children: '暂无靶标' })
      }),
      jsx('div', {
        className: 'flex flex-wrap gap-1',
        children: TABS.map(([id, label]) => jsx('button', {
          className: id === tab ? 'rounded px-2 py-1 text-(--ui-text)' : 'rounded px-2 py-1 text-(--ui-text-quaternary)',
          onClick: () => setTab(id),
          children: label
        }, id))
      }),
      jsx('div', {
        className: 'flex flex-col gap-1',
        children: linesFor(tab, data).map((line, index) => jsx('div', {
          className: 'rounded border border-(--ui-stroke-secondary) px-2 py-1',
          children: line
        }, index))
      }),
      tab === 'score' ? jsx('select', {
        value: mode,
        onChange: (event) => {
          const next = event.target.value
          setMode(next)
          rest('/score-rules', { method: 'POST', body: JSON.stringify({ mode: next }) })
            .then(() => setNotice('已保存，新会话生效'))
            .catch(() => setNotice('加载失败'))
        },
        children: SCORE.map(([value, label]) => jsx('option', { value, children: label }, value))
      }) : null,
      jsx('div', { children: notice || '只读索引。不显示命令、凭据或 payload。' })
    ]
  })
}

export default {
  id: ID,
  name: '红队面板',
  defaultEnabled: false,
  register(ctx) {
    ctx.register({
      id: 'board',
      area: 'panes',
      title: '红队面板',
      data: { placement: 'right', width: '320px' },
      render: () => jsx(Pane, { rest: ctx.rest })
    })
  }
}
