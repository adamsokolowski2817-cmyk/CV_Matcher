import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

export default function SkillStats({ offers }) {
  const counter = {}

  offers.forEach((offer) => {
    ;(offer.missing_keywords || []).forEach((skill) => {
      counter[skill] = (counter[skill] || 0) + 1
    })
  })

  const data = Object.entries(counter)
    .map(([skill, count]) => ({ skill, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8)

  if (data.length === 0) {
    return null
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
      <h2 className="text-xl font-bold mb-2">
        Najczęściej brakujące technologie
      </h2>

      <p className="text-slate-400 mb-6">
        Wykres pokazuje, które technologie najczęściej pojawiają się jako braki względem analizowanych ofert.
      </p>

      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <XAxis dataKey="skill" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}