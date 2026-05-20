export default function StatsCards({ offers }) {
  const scores = offers.map((offer) => Number(offer.match ?? offer.score ?? 0))

  const avg = scores.length
    ? (scores.reduce((sum, score) => sum + score, 0) / scores.length).toFixed(1)
    : '0.0'

  const best = scores.length
    ? Math.max(...scores).toFixed(1)
    : '0.0'

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
        <h3 className="text-slate-400 text-sm">Liczba ofert</h3>
        <p className="text-4xl font-bold mt-2">{offers.length}</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
        <h3 className="text-slate-400 text-sm">Średnie dopasowanie</h3>
        <p className="text-4xl font-bold mt-2">{avg}%</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
        <h3 className="text-slate-400 text-sm">Najlepszy wynik</h3>
        <p className="text-4xl font-bold mt-2">{best}%</p>
      </div>

    </div>
  )
}