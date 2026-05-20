export default function OfferCard({ offer, onClick }) {
  return (
    <div
      onClick={onClick}
      className="bg-slate-900 border border-slate-800 rounded-3xl p-6 hover:border-blue-500 transition cursor-pointer"
    >
      <div className="flex items-start justify-between gap-4">

        <div>
          <h2 className="text-xl font-bold">
            {offer.title}
          </h2>

          <p className="text-slate-400 mt-2">
            {offer.location || 'Brak lokalizacji'}
          </p>

          <span className="inline-block mt-3 bg-blue-500/10 text-blue-300 border border-blue-500/30 px-3 py-1 rounded-full text-xs font-medium">
            {offer.source || 'Nieznane źródło'}
          </span>
        </div>

        <div className="text-right">
          <div className="text-3xl font-bold text-blue-400">
            {offer.score}%
          </div>

          <div className="text-sm text-slate-500">
            dopasowanie
          </div>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        {(offer.skills || []).map((skill, index) => (
          <span
            key={index}
            className="bg-slate-800 px-3 py-1 rounded-full text-sm"
          >
            {skill}
          </span>
        ))}
      </div>

      <div className="mt-6 text-blue-400 hover:text-blue-300">
        Kliknij, aby zobaczyć szczegóły
      </div>
    </div>
  )
}