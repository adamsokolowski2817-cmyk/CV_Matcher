export default function OfferModal({ offer, onClose }) {
  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center px-6">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 max-w-3xl w-full max-h-[85vh] overflow-y-auto">

        <div className="flex justify-between gap-6">
          <div>
            <h2 className="text-3xl font-bold">
              {offer.title}
            </h2>

            <p className="text-slate-400 mt-2">
              {offer.location}
            </p>

            <p className="text-blue-300 mt-2">
              {offer.source}
            </p>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white text-2xl"
          >
            ×
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
          <div className="bg-slate-800 rounded-2xl p-4">
            <p className="text-slate-400 text-sm">Dopasowanie</p>
            <p className="text-3xl font-bold text-blue-400">
              {Number(offer.match || 0).toFixed(1)}%
            </p>
          </div>

          <div className="bg-slate-800 rounded-2xl p-4">
            <p className="text-slate-400 text-sm">Semantyka</p>
            <p className="text-3xl font-bold">
              {Number(offer.semantic_score || 0).toFixed(1)}%
            </p>
          </div>

          <div className="bg-slate-800 rounded-2xl p-4">
            <p className="text-slate-400 text-sm">Słowa kluczowe</p>
            <p className="text-3xl font-bold">
              {Number(offer.keyword_score || 0).toFixed(1)}%
            </p>
          </div>
        </div>

        <div className="mt-8">
          <h3 className="font-bold mb-3">Zgodne technologie</h3>
          <div className="flex flex-wrap gap-2">
            {(offer.matched_keywords || []).map((skill) => (
              <span key={skill} className="bg-green-500/10 text-green-300 border border-green-500/30 px-3 py-1 rounded-full text-sm">
                {skill}
              </span>
            ))}
          </div>
        </div>

        <div className="mt-8">
          <h3 className="font-bold mb-3">Brakujące technologie</h3>
          <div className="flex flex-wrap gap-2">
            {(offer.missing_keywords || []).map((skill) => (
              <span key={skill} className="bg-red-500/10 text-red-300 border border-red-500/30 px-3 py-1 rounded-full text-sm">
                {skill}
              </span>
            ))}
          </div>
        </div>

        <a
          href={offer.url}
          target="_blank"
          rel="noreferrer"
          className="inline-block mt-8 bg-blue-600 hover:bg-blue-500 px-5 py-3 rounded-2xl font-semibold"
        >
          Otwórz ofertę
        </a>
      </div>
    </div>
  )
}