export default function SearchPanel({
  city,
  setCity,
  query,
  setQuery,
  source,
  setSource,
  cvFile,
  setCvFile,
  onSearch,
  loading,
}) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-4">

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <input
          value={city}
          onChange={(e) => setCity(e.target.value)}
          placeholder="Miasto"
          className="bg-slate-800 rounded-2xl px-4 py-3 outline-none border border-slate-700"
        />

        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Technologia"
          className="bg-slate-800 rounded-2xl px-4 py-3 outline-none border border-slate-700"
        />

        <select
          value={source}
          onChange={(e) => setSource(e.target.value)}
          className="bg-slate-800 rounded-2xl px-4 py-3 border border-slate-700"
        >
          <option value="all">Wszystkie źródła</option>
          <option value="olx">OLX</option>
          <option value="pracuj">Pracuj.pl</option>
          <option value="protocol">The Protocol</option>
        </select>

        <button
          onClick={onSearch}
          disabled={loading}
          className={`transition rounded-2xl py-3 font-semibold ${
            loading
              ? 'bg-slate-700 cursor-not-allowed text-slate-400'
              : 'bg-blue-600 hover:bg-blue-500 text-white'
          }`}
        >
          {loading ? 'Przetwarzanie...' : 'Uruchom scraper'}
        </button>
      </div>

      <div>
        <label className="block text-sm text-slate-400 mb-2">
          CV PDF
        </label>

        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setCvFile(e.target.files[0])}
          className="block w-full text-sm text-slate-300 file:mr-4 file:rounded-xl file:border-0 file:bg-blue-600 file:px-4 file:py-2 file:text-white hover:file:bg-blue-500"
        />

        {cvFile && (
          <p className="text-sm text-slate-400 mt-2">
            Wybrano: {cvFile.name}
          </p>
        )}
      </div>
    </div>
  )
}