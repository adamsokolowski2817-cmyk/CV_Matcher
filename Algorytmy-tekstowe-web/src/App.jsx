import { useState } from 'react'
import axios from 'axios'

import Navbar from './components/Navbar'
import SearchPanel from './components/SearchPanel'
import StatsCards from './components/StatsCards'
import OfferCard from './components/OfferCard'
import OfferModal from './components/OfferModal'
import SkillStats from './components/SkillStats'

export default function App() {
  const [city, setCity] = useState('Krakow')
  const [query, setQuery] = useState('Python')
  const [source, setSource] = useState('all')
  const [cvFile, setCvFile] = useState(null)

  const [offers, setOffers] = useState([])
  const [advisor, setAdvisor] = useState(null)
  const [loading, setLoading] = useState(false)
  const [progressText, setProgressText] = useState('')
  const [selectedOffer, setSelectedOffer] = useState(null)

  const runSearch = async () => {
    try {
      setLoading(true)
      setAdvisor(null)
      setOffers([])
      setProgressText('Przygotowywanie zapytania...')

      const steps = [
        'Scrapowanie ofert z wybranych źródeł...',
        'Pobieranie opisów ofert...',
        'Obliczanie embeddingów...',
        'Porównywanie CV z ofertami...',
        'Generowanie sugestii poprawy CV...',
      ]

      let i = 0
      const interval = setInterval(() => {
        setProgressText(steps[i % steps.length])
        i++
      }, 3500)

      const formData = new FormData()
      formData.append('city', city)
      formData.append('query', query)
      formData.append('source', source)

      if (cvFile) {
        formData.append('cv_file', cvFile)
      }

      const response = await axios.post(
        'http://127.0.0.1:8000/search',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )

      clearInterval(interval)

      setOffers(response.data.results || [])
      setAdvisor(response.data.advisor || null)
      setProgressText('Gotowe.')
    } catch (error) {
      console.error(error)
      alert('Błąd połączenia z backendem.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Navbar />

      <div className="max-w-7xl mx-auto px-6 py-10 space-y-10">
        <div>
          <h1 className="text-5xl font-bold leading-tight max-w-3xl">
            Inteligentna analiza dopasowania CV do ofert pracy
          </h1>

          <p className="text-slate-400 mt-6 max-w-2xl text-lg">
            Scraper ofert pracy + analiza semantyczna + ranking dopasowania CV.
          </p>
        </div>

        <SearchPanel
          city={city}
          setCity={setCity}
          query={query}
          setQuery={setQuery}
          source={source}
          setSource={setSource}
          cvFile={cvFile}
          setCvFile={setCvFile}
          onSearch={runSearch}
          loading={loading}
        />

        {loading && (
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-3xl p-6 text-blue-200">
            {progressText}
          </div>
        )}

        {advisor && (
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
            <h2 className="text-xl font-bold mb-2">Analiza CV</h2>
            <p className="text-slate-300">{advisor.message}</p>

            {advisor.suggestions?.length > 0 && (
              <ul className="mt-4 space-y-2 text-slate-300">
                {advisor.suggestions.map((suggestion, index) => (
                  <li key={index}>• {suggestion}</li>
                ))}
              </ul>
            )}
          </div>
        )}

        <StatsCards offers={offers} />

        {offers.length > 0 && (
          <SkillStats offers={offers} />
        )}

        {!loading && offers.length === 0 && (
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 text-slate-400">
            Wgraj CV PDF lub użyj domyślnego CV, a następnie kliknij „Uruchom scraper”.
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {offers.map((offer, index) => (
            <OfferCard
              key={offer.id || index}
              offer={{
                ...offer,
                score: Number(offer.match || 0).toFixed(1),
                skills: offer.matched_keywords || [],
              }}
              onClick={() => setSelectedOffer(offer)}
            />
          ))}
        </div>
      </div>

      {selectedOffer && (
        <OfferModal
          offer={selectedOffer}
          onClose={() => setSelectedOffer(null)}
        />
      )}
    </div>
  )
}