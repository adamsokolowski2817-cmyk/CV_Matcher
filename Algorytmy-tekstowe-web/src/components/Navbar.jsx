export default function Navbar() {
  return (
    <nav className="w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">

        <div>
          <h1 className="text-2xl font-bold text-white">
            CV Matcher
          </h1>

          <p className="text-sm text-slate-400">
            Algorytmy tekstowe
          </p>
        </div>

        <div className="flex items-center gap-4 text-sm text-slate-300">
          <span>OLX</span>
          <span>Pracuj.pl</span>
          <span>The Protocol</span>
        </div>

      </div>
    </nav>
  )
}