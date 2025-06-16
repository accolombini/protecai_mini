import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './index.css' // usando Tailwind aqui

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-100 to-slate-300 flex flex-col items-center justify-center p-6">
      {/* Logotipos com espaçamento e animação */}
      <div className="flex gap-10 mb-8">
        <a href="https://vite.dev" target="_blank" rel="noopener noreferrer">
          <img src={viteLogo} className="w-20 hover:scale-110 transition-transform duration-300" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank" rel="noopener noreferrer">
          <img src={reactLogo} className="w-20 hover:scale-110 transition-transform duration-300" alt="React logo" />
        </a>
      </div>

      {/* Título centralizado com estilo moderno */}
      <h1 className="text-4xl font-bold text-blue-700 mb-4">Vite + React + TailwindCSS</h1>

      {/* Cartão com contador */}
      <div className="bg-white shadow-md rounded-xl px-8 py-6 text-center mb-4">
        <button
          onClick={() => setCount((count) => count + 1)}
          className="bg-blue-600 text-white font-medium px-4 py-2 rounded hover:bg-blue-700 transition"
        >
          count is {count}
        </button>
        <p className="text-gray-600 mt-3">
          Edit <code className="bg-gray-100 px-1 rounded text-sm">src/App.tsx</code> and save to test HMR
        </p>
      </div>

      {/* Rodapé com instruções */}
      <p className="text-gray-500 text-sm">
        Click on the Vite and React logos to learn more
      </p>
    </div>
  )
}

export default App
