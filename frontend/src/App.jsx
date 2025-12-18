import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [drugName, setDrugName] = useState('')
  const [quantity, setQuantity] = useState(1)
  const [qrCodes, setQrCodes] = useState([])
  const [loading, setLoading] = useState(false)

  const handleGenerate = async () => {
    if(!drugName) return alert("Please enter a drug name!")
    
    setLoading(true)
    try {
      // Backend ko call kar rahe hain
      const response = await axios.get(`http://127.0.0.1:8000/generate-batch/${drugName}/${quantity}`)
      setQrCodes(response.data.qr_codes)
      alert(`Success! Generated Batch ID: ${response.data.batch_id}`)
    } catch (error) {
      console.error("Error connecting to backend:", error)
      alert("Backend se connect nahi ho pa raha. Kya uvicorn chal raha hai?")
    }
    setLoading(false)
  }

  return (
    <div className="container">
      <h1>💊 MediTrace Manufacturer Dashboard</h1>
      
      <div className="card">
        <h3>Create New Batch</h3>
        <input 
          type="text" 
          placeholder="Enter Drug Name (e.g. Paracetamol)" 
          value={drugName}
          onChange={(e) => setDrugName(e.target.value)}
        />
        
        <input 
          type="number" 
          min="1" max="10"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
        />
        
        <button onClick={handleGenerate} disabled={loading}>
          {loading ? "Generating..." : "Generate QR Codes"}
        </button>
      </div>

      <div className="qr-grid">
        {qrCodes.map((url, index) => (
          <div key={index} className="qr-card">
            <img src={url} alt="QR Code" />
            <p>Unit #{index + 1}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App