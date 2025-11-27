import { Lightbulb } from 'lucide-react'
import './ExampleQueries.css'

const examples = [
  {
    title: "Type 2 Diabetes Trial",
    query: "Find sites for a Phase III Type 2 Diabetes trial targeting 200 patients in the Northeast US with strong endocrinology departments"
  },
  {
    title: "Lung Cancer Trial",
    query: "I need 5 sites for a Phase II lung cancer trial in California, preferably academic medical centers with PET imaging capabilities"
  },
  {
    title: "Rare Disease Trial",
    query: "Looking for sites with experience in rare metabolic disorders, any US location, need at least 50 potential patients per site"
  },
  {
    title: "Hypertension Trial",
    query: "Find sites for Phase III hypertension study in major metropolitan areas with proven track record in cardiology trials"
  }
]

function ExampleQueries({ onSelectExample }) {
  return (
    <div className="card example-queries">
      <div className="example-header">
        <Lightbulb size={20} className="example-icon" />
        <h3 className="example-title">Sample Protocols</h3>
      </div>

      <p className="example-description">
        Select a sample protocol to run a feasibility analysis:
      </p>

      <div className="example-grid">
        {examples.map((example, index) => (
          <button
            key={index}
            className="example-card"
            onClick={() => onSelectExample(example.query)}
          >
            <h4 className="example-card-title">{example.title}</h4>
            <p className="example-card-text">{example.query}</p>
          </button>
        ))}
      </div>
    </div>
  )
}

export default ExampleQueries
