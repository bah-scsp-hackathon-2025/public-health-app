import './ScenarioCard.css'

function ScenarioCard({scenario, onClick}) {
    return (
        <div style={{display: "flex", flexDirection:"row"}}>
        <div onClick={onClick} style={{border: "1px solid black", width: "80%", minHeight: "50px", 
            padding: "10px", borderRadius: "10px", gap: "10px", background:"lightgrey", marginBottom: "10px"}}>
            <strong>{scenario.title}</strong>
            <div>{scenario.description}</div>
        </div>
        <div style={{display: "flex", alignItems:"center"}}>
        <button>Generate policy</button>
        </div>
        </div>
    )
}

export default ScenarioCard