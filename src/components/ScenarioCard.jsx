function ScenarioCard({scenario, onClick}) {
    return (
        <div style={{display: "flex", flexDirection:"row"}}>
        <div onClick={onClick} style={{border: "1px solid black", width: "80%", minHeight: "50px", 
            padding: "10px", borderRadius: "10px",marginBottom: "10px", background:"#FFE5B4"}}>
            <strong>{scenario.title}</strong>
            <div>{scenario.description}</div>
        </div>
        <div>
        <button style={{height: "50px"}}>Generate policy</button>
        </div>
        </div>
    )
}

export default ScenarioCard