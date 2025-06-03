import './ScenarioCard.css'
import { generatePolicyFromStrategy } from "../common/api";


function ScenarioCard({scenario, onClick}) {

  async function generatePolicy () {
    const result = await generatePolicyFromStrategy(scenario.id);
    console.log(result);
  }

    return (
        <div style={{display: "flex", flexDirection:"row"}}>
        <div onClick={onClick} style={{border: "1px solid black", width: "80%", minHeight: "50px", 
            padding: "10px", borderRadius: "10px", gap: "10px", background:"lightgrey", marginBottom: "10px"}}>
            <strong>{scenario.short_description}</strong>
            <div>{scenario.full_description}</div>
        </div>
        <div style={{display: "flex", alignItems:"center"}}>
        <button onClick={generatePolicy}>Generate policy</button>
        </div>
        </div>
    )
}

export default ScenarioCard