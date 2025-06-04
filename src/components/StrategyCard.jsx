import './StrategyCard.css'
import { generatePolicyFromStrategy } from "../common/api";


function StrategyCard({strategy, onClick}) {

  async function generatePolicy () {
    const result = await generatePolicyFromStrategy(strategy.id);
    console.log(result);
  }

    return (
        <div style={{display: "flex", flexDirection:"row"}}>
        <div onClick={onClick} style={{border: "1px solid black", width: "80%", minHeight: "50px", 
            padding: "10px", borderRadius: "10px", gap: "10px", background:"lightgrey", marginBottom: "10px"}}>
            <strong>{strategy.short_description}</strong>
            <div>{strategy.full_description}</div>
        </div>
        <div style={{display: "flex", alignItems:"center"}}>
        <button onClick={generatePolicy}>Generate policy</button>
        </div>
        </div>
    )
}

export default StrategyCard