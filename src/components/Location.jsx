import React from 'react'

function Location() {
    const [showModal, setShowModal] = React.useState(false)

    const [currText, setCurrText] = React.useState("")

    const [currentLocation, setCurrentLocation] = useState()


    return (
        <div>

            {currentLocation ? 
            <div>
            <div>{currentLocation.city}</div>
            <div>{currentLocation.state}</div>
            </div>
            : <div>No location selected</div>
            }

            <button onClick={() => setShowModal(true)}>Change Location</button>

            {showModal &&
            <div>
            <input placeholder="enter zipcode" value={currText} onChange={(e) => setCurrText(e.target.value)}></input>
            <button onClick={setCurrentLocation(currText)}>Set</button>
            </div>
            }
        </div>
    )
}

export default Location