function TopBar () {
    return (
     <div style={{
        display: "flex",
        position: "fixed",
        height: "10%",
        justifyContent: "center",
        background: "white", // removed the #, since "lightgray" is a named color
        top: 0,
        left: 0,
        right: 0,
        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)"
        //   zIndex: 1000 // optional, ensures it's above other content
        }}>
            <h1>Public Health Sentinel</h1>   
        </div>
    )
}

export default TopBar