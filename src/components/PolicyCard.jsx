function PolicyCard({policy}) {
    return (
        <div key={policy.id} className="data-card">
            <h3>{policy.name}</h3>
            <p><strong>Title:</strong> {policy.title}</p>
            <p><strong>Description:</strong> {policy.description}</p>
            {policy.approved && <button>Translate to</button>}
          </div>
    )
}

export default PolicyCard;