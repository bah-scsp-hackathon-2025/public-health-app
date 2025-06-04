
function PolicyDocument({ policy }) {
    
  return (
    <div key={policy.id} className="data-card">
      <h3>{policy.name}</h3>
      <p>
        <strong>Title:</strong> {policy.title}
      </p>
      <p>
        <strong>Author:</strong> {policy.author}
      </p>
        <p>
        {policy.content}
      </p>
    </div>

  );
}

export default PolicyDocument;
