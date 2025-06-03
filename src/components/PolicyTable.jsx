import PolicyCard from './PolicyCard';
import './PolicyTable.css';

// Divider.jsx
const Divider = ({ vertical = false, style = {} }) => {
  const baseStyle = vertical
    ? {
        width: '2px',
        backgroundColor: '#ccc',
        margin: '0 20px',
        alignSelf: 'stretch',
      }
    : {
        height: '1px',
        backgroundColor: '#ccc',
        margin: '10px 0',
        width: '100%',
      };

  return <div style={{ ...baseStyle, ...style }} />;
};

const PolicyTable = () => {
  const draftPolicies = [
    { id: 1, name: 'Draft 1', age: 30, approved: false },
    { id: 2, name: 'Draft 2', age: 28, approved: false },
  ];

  const approvedPolicies = [
    { id: 3, name: 'Policy A', age: 35, approved: true },
    { id: 4, name: 'Policy B', age: 40, approved: true },
  ];

  return (
    <div className="two-column-container">
      <div className="column">


        <h2>Draft Policies</h2>
        {draftPolicies.map((item) => (
         <PolicyCard policy={item}></PolicyCard>
        ))}
      </div>

         <Divider vertical={true} />

      <div className="column">
        <h2>Approved Policies</h2>
        {approvedPolicies.map((item) => (
             <PolicyCard policy={item}></PolicyCard>
    
        ))}
      </div>
    </div>
  );
};

export default PolicyTable;
