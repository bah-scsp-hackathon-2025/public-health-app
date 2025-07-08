import { SquareCheckBig, SquarePen } from "lucide-react";
import { marked } from 'marked';
import React from 'react';
import { updatePolicy } from '../common/api';
import Modal from './Modal';

function PolicyCard({ policy, onUpdate }) {
    
    const initialContentText = policy.content
    const [openEditModal, setOpenEditModal] = React.useState(false)
    const [openApproveModal, setOpenApproveModal] = React.useState(false)
    const [contentText, setContentText] = React.useState(policy.content)
    const [changes, setChanges] = React.useState(false)

    const closeEditModal = () => {
        setOpenEditModal(false)
        setContentText(initialContentText)
    }

      async function updateContent() {
        const result = await updatePolicy(policy.id, {content: contentText});
        setChanges(false)
        onUpdate();  // triggers 
      }

    async function approvePolicy() {
        const result = await updatePolicy(policy.id, {approved: true });
        setOpenApproveModal(false)
        onUpdate();  // triggers 
      }

    const updateText = (e) => {
        setContentText(e.target.value)
        setChanges(true)
    }

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
        <strong>Description:</strong>  <div 
          dangerouslySetInnerHTML={{ __html: marked(policy.content) }}
        />
      </p>
      {/* {policy.approved && <button>Translate to</button>} */}
      {!policy.approved && 
        <div style={{ display: "flex", alignItems: "center", gap: "12px", justifyContent: "flex-end" }}>

        <button 
        onClick={() => setOpenEditModal(true)} 
        style={{ display: "flex", alignItems: "center", gap: "8px" }}
        >
        <SquarePen />
        Edit
        </button>

         <button 
        onClick={() => setOpenApproveModal(true)} 
        style={{ display: "flex", alignItems: "center", gap: "8px" }}
        >
        <SquareCheckBig />
        Approve
        </button>
         </div>}

        {openEditModal && 
        <Modal height="500px" show={openEditModal} 
        onClose={() => setOpenEditModal(false)}>
            <div>
                <h3>{policy.title}</h3>
                <textarea 
                onChange={(e) => updateText(e)}
                style={{overflow: "auto", minWidth: "600px", minHeight: "400px"}}
                value={contentText}></textarea>
            </div>
            {changes &&
            <div style={{display: "flex", flexDirection: "row", justifyContent: "flex-end"}}>
            <button style={{width: "20%"}} onClick={() => updateContent()}>Save</button>
            <button style={{width: "20%",}} onClick={() => closeEditModal()}>Cancel</button>
           
            </div>
             }

        </Modal>}

     {openApproveModal && 
        <Modal height="150px" show={openApproveModal} 
        onClose={() => setOpenApproveModal(false)}>
            <div>
                <h3>Confirm Approval for Policy</h3>
                <button onClick={() => approvePolicy()}>Yes, approve this policy</button>
                 <button onClick={() => setOpenApproveModal(false)}>No, go back to editing</button>
                    
            </div>
        </Modal>}
    </div>

  );
}

export default PolicyCard;
