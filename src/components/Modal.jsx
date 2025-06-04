import ReactDOM from "react-dom";

const Modal = ({ height, show, onClose, children }) => {
  if (!show) return null;

  return ReactDOM.createPortal(
    <div style={styles.overlay} onClick={onClose}>
      <div style={{ ...styles.modal, height: height || "auto" }} onClick={(e) => e.stopPropagation()}>
        <button onClick={onClose} style={styles.close}>×</button>
        {children}
      </div>
    </div>,
    document.body
  );
};

const styles = {
  overlay: {
    position: "fixed",
    top: 0, left: 0,
    width: "100vw", height: "100vh",
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 9999,
  },
  modal: {
    background: "#fff",
    width: "400px",
    // height: "500px",
    padding: "24px 20px",
    borderRadius: "10px",
    position: "relative",
    boxShadow: "0 10px 25px rgba(0,0,0,0.2)",
    textAlign: "center",
  },
  close: {
    position: "absolute",
    top: "10px",
    right: "15px",
    fontSize: "20px",
    background: "none",
    border: "none",
    cursor: "pointer",
  },
};

export default Modal;
