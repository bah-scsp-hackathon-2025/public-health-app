import { useState } from "react";
import { generatePolicyFromStrategy } from "../common/api";
import styles from './StrategyCard.module.css';

function StrategyCard({ strategy, isSelected, onClick }) {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  async function generatePolicy() {
    setLoading(true);
    setSuccess(false); // Reset success state
    try {
      await generatePolicyFromStrategy(strategy.id);
      setSuccess(true);
    } catch (err) {
      console.error("Failed to generate policy", err);
      setSuccess(false);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.card} onClick={onClick}>
      <div className={styles.headerRow}>
        <strong className={styles.title}>{strategy.short_description}</strong>
        <div className={styles.buttonSection}>
          {isSelected && !success &&  (
            <button
              onClick={(e) => {
                e.stopPropagation(); // prevent card from toggling again
                generatePolicy();
              }}
              disabled={loading}
              className={styles.button}
            >
              {loading ? "Generating..." : "Generate Policy"}
            </button>
          )}
          {success && (
            <div className={styles.success}>✅ Policy created successfully!</div>
          )}
        </div>
      </div>
      <div>{strategy.full_description}</div>
    </div>
  );
}

export default StrategyCard;