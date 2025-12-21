import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Shield,
  AlertTriangle,
  CheckCircle2,
  Activity,
  Cpu,
  Database,
  Link,
  Zap,
  TrendingUp,
  MapPin,
  Clock,
  Hash,
} from "lucide-react";

export default function SystemMonitor() {
  const [blockchainStatus, setBlockchainStatus] = useState({
    integrity: "verifying",
    chainLength: 0,
    latestHash: "",
    genesisHash: "",
    lastVerified: "",
  });

  const [anomalies, setAnomalies] = useState([]);
  const [systemHealth, setSystemHealth] = useState({
    database: "checking",
    api: "checking",
    uptime: "0h 0m",
    totalScans: 0,
  });

  // ═══════════════════════════════════════════════════
  // FETCH BLOCKCHAIN STATUS
  // ═══════════════════════════════════════════════════
  useEffect(() => {
    // Simulated blockchain verification
    // In production, this would call backend API
    setTimeout(() => {
      setBlockchainStatus({
        integrity: "verified",
        chainLength: 156,
        latestHash: "b9f1f7c8859e6dbc815c020c2187d9fc",
        genesisHash: "bea1e0522e9a2b86cf89e9f0a1b2c3d4",
        lastVerified: new Date().toLocaleString(),
      });

      // Simulated anomalies
      setAnomalies([
        {
          id: 1,
          type: "IMPOSSIBLE_SPEED",
          severity: "critical",
          drugId: "SEED1234-1",
          from: "Mumbai Distribution Hub",
          to: "Delhi Pharmacy",
          distance: 1153.24,
          timeMinutes: 10,
          speed: 6919.45,
          maxSpeed: 900,
          timestamp: "2024-12-21 11:45:23",
          status: "flagged",
        },
        {
          id: 2,
          type: "SUSPICIOUS_FREQUENCY",
          severity: "medium",
          drugId: "SEED5678-3",
          location: "Chennai Warehouse",
          scanCount: 15,
          timeWindow: "1 hour",
          timestamp: "2024-12-21 10:30:15",
          status: "investigating",
        },
      ]);

      setSystemHealth({
        database: "connected",
        api: "healthy",
        uptime: "48h 32m",
        totalScans: 1247,
      });
    }, 1500);
  }, []);

  return (
    <div style={{ paddingTop: "2rem" }}>
      {/* Header */}
      <div className="hero-section" style={{ marginBottom: "3rem" }}>
        <h1 className="hero-title" style={{ fontSize: "3rem" }}>
          System Monitor
        </h1>
        <p className="hero-subtitle">
          Real-time blockchain integrity verification and anomaly detection
        </p>
      </div>

      {/* System Health Cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "1.5rem",
          marginBottom: "3rem",
        }}
      >
        {/* Database Status */}
        <div className="stat-card">
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "1rem",
              marginBottom: "0.5rem",
            }}
          >
            <Database size={24} color="#06b6d4" />
            <div className="stat-label">Database</div>
          </div>
          <div
            className="stat-value"
            style={{
              fontSize: "1.5rem",
              color:
                systemHealth.database === "connected" ? "#10b981" : "#64748b",
            }}
          >
            {systemHealth.database === "checking" ? "Checking..." : "Connected"}
          </div>
        </div>

        {/* API Status */}
        <div className="stat-card">
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "1rem",
              marginBottom: "0.5rem",
            }}
          >
            <Activity size={24} color="#06b6d4" />
            <div className="stat-label">API Status</div>
          </div>
          <div
            className="stat-value"
            style={{
              fontSize: "1.5rem",
              color: systemHealth.api === "healthy" ? "#10b981" : "#64748b",
            }}
          >
            {systemHealth.api === "checking" ? "Checking..." : "Healthy"}
          </div>
        </div>

        {/* Uptime */}
        <div className="stat-card">
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "1rem",
              marginBottom: "0.5rem",
            }}
          >
            <Clock size={24} color="#06b6d4" />
            <div className="stat-label">Uptime</div>
          </div>
          <div className="stat-value" style={{ fontSize: "1.5rem" }}>
            {systemHealth.uptime}
          </div>
        </div>

        {/* Total Scans */}
        <div className="stat-card">
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "1rem",
              marginBottom: "0.5rem",
            }}
          >
            <Zap size={24} color="#06b6d4" />
            <div className="stat-label">Total Scans</div>
          </div>
          <div className="stat-value" style={{ fontSize: "1.5rem" }}>
            {systemHealth.totalScans.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "2rem",
          marginBottom: "3rem",
        }}
      >
        {/* LEFT: Blockchain Status */}
        <motion.div
          className="glass-card"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <h2 className="card-title">
            <Link size={24} /> Blockchain Integrity
          </h2>

          {blockchainStatus.integrity === "verifying" ? (
            <div
              style={{
                textAlign: "center",
                padding: "3rem",
                color: "#64748b",
              }}
            >
              <Cpu
                size={48}
                style={{
                  margin: "0 auto 1rem",
                  animation: "spin 2s linear infinite",
                }}
              />
              <div style={{ fontSize: "1.125rem" }}>
                Verifying blockchain integrity...
              </div>
            </div>
          ) : (
            <>
              {/* Status Banner */}
              <div
                style={{
                  background:
                    "linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.1))",
                  border: "2px solid rgba(16, 185, 129, 0.3)",
                  borderRadius: "16px",
                  padding: "1.5rem",
                  marginBottom: "2rem",
                  display: "flex",
                  alignItems: "center",
                  gap: "1rem",
                }}
              >
                <div
                  style={{
                    width: "60px",
                    height: "60px",
                    background: "linear-gradient(135deg, #10b981, #059669)",
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    boxShadow: "0 8px 24px rgba(16, 185, 129, 0.4)",
                  }}
                >
                  <Shield size={32} color="#ffffff" />
                </div>
                <div style={{ flex: 1 }}>
                  <div
                    style={{
                      fontSize: "1.5rem",
                      fontWeight: "800",
                      color: "#10b981",
                      marginBottom: "0.25rem",
                    }}
                  >
                    ✅ Chain Verified
                  </div>
                  <div style={{ fontSize: "0.875rem", color: "#64748b" }}>
                    No tampering detected • All blocks validated
                  </div>
                </div>
              </div>

              {/* Chain Stats */}
              <div style={{ display: "grid", gap: "1.5rem" }}>
                <div>
                  <div className="form-label">Chain Length</div>
                  <div
                    style={{
                      fontSize: "1.25rem",
                      fontWeight: "700",
                      color: "#cbd5e1",
                      display: "flex",
                      alignItems: "center",
                      gap: "0.5rem",
                    }}
                  >
                    <TrendingUp size={20} color="#10b981" />
                    {blockchainStatus.chainLength} blocks
                  </div>
                </div>

                <div>
                  <div className="form-label">
                    <Hash size={14} style={{ display: "inline" }} /> Latest
                    Block Hash
                  </div>
                  <div
                    style={{
                      padding: "0.75rem",
                      background: "rgba(59, 130, 246, 0.1)",
                      border: "1px solid rgba(59, 130, 246, 0.3)",
                      borderRadius: "10px",
                      fontFamily: "monospace",
                      fontSize: "0.75rem",
                      color: "#06b6d4",
                      wordBreak: "break-all",
                    }}
                  >
                    {blockchainStatus.latestHash}
                  </div>
                </div>

                <div>
                  <div className="form-label">
                    <Hash size={14} style={{ display: "inline" }} /> Genesis
                    Block Hash
                  </div>
                  <div
                    style={{
                      padding: "0.75rem",
                      background: "rgba(139, 92, 246, 0.1)",
                      border: "1px solid rgba(139, 92, 246, 0.3)",
                      borderRadius: "10px",
                      fontFamily: "monospace",
                      fontSize: "0.75rem",
                      color: "#8b5cf6",
                      wordBreak: "break-all",
                    }}
                  >
                    {blockchainStatus.genesisHash}
                  </div>
                </div>

                <div
                  style={{
                    padding: "1rem",
                    background: "rgba(0, 0, 0, 0.3)",
                    borderRadius: "12px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <div>
                    <div
                      style={{
                        fontSize: "0.875rem",
                        color: "#64748b",
                        marginBottom: "0.25rem",
                      }}
                    >
                      Last Verified
                    </div>
                    <div style={{ color: "#cbd5e1", fontWeight: "600" }}>
                      {blockchainStatus.lastVerified}
                    </div>
                  </div>
                  <CheckCircle2 size={24} color="#10b981" />
                </div>
              </div>

              {/* Verification Info */}
              <div
                style={{
                  marginTop: "2rem",
                  padding: "1rem",
                  background: "rgba(59, 130, 246, 0.05)",
                  border: "1px solid rgba(59, 130, 246, 0.2)",
                  borderRadius: "12px",
                  fontSize: "0.875rem",
                  color: "#94a3b8",
                }}
              >
                <strong style={{ color: "#06b6d4" }}>ℹ️ How it works:</strong>
                <br />
                Each block contains a cryptographic hash of the previous block.
                Any tampering with historical data breaks the chain and is
                immediately detected.
              </div>
            </>
          )}
        </motion.div>

        {/* RIGHT: Anomaly Detection */}
        <motion.div
          className="glass-card"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <h2 className="card-title">
            <AlertTriangle size={24} /> Anomaly Alerts
          </h2>

          {anomalies.length === 0 ? (
            <div
              style={{
                textAlign: "center",
                padding: "3rem",
                color: "#64748b",
              }}
            >
              <CheckCircle2
                size={48}
                color="#10b981"
                style={{ margin: "0 auto 1rem" }}
              />
              <div style={{ fontSize: "1.125rem", marginBottom: "0.5rem" }}>
                No Anomalies Detected
              </div>
              <div style={{ fontSize: "0.875rem" }}>
                All supply chain events are within normal parameters
              </div>
            </div>
          ) : (
            <div style={{ display: "grid", gap: "1.5rem" }}>
              {anomalies.map((anomaly) => (
                <div
                  key={anomaly.id}
                  style={{
                    background:
                      anomaly.severity === "critical"
                        ? "linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(220, 38, 38, 0.1))"
                        : "linear-gradient(135deg, rgba(251, 146, 60, 0.15), rgba(249, 115, 22, 0.1))",
                    border: `2px solid ${
                      anomaly.severity === "critical"
                        ? "rgba(239, 68, 68, 0.4)"
                        : "rgba(251, 146, 60, 0.4)"
                    }`,
                    borderRadius: "16px",
                    padding: "1.5rem",
                    position: "relative",
                  }}
                >
                  {/* Severity Badge */}
                  <div
                    style={{
                      position: "absolute",
                      top: "1rem",
                      right: "1rem",
                      padding: "0.375rem 0.75rem",
                      background:
                        anomaly.severity === "critical" ? "#ef4444" : "#f59e0b",
                      borderRadius: "20px",
                      fontSize: "0.75rem",
                      fontWeight: "700",
                      color: "#ffffff",
                      textTransform: "uppercase",
                    }}
                  >
                    {anomaly.severity}
                  </div>

                  {/* Alert Header */}
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.75rem",
                      marginBottom: "1rem",
                    }}
                  >
                    <AlertTriangle
                      size={28}
                      color={
                        anomaly.severity === "critical" ? "#ef4444" : "#f59e0b"
                      }
                    />
                    <div>
                      <div
                        style={{
                          fontSize: "1.125rem",
                          fontWeight: "700",
                          color: "#ffffff",
                        }}
                      >
                        {anomaly.type === "IMPOSSIBLE_SPEED"
                          ? "Impossible Travel Detected"
                          : "Suspicious Scan Pattern"}
                      </div>
                      <div style={{ fontSize: "0.875rem", color: "#94a3b8" }}>
                        Drug ID: {anomaly.drugId}
                      </div>
                    </div>
                  </div>

                  {/* Alert Details */}
                  {anomaly.type === "IMPOSSIBLE_SPEED" ? (
                    <div
                      style={{
                        background: "rgba(0, 0, 0, 0.3)",
                        borderRadius: "12px",
                        padding: "1rem",
                        marginBottom: "1rem",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "0.5rem",
                          marginBottom: "0.75rem",
                        }}
                      >
                        <MapPin size={16} color="#64748b" />
                        <span
                          style={{ color: "#cbd5e1", fontSize: "0.875rem" }}
                        >
                          {anomaly.from} → {anomaly.to}
                        </span>
                      </div>
                      <div
                        style={{
                          display: "grid",
                          gridTemplateColumns: "1fr 1fr",
                          gap: "0.75rem",
                          fontSize: "0.875rem",
                        }}
                      >
                        <div>
                          <div style={{ color: "#64748b" }}>Distance</div>
                          <div style={{ color: "#cbd5e1", fontWeight: "600" }}>
                            {anomaly.distance.toFixed(2)} km
                          </div>
                        </div>
                        <div>
                          <div style={{ color: "#64748b" }}>Time Elapsed</div>
                          <div style={{ color: "#cbd5e1", fontWeight: "600" }}>
                            {anomaly.timeMinutes} minutes
                          </div>
                        </div>
                        <div>
                          <div style={{ color: "#64748b" }}>
                            Calculated Speed
                          </div>
                          <div style={{ color: "#ef4444", fontWeight: "700" }}>
                            {anomaly.speed.toFixed(0)} km/h
                          </div>
                        </div>
                        <div>
                          <div style={{ color: "#64748b" }}>
                            Max Allowed Speed
                          </div>
                          <div style={{ color: "#10b981", fontWeight: "600" }}>
                            {anomaly.maxSpeed} km/h
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div
                      style={{
                        background: "rgba(0, 0, 0, 0.3)",
                        borderRadius: "12px",
                        padding: "1rem",
                        marginBottom: "1rem",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "0.5rem",
                          marginBottom: "0.75rem",
                        }}
                      >
                        <MapPin size={16} color="#64748b" />
                        <span
                          style={{ color: "#cbd5e1", fontSize: "0.875rem" }}
                        >
                          {anomaly.location}
                        </span>
                      </div>
                      <div
                        style={{
                          display: "grid",
                          gridTemplateColumns: "1fr 1fr",
                          gap: "0.75rem",
                          fontSize: "0.875rem",
                        }}
                      >
                        <div>
                          <div style={{ color: "#64748b" }}>Scan Count</div>
                          <div style={{ color: "#f59e0b", fontWeight: "700" }}>
                            {anomaly.scanCount} scans
                          </div>
                        </div>
                        <div>
                          <div style={{ color: "#64748b" }}>Time Window</div>
                          <div style={{ color: "#cbd5e1", fontWeight: "600" }}>
                            {anomaly.timeWindow}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Recommendation */}
                  <div
                    style={{
                      padding: "0.75rem",
                      background:
                        anomaly.severity === "critical"
                          ? "rgba(239, 68, 68, 0.1)"
                          : "rgba(251, 146, 60, 0.1)",
                      borderRadius: "8px",
                      fontSize: "0.8125rem",
                      color: "#cbd5e1",
                    }}
                  >
                    <strong style={{ color: "#ffffff" }}>
                      🚨 Recommendation:
                    </strong>{" "}
                    {anomaly.type === "IMPOSSIBLE_SPEED"
                      ? "Potential QR cloning detected. Flag for manual investigation and contact authorities."
                      : "Possible photocopy attack. Verify packaging authenticity at source location."}
                  </div>

                  {/* Timestamp */}
                  <div
                    style={{
                      marginTop: "1rem",
                      fontSize: "0.75rem",
                      color: "#64748b",
                      display: "flex",
                      alignItems: "center",
                      gap: "0.5rem",
                    }}
                  >
                    <Clock size={12} />
                    Detected at {anomaly.timestamp}
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </div>

      {/* Technical Info Banner */}
      <motion.div
        className="glass-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{
          background:
            "linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1))",
          border: "1px solid rgba(59, 130, 246, 0.3)",
        }}
      >
        <h3
          style={{
            fontSize: "1.25rem",
            fontWeight: "700",
            marginBottom: "1rem",
            display: "flex",
            alignItems: "center",
            gap: "0.75rem",
          }}
        >
          <Cpu size={24} color="#06b6d4" />
          Detection Algorithms
        </h3>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "1.5rem",
          }}
        >
          <div>
            <div
              style={{
                fontSize: "1rem",
                fontWeight: "600",
                color: "#ffffff",
                marginBottom: "0.5rem",
              }}
            >
              🔗 Blockchain Verification
            </div>
            <div style={{ fontSize: "0.875rem", color: "#94a3b8" }}>
              SHA-256 cryptographic hashing with chain linking. Each block
              references the previous block's hash. Any tampering breaks the
              chain and is immediately detected.
            </div>
          </div>

          <div>
            <div
              style={{
                fontSize: "1rem",
                fontWeight: "600",
                color: "#ffffff",
                marginBottom: "0.5rem",
              }}
            >
              📍 Haversine Distance Formula
            </div>
            <div style={{ fontSize: "0.875rem", color: "#94a3b8" }}>
              Calculates great-circle distance between GPS coordinates. Detects
              impossible travel speeds ({">"} 900 km/h) indicating potential QR
              cloning attacks.
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
