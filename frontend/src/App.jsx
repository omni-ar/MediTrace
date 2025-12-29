import { useState, useRef, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Sphere, MeshDistortMaterial } from "@react-three/drei";
import { motion, AnimatePresence } from "framer-motion";
import {
  Pill,
  ShieldCheck,
  ScanLine,
  Database,
  TrendingUp,
  Fingerprint,
  Sparkles,
  Lock,
  Zap,
  Globe,
  FileText,
  AlertTriangle,
  CheckCircle2,
  Clock,
  MapPin,
  Activity,
} from "lucide-react";
import "./App.css";
import VerifyPage from "./VerifyPage";
import LedgerPage from "./LedgerPage";
import SystemMonitor from "./SystemMonitor";

// ============================================
// 3D COMPONENT: DNA HELIX
// ============================================
function DNAHelix() {
  const group = useRef();
  useFrame((state) => {
    if (group.current) {
      group.current.rotation.y += 0.005;
      group.current.position.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.3;
    }
  });

  const count = 40;
  const points = [];
  for (let i = 0; i < count; i++) {
    const t = i / count;
    const angle = t * Math.PI * 6;
    const x = Math.cos(angle) * 1.5;
    const y = (t - 0.5) * 12;
    const z = Math.sin(angle) * 1.5;
    points.push([x, y, z, "#06b6d4"]);
    points.push([-x, y, -z, "#3b82f6"]);
  }

  return (
    <group ref={group} rotation={[0.2, 0, 0]}>
      {points.map((p, i) => (
        <mesh key={i} position={[p[0], p[1], p[2]]}>
          <sphereGeometry args={[0.12, 16, 16]} />
          <meshStandardMaterial
            color={p[3]}
            emissive={p[3]}
            emissiveIntensity={2}
          />
        </mesh>
      ))}
    </group>
  );
}

// ============================================
// 3D COMPONENT: FLOATING ORBS
// ============================================
function FloatingOrbs() {
  return (
    <>
      <Float speed={1.5} rotationIntensity={0.5} floatIntensity={0.5}>
        <mesh position={[-5, 2, -3]}>
          <Sphere args={[0.8, 64, 64]}>
            <MeshDistortMaterial color="#8b5cf6" speed={2} distort={0.3} />
          </Sphere>
        </mesh>
      </Float>
      <Float speed={2} rotationIntensity={0.8} floatIntensity={0.8}>
        <mesh position={[5, -1, -4]}>
          <Sphere args={[0.6, 64, 64]}>
            <MeshDistortMaterial color="#06b6d4" speed={3} distort={0.4} />
          </Sphere>
        </mesh>
      </Float>
    </>
  );
}

// ============================================
// DASHBOARD COMPONENT
// ============================================
function Dashboard({ stats }) {
  const [formData, setFormData] = useState({
    drugName: "",
    genericName: "",
    manufacturer: "",
    licenseNumber: "",
    quantity: "",
    dosage: "",
    composition: "",
    mrp: "",
    mfgDate: "",
    expDate: "",
  });

  const [qrCodes, setQrCodes] = useState([]);
  const [batchId, setBatchId] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [formErrors, setFormErrors] = useState({});

  const validateForm = () => {
    const errors = {};

    if (!formData.drugName.trim()) errors.drugName = "Drug name required";
    if (!formData.manufacturer.trim())
      errors.manufacturer = "Manufacturer required";
    if (!formData.quantity || formData.quantity < 1)
      errors.quantity = "Valid quantity required";
    if (!formData.mfgDate) errors.mfgDate = "Manufacturing date required";
    if (!formData.expDate) errors.expDate = "Expiry date required";

    if (
      formData.mfgDate &&
      formData.expDate &&
      formData.expDate <= formData.mfgDate
    ) {
      errors.expDate = "Expiry must be after manufacturing date";
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleGenerateQR = async () => {
    if (!validateForm()) {
      alert("⚠️ Please fill all required fields correctly!");
      return;
    }

    setIsGenerating(true);
    setQrCodes([]);
    setBatchId("");

    try {
      const response = await fetch("http://10.22.214.149:8000/generate-batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (data.status === "Success") {
        setQrCodes(data.qr_codes);
        setBatchId(data.batch_id);

        // Reset form
        setFormData({
          drugName: "",
          genericName: "",
          manufacturer: "",
          licenseNumber: "",
          quantity: "",
          dosage: "",
          composition: "",
          mrp: "",
          mfgDate: "",
          expDate: "",
        });
      }
    } catch (error) {
      console.error("Batch generation error:", error);
      alert("Failed to generate batch!");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (formErrors[field]) {
      setFormErrors((prev) => ({ ...prev, [field]: null }));
    }
  };

  return (
    <motion.div
      key="dashboard"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      {/* Hero Header */}
      <div className="hero-section">
        <h1 className="hero-title">Pharmaceutical Integrity System</h1>
        <p className="hero-subtitle">
          Blockchain-Inspired Supply Chain Protection with Cryptographic
          Serialization
        </p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <div>
              <div className="stat-label">Total Batches</div>
              <div className="stat-value">
                {stats.totalBatches.toLocaleString()}
              </div>
              <div className="stat-change">
                <TrendingUp size={14} /> +{stats.growth || 12.5}% from last
                month
              </div>
            </div>
            <div className="stat-icon">
              <Database size={28} color="#ffffff" />
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <div>
              <div className="stat-label">Verified Units</div>
              <div className="stat-value">
                {stats.verified.toLocaleString()}
              </div>
              <div className="stat-change">
                <CheckCircle2 size={14} /> {stats.efficiency}% accuracy
              </div>
            </div>
            <div className="stat-icon">
              <ShieldCheck size={28} color="#ffffff" />
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <div>
              <div className="stat-label">Flagged Items</div>
              <div className="stat-value">{stats.flagged}</div>
              <div className="stat-change" style={{ color: "#f59e0b" }}>
                <AlertTriangle size={14} /> Requires attention
              </div>
            </div>
            <div className="stat-icon">
              <Fingerprint size={28} color="#ffffff" />
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <div>
              <div className="stat-label">System Efficiency</div>
              <div className="stat-value">{stats.efficiency}%</div>
              <div className="stat-change">
                <Zap size={14} /> Optimal performance
              </div>
            </div>
            <div className="stat-icon">
              <Sparkles size={28} color="#ffffff" />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content: Enhanced Form + Activity */}
      <div className="content-grid">
        {/* Left: Enhanced Registration Form */}
        <div className="glass-card">
          <h2 className="card-title">
            <Pill size={24} /> Batch Registration
          </h2>

          {/* Drug Information */}
          <div style={{ marginBottom: "2rem" }}>
            <h3
              style={{
                fontSize: "1rem",
                fontWeight: "600",
                marginBottom: "1rem",
                color: "#06b6d4",
              }}
            >
              Drug Information
            </h3>

            <div className="form-group">
              <label className="form-label">Brand Name *</label>
              <input
                className="form-input"
                placeholder="e.g., Dolo 650"
                value={formData.drugName}
                onChange={(e) => handleChange("drugName", e.target.value)}
                style={{
                  borderColor: formErrors.drugName ? "#ef4444" : undefined,
                }}
              />
              {formErrors.drugName && (
                <div
                  style={{
                    color: "#ef4444",
                    fontSize: "0.75rem",
                    marginTop: "0.25rem",
                  }}
                >
                  {formErrors.drugName}
                </div>
              )}
            </div>

            <div className="form-group">
              <label className="form-label">Generic Name</label>
              <input
                className="form-input"
                placeholder="e.g., Paracetamol"
                value={formData.genericName}
                onChange={(e) => handleChange("genericName", e.target.value)}
              />
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "1rem",
              }}
            >
              <div className="form-group">
                <label className="form-label">Dosage</label>
                <input
                  className="form-input"
                  placeholder="e.g., 650mg"
                  value={formData.dosage}
                  onChange={(e) => handleChange("dosage", e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">MRP (₹)</label>
                <input
                  className="form-input"
                  type="number"
                  placeholder="e.g., 45"
                  value={formData.mrp}
                  onChange={(e) => handleChange("mrp", e.target.value)}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Composition</label>
              <textarea
                className="form-input"
                placeholder="e.g., Paracetamol IP 650mg, Excipients q.s."
                value={formData.composition}
                onChange={(e) => handleChange("composition", e.target.value)}
                rows="2"
              />
            </div>
          </div>

          {/* Manufacturer Information */}
          <div style={{ marginBottom: "2rem" }}>
            <h3
              style={{
                fontSize: "1rem",
                fontWeight: "600",
                marginBottom: "1rem",
                color: "#06b6d4",
              }}
            >
              Manufacturer Details
            </h3>

            <div className="form-group">
              <label className="form-label">Manufacturer Name *</label>
              <input
                className="form-input"
                placeholder="e.g., Micro Labs Ltd."
                value={formData.manufacturer}
                onChange={(e) => handleChange("manufacturer", e.target.value)}
                style={{
                  borderColor: formErrors.manufacturer ? "#ef4444" : undefined,
                }}
              />
              {formErrors.manufacturer && (
                <div
                  style={{
                    color: "#ef4444",
                    fontSize: "0.75rem",
                    marginTop: "0.25rem",
                  }}
                >
                  {formErrors.manufacturer}
                </div>
              )}
            </div>

            <div className="form-group">
              <label className="form-label">License Number</label>
              <input
                className="form-input"
                placeholder="e.g., 20B/UA/2018"
                value={formData.licenseNumber}
                onChange={(e) => handleChange("licenseNumber", e.target.value)}
              />
            </div>
          </div>

          {/* Batch Details */}
          <div style={{ marginBottom: "2rem" }}>
            <h3
              style={{
                fontSize: "1rem",
                fontWeight: "600",
                marginBottom: "1rem",
                color: "#06b6d4",
              }}
            >
              Batch Details
            </h3>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "1rem",
              }}
            >
              <div className="form-group">
                <label className="form-label">Manufacturing Date *</label>
                <input
                  className="form-input"
                  type="date"
                  value={formData.mfgDate}
                  onChange={(e) => handleChange("mfgDate", e.target.value)}
                  style={{
                    borderColor: formErrors.mfgDate ? "#ef4444" : undefined,
                  }}
                />
                {formErrors.mfgDate && (
                  <div
                    style={{
                      color: "#ef4444",
                      fontSize: "0.75rem",
                      marginTop: "0.25rem",
                    }}
                  >
                    {formErrors.mfgDate}
                  </div>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">Expiry Date *</label>
                <input
                  className="form-input"
                  type="date"
                  value={formData.expDate}
                  onChange={(e) => handleChange("expDate", e.target.value)}
                  style={{
                    borderColor: formErrors.expDate ? "#ef4444" : undefined,
                  }}
                />
                {formErrors.expDate && (
                  <div
                    style={{
                      color: "#ef4444",
                      fontSize: "0.75rem",
                      marginTop: "0.25rem",
                    }}
                  >
                    {formErrors.expDate}
                  </div>
                )}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Batch Quantity *</label>
              <input
                className="form-input"
                type="number"
                placeholder="Number of units (max 50)"
                value={formData.quantity}
                onChange={(e) => handleChange("quantity", e.target.value)}
                min="1"
                max="50"
                style={{
                  borderColor: formErrors.quantity ? "#ef4444" : undefined,
                }}
              />
              {formErrors.quantity && (
                <div
                  style={{
                    color: "#ef4444",
                    fontSize: "0.75rem",
                    marginTop: "0.25rem",
                  }}
                >
                  {formErrors.quantity}
                </div>
              )}
            </div>
          </div>

          <button
            className="primary-btn"
            onClick={handleGenerateQR}
            disabled={isGenerating}
          >
            <Lock size={20} />
            {isGenerating
              ? "Generating Batch..."
              : "Generate Cryptographic Batch"}
          </button>

          {/* Batch Info Display */}
          {batchId && (
            <div
              style={{
                marginTop: "1.5rem",
                padding: "1rem",
                background: "rgba(59, 130, 246, 0.1)",
                border: "1px solid rgba(59, 130, 246, 0.3)",
                borderRadius: "12px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                  marginBottom: "0.5rem",
                }}
              >
                <CheckCircle2 size={20} color="#10b981" />
                <span style={{ color: "#10b981", fontWeight: "700" }}>
                  Batch Generated Successfully
                </span>
              </div>
              <div style={{ fontSize: "0.875rem", color: "#94a3b8" }}>
                <strong>Batch ID:</strong>{" "}
                <span style={{ fontFamily: "monospace", color: "#06b6d4" }}>
                  {batchId}
                </span>
              </div>
              <div
                style={{
                  fontSize: "0.875rem",
                  color: "#94a3b8",
                  marginTop: "0.25rem",
                }}
              >
                <strong>Units:</strong> {qrCodes.length}
              </div>
            </div>
          )}

          {/* QR Output */}
          <div className="qr-output" style={{ marginTop: "2rem" }}>
            {qrCodes.length === 0 ? (
              <div
                style={{
                  color: "#475569",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: "1rem",
                }}
              >
                <Fingerprint size={48} />
                <span>Awaiting batch initialization</span>
              </div>
            ) : (
              <div className="qr-grid-container">
                {qrCodes.map((qrUrl, index) => (
                  <div key={index} className="qr-card">
                    <img src={qrUrl} alt={`QR ${index + 1}`} />
                    <small>Unit {index + 1}</small>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right: Activity Panel */}
        <div className="glass-card">
          <h2 className="card-title">
            <Clock size={24} /> Recent Activity
          </h2>

          <div className="activity-item">
            <div className="activity-icon">
              <CheckCircle2 size={20} color="#ffffff" />
            </div>
            <div className="activity-content">
              <div className="activity-title">Batch #8472 Verified</div>
              <div className="activity-meta">
                Paracetamol 500mg • 2 minutes ago
              </div>
            </div>
          </div>

          <div className="activity-item">
            <div className="activity-icon">
              <Globe size={20} color="#ffffff" />
            </div>
            <div className="activity-content">
              <div className="activity-title">Geographic Scan Detected</div>
              <div className="activity-meta">
                Mumbai Distribution Hub • 15 minutes ago
              </div>
            </div>
          </div>

          <div className="activity-item">
            <div className="activity-icon">
              <AlertTriangle size={20} color="#ffffff" />
            </div>
            <div className="activity-content">
              <div className="activity-title">Anomaly Flagged</div>
              <div className="activity-meta">
                Impossible travel speed detected • 1 hour ago
              </div>
            </div>
          </div>

          <div className="activity-item">
            <div className="activity-icon">
              <MapPin size={20} color="#ffffff" />
            </div>
            <div className="activity-content">
              <div className="activity-title">Supply Chain Update</div>
              <div className="activity-meta">Delhi Warehouse • 3 hours ago</div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// ============================================
// MAIN APPLICATION
// ============================================
export default function App() {
  const [activeView, setActiveView] = useState("dashboard");
  const [stats, setStats] = useState({
    totalBatches: 0,
    verified: 0,
    flagged: 0,
    efficiency: 0,
    growth: 0,
  });

  // Fetch real stats on component mount
  useEffect(() => {
    fetch("http://10.22.214.149:8000/stats")
      .then((res) => res.json())
      .then((data) => setStats(data))
      .catch((err) => console.error("Failed to fetch stats:", err));
  }, []);

  return (
    <div className="main-container">
      {/* Background Elements */}
      <div className="gradient-orb orb-1"></div>
      <div className="gradient-orb orb-2"></div>
      <div className="gradient-orb orb-3"></div>

      {/* 3D Canvas Layer */}
      <div className="canvas-layer">
        <Canvas camera={{ position: [0, 0, 8], fov: 50 }}>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          <DNAHelix />
          <FloatingOrbs />
        </Canvas>
      </div>

      {/* Content Layer */}
      <div className="content-wrapper">
        {/* Navbar */}
        <nav className="navbar">
          <div className="brand">
            <div className="brand-icon">
              <ShieldCheck size={24} color="#ffffff" />
            </div>
            <span className="brand-text">MediTrace</span>
          </div>

          <div className="nav-links">
            <button
              className={`nav-btn ${
                activeView === "dashboard" ? "active" : ""
              }`}
              onClick={() => setActiveView("dashboard")}
            >
              <TrendingUp size={18} /> Dashboard
            </button>
            <button
              className={`nav-btn ${activeView === "verify" ? "active" : ""}`}
              onClick={() => setActiveView("verify")}
            >
              <ScanLine size={18} /> Verify
            </button>
            <button
              className={`nav-btn ${activeView === "ledger" ? "active" : ""}`}
              onClick={() => setActiveView("ledger")}
            >
              <FileText size={18} /> Ledger
            </button>
            <button
              className={`nav-btn ${activeView === "monitor" ? "active" : ""}`}
              onClick={() => setActiveView("monitor")}
            >
              <Activity size={18} /> Monitor
            </button>
          </div>

          <div className="status-badge">
            <span className="status-dot"></span> SYSTEM ONLINE
          </div>
        </nav>

        {/* Dynamic Content Views */}
        <AnimatePresence mode="wait">
          {activeView === "dashboard" && <Dashboard stats={stats} />}
          {activeView === "verify" && <VerifyPage />}
          {activeView === "ledger" && <LedgerPage />}
          {activeView === "monitor" && <SystemMonitor />}
        </AnimatePresence>
      </div>
    </div>
  );
}
