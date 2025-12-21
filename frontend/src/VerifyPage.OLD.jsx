import { useState } from "react";
import { motion } from "framer-motion";
import {
  Camera,
  Upload,
  CheckCircle2,
  XCircle,
  MapPin,
  Calendar,
  Package,
  Factory,
  Warehouse,
  Store,
  AlertTriangle,
  Shield,
  Fingerprint,
} from "lucide-react";

// Dummy Drug Data
const dummyDrugData = {
  name: "Dolo 650 (Paracetamol)",
  batchId: "BTH-2024-8472",
  manufacturer: "Micro Labs Ltd.",
  hash: "a3f8c9d2e1b4f7a6c8e9d2b5f8a3c6e9d2b5f8a3",
  mfgDate: "15-Nov-2024",
  expDate: "14-Nov-2026",
  status: "authentic", // or 'fake'
  locations: [
    {
      place: "Bangalore Factory",
      date: "15-Nov-2024",
      time: "08:30 AM",
      lat: 12.9716,
      lon: 77.5946,
      icon: Factory,
      status: "verified",
    },
    {
      place: "Chennai Warehouse",
      date: "17-Nov-2024",
      time: "02:45 PM",
      lat: 13.0827,
      lon: 80.2707,
      icon: Warehouse,
      status: "verified",
    },
    {
      place: "Mumbai Retail Store",
      date: "19-Nov-2024",
      time: "11:20 AM",
      lat: 19.076,
      lon: 72.8777,
      icon: Store,
      status: "verified",
    },
  ],
};

export default function VerifyPage() {
  const [scanResult, setScanResult] = useState(null);
  const [isScanning, setIsScanning] = useState(false);

  const handleScan = async () => {
    setIsScanning(true);

    // Simulate QR scan - in real app, this would use camera
    const dummyUniqueId = "A1B2C3D4-1"; // Replace with actual scanned ID

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/verify/${dummyUniqueId}`
      );
      const data = await response.json();

      setScanResult(data);
    } catch (error) {
      console.error("Verification error:", error);
    } finally {
      setIsScanning(false);
    }
  };

  // Simulate File Upload
  const handleFileUpload = () => {
    setScanResult(dummyDrugData);
  };

  return (
    <div style={{ paddingTop: "2rem" }}>
      {/* Header */}
      <div className="hero-section" style={{ marginBottom: "3rem" }}>
        <h1 className="hero-title" style={{ fontSize: "3em" }}>
          Drug Verification Portal
        </h1>
        <p className="hero-subtitle">
          Scan QR code or upload image to verify pharmaceutical authenticity
        </p>
      </div>

      {/* Scan Options - FULL WIDTH 2 COLUMN */}
      {!scanResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "2rem",
            marginBottom: "3rem",
          }}
        >
          {/* Camera Scan */}
          <div className="glass-card" style={{ textAlign: "center" }}>
            <div
              style={{
                width: "100px",
                height: "100px",
                margin: "0 auto 1.5rem",
                background: "linear-gradient(135deg, #3b82f6, #06b6d4)",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 8px 32px rgba(59, 130, 246, 0.4)",
              }}
            >
              <Camera size={48} color="#ffffff" />
            </div>
            <h3
              style={{
                fontSize: "1.5rem",
                fontWeight: "700",
                marginBottom: "1rem",
              }}
            >
              Scan with Camera
            </h3>
            <p style={{ color: "#64748b", marginBottom: "2rem" }}>
              Use your device camera to scan QR code directly
            </p>
            <button
              className="primary-btn"
              onClick={handleScan}
              disabled={isScanning}
            >
              {isScanning ? "Scanning..." : "Start Camera Scan"}
            </button>
          </div>

          {/* File Upload */}
          <div className="glass-card" style={{ textAlign: "center" }}>
            <div
              style={{
                width: "100px",
                height: "100px",
                margin: "0 auto 1.5rem",
                background: "linear-gradient(135deg, #8b5cf6, #06b6d4)",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 8px 32px rgba(139, 92, 246, 0.4)",
              }}
            >
              <Upload size={48} color="#ffffff" />
            </div>
            <h3
              style={{
                fontSize: "1.5rem",
                fontWeight: "700",
                marginBottom: "1rem",
              }}
            >
              Upload QR Image
            </h3>
            <p style={{ color: "#64748b", marginBottom: "2rem" }}>
              Upload a photo containing the QR code
            </p>
            <label className="primary-btn" style={{ cursor: "pointer" }}>
              <input
                type="file"
                accept="image/*"
                style={{ display: "none" }}
                onChange={handleFileUpload}
              />
              Choose File
            </label>
          </div>
        </motion.div>
      )}

      {/* Verification Results */}
      {scanResult && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          {/* Status Banner - FULL WIDTH */}
          <div
            style={{
              background:
                scanResult.status === "authentic"
                  ? "linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.1))"
                  : "linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.1))",
              border: `2px solid ${
                scanResult.status === "authentic" ? "#10b981" : "#ef4444"
              }`,
              borderRadius: "24px",
              padding: "2rem",
              marginBottom: "2rem",
              display: "flex",
              alignItems: "center",
              gap: "1.5rem",
            }}
          >
            <div
              style={{
                width: "80px",
                height: "80px",
                background:
                  scanResult.status === "authentic"
                    ? "linear-gradient(135deg, #10b981, #059669)"
                    : "linear-gradient(135deg, #ef4444, #dc2626)",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow:
                  scanResult.status === "authentic"
                    ? "0 8px 32px rgba(16, 185, 129, 0.5)"
                    : "0 8px 32px rgba(239, 68, 68, 0.5)",
              }}
            >
              {scanResult.status === "authentic" ? (
                <CheckCircle2 size={48} color="#ffffff" />
              ) : (
                <XCircle size={48} color="#ffffff" />
              )}
            </div>
            <div style={{ flex: 1 }}>
              <h2
                style={{
                  fontSize: "2rem",
                  fontWeight: "800",
                  marginBottom: "0.5rem",
                  color:
                    scanResult.status === "authentic" ? "#10b981" : "#ef4444",
                }}
              >
                {scanResult.status === "authentic"
                  ? "AUTHENTIC DRUG VERIFIED ✓"
                  : "COUNTERFEIT DETECTED ✗"}
              </h2>
              <p style={{ color: "#94a3b8", fontSize: "1.125rem" }}>
                {scanResult.status === "authentic"
                  ? "This pharmaceutical unit has been cryptographically verified through our supply chain."
                  : "This drug failed verification. Do not consume. Report to authorities immediately."}
              </p>
            </div>
          </div>

          {/* TWO COLUMN LAYOUT: Info Left (40%), Timeline Right (60%) */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "2fr 3fr",
              gap: "2rem",
              marginBottom: "3rem",
            }}
          >
            {/* LEFT COLUMN: Drug Info + Hash */}
            <div
              style={{ display: "flex", flexDirection: "column", gap: "2rem" }}
            >
              {/* Drug Details Card */}
              <div className="glass-card">
                <h3 className="card-title">
                  <Package size={24} /> Product Information
                </h3>

                <div style={{ marginBottom: "1.5rem" }}>
                  <div className="form-label">Drug Name</div>
                  <div
                    style={{
                      fontSize: "1.25rem",
                      fontWeight: "700",
                      background: "linear-gradient(135deg, #ffffff, #06b6d4)",
                      WebkitBackgroundClip: "text",
                      WebkitTextFillColor: "transparent",
                    }}
                  >
                    {scanResult.name}
                  </div>
                </div>

                <div style={{ marginBottom: "1.5rem" }}>
                  <div className="form-label">Batch ID</div>
                  <div style={{ color: "#cbd5e1", fontFamily: "monospace" }}>
                    {scanResult.batchId}
                  </div>
                </div>

                <div style={{ marginBottom: "1.5rem" }}>
                  <div className="form-label">Manufacturer</div>
                  <div style={{ color: "#cbd5e1" }}>
                    {scanResult.manufacturer}
                  </div>
                </div>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: "1rem",
                  }}
                >
                  <div>
                    <div className="form-label">Manufactured</div>
                    <div
                      style={{
                        color: "#cbd5e1",
                        display: "flex",
                        alignItems: "center",
                        gap: "0.5rem",
                        fontSize: "0.875rem",
                      }}
                    >
                      <Calendar size={14} /> {scanResult.mfgDate}
                    </div>
                  </div>
                  <div>
                    <div className="form-label">Expires</div>
                    <div
                      style={{
                        color: "#cbd5e1",
                        display: "flex",
                        alignItems: "center",
                        gap: "0.5rem",
                        fontSize: "0.875rem",
                      }}
                    >
                      <Calendar size={14} /> {scanResult.expDate}
                    </div>
                  </div>
                </div>
              </div>

              {/* Cryptographic Hash Card */}
              <div className="glass-card">
                <h3 className="card-title">
                  <Fingerprint size={24} /> Cryptographic Signature
                </h3>

                <div style={{ marginBottom: "1.5rem" }}>
                  <div className="form-label">SHA-256 Hash</div>
                  <div
                    style={{
                      padding: "1rem",
                      background: "rgba(0, 0, 0, 0.4)",
                      border: "1px solid rgba(59, 130, 246, 0.3)",
                      borderRadius: "12px",
                      fontFamily: "monospace",
                      fontSize: "0.75rem",
                      color: "#06b6d4",
                      wordBreak: "break-all",
                      lineHeight: "1.6",
                    }}
                  >
                    {scanResult.hash}
                  </div>
                </div>

                <div
                  style={{
                    padding: "1rem",
                    background: "rgba(16, 185, 129, 0.1)",
                    border: "1px solid rgba(16, 185, 129, 0.3)",
                    borderRadius: "12px",
                    display: "flex",
                    alignItems: "center",
                    gap: "0.75rem",
                  }}
                >
                  <Shield size={24} color="#10b981" />
                  <div>
                    <div style={{ fontWeight: "600", color: "#10b981" }}>
                      Hash Verified
                    </div>
                    <div style={{ fontSize: "0.875rem", color: "#64748b" }}>
                      Matches blockchain ledger record
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* RIGHT COLUMN: Supply Chain Timeline - BIGGER! */}
            <div className="glass-card">
              <h3 className="card-title">
                <MapPin size={24} /> Supply Chain Journey
              </h3>

              <div style={{ position: "relative", paddingLeft: "3rem" }}>
                {/* Vertical Line */}
                <div
                  style={{
                    position: "absolute",
                    left: "1.25rem",
                    top: "1rem",
                    bottom: "1rem",
                    width: "3px",
                    background: "linear-gradient(180deg, #3b82f6, #06b6d4)",
                    opacity: 0.6,
                  }}
                ></div>

                {scanResult.locations.map((location, index) => {
                  const Icon = location.icon;
                  return (
                    <div
                      key={index}
                      style={{
                        position: "relative",
                        marginBottom:
                          index === scanResult.locations.length - 1
                            ? 0
                            : "2.5rem",
                      }}
                    >
                      {/* Icon Circle - BIGGER */}
                      <div
                        style={{
                          position: "absolute",
                          left: "-2.75rem",
                          width: "50px",
                          height: "50px",
                          background:
                            "linear-gradient(135deg, #3b82f6, #06b6d4)",
                          borderRadius: "50%",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          boxShadow: "0 8px 24px rgba(59, 130, 246, 0.5)",
                          zIndex: 1,
                          border: "3px solid rgba(0, 0, 0, 0.3)",
                        }}
                      >
                        <Icon size={24} color="#ffffff" />
                      </div>

                      {/* Content Box - BIGGER */}
                      <div
                        style={{
                          background: "rgba(0, 0, 0, 0.3)",
                          border: "1px solid rgba(255, 255, 255, 0.1)",
                          borderRadius: "16px",
                          padding: "2rem",
                          transition: "all 0.3s",
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background =
                            "rgba(59, 130, 246, 0.08)";
                          e.currentTarget.style.borderColor =
                            "rgba(59, 130, 246, 0.4)";
                          e.currentTarget.style.transform = "translateX(8px)";
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background =
                            "rgba(0, 0, 0, 0.3)";
                          e.currentTarget.style.borderColor =
                            "rgba(255, 255, 255, 0.1)";
                          e.currentTarget.style.transform = "translateX(0)";
                        }}
                      >
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "flex-start",
                            marginBottom: "1rem",
                          }}
                        >
                          <div>
                            <h4
                              style={{
                                fontSize: "1.375rem",
                                fontWeight: "700",
                                marginBottom: "0.5rem",
                              }}
                            >
                              {location.place}
                            </h4>
                            <div
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "1.5rem",
                                fontSize: "0.9375rem",
                                color: "#64748b",
                              }}
                            >
                              <span
                                style={{
                                  display: "flex",
                                  alignItems: "center",
                                  gap: "0.5rem",
                                }}
                              >
                                <Calendar size={16} /> {location.date}
                              </span>
                              <span style={{ fontWeight: "600" }}>
                                {location.time}
                              </span>
                            </div>
                          </div>
                          <div
                            style={{
                              padding: "0.625rem 1.25rem",
                              background: "rgba(16, 185, 129, 0.2)",
                              border: "1px solid rgba(16, 185, 129, 0.4)",
                              borderRadius: "24px",
                              color: "#10b981",
                              fontSize: "0.875rem",
                              fontWeight: "700",
                            }}
                          >
                            ✓ {location.status.toUpperCase()}
                          </div>
                        </div>
                        <div
                          style={{
                            fontSize: "0.9375rem",
                            color: "#64748b",
                            fontFamily: "monospace",
                            background: "rgba(0, 0, 0, 0.3)",
                            padding: "0.75rem 1rem",
                            borderRadius: "8px",
                            border: "1px solid rgba(255, 255, 255, 0.05)",
                          }}
                        >
                          📍 {location.lat.toFixed(4)}°N,{" "}
                          {location.lon.toFixed(4)}°E
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Action Buttons - CENTER ALIGNED */}
          <div
            style={{
              marginTop: "3rem",
              display: "flex",
              gap: "1rem",
              justifyContent: "center",
            }}
          >
            <button
              className="primary-btn"
              onClick={() => setScanResult(null)}
              style={{
                width: "auto",
                paddingLeft: "3rem",
                paddingRight: "3rem",
              }}
            >
              Scan Another Drug
            </button>
            {scanResult.status === "fake" && (
              <button
                className="primary-btn"
                style={{
                  width: "auto",
                  paddingLeft: "3rem",
                  paddingRight: "3rem",
                  background: "linear-gradient(135deg, #ef4444, #dc2626)",
                }}
              >
                <AlertTriangle size={20} /> Report to Authorities
              </button>
            )}
          </div>
        </motion.div>
      )}
    </div>
  );
}
