import { useState } from "react";
import { motion } from "framer-motion";
import CameraScanner from "./CameraScanner";
import {
  CheckCircle2,
  XCircle,
  MapPin,
  Calendar,
  Package,
  Factory,
  Shield,
  Fingerprint,
  AlertTriangle,
  Upload,
  Keyboard,
  Camera,
} from "lucide-react";

export default function VerifyPage() {
  const [scanResult, setScanResult] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [uniqueId, setUniqueId] = useState("");
  const [uploadedImage, setUploadedImage] = useState(null);
  const [showCamera, setShowCamera] = useState(false);

  // ═══════════════════════════════════════════
  // MANUAL ID VERIFICATION
  // ═══════════════════════════════════════════
  const handleVerify = async () => {
    if (!uniqueId.trim()) {
      alert("⚠️ Please enter a Unique ID!");
      return;
    }

    setIsScanning(true);
    setScanResult(null);

    try {
      // Use your laptop's IP address
      const response = await fetch(
        `http://10.22.214.149:8000/verify/${uniqueId}`
      );
      const data = await response.json();

      console.log("✅ Backend response:", data);
      setScanResult(data);
    } catch (error) {
      console.error("❌ Verification failed:", error);
      alert("Failed to verify. Ensure backend is running on port 8000!");
    } finally {
      setIsScanning(false);
    }
  };

  // ═══════════════════════════════════════════
  // FILE UPLOAD HANDLER - REAL AI ENDPOINT
  // ═══════════════════════════════════════════
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setUploadedImage(e.target.result);
    };
    reader.readAsDataURL(file);

    setIsScanning(true);
    setScanResult(null);

    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append("file", file);

      console.log("📤 Uploading image to AI endpoint...");

      // Call backend AI endpoint using your laptop's IP
      const response = await fetch("http://10.22.214.149:8000/verify-image", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log("✅ AI Verification result:", data);

      if (data.status === "authentic") {
        setScanResult(data);
        if (data.unique_id) {
          setUniqueId(data.unique_id);
        }
      } else if (data.status === "fake") {
        setScanResult(data);
      } else {
        alert(
          "⚠️ " +
            (data.message ||
              "QR code not detected in image. Please try another image.")
        );
      }
    } catch (error) {
      console.error("❌ AI verification failed:", error);
      alert(
        "Failed to process image. Ensure backend is running with OpenCV installed!"
      );
    } finally {
      setIsScanning(false);
    }
  };

  // ═══════════════════════════════════════════
  // CAMERA SCAN HANDLER (Future: WebRTC)
  // ═══════════════════════════════════════════
  const handleCameraScan = (scannedId) => {
    console.log("📷 Camera scanned ID:", scannedId);
    setShowCamera(false);
    setUniqueId(scannedId);

    // Auto-verify the scanned ID
    setTimeout(() => {
      handleVerifyWithId(scannedId);
    }, 300);
  };

  const handleVerifyWithId = async (id) => {
    setIsScanning(true);
    setScanResult(null);

    try {
      const response = await fetch(`http://10.22.214.149:8000/verify/${id}`);
      const data = await response.json();

      console.log("✅ Backend response:", data);
      setScanResult(data);
    } catch (error) {
      console.error("❌ Verification failed:", error);
      alert("Failed to verify. Ensure backend is running on port 8000!");
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div
      style={{
        paddingTop: "2rem",
        maxWidth: "1100px",
        margin: "0 auto",
        paddingLeft: "1.5rem",
        paddingRight: "1.5rem",
      }}
    >
      {/* Header */}
      <div className="hero-section" style={{ marginBottom: "3rem" }}>
        <h1 className="hero-title" style={{ fontSize: "3rem" }}>
          Drug Verification Portal
        </h1>
        <p className="hero-subtitle">
          Multiple verification methods for pharmaceutical authenticity
        </p>
      </div>

      {/* THREE VERIFICATION OPTIONS */}
      {!scanResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "1.5rem",
            marginBottom: "3rem",
          }}
        >
          {/* OPTION 1: Manual ID Entry */}
          <div className="glass-card" style={{ textAlign: "center" }}>
            <div
              style={{
                width: "80px",
                height: "80px",
                margin: "0 auto 1rem",
                background: "linear-gradient(135deg, #3b82f6, #06b6d4)",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 8px 32px rgba(59, 130, 246, 0.4)",
              }}
            >
              <Keyboard size={36} color="#ffffff" />
            </div>

            <h3
              style={{
                fontSize: "1.25rem",
                fontWeight: "700",
                marginBottom: "0.75rem",
              }}
            >
              Enter Unique ID
            </h3>
            <p
              style={{
                color: "#64748b",
                fontSize: "0.875rem",
                marginBottom: "1.5rem",
              }}
            >
              Type ID from medicine package
            </p>

            <div className="form-group" style={{ marginBottom: "1rem" }}>
              <input
                className="form-input"
                placeholder="e.g., 6F58DB68-1"
                value={uniqueId}
                onChange={(e) => setUniqueId(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === "Enter") handleVerify();
                }}
                autoFocus
                style={{ fontSize: "1rem", textAlign: "center" }}
              />
            </div>

            <button
              className="primary-btn"
              onClick={handleVerify}
              disabled={isScanning}
              style={{ fontSize: "0.875rem", padding: "0.875rem" }}
            >
              <Shield size={18} />
              {isScanning ? "Verifying..." : "Verify Now"}
            </button>

            <div
              style={{
                marginTop: "1rem",
                padding: "0.5rem",
                background: "rgba(59, 130, 246, 0.05)",
                borderRadius: "8px",
                fontSize: "0.7rem",
                color: "#64748b",
              }}
            >
              ✅ Currently Active
            </div>
          </div>

          {/* OPTION 2: Upload QR Image (AI/ML Ready) */}
          <div className="glass-card" style={{ textAlign: "center" }}>
            <div
              style={{
                width: "80px",
                height: "80px",
                margin: "0 auto 1rem",
                background: "linear-gradient(135deg, #8b5cf6, #06b6d4)",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 8px 32px rgba(139, 92, 246, 0.4)",
              }}
            >
              <Upload size={36} color="#ffffff" />
            </div>

            <h3
              style={{
                fontSize: "1.25rem",
                fontWeight: "700",
                marginBottom: "0.75rem",
              }}
            >
              Upload QR Image
            </h3>
            <p
              style={{
                color: "#64748b",
                fontSize: "0.875rem",
                marginBottom: "1.5rem",
              }}
            >
              AI will detect & decode QR
            </p>

            {/* Image Preview */}
            {uploadedImage && (
              <div
                style={{
                  marginBottom: "1rem",
                  padding: "0.75rem",
                  background: "rgba(0, 0, 0, 0.3)",
                  borderRadius: "8px",
                }}
              >
                <img
                  src={uploadedImage}
                  alt="Uploaded"
                  style={{
                    maxWidth: "120px",
                    maxHeight: "120px",
                    borderRadius: "8px",
                    border: "2px solid rgba(139, 92, 246, 0.3)",
                  }}
                />
                <div
                  style={{
                    marginTop: "0.5rem",
                    fontSize: "0.75rem",
                    color: "#8b5cf6",
                  }}
                >
                  ✅ Uploaded
                </div>
              </div>
            )}

            <label
              className="primary-btn"
              style={{
                cursor: "pointer",
                fontSize: "0.875rem",
                padding: "0.875rem",
                opacity: isScanning ? 0.6 : 1,
              }}
            >
              <input
                type="file"
                accept="image/*"
                style={{ display: "none" }}
                onChange={handleFileUpload}
                disabled={isScanning}
              />
              <Upload size={18} />
              {isScanning ? "🤖 Processing..." : "Choose File"}
            </label>

            <div
              style={{
                marginTop: "1rem",
                padding: "0.5rem",
                background: "rgba(139, 92, 246, 0.05)",
                borderRadius: "8px",
                fontSize: "0.7rem",
                color: "#64748b",
              }}
            >
              🤖 OpenCV + pyzbar
            </div>
          </div>

          {/* OPTION 3: Camera Scan (Future) */}
          <div className="glass-card" style={{ textAlign: "center" }}>
            <div
              style={{
                width: "80px",
                height: "80px",
                margin: "0 auto 1rem",
                background: "linear-gradient(135deg, #3b82f6, #06b6d4)",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 8px 32px rgba(59, 130, 246, 0.4)",
              }}
            >
              <Camera size={36} color="#ffffff" />
            </div>

            <h3
              style={{
                fontSize: "1.25rem",
                fontWeight: "700",
                marginBottom: "0.75rem",
              }}
            >
              Live Camera Scan
            </h3>
            <p
              style={{
                color: "#64748b",
                fontSize: "0.875rem",
                marginBottom: "1.5rem",
              }}
            >
              Real-time QR detection
            </p>

            <button
              className="primary-btn"
              onClick={() => setShowCamera(true)}
              style={{
                fontSize: "0.875rem",
                padding: "0.875rem",
                background: "linear-gradient(135deg, #3b82f6, #06b6d4)",
              }}
            >
              <Camera size={18} />
              Start Camera
            </button>

            <div
              style={{
                marginTop: "1rem",
                padding: "0.5rem",
                background: "rgba(59, 130, 246, 0.05)",
                borderRadius: "8px",
                fontSize: "0.7rem",
                color: "#64748b",
              }}
            >
              📹 JSQR
            </div>
          </div>
        </motion.div>
      )}

      {/* Results Section */}
      {scanResult && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          {/* Status Banner */}
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
                  ? "✅ AUTHENTIC DRUG VERIFIED"
                  : "❌ COUNTERFEIT DETECTED"}
              </h2>
              <p style={{ color: "#94a3b8", fontSize: "1.125rem" }}>
                {scanResult.status === "authentic"
                  ? "This pharmaceutical unit has been cryptographically verified."
                  : scanResult.message || "Drug not found in database."}
              </p>
            </div>
          </div>

          {/* Details (Only if authentic) */}
          {scanResult.status === "authentic" && (
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "2fr 3fr",
                gap: "2rem",
                marginBottom: "2rem",
              }}
            >
              {/* LEFT: Drug Info + Hash */}
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "2rem",
                }}
              >
                {/* Product Info */}
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
                      <div style={{ color: "#cbd5e1", fontSize: "0.875rem" }}>
                        <Calendar
                          size={14}
                          style={{ display: "inline", marginRight: "0.5rem" }}
                        />
                        {scanResult.mfgDate}
                      </div>
                    </div>
                    <div>
                      <div className="form-label">Expires</div>
                      <div style={{ color: "#cbd5e1", fontSize: "0.875rem" }}>
                        <Calendar
                          size={14}
                          style={{ display: "inline", marginRight: "0.5rem" }}
                        />
                        {scanResult.expDate}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Hash */}
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
                        Hash Verified ✓
                      </div>
                      <div style={{ fontSize: "0.875rem", color: "#64748b" }}>
                        Matches blockchain ledger
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* RIGHT: Supply Chain */}
              <div className="glass-card">
                <h3 className="card-title">
                  <MapPin size={24} /> Supply Chain Journey
                </h3>

                {scanResult.locations && scanResult.locations.length > 0 ? (
                  <div style={{ position: "relative", paddingLeft: "3rem" }}>
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

                    {scanResult.locations.map((location, index) => (
                      <div
                        key={index}
                        style={{
                          position: "relative",
                          marginBottom:
                            index === scanResult.locations.length - 1
                              ? 0
                              : "2rem",
                        }}
                      >
                        <div
                          style={{
                            position: "absolute",
                            left: "-2.5rem",
                            width: "40px",
                            height: "40px",
                            background:
                              "linear-gradient(135deg, #3b82f6, #06b6d4)",
                            borderRadius: "50%",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            boxShadow: "0 8px 24px rgba(59, 130, 246, 0.5)",
                            border: "3px solid rgba(0, 0, 0, 0.3)",
                          }}
                        >
                          <Factory size={20} color="#ffffff" />
                        </div>

                        <div
                          style={{
                            background: "rgba(0, 0, 0, 0.3)",
                            border: "1px solid rgba(255, 255, 255, 0.1)",
                            borderRadius: "16px",
                            padding: "1.5rem",
                          }}
                        >
                          <h4
                            style={{
                              fontSize: "1.125rem",
                              fontWeight: "700",
                              marginBottom: "0.5rem",
                            }}
                          >
                            {location.place}
                          </h4>
                          <div
                            style={{
                              fontSize: "0.875rem",
                              color: "#64748b",
                              marginBottom: "0.5rem",
                            }}
                          >
                            {location.date} • {location.time}
                          </div>
                          <div
                            style={{
                              fontSize: "0.875rem",
                              color: "#64748b",
                              fontFamily: "monospace",
                            }}
                          >
                            📍 {location.lat?.toFixed(4)}°N,{" "}
                            {location.lon?.toFixed(4)}°E
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div
                    style={{
                      textAlign: "center",
                      padding: "2rem",
                      color: "#64748b",
                    }}
                  >
                    No supply chain data available
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Buttons */}
          <div
            style={{
              marginTop: "2rem",
              display: "flex",
              gap: "1rem",
              justifyContent: "center",
            }}
          >
            <button
              className="primary-btn"
              onClick={() => {
                setScanResult(null);
                setUniqueId("");
                setUploadedImage(null);
              }}
              style={{
                width: "auto",
                paddingLeft: "3rem",
                paddingRight: "3rem",
              }}
            >
              ✨ Verify Another Drug
            </button>
          </div>
        </motion.div>
      )}
      {/* 🆕 Camera Scanner Modal - ADD THIS! */}
      {showCamera && (
        <CameraScanner
          onScanSuccess={handleCameraScan}
          onClose={() => setShowCamera(false)}
        />
      )}
    </div>
  );
}
