import { useState, useEffect } from "react"; // ← Added useEffect
import { motion } from "framer-motion";
import {
  Search,
  Filter,
  Database,
  CheckCircle2,
  XCircle,
  Package,
  Factory,
  Truck,
  Store,
  ShieldCheck,
  Clock,
  MapPin,
  Hash,
} from "lucide-react";

// Dummy Ledger Data (Fallback if API fails)
const dummyLedgerData = [
  {
    blockNumber: "#00847",
    hash: "0xa3f8c9d2e1b4f7a6c8e9d2b5f8a3c6e9",
    previousHash: "0x7b2d5f8c3e9a1c6db4f7a8e9c2d5f8a3",
    timestamp: "2024-12-19 14:23:17",
    drug: "Dolo 650 (Paracetamol)",
    batchId: "BTH-2024-8472",
    event: "Production Complete",
    location: "Bangalore Factory",
    icon: Factory,
    verified: true,
  },
  {
    blockNumber: "#00848",
    hash: "0xb4c9d2e1a3f8b7a6c8e9d2b5f8a3c6e9",
    previousHash: "0xa3f8c9d2e1b4f7a6c8e9d2b5f8a3c6e9",
    timestamp: "2024-12-19 15:10:42",
    drug: "Dolo 650 (Paracetamol)",
    batchId: "BTH-2024-8472",
    event: "Quality Check Passed",
    location: "Bangalore Factory",
    icon: ShieldCheck,
    verified: true,
  },
];

// Icon mapping for backend data
const iconMap = {
  "Production Complete": Factory,
  "Quality Check Passed": ShieldCheck,
  "Dispatched to Warehouse": Truck,
  "Warehouse Receipt": Store,
  "Retail Scan": Package,
  "Anomaly Detected": XCircle,
};

export default function LedgerPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [filteredData, setFilteredData] = useState(dummyLedgerData);
  const [allBlocks, setAllBlocks] = useState(dummyLedgerData); // ← Store all blocks
  const [isLoading, setIsLoading] = useState(false);

  // ═══════════════════════════════════════════════════
  // FETCH DATA FROM BACKEND ON PAGE LOAD
  // ═══════════════════════════════════════════════════
  useEffect(() => {
    setIsLoading(true);

    fetch("http://127.0.0.1:8000/ledger")
      .then((res) => res.json())
      .then((data) => {
        // Add icon property to each block
        const blocksWithIcons = data.blocks.map((block) => ({
          ...block,
          icon: iconMap[block.event] || Package,
        }));

        setAllBlocks(blocksWithIcons);
        setFilteredData(blocksWithIcons);
        setIsLoading(false);
        console.log("✅ Ledger data loaded from backend");
      })
      .catch((err) => {
        console.error("❌ Backend error, using dummy data:", err);
        setIsLoading(false);
        // Keep dummy data as fallback
      });
  }, []); // Empty dependency array = runs once on mount

  // Handle Search & Filter
  const handleSearch = (query) => {
    setSearchQuery(query);
    applyFilters(query, filterStatus);
  };

  const handleFilterChange = (status) => {
    setFilterStatus(status);
    applyFilters(searchQuery, status);
  };

  const applyFilters = (query, status) => {
    let filtered = allBlocks; // ← Use allBlocks instead of dummy data

    // Filter by search query
    if (query) {
      filtered = filtered.filter(
        (item) =>
          item.drug.toLowerCase().includes(query.toLowerCase()) ||
          item.batchId.toLowerCase().includes(query.toLowerCase()) ||
          item.location.toLowerCase().includes(query.toLowerCase()) ||
          item.event.toLowerCase().includes(query.toLowerCase())
      );
    }

    // Filter by status
    if (status === "verified") {
      filtered = filtered.filter((item) => item.verified);
    } else if (status === "flagged") {
      filtered = filtered.filter((item) => !item.verified);
    }

    setFilteredData(filtered);
  };

  // Calculate Stats
  const totalBlocks = allBlocks.length;
  const verifiedBlocks = allBlocks.filter((b) => b.verified).length;
  const flaggedBlocks = allBlocks.filter((b) => !b.verified).length;
  const successRate =
    totalBlocks > 0 ? ((verifiedBlocks / totalBlocks) * 100).toFixed(1) : "0.0";

  return (
    <div style={{ paddingTop: "2rem" }}>
      {/* Header */}
      <div className="hero-section" style={{ marginBottom: "3rem" }}>
        <h1 className="hero-title" style={{ fontSize: "3rem" }}>
          Blockchain Ledger
        </h1>
        <p className="hero-subtitle">
          Immutable record of all supply chain events with cryptographic proof
        </p>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div style={{ textAlign: "center", padding: "2rem", color: "#64748b" }}>
          <div style={{ fontSize: "1.25rem" }}>Loading ledger data...</div>
        </div>
      )}

      {/* Stats Overview - 4 COLUMN GRID */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "1.5rem",
          marginBottom: "3rem",
        }}
      >
        <div className="stat-card">
          <div className="stat-label">Total Blocks</div>
          <div className="stat-value" style={{ fontSize: "2.5rem" }}>
            {totalBlocks}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Verified</div>
          <div
            className="stat-value"
            style={{ fontSize: "2.5rem", color: "#10b981" }}
          >
            {verifiedBlocks}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Flagged</div>
          <div
            className="stat-value"
            style={{ fontSize: "2.5rem", color: "#ef4444" }}
          >
            {flaggedBlocks}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Success Rate</div>
          <div className="stat-value" style={{ fontSize: "2.5rem" }}>
            {successRate}%
          </div>
        </div>
      </div>

      {/* Search & Filter Bar - FULL WIDTH */}
      <div
        className="glass-card"
        style={{ marginBottom: "2rem", padding: "1.5rem" }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr auto",
            gap: "1.5rem",
            alignItems: "center",
          }}
        >
          {/* Search Input */}
          <div style={{ position: "relative" }}>
            <Search
              size={20}
              color="#64748b"
              style={{
                position: "absolute",
                left: "1rem",
                top: "50%",
                transform: "translateY(-50%)",
              }}
            />
            <input
              className="form-input"
              placeholder="Search by drug name, batch ID, location, or event..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              style={{ paddingLeft: "3rem" }}
            />
          </div>

          {/* Filter Buttons */}
          <div style={{ display: "flex", gap: "0.75rem" }}>
            <button
              className={`nav-btn ${filterStatus === "all" ? "active" : ""}`}
              onClick={() => handleFilterChange("all")}
              style={{ padding: "0.875rem 1.75rem" }}
            >
              <Filter size={16} /> All
            </button>
            <button
              className={`nav-btn ${
                filterStatus === "verified" ? "active" : ""
              }`}
              onClick={() => handleFilterChange("verified")}
              style={{ padding: "0.875rem 1.75rem" }}
            >
              <CheckCircle2 size={16} /> Verified
            </button>
            <button
              className={`nav-btn ${
                filterStatus === "flagged" ? "active" : ""
              }`}
              onClick={() => handleFilterChange("flagged")}
              style={{ padding: "0.875rem 1.75rem" }}
            >
              <XCircle size={16} /> Flagged
            </button>
          </div>
        </div>
      </div>

      {/* Ledger Blocks - 2 COLUMN GRID FOR BETTER USE OF SPACE */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, 1fr)",
          gap: "1.5rem",
        }}
      >
        {filteredData.length === 0 ? (
          <div
            className="glass-card"
            style={{
              padding: "4rem",
              textAlign: "center",
              color: "#64748b",
              gridColumn: "1 / -1",
            }}
          >
            <Database
              size={64}
              style={{ margin: "0 auto 1rem", opacity: 0.3 }}
            />
            <h3 style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>
              No Blocks Found
            </h3>
            <p>Try adjusting your search or filter criteria</p>
          </div>
        ) : (
          filteredData.map((block, index) => {
            const Icon = block.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="glass-card"
                style={{
                  padding: "1.75rem",
                  border: block.verified
                    ? "1px solid rgba(255, 255, 255, 0.1)"
                    : "1px solid rgba(239, 68, 68, 0.3)",
                  position: "relative",
                  overflow: "hidden",
                }}
              >
                {/* Status Indicator */}
                <div
                  style={{
                    position: "absolute",
                    top: 0,
                    right: 0,
                    padding: "0.625rem 1.25rem",
                    background: block.verified
                      ? "linear-gradient(135deg, rgba(16, 185, 129, 0.2), transparent)"
                      : "linear-gradient(135deg, rgba(239, 68, 68, 0.2), transparent)",
                    borderBottomLeftRadius: "12px",
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                    color: block.verified ? "#10b981" : "#ef4444",
                    fontWeight: "700",
                    fontSize: "0.8125rem",
                  }}
                >
                  {block.verified ? (
                    <CheckCircle2 size={14} />
                  ) : (
                    <XCircle size={14} />
                  )}
                  {block.verified ? "VERIFIED" : "FLAGGED"}
                </div>

                {/* Block Header */}
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "auto 1fr",
                    gap: "1.5rem",
                    marginBottom: "1.25rem",
                  }}
                >
                  {/* Icon */}
                  <div
                    style={{
                      width: "60px",
                      height: "60px",
                      background: block.verified
                        ? "linear-gradient(135deg, #3b82f6, #06b6d4)"
                        : "linear-gradient(135deg, #ef4444, #dc2626)",
                      borderRadius: "16px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      boxShadow: block.verified
                        ? "0 6px 24px rgba(59, 130, 246, 0.4)"
                        : "0 6px 24px rgba(239, 68, 68, 0.4)",
                    }}
                  >
                    <Icon size={28} color="#ffffff" />
                  </div>

                  {/* Block Info */}
                  <div>
                    <div
                      style={{
                        fontSize: "1.375rem",
                        fontWeight: "800",
                        marginBottom: "0.5rem",
                        background: "linear-gradient(135deg, #ffffff, #06b6d4)",
                        WebkitBackgroundClip: "text",
                        WebkitTextFillColor: "transparent",
                      }}
                    >
                      Block {block.blockNumber}
                    </div>
                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "0.375rem",
                        fontSize: "0.8125rem",
                        color: "#64748b",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "0.5rem",
                        }}
                      >
                        <Clock size={13} /> {block.timestamp}
                      </div>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "0.5rem",
                        }}
                      >
                        <MapPin size={13} /> {block.location}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Event Details */}
                <div
                  style={{
                    background: "rgba(0, 0, 0, 0.3)",
                    border: "1px solid rgba(255, 255, 255, 0.1)",
                    borderRadius: "12px",
                    padding: "1.25rem",
                    marginBottom: "1.25rem",
                  }}
                >
                  <div style={{ display: "grid", gap: "1rem" }}>
                    <div>
                      <div
                        className="form-label"
                        style={{ marginBottom: "0.375rem" }}
                      >
                        Drug
                      </div>
                      <div
                        style={{
                          color: "#cbd5e1",
                          fontWeight: "600",
                          fontSize: "0.9375rem",
                        }}
                      >
                        {block.drug}
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
                        <div
                          className="form-label"
                          style={{ marginBottom: "0.375rem" }}
                        >
                          Batch ID
                        </div>
                        <div
                          style={{
                            color: "#cbd5e1",
                            fontFamily: "monospace",
                            fontSize: "0.8125rem",
                          }}
                        >
                          {block.batchId}
                        </div>
                      </div>
                      <div>
                        <div
                          className="form-label"
                          style={{ marginBottom: "0.375rem" }}
                        >
                          Event
                        </div>
                        <div
                          style={{
                            color: "#cbd5e1",
                            fontWeight: "600",
                            fontSize: "0.8125rem",
                          }}
                        >
                          {block.event}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Cryptographic Hashes */}
                <div style={{ display: "grid", gap: "1rem" }}>
                  <div>
                    <div
                      className="form-label"
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "0.5rem",
                        marginBottom: "0.5rem",
                      }}
                    >
                      <Hash size={12} /> Current Hash
                    </div>
                    <div
                      style={{
                        padding: "0.625rem",
                        background: "rgba(59, 130, 246, 0.1)",
                        border: "1px solid rgba(59, 130, 246, 0.3)",
                        borderRadius: "8px",
                        fontFamily: "monospace",
                        fontSize: "0.6875rem",
                        color: "#06b6d4",
                        wordBreak: "break-all",
                      }}
                    >
                      {block.hash}
                    </div>
                  </div>
                  <div>
                    <div
                      className="form-label"
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "0.5rem",
                        marginBottom: "0.5rem",
                      }}
                    >
                      <Hash size={12} /> Previous Hash
                    </div>
                    <div
                      style={{
                        padding: "0.625rem",
                        background: "rgba(139, 92, 246, 0.1)",
                        border: "1px solid rgba(139, 92, 246, 0.3)",
                        borderRadius: "8px",
                        fontFamily: "monospace",
                        fontSize: "0.6875rem",
                        color: "#8b5cf6",
                        wordBreak: "break-all",
                      }}
                    >
                      {block.previousHash}
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })
        )}
      </motion.div>
    </div>
  );
}
