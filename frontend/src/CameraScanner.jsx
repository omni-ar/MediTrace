import { useState, useRef, useEffect } from "react";
import jsQR from "jsqr";
import "./CameraScanner.css";

function CameraScanner({ onScanSuccess, onClose }) {
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const animationRef = useRef(null);

  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    try {
      setError(null);
      setScanning(true);

      // Request camera access
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" }, // Use back camera on mobile
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();

        // Start scanning once video is playing
        videoRef.current.onloadedmetadata = () => {
          scanQRCode();
        };
      }
    } catch (err) {
      console.error("Camera error:", err);
      setError("Camera access denied. Please allow camera permissions.");
      setScanning(false);
    }
  };

  const scanQRCode = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    if (video.readyState === video.HAVE_ENOUGH_DATA) {
      // Set canvas size to video size
      canvas.height = video.videoHeight;
      canvas.width = video.videoWidth;

      // Draw video frame to canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Get image data
      const imageData = context.getImageData(0, 0, canvas.width, canvas.height);

      // Scan for QR code
      const code = jsQR(imageData.data, imageData.width, imageData.height, {
        inversionAttempts: "dontInvert",
      });

      if (code) {
        // QR code detected!
        console.log("QR Code detected:", code.data);

        // Draw detection box
        drawDetectionBox(context, code.location);

        // Extract unique_id from QR data
        let uniqueId = code.data;
        if (code.data.includes("id=")) {
          uniqueId = code.data.split("id=")[1];
        }

        // Stop scanning
        stopCamera();

        // Callback with result
        onScanSuccess(uniqueId);
        return;
      }
    }

    // Continue scanning
    animationRef.current = requestAnimationFrame(scanQRCode);
  };

  const drawDetectionBox = (context, location) => {
    // Draw green box around detected QR
    context.beginPath();
    context.moveTo(location.topLeftCorner.x, location.topLeftCorner.y);
    context.lineTo(location.topRightCorner.x, location.topRightCorner.y);
    context.lineTo(location.bottomRightCorner.x, location.bottomRightCorner.y);
    context.lineTo(location.bottomLeftCorner.x, location.bottomLeftCorner.y);
    context.closePath();
    context.lineWidth = 4;
    context.strokeStyle = "#00ff00";
    context.stroke();
  };

  const stopCamera = () => {
    // Stop video stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    // Cancel animation frame
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }

    setScanning(false);
  };

  const handleClose = () => {
    stopCamera();
    onClose();
  };

  return (
    <div className="camera-scanner-overlay">
      <div className="camera-scanner-container">
        <div className="camera-header">
          <h3>📷 Scan QR Code</h3>
          <button className="close-btn" onClick={handleClose}>
            ✕
          </button>
        </div>

        <div className="camera-viewport">
          {error ? (
            <div className="camera-error">
              <p>❌ {error}</p>
              <button onClick={startCamera}>Try Again</button>
            </div>
          ) : (
            <>
              <video
                ref={videoRef}
                className="camera-video"
                playsInline
                muted
              />
              <canvas ref={canvasRef} className="camera-canvas" />

              {scanning && (
                <div className="scan-overlay">
                  <div className="scan-frame"></div>
                  <p className="scan-instruction">
                    Position QR code within the frame
                  </p>
                </div>
              )}
            </>
          )}
        </div>

        <div className="camera-footer">
          <p className="camera-status">
            {scanning ? "🔍 Scanning..." : "⏸️ Camera stopped"}
          </p>
        </div>
      </div>
    </div>
  );
}

export default CameraScanner;
