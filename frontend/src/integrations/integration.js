import { useState, useEffect } from "react";
import { Box, Button, CircularProgress } from "@mui/material";
import axios from "axios";

export const Integration = ({
  user,
  org,
  integrationParams,
  setIntegrationParams,
  onIntegrationComplete,
  integration,
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  console.log(integration.toLowerCase());
  const handleConnectClick = async () => {
    try {
      setIsConnecting(true);
      const formData = new FormData();
      formData.append("user_id", user);
      formData.append("org_id", org);
      const response = await axios.post(
        `http://localhost:8000/integrations/${integration.toLowerCase()}/authorize`,
        formData
      );
      const authURL = response?.data;

      const screenWidth = window.screen.width;
      const screenHeight = window.screen.height;
      const popupWidth = 800;
      const popupHeight = 800;
      const top = (screenHeight - popupHeight) / 2;
      const left = (screenWidth - popupWidth) / 3;

      const newWindow = window.open(
        authURL,
        "Hubspot Authorization",
        `width=${popupWidth}, height=${popupHeight}, top=${top}, left=${left}`
      );

      const pollTimer = window.setInterval(() => {
        if (newWindow?.closed !== false) {
          window.clearInterval(pollTimer);
          handleWindowClosed();
        }
      }, 200);
    } catch (e) {
      setIsConnecting(false);
      alert(e?.response?.data?.detail);
    }
  };

  const handleWindowClosed = async () => {
    try {
      const formData = new FormData();
      formData.append("user_id", user);
      formData.append("org_id", org);
      const response = await axios.post(
        `http://localhost:8000/integrations/${integration.toLowerCase()}/credentials`,
        formData
      );
      const credentials = response.data;
      if (credentials) {
        setIsConnecting(false);
        setIsConnected(true);
        setIntegrationParams((prev) => ({ ...prev, credentials: credentials, type: integration }));
        onIntegrationComplete(); // Notify parent
      }
      setIsConnecting(false);
    } catch (e) {
      setIsConnecting(false);
      alert(e?.response?.data?.detail);
    }
  };

  useEffect(() => {
    setIsConnected(integrationParams?.credentials ? true : false);
  }, []);

  return (
    <Box sx={{ mt: 2 }}>
      <Box display="flex" alignItems="center" justifyContent="center" sx={{ mt: 2 }}>
        <Button
          variant="contained"
          onClick={isConnected ? () => {} : handleConnectClick}
          color={isConnected ? "success" : "primary"}
          disabled={isConnecting}
          style={{
            pointerEvents: isConnected ? "none" : "auto",
            cursor: isConnected ? "default" : "pointer",
            // opacity: isConnected ? 1 : undefined,
          }}
        >
          {isConnected ? (
            integration + " Connected"
          ) : isConnecting ? (
            <CircularProgress size={20} />
          ) : (
            "Connect to " + integration
          )}
        </Button>
      </Box>
    </Box>
  );
};
