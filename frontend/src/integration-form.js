import { useState } from "react";
import { Box, Autocomplete, TextField, Typography, Button } from "@mui/material";
import { Integration } from "./integrations/integration";
import { DataForm } from "./data-form";

export const HomePage = () => {
  const [integrationParams, setIntegrationParams] = useState({});
  const [user, setUser] = useState("Prawin");
  const [org, setOrg] = useState("VectorShift");
  const [currType, setCurrType] = useState(null);
  const [isDataFormVisible, setIsDataFormVisible] = useState(false);

  const handleDisconnect = () => {
    setIsDataFormVisible(false);
    setIntegrationParams({});
    setCurrType(null);
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      sx={{
        background: "linear-gradient(to bottom, #1da1f2, #f5f8fa)",
        color: "white",
        padding: "16px",
        position: "relative",
      }}
    >
      {/* Background message */}
      <Box
        position="absolute"
        top="10%"
        left="60%"
        transform="translateX(-50%)"
        textAlign="center"
        zIndex={0}
        color="white"
        maxWidth="80%"
        sx={{ opacity: 0.9 }}
      >
        <Typography variant="h4" sx={{ fontWeight: "bold", mb: 1 }}>
          Seamlessly Connecting Your Tools,
        </Typography>
        <Typography variant="h4" sx={{ fontWeight: "bold" }}>
          Effortlessly Unlocking Your Data.
        </Typography>
        <Typography variant="body1" sx={{ mt: 2, fontSize: "16px" }}>
          Save time, improve revenue, and supercharge your workflows with easy integrations.
        </Typography>
      </Box>

      {/* Integration Form */}
      <Box
        sx={{
          width: "100%",
          maxWidth: "400px",
          padding: "24px",
          borderRadius: "12px",
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
          backgroundColor: "white",
          zIndex: 1,
        }}
      >
        <Typography
          variant="h5"
          align="center"
          sx={{ mb: 3, color: "#1da1f2", fontWeight: "bold" }}
        >
          Welcome to Integrify
        </Typography>

        {!isDataFormVisible && (
          <>
            <Box display="flex" flexDirection="column">
              <TextField
                label="User"
                value={user}
                onChange={(e) => setUser(e.target.value)}
                sx={{
                  mt: 2,
                  borderRadius: "8px",
                  backgroundColor: "#f5f5f5",
                  "& .MuiInputBase-root": { borderRadius: "8px" },
                }}
              />
              <TextField
                label="Organization"
                value={org}
                onChange={(e) => setOrg(e.target.value)}
                sx={{
                  mt: 2,
                  borderRadius: "8px",
                  backgroundColor: "#f5f5f5",
                  "& .MuiInputBase-root": { borderRadius: "8px" },
                }}
              />
              <Autocomplete
                id="integration-type"
                options={["Notion", "Airtable", "Hubspot"]}
                sx={{
                  width: "100%",
                  mt: 2,
                  borderRadius: "8px",
                  backgroundColor: "#f5f5f5",
                }}
                renderInput={(params) => <TextField {...params} label="Integration Type" />}
                onChange={(e, value) => setCurrType(value)}
              />
            </Box>

            {currType && (
              <Box sx={{ mt: 3 }}>
                <Integration
                  user={user}
                  org={org}
                  integrationParams={integrationParams}
                  setIntegrationParams={setIntegrationParams}
                  onIntegrationComplete={() => setIsDataFormVisible(true)}
                  integration={currType}
                />
              </Box>
            )}
          </>
        )}

        {isDataFormVisible && integrationParams?.credentials && (
          <Box sx={{ mt: 3, textAlign: "center" }}>
            <DataForm
              integrationType={integrationParams?.type}
              credentials={integrationParams?.credentials}
            />
            <Button
              variant="contained"
              color="secondary"
              sx={{ borderRadius: "8px", mt: 2 }}
              onClick={handleDisconnect}
            >
              Disintegrate {currType}
            </Button>
          </Box>
        )}
      </Box>
    </Box>
  );
};
