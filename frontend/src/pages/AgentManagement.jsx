import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

function AgentCard({ agent, onStart, onStop, onSettings }) {
  return (
    <Paper
      sx={{
        p: 3,
        background: 'rgba(255, 255, 255, 0.25)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.4)',
        borderRadius: '16px',
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
        <Box>
          <Typography variant="h6" sx={{ mb: 1 }}>
            {agent.name}
          </Typography>
          <Chip
            label={agent.status}
            color={agent.status === 'Aktywny' ? 'success' : 'default'}
            size="small"
          />
        </Box>
        <IconButton onClick={onSettings}>
          <SettingsIcon />
        </IconButton>
      </Box>
      
      <Typography color="text.secondary" sx={{ mb: 2 }}>
        {agent.description}
      </Typography>
      
      <Box sx={{ display: 'flex', gap: 1 }}>
        <Button
          variant="contained"
          startIcon={agent.status === 'Aktywny' ? <StopIcon /> : <StartIcon />}
          onClick={agent.status === 'Aktywny' ? onStop : onStart}
          color={agent.status === 'Aktywny' ? 'error' : 'success'}
          size="small"
        >
          {agent.status === 'Aktywny' ? 'Zatrzymaj' : 'Uruchom'}
        </Button>
      </Box>
    </Paper>
  );
}

function AgentManagement() {
  const [agents] = useState([
    {
      id: 1,
      name: 'Business Agent',
      description: 'Główny agent biznesowy zarządzający workflow i integracjami',
      status: 'Aktywny',
    },
    {
      id: 2,
      name: 'Email Agent',
      description: 'Agent odpowiedzialny za obsługę poczty i komunikacji',
      status: 'Nieaktywny',
    },
    {
      id: 3,
      name: 'Calendar Agent',
      description: 'Agent zarządzający kalendarzem i spotkaniami',
      status: 'Aktywny',
    },
  ]);

  const [openDialog, setOpenDialog] = useState(false);

  const handleStart = (agentId) => {
    console.log('Start agent:', agentId);
  };

  const handleStop = (agentId) => {
    console.log('Stop agent:', agentId);
  };

  const handleSettings = (agentId) => {
    console.log('Settings agent:', agentId);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Zarządzanie Agentami
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Dodaj Agenta
        </Button>
      </Box>

      <Grid container spacing={3}>
        {agents.map((agent) => (
          <Grid item xs={12} md={6} lg={4} key={agent.id}>
            <AgentCard
              agent={agent}
              onStart={() => handleStart(agent.id)}
              onStop={() => handleStop(agent.id)}
              onSettings={() => handleSettings(agent.id)}
            />
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Dodaj nowego agenta</DialogTitle>
        <DialogContent>
          <Typography color="text.secondary">
            Formularz dodawania nowego agenta będzie dostępny wkrótce.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Anuluj</Button>
          <Button variant="contained" onClick={() => setOpenDialog(false)}>
            Dodaj
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default AgentManagement; 