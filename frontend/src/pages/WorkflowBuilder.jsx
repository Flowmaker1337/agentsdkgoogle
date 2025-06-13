import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  PlayArrow as RunIcon,
} from '@mui/icons-material';

function WorkflowCard({ workflow, onEdit, onDelete, onRun }) {
  return (
    <Card
      sx={{
        background: 'rgba(255, 255, 255, 0.25)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.4)',
        borderRadius: '16px',
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="h6">
            {workflow.name}
          </Typography>
          <Box>
            <IconButton size="small" onClick={onEdit}>
              <EditIcon />
            </IconButton>
            <IconButton size="small" onClick={onDelete}>
              <DeleteIcon />
            </IconButton>
          </Box>
        </Box>
        
        <Typography color="text.secondary" sx={{ mb: 2 }}>
          {workflow.description}
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="contained"
            startIcon={<RunIcon />}
            onClick={onRun}
            size="small"
          >
            Uruchom
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
}

function WorkflowBuilder() {
  const [workflows] = useState([
    {
      id: 1,
      name: 'Lead Processing',
      description: 'Automatyczne przetwarzanie nowych leadów i tworzenie propozycji',
    },
    {
      id: 2,
      name: 'Raport Tygodniowy',
      description: 'Generowanie i wysyłanie raportów tygodniowych',
    },
    {
      id: 3,
      name: 'Onboarding Klienta',
      description: 'Automatyczny proces onboardingu nowych klientów',
    },
  ]);

  const [openDialog, setOpenDialog] = useState(false);

  const handleEdit = (workflowId) => {
    console.log('Edit workflow:', workflowId);
  };

  const handleDelete = (workflowId) => {
    console.log('Delete workflow:', workflowId);
  };

  const handleRun = (workflowId) => {
    console.log('Run workflow:', workflowId);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Builder Workflow
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Nowy Workflow
        </Button>
      </Box>

      <Grid container spacing={3}>
        {workflows.map((workflow) => (
          <Grid item xs={12} md={6} lg={4} key={workflow.id}>
            <WorkflowCard
              workflow={workflow}
              onEdit={() => handleEdit(workflow.id)}
              onDelete={() => handleDelete(workflow.id)}
              onRun={() => handleRun(workflow.id)}
            />
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Nowy Workflow</DialogTitle>
        <DialogContent>
          <Typography color="text.secondary">
            Edytor workflow będzie dostępny wkrótce.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Anuluj</Button>
          <Button variant="contained" onClick={() => setOpenDialog(false)}>
            Zapisz
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default WorkflowBuilder; 